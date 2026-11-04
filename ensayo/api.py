"""API y página del demo: el escudo antiestafas (producto desde el 3-nov) y, detrás, los endpoints de Ensayo.

- POST /api/check: veredicto del escudo para un mensaje, hasta 3 pantallazos y una nota de voz (ensayo.shield).
- POST /api/investigate: pistas aparte del veredicto: la familia de estafas a la que se parece (ensayo.campaigns) y el
  agente que revisa enlaces y dominios con herramientas (ensayo.investigate). No cambia el puntaje del escudo.
- GET/POST /api/whatsapp: webhook de la WhatsApp Cloud API (ensayo.whatsapp): verificación con el verify token y
  mensajes firmados con el App Secret; responde por WhatsApp en segundo plano.
- POST /api/act: el agente de respuesta prepara acciones para la persona (ensayo.act). Simuladas: nada se envía.
- GET /api/network: repetición de alerta temprana con los casos públicos de Reddit (results/scam_network.json).
- GET /api/campaigns: qué está circulando, desde los casos públicos de Reddit (results/scam_campaigns.json).
- GET /api/evidence: la validación preregistrada del escudo (dos intentos, hashes y bandas; results/scam_bands.json).

- Idea anterior (anuncios): no existen en producción (ENSAYO_REAL=1) y fuera de ella solo corren con el servidor falso.
- POST /api/simulate: ensaya las variantes de un anuncio con una población sintética y el rival de llamada única.
- POST /api/chat: una pregunta a una persona de la audiencia sobre su reacción a las variantes.
- POST /api/variants: propone variantes (título, texto e imagen de Muse Image) desde una descripción y una foto.
- GET /api/examples: lanzamientos reales del set de desarrollo (nunca del sellado) para la pantalla "anuncio real", con
  la predicción precalculada del último backtest real de dev si existe (así el jurado ve predicciones reales sin gastar).
- GET /api/backtest: el último resultado de scripts/run_backtest.py (prefiere corridas reales a las de prueba).
- GET /privacy: la política de privacidad (web/privacy.html, fuente en frontend/public/).
- GET /: la página (web/).

Por defecto todo corre con el servidor falso. El modo real usa Spark 1.3 estándar (datos de clientes nunca van al
contributor) en la fase "demo" del medidor, y solo se habilita con ENSAYO_REAL=1 en el entorno. En modo real cada
visitante tiene un tope diario de pedidos (REAL_DAILY_LIMITS); el tope total lo pone la fase "demo" del Ledger.

Uso: uv run uvicorn ensayo.api:app --reload --port 8040
"""

import asyncio
import base64
import binascii
import hashlib
import json
import logging
import os
import time
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any, Literal

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ensayo import DATA, RESULTS, ROOT, act, campaigns, whatsapp
from ensayo.chat import ask_persona
from ensayo.costs import BudgetExceeded
from ensayo.images import MAX_VARIANTS, generate_variants
from ensayo.investigate import investigate as run_investigation
from ensayo.llm import PRODUCT_DEADLINE, ModelClient
from ensayo.population import build_population, spec_from_ad
from ensayo.shield import MAX_IMAGES as SHIELD_MAX_IMAGES
from ensayo.shield import check as shield_check
from ensayo.shield import shrink_image
from ensayo.simulate import simulate_batch, single_call_ranking

log = logging.getLogger(__name__)

WEB = ROOT / "web"  # build de frontend/ (npm run build)
DEV_BATCHES = DATA / "batches" / "dev.json"
AD_IMAGES = DATA / "images"  # copia local de la idea anterior, fuera del repo
MAX_EXAMPLES = 20
# Pedidos en modo real por visitante (IP) y por día. El gasto total lo limita la fase "demo" del Ledger.
REAL_DAILY_LIMITS = {"check": 30, "investigate": 30, "act": 30}
_real_usage: dict[tuple[str, str, str], int] = defaultdict(int)
REAL_MODEL = "muse-spark-1.3"
MODEL_DOWN = "The model isn't responding right now. Please try again in a minute."
REAL_MAX_PERSONAS = 300
MAX_IMAGE_CHARS = 4_000_000  # ~3 MB en base64
MAX_AUDIO_CHARS = 14_000_000  # ~10 MB en base64 (una nota de voz de varios minutos)

# Sin /docs, /redoc ni /openapi.json: el sitio público no necesita publicar el catálogo de la API.
app = FastAPI(title="Second Look", docs_url=None, redoc_url=None, openapi_url=None)
SECURITY_HEADERS = {"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer"}


@app.middleware("http")
async def security_headers(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    response = await call_next(request)
    response.headers.update(SECURITY_HEADERS)
    return response


def real_allowed() -> bool:
    return os.environ.get("ENSAYO_REAL") == "1"


def model_client(mock: bool) -> ModelClient:
    """El cliente del modelo; sin key, un 503 en vez de botar el servidor."""
    try:
        client = ModelClient.from_env(mock=mock)
        client.deadline = PRODUCT_DEADLINE
        return client
    except SystemExit as exc:
        log.error("Modo real sin MODEL_API_KEY")
        raise HTTPException(503, "Real mode is not configured on this server.") from exc


def earlier_idea_off() -> None:
    """En producción no existen los endpoints de la idea anterior: gastarían el tope del demo de Second Look."""
    if real_allowed():
        raise HTTPException(404, "Not found.")


def mock_only(mode: str) -> None:
    """Fuera de producción, los endpoints de la idea anterior corren solo con el servidor falso."""
    if mode != "mock":
        raise HTTPException(403, "Real mode is disabled for this endpoint.")


def guard_real(request: Request, kind: str) -> None:
    """403 si el modo real está apagado; 429 si este visitante ya usó su cupo de hoy."""
    if not real_allowed():
        raise HTTPException(403, "Real mode is disabled on this server.")
    # El último valor es el que agregó nginx; los anteriores los puede inventar el cliente para saltarse el cupo.
    forwarded = request.headers.get("x-forwarded-for", "").rsplit(",", 1)[-1].strip()
    ip = forwarded or (request.client.host if request.client else "?")
    key = (time.strftime("%Y-%m-%d"), ip, kind)
    if _real_usage[key] >= REAL_DAILY_LIMITS[kind]:
        raise HTTPException(429, "Daily limit reached for this demo. Come back tomorrow.")
    _real_usage[key] += 1


class VariantIn(BaseModel):
    title: str = Field("", max_length=200)
    body: str = Field("", max_length=2000)
    image_url: str | None = Field(None, max_length=MAX_IMAGE_CHARS)


class TargetIn(BaseModel):
    age_min: int = Field(18, ge=18, le=65)
    age_max: int = Field(65, ge=18, le=65)
    gender: Literal["All", "Women", "Men"] = "All"
    countries: list[str] = Field(default_factory=lambda: ["GB"], max_length=10)


class SimulateIn(BaseModel):
    brand: str = Field("", max_length=120)
    variants: list[VariantIn] = Field(min_length=2, max_length=6)
    target: TargetIn = TargetIn()
    personas: int = Field(200, ge=20, le=1000)
    mode: Literal["mock", "real"] = "mock"


class VariantsIn(BaseModel):
    brand: str = Field("", max_length=120)
    brief: str = Field("", max_length=2000)
    photo_url: str | None = Field(None, max_length=MAX_IMAGE_CHARS)
    n: int = Field(3, ge=2, le=MAX_VARIANTS)
    mode: Literal["mock", "real"] = "mock"


class TurnIn(BaseModel):
    role: Literal["user", "persona"]
    text: str = Field(max_length=2000)


class ChatIn(BaseModel):
    brand: str = Field("", max_length=120)
    persona: str = Field(min_length=1, max_length=1000)
    variants: list[VariantIn] = Field(min_length=1, max_length=6)
    stopped: list[str] = Field(default_factory=list, max_length=6)
    clicked: list[str] = Field(default_factory=list, max_length=6)
    reason: str = Field("", max_length=500)
    history: list[TurnIn] = Field(default_factory=list, max_length=40)
    question: str = Field(min_length=1, max_length=500)
    mode: Literal["mock", "real"] = "mock"


class CheckIn(BaseModel):
    text: str = Field("", max_length=6000)
    note: str = Field("", max_length=500)
    images: list[str] = Field(default_factory=list, max_length=SHIELD_MAX_IMAGES)
    audio: str | None = Field(None, max_length=MAX_AUDIO_CHARS)
    mode: Literal["mock", "real"] = "mock"


class InvestigateIn(BaseModel):
    text: str = Field("", max_length=12000)  # el mensaje más la transcripción de la nota de voz, si hubo
    images: list[str] = Field(default_factory=list, max_length=SHIELD_MAX_IMAGES)
    mode: Literal["mock", "real"] = "mock"


class ActIn(BaseModel):
    text: str = Field("", max_length=12000)
    images: list[str] = Field(default_factory=list, max_length=SHIELD_MAX_IMAGES)
    verdict: dict[str, Any]
    family: dict[str, Any] | None = None
    clues: list[dict[str, Any]] = Field(default_factory=list, max_length=10)
    mode: Literal["mock", "real"] = "mock"


def to_batch(req: SimulateIn) -> dict[str, Any]:
    """El pedido del demo con la misma forma que un lote de ensayo.batches."""
    ages = sorted((req.target.age_min, req.target.age_max))
    countries = [c.strip().upper()[:2] for c in req.target.countries if c.strip()] or ["GB"]
    variants = [
        {"ad_id": f"v{i + 1}", "title": v.title, "body": v.body, "image_url": v.image_url or None}
        for i, v in enumerate(req.variants)
    ]
    key = hashlib.sha256(json.dumps([req.brand, [v.title + v.body for v in req.variants]]).encode()).hexdigest()[:10]
    return {
        "batch_id": f"demo-{key}",
        "page_name": req.brand or None,
        "target": {
            "target_ages": [str(ages[0]), "65+" if ages[1] >= 65 else str(ages[1])],
            "target_gender": req.target.gender,
            "target_locations": [{"name": c, "type": "countries", "excluded": False} for c in countries],
        },
        "variants": variants,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config")
def config() -> dict[str, Any]:
    return {"real_allowed": real_allowed(), "real_max_personas": REAL_MAX_PERSONAS, "real_model": REAL_MODEL}


@app.post("/api/simulate", dependencies=[Depends(earlier_idea_off)])
async def simulate(req: SimulateIn) -> dict[str, Any]:
    mock_only(req.mode)
    personas = req.personas
    batch = to_batch(req)
    people = build_population(spec_from_ad(batch["target"]), n=personas)
    client = model_client(mock=True)
    spent_before = client.ledger.spent()
    try:
        sim = await simulate_batch(client, batch, people, model=REAL_MODEL, phase="demo", sample_size=8)
        single = await single_call_ranking(client, batch, model=REAL_MODEL, phase="demo")
    except BudgetExceeded as exc:
        raise HTTPException(402, "The demo has reached its spending cap.") from exc
    except RuntimeError as exc:
        log.exception("Fallo de la Model API")
        raise HTTPException(502, MODEL_DOWN) from exc
    finally:
        await client.aclose()
    return {
        "mode": req.mode,
        "model": REAL_MODEL,
        "personas": personas,
        "usd": round(client.ledger.spent() - spent_before, 4),
        "population": sim,
        "single_call": single,
    }


@app.post("/api/check")
async def check(req: CheckIn, request: Request) -> dict[str, Any]:
    if any(len(i) > MAX_IMAGE_CHARS for i in req.images):
        raise HTTPException(413, "Each screenshot must be under 3 MB.")
    try:
        audio = base64.b64decode(req.audio.split(",", 1)[-1], validate=True) if req.audio else None
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(422, "The voice note could not be read.") from exc
    if not (req.text.strip() or req.note.strip() or req.images or audio):
        raise HTTPException(422, "Paste a message, add a screenshot or a voice note.")
    mock = req.mode == "mock"
    if not mock:
        guard_real(request, "check")
    client = model_client(mock)
    spent_before = client.ledger.spent()
    try:
        out = await shield_check(
            client, model=REAL_MODEL, phase="demo", text=req.text, note=req.note, images=req.images, audio=audio
        )
    except BudgetExceeded as exc:
        raise HTTPException(402, "The demo has reached its spending cap.") from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except (RuntimeError, KeyError, TypeError, httpx.HTTPError) as exc:
        log.exception("Fallo del escudo")
        raise HTTPException(502, MODEL_DOWN) from exc
    finally:
        await client.aclose()
    return {"mode": req.mode, "model": REAL_MODEL, "usd": round(client.ledger.spent() - spent_before, 5), **out}


@app.post("/api/investigate")
async def investigate(req: InvestigateIn, request: Request) -> dict[str, Any]:
    if any(len(i) > MAX_IMAGE_CHARS for i in req.images):
        raise HTTPException(413, "Each screenshot must be under 3 MB.")
    if not (req.text.strip() or req.images):
        raise HTTPException(422, "Nothing to investigate.")
    try:
        pics = [shrink_image(u) for u in req.images]
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    mock = req.mode == "mock"
    if not mock:
        guard_real(request, "investigate")
    client = model_client(mock)
    client.effort = "low"
    spent_before = client.ledger.spent()
    data = campaigns.load()
    try:
        family, clues = await asyncio.gather(
            campaigns.match(client, data, model=REAL_MODEL, phase="demo", text=req.text, images=pics) if data else _none(),
            run_investigation(client, model=REAL_MODEL, phase="demo", text=req.text, images=pics),
            return_exceptions=True,
        )
    finally:
        await client.aclose()
    for part in (family, clues):
        if isinstance(part, BudgetExceeded):
            raise HTTPException(402, "The demo has reached its spending cap.")
        if isinstance(part, BaseException):
            log.error(f"Fallo de la investigación: {part!r}")
    return {
        "mode": req.mode,
        "usd": round(client.ledger.spent() - spent_before, 5),
        "family": None if isinstance(family, BaseException) else family,
        "investigation": None if isinstance(clues, BaseException) else clues,
    }


@app.post("/api/act")
async def act_on(req: ActIn, request: Request) -> dict[str, Any]:
    if any(len(i) > MAX_IMAGE_CHARS for i in req.images):
        raise HTTPException(413, "Each screenshot must be under 3 MB.")
    try:
        pics = [shrink_image(u) for u in req.images]
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    mock = req.mode == "mock"
    if not mock and req.verdict.get("band") != "genuine":
        guard_real(request, "act")
    client = model_client(mock)
    client.effort = "low"
    spent_before = client.ledger.spent()
    try:
        out = await act.respond(client, model=REAL_MODEL, phase="demo", verdict=req.verdict, text=req.text, images=pics,
                                family=req.family, clues=req.clues)
    except BudgetExceeded as exc:
        raise HTTPException(402, "The demo has reached its spending cap.") from exc
    except (RuntimeError, KeyError, TypeError, httpx.HTTPError) as exc:
        log.exception("Fallo del agente de respuesta")
        raise HTTPException(502, MODEL_DOWN) from exc
    finally:
        await client.aclose()
    return {"mode": req.mode, "usd": round(client.ledger.spent() - spent_before, 5), **out}


async def _none() -> None:
    return None


_tasks: set[asyncio.Task[None]] = set()


@app.get("/api/whatsapp")
def whatsapp_verify(request: Request) -> PlainTextResponse:
    q = request.query_params
    token = whatsapp.env("WHATSAPP_VERIFY_TOKEN")
    if q.get("hub.mode") == "subscribe" and token and q.get("hub.verify_token") == token:
        return PlainTextResponse(q.get("hub.challenge", ""))
    raise HTTPException(403, "Verification failed.")


@app.post("/api/whatsapp")
async def whatsapp_webhook(request: Request) -> dict[str, str]:
    body = await request.body()
    if not whatsapp.valid_signature(body, request.headers.get("x-hub-signature-256")):
        raise HTTPException(401, "Bad signature.")
    if not real_allowed():
        raise HTTPException(403, "Real mode is disabled on this server.")
    # Meta espera un 200 rápido y reintenta si no llega: se responde ya y la revisión sigue en segundo plano.
    for message in whatsapp.messages_in(json.loads(body or b"{}")):
        if whatsapp.first_time(message.get("id", "")):
            task = asyncio.create_task(whatsapp.handle(message))
            _tasks.add(task)
            task.add_done_callback(_tasks.discard)
    return {"status": "ok"}


@app.get("/api/campaigns")
def campaigns_view() -> dict[str, Any]:
    data = campaigns.load()
    if not data:
        raise HTTPException(404, "No campaign data yet.")
    return data


@app.get("/api/network")
def network_view() -> dict[str, Any]:
    path = RESULTS / "scam_network.json"
    if not path.exists():
        raise HTTPException(404, "No network replay yet.")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/evidence")
def evidence() -> dict[str, Any]:
    path = RESULTS / "scam_bands.json"
    if not path.exists():
        raise HTTPException(404, "No validation results yet.")
    return json.loads(path.read_text(encoding="utf-8"))


@app.post("/api/chat", dependencies=[Depends(earlier_idea_off)])
async def chat(req: ChatIn) -> dict[str, Any]:
    mock_only(req.mode)
    variants = [
        {"ad_id": f"v{i + 1}", "title": v.title, "body": v.body, "image_url": v.image_url or None}
        for i, v in enumerate(req.variants)
    ]
    client = model_client(mock=True)
    spent_before = client.ledger.spent()
    try:
        answer = await ask_persona(
            client,
            model=REAL_MODEL,
            phase="demo",
            brand=req.brand,
            persona=req.persona,
            variants=variants,
            stopped=req.stopped,
            clicked=req.clicked,
            reason=req.reason,
            history=[t.model_dump() for t in req.history],
            question=req.question,
        )
    except BudgetExceeded as exc:
        raise HTTPException(402, "The demo has reached its spending cap.") from exc
    except RuntimeError as exc:
        log.exception("Fallo de la Model API")
        raise HTTPException(502, MODEL_DOWN) from exc
    finally:
        await client.aclose()
    return {"mode": req.mode, "usd": round(client.ledger.spent() - spent_before, 4), "answer": answer}


@app.post("/api/variants", dependencies=[Depends(earlier_idea_off)])
async def variants(req: VariantsIn) -> dict[str, Any]:
    if not req.brief.strip() and not req.photo_url:
        raise HTTPException(422, "Describe the product or upload a photo.")
    mock_only(req.mode)
    client = model_client(mock=True)
    spent_before = client.ledger.spent()
    try:
        out = await generate_variants(
            client, brand=req.brand, brief=req.brief, n=req.n, photo_url=req.photo_url, model=REAL_MODEL, phase="demo"
        )
    except BudgetExceeded as exc:
        raise HTTPException(402, "The demo has reached its spending cap.") from exc
    except (RuntimeError, ValueError) as exc:
        log.exception("Fallo al generar variantes")
        raise HTTPException(502, f"Could not generate the versions: {exc}") from exc
    finally:
        await client.aclose()
    return {"mode": req.mode, "usd": round(client.ledger.spent() - spent_before, 4), "variants": out}


def example_target(target: dict[str, Any]) -> dict[str, Any]:
    """La segmentación de un lote con la forma de TargetIn."""
    ages = target.get("target_ages") or ["18", "65"]
    try:
        age_min = int(str(ages[0]).rstrip("+"))
        age_max = int(str(ages[-1]).rstrip("+"))
    except ValueError:
        age_min, age_max = 18, 65
    gender = str(target.get("target_gender") or "All").lower()
    countries = [
        str(loc.get("name"))[:2].upper()
        for loc in target.get("target_locations") or []
        if not loc.get("excluded") and len(str(loc.get("name") or "")) == 2
    ]
    return {
        "age_min": max(18, min(age_min, 65)),
        "age_max": max(18, min(age_max, 65)),
        "gender": "Women" if gender in ("women", "female") else "Men" if gender in ("men", "male") else "All",
        "countries": countries[:10] or ["GB"],
    }


def dev_predictions() -> dict[str, dict[str, Any]]:
    """Predicciones del último backtest real sobre dev (results/backtest_dev*.json sin _mock), por lote."""
    files = sorted((p for p in RESULTS.glob("backtest_dev*.json") if "_mock" not in p.name), key=lambda p: p.stat().st_mtime)
    if not files:
        return {}
    data = json.loads(files[-1].read_text(encoding="utf-8"))
    if data.get("mock"):
        return {}
    cfg = data.get("config") or {}
    out = {}
    for r in data.get("batches") or []:
        pop = r["population"]
        out[r["batch_id"]] = {
            "model": cfg.get("model"),
            "personas": cfg.get("personas"),
            "ran_at": data.get("ran_at"),
            "ranking": pop["ranking"],
            "stats": {ad: {"stop_rate": st["stop_rate"], "click_rate": st["click_rate"]} for ad, st in pop["stats"].items()},
            "single_call": (r.get("single_call") or {}).get("ranking"),
        }
    return out


def ad_image_url(ad_id: str, remote: str | None) -> str | None:
    """La copia local si existe (ruta relativa: funciona bajo cualquier ruta); si no, la URL original."""
    return f"api/ad-image/{ad_id}" if (AD_IMAGES / f"{ad_id}.jpg").exists() else remote


@app.get("/api/ad-image/{ad_id}", dependencies=[Depends(earlier_idea_off)])
def ad_image(ad_id: str) -> FileResponse:
    if not ad_id.isdigit():
        raise HTTPException(404, "Unknown ad.")
    path = AD_IMAGES / f"{ad_id}.jpg"
    if not path.exists():
        raise HTTPException(404, "Unknown ad.")
    return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=604800"})


@app.get("/api/examples", dependencies=[Depends(earlier_idea_off)])
def examples() -> list[dict[str, Any]]:
    """Lotes reales del set de desarrollo con su alcance real. El set sellado nunca sale por aquí."""
    if not DEV_BATCHES.exists():
        return []
    predictions = dev_predictions()
    batches = [
        b
        for b in json.loads(DEV_BATCHES.read_text(encoding="utf-8"))
        if not b.get("sealed")
    ]
    # Primero los que tienen imagen en todas las variantes y 3 o 4 versiones: se ven mejor en el demo.
    batches.sort(
        key=lambda b: (b["batch_id"] not in predictions, not all(v.get("image_url") for v in b["variants"]), abs(len(b["variants"]) - 3), b["batch_id"])
    )
    out = []
    for b in batches[:MAX_EXAMPLES]:
        variants = b["variants"][:6]
        out.append(
            {
                "batch_id": b["batch_id"],
                "brand": b.get("page_name") or "",
                "week": b.get("week"),
                "target": example_target(b.get("target") or {}),
                "variants": [
                    {"ad_id": v["ad_id"], "title": v.get("title") or "", "body": v.get("body") or "", "image_url": ad_image_url(v["ad_id"], v.get("image_url"))}
                    for v in variants
                ],
                "reach": {v["ad_id"]: (b.get("labels") or {}).get(v["ad_id"], {}).get("reach") for v in variants},
                "prediction": predictions.get(b["batch_id"]),
            }
        )
    return out


@app.get("/api/backtest", dependencies=[Depends(earlier_idea_off)])
def backtest() -> dict[str, Any]:
    files = sorted(RESULTS.glob("backtest_*.json"), key=lambda p: ("_mock" not in p.name, p.stat().st_mtime))
    scored = [p for p in files if "summary" in json.loads(p.read_text(encoding="utf-8"))]
    if not scored:
        raise HTTPException(404, "No backtest results yet.")
    data = json.loads(scored[-1].read_text(encoding="utf-8"))
    return {
        "file": scored[-1].name,
        "mock": data.get("mock"),
        "source": data.get("source"),
        "ran_at": data.get("ran_at"),
        "usd": data.get("usd"),
        "batches": len(data.get("batches") or []),
        "personas": (data.get("config") or {}).get("personas"),
        "model": (data.get("config") or {}).get("model"),
        "summary": data["summary"],
    }


@app.get("/privacy")
def privacy() -> FileResponse:
    return FileResponse(WEB / "privacy.html", headers={"Cache-Control": "no-cache"})


@app.get("/")
def index() -> FileResponse:
    # Sin caché: el index apunta a los bundles con hash, así cada despliegue se ve al recargar.
    return FileResponse(WEB / "index.html", headers={"Cache-Control": "no-cache"})


app.mount("/static", StaticFiles(directory=WEB / "static", check_dir=False), name="static")
