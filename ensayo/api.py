"""API y página del demo de Ensayo.

- POST /api/simulate: ensaya las variantes de un anuncio con una población sintética y el rival de llamada única.
- POST /api/chat: una pregunta a una persona de la audiencia sobre su reacción a las variantes.
- POST /api/variants: propone variantes (título, texto e imagen de Muse Image) desde una descripción y una foto.
- GET /api/examples: lanzamientos reales del set de desarrollo (nunca del sellado) para la pantalla "anuncio real", con
  la predicción precalculada del último backtest real de dev si existe (así el jurado ve predicciones reales sin gastar).
- GET /api/backtest: el último resultado de scripts/run_backtest.py (prefiere corridas reales a las de prueba).
- GET /: la página (web/).

Por defecto todo corre con el servidor falso. El modo real usa Spark 1.3 estándar (datos de clientes nunca van al
contributor) en la fase "demo" del medidor, y solo se habilita con ENSAYO_REAL=1 en el entorno. En modo real cada
visitante tiene un tope diario de pedidos (REAL_DAILY_LIMITS); el tope total lo pone la fase "demo" del Ledger.

Uso: uv run uvicorn ensayo.api:app --reload --port 8040
"""

import hashlib
import json
import logging
import os
import time
from collections import defaultdict
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ensayo import DATA, RESULTS, ROOT
from ensayo.chat import ask_persona
from ensayo.costs import BudgetExceeded
from ensayo.images import MAX_VARIANTS, generate_variants
from ensayo.llm import ModelClient
from ensayo.population import build_population, spec_from_ad
from ensayo.simulate import simulate_batch, single_call_ranking

log = logging.getLogger(__name__)

WEB = ROOT / "web"  # build de frontend/ (npm run build)
DEV_BATCHES = DATA / "batches" / "dev.json"
AD_IMAGES = DATA / "images"  # scripts/download_images.py: copia local porque las URLs de fbcdn vencen
MAX_EXAMPLES = 20
# Pedidos en modo real por visitante (IP) y por día. El gasto total lo limita la fase "demo" del Ledger.
REAL_DAILY_LIMITS = {"simulate": 5, "variants": 3, "chat": 30}
_real_usage: dict[tuple[str, str, str], int] = defaultdict(int)
REAL_MODEL = "muse-spark-1.3"
REAL_MAX_PERSONAS = 300
MAX_IMAGE_CHARS = 4_000_000  # ~3 MB en base64

app = FastAPI(title="Ensayo para anuncios")


def real_allowed() -> bool:
    return os.environ.get("ENSAYO_REAL") == "1"


def guard_real(request: Request, kind: str) -> None:
    """403 si el modo real está apagado; 429 si este visitante ya usó su cupo de hoy."""
    if not real_allowed():
        raise HTTPException(403, "Real mode is disabled on this server.")
    ip = request.client.host if request.client else "?"
    key = (time.strftime("%Y-%m-%d"), ip, kind)
    if _real_usage[key] >= REAL_DAILY_LIMITS[kind]:
        raise HTTPException(429, "Daily limit reached for this demo. Try the real-ad examples, or come back tomorrow.")
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


@app.post("/api/simulate")
async def simulate(req: SimulateIn, request: Request) -> dict[str, Any]:
    mock = req.mode == "mock"
    if not mock:
        guard_real(request, "simulate")
    personas = req.personas if mock else min(req.personas, REAL_MAX_PERSONAS)
    batch = to_batch(req)
    people = build_population(spec_from_ad(batch["target"]), n=personas)
    client = ModelClient.from_env(mock=mock)
    spent_before = client.ledger.spent()
    try:
        sim = await simulate_batch(client, batch, people, model=REAL_MODEL, phase="demo", sample_size=8)
        single = await single_call_ranking(client, batch, model=REAL_MODEL, phase="demo")
    except BudgetExceeded as exc:
        raise HTTPException(402, "The demo has reached its spending cap. The real-ad examples still work.") from exc
    except RuntimeError as exc:
        log.exception("Fallo de la Model API")
        raise HTTPException(502, f"The Model API returned an error: {exc}") from exc
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


@app.post("/api/chat")
async def chat(req: ChatIn, request: Request) -> dict[str, Any]:
    mock = req.mode == "mock"
    if not mock:
        guard_real(request, "chat")
    variants = [
        {"ad_id": f"v{i + 1}", "title": v.title, "body": v.body, "image_url": v.image_url or None}
        for i, v in enumerate(req.variants)
    ]
    client = ModelClient.from_env(mock=mock)
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
        raise HTTPException(402, "The demo has reached its spending cap. The real-ad examples still work.") from exc
    except RuntimeError as exc:
        log.exception("Fallo de la Model API")
        raise HTTPException(502, f"The Model API returned an error: {exc}") from exc
    finally:
        await client.aclose()
    return {"mode": req.mode, "usd": round(client.ledger.spent() - spent_before, 4), "answer": answer}


@app.post("/api/variants")
async def variants(req: VariantsIn, request: Request) -> dict[str, Any]:
    if not req.brief.strip() and not req.photo_url:
        raise HTTPException(422, "Describe the product or upload a photo.")
    mock = req.mode == "mock"
    if not mock:
        guard_real(request, "variants")
    client = ModelClient.from_env(mock=mock)
    spent_before = client.ledger.spent()
    try:
        out = await generate_variants(
            client, brand=req.brand, brief=req.brief, n=req.n, photo_url=req.photo_url, model=REAL_MODEL, phase="demo"
        )
    except BudgetExceeded as exc:
        raise HTTPException(402, "The demo has reached its spending cap. The real-ad examples still work.") from exc
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
    """La copia local si existe (ruta relativa: funciona bajo /ensayo/); si no, la URL original."""
    return f"api/ad-image/{ad_id}" if (AD_IMAGES / f"{ad_id}.jpg").exists() else remote


@app.get("/api/ad-image/{ad_id}")
def ad_image(ad_id: str) -> FileResponse:
    if not ad_id.isdigit():
        raise HTTPException(404, "Unknown ad.")
    path = AD_IMAGES / f"{ad_id}.jpg"
    if not path.exists():
        raise HTTPException(404, "Unknown ad.")
    return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=604800"})


@app.get("/api/examples")
def examples() -> list[dict[str, Any]]:
    """Lotes reales del set de desarrollo con su alcance real. El set sellado nunca sale por aquí."""
    if not DEV_BATCHES.exists():
        return []
    predictions = dev_predictions()
    batches = [b for b in json.loads(DEV_BATCHES.read_text(encoding="utf-8")) if not b.get("sealed")]
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


@app.get("/api/backtest")
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


@app.get("/")
def index() -> FileResponse:
    # Sin caché: el index apunta a los bundles con hash, así cada despliegue se ve al recargar.
    return FileResponse(WEB / "index.html", headers={"Cache-Control": "no-cache"})


app.mount("/static", StaticFiles(directory=WEB / "static", check_dir=False), name="static")
