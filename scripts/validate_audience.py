"""Hipótesis nueva (2-nov): ¿la IA predice a QUIÉN le muestra Meta un anuncio, a partir del creativo?

Con segmentación amplia (todos, 18 a 65+), Meta reparte cada anuncio a audiencias muy distintas: la proporción de
mujeres alcanzadas va del 5 % al 99 % y, dentro de una misma marca, el creativo la mueve ±10–20 puntos.

Prueba barata, antes de construir nada:
- Anuncios de la Ad Library entregados después del 2-sep-2026, segmentación amplia, alcance ≥ 1.000, con imagen,
  de páginas con ≥ 5 anuncios así (máx. MAX_PER_PAGE por página).
- Una llamada por anuncio a Spark 1.3 contributor (datos públicos): imagen + texto → % de mujeres, % 18–34, % 55+.
- Métrica fijada antes de correr: correlación DENTRO de cada página (desvío de la predicción respecto del promedio
  de la página contra el desvío real), con nulo por permutación dentro de la página. Así no cuenta saber que una
  marca de joyas llega a mujeres; cuenta acertar qué versión llega a más mujeres que las otras de la misma marca.
- Se informa también por mitades A/B de páginas (por hash del page_id) para ver si se sostiene.

Uso: uv run python scripts/validate_audience.py [--limit N] [--yes]
"""

import argparse
import asyncio
import base64
import glob
import hashlib
import io
import json
import logging
import random
import statistics as st
from collections import defaultdict
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError

from ensayo import DATA, RESULTS
from ensayo.llm import ModelClient, estimate_call_usd, extract_json
from ensayo.population import Persona, load_or_build, spec_from_ad
from ensayo.simulate import simulation_messages

log = logging.getLogger("audience")

AGES = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
CUTOFF = "2026-09-02"
MAX_PER_PAGE = 20
IMAGES = DATA / "images"
MODEL = "muse-spark-1.3-contributor"
TARGETS = ("women", "age_18_34", "age_55_plus")

SYSTEM = "You are an expert in how Meta delivers ads on Facebook and Instagram. Reply with valid JSON only."


def broad(it: dict[str, Any]) -> bool:
    ages = it.get("target_ages") or []
    return bool(ages) and ages[-1] == "65+" and int(ages[0]) <= 25 and it.get("target_gender") == "All"


def truth(it: dict[str, Any]) -> dict[str, float] | None:
    by_age: dict[str, float] = defaultdict(float)
    women = men = 0.0
    for country in it.get("age_country_gender_reach_breakdown") or []:
        for g in country.get("age_gender_breakdowns") or []:
            by_age[g["age_range"]] += sum(g.get(k) or 0 for k in ("male", "female", "unknown"))
            women += g.get("female") or 0
            men += g.get("male") or 0
    total = sum(by_age.values())
    if total < 1000 or women + men == 0:
        return None
    return {
        "women": women / (women + men),
        "age_18_34": (by_age["18-24"] + by_age["25-34"]) / total,
        "age_55_plus": (by_age["55-64"] + by_age["65+"]) / total,
        "reach": total,
    }


def load_ads(raw: Path = DATA / "raw" / "ad_library") -> list[dict[str, Any]]:
    by_page: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: set[str] = set()
    for path in sorted(glob.glob(str(raw / "*.json"))):
        for it in json.loads(Path(path).read_text(encoding="utf-8")).get("data") or []:
            ad_id = str(it["id"])
            if ad_id in seen or (it.get("ad_delivery_start_time") or "") <= CUTOFF or not broad(it):
                continue
            t = truth(it)
            if t is None or not it.get("image_url"):
                continue
            seen.add(ad_id)
            countries = [x["name"] for x in it.get("target_locations") or [] if not x.get("excluded")]
            by_page[str(it["page_id"])].append(
                {
                    "ad_id": ad_id,
                    "page_id": str(it["page_id"]),
                    "page_name": it.get("page_name"),
                    "body": " ".join(((it.get("ad_creative_bodies") or [""])[0] or "").split()),
                    "title": ((it.get("ad_creative_link_titles") or [""])[0] or "").strip(),
                    "countries": countries,
                    "target": {k: it.get(k) for k in ("target_ages", "target_gender", "target_locations")},
                    "image_url": it["image_url"],
                    "truth": t,
                }
            )
    ads: list[dict[str, Any]] = []
    for page_ads in by_page.values():
        if len(page_ads) >= 5:
            ads += sorted(page_ads, key=lambda a: a["ad_id"])[:MAX_PER_PAGE]
    return ads


async def image_data_uri(http: httpx.AsyncClient, ad: dict[str, Any]) -> str | None:
    path = IMAGES / f"{ad['ad_id']}.jpg"
    if not path.exists():
        try:
            r = await http.get(ad["image_url"], timeout=30)
            r.raise_for_status()
            img = Image.open(io.BytesIO(r.content)).convert("RGB")
        except (httpx.HTTPError, UnidentifiedImageError, OSError) as exc:
            log.warning(f"{ad['ad_id']}: sin imagen ({exc})")
            return None
        img.thumbnail((720, 720))
        IMAGES.mkdir(parents=True, exist_ok=True)
        img.save(path, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


def messages(ad: dict[str, Any], image: str) -> list[dict[str, Any]]:
    text = (
        f"Advertiser: {ad['page_name']}. Countries: {', '.join(ad['countries']) or 'EU'}.\n"
        "Targeting: everyone, men and women, age 18 to 65+ (broad targeting). Meta's delivery system then shows "
        "the ad to the people most likely to respond to it, so the creative decides who actually sees it.\n"
        f"Ad text: {ad['body'] or '(none)'}\nHeadline: {ad['title'] or '(none)'}\nImage:"
    )
    footer = (
        "Estimate who this ad actually reached: the percentage of people reached who were women, the percentage "
        "aged 18-34 and the percentage aged 55 or older. Judge this specific creative, not only the brand.\n"
        'Format: {"women": 55, "age_18_34": 40, "age_55_plus": 15, "reason": "max 15 words"}'
    )
    content = [
        {"type": "text", "text": text},
        {"type": "image_url", "image_url": {"url": image}},
        {"type": "text", "text": footer},
    ]
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": content}]


async def predict(client: ModelClient, http: httpx.AsyncClient, ad: dict[str, Any]) -> dict[str, Any] | None:
    image = await image_data_uri(http, ad)
    if image is None:
        return None
    msgs = messages(ad, image)
    try:
        res = await client.chat(
            MODEL, msgs, phase="pruebas", max_tokens=150, upcoming_usd=estimate_call_usd(MODEL, 1200, 400, 300), note=f"quién {ad['ad_id']}"
        )
    except RuntimeError as exc:
        log.warning(f"{ad['ad_id']}: {exc}")
        return None
    try:
        body = extract_json(res.text)
        return {k: float(body[k]) / 100 for k in TARGETS} | {"reason": body.get("reason")}
    except (ValueError, KeyError, TypeError) as exc:
        log.warning(f"{ad['ad_id']}: {exc}")
        return None


async def predict_population(
    client: ModelClient, http: httpx.AsyncClient, ad: dict[str, Any], personas: int, per_call: int = 20
) -> dict[str, Any] | None:
    """La población ve el anuncio en su feed; la audiencia predicha es quien frena (frenar = 1, clic suma 1)."""
    image = await image_data_uri(http, ad)
    if image is None:
        return None
    people = load_or_build(spec_from_ad(ad["target"]), n=personas, seed=7)
    batch = {"page_name": ad["page_name"], "variants": [{"body": ad["body"], "title": ad["title"], "image_url": image}]}

    async def one(group: list[Persona]) -> list[tuple[Persona, float]]:
        msgs = simulation_messages(batch, [0], group, view="feed")
        try:
            res = await client.chat(
                MODEL, msgs, phase="pruebas", max_tokens=per_call * 40, upcoming_usd=estimate_call_usd(MODEL, 4000, 800, 300),
                note=f"quién-pob {ad['ad_id']}",
            )
            body = extract_json(res.text)
        except (RuntimeError, ValueError) as exc:
            log.warning(f"{ad['ad_id']}: {exc}")
            return []
        out = []
        for r in body.get("reactions") or []:
            try:
                person = group[int(r.get("p")) - 1]
            except (TypeError, ValueError, IndexError):
                continue
            w = (1.0 if r.get("stop") else 0.0) + (1.0 if r.get("stop") and r.get("click") else 0.0)
            out.append((person, w))
        return out

    groups = [people[i : i + per_call] for i in range(0, len(people), per_call)]
    pairs = [x for chunk in await asyncio.gather(*(one(g) for g in groups)) for x in chunk]
    total = sum(w for _, w in pairs)
    if total == 0:
        return None
    share = lambda cond: sum(w for p, w in pairs if cond(p)) / total  # noqa: E731
    return {
        "women": share(lambda p: p.gender == "female"),
        "age_18_34": share(lambda p: p.age_bucket in ("18-24", "25-34")),
        "age_55_plus": share(lambda p: p.age_bucket in ("55-64", "65+")),
        "stoppers": total,
    }


def pearson(x: list[float], y: list[float]) -> float:
    mx, my = st.mean(x), st.mean(y)
    sx = sum((a - mx) ** 2 for a in x) ** 0.5
    sy = sum((b - my) ** 2 for b in y) ** 0.5
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx and sy else 0.0


def within_page(rows: list[dict[str, Any]], key: str, perms: int = 2000) -> dict[str, Any]:
    pages: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        pages[r["page_id"]].append(r)
    groups = []
    for g in pages.values():
        if len(g) < 3:
            continue
        mp = st.mean(r["pred"][key] for r in g)
        mt = st.mean(r["truth"][key] for r in g)
        groups.append(([r["pred"][key] - mp for r in g], [r["truth"][key] - mt for r in g]))
    if not groups:
        return {"pages": 0}
    xs = [x for p, _ in groups for x in p]
    ys = [y for _, t in groups for y in t]
    obs = pearson(xs, ys)
    rng = random.Random(7)
    null = []
    for _ in range(perms):
        xx = []
        for p, _ in groups:
            q = p[:]
            rng.shuffle(q)
            xx += q
        null.append(pearson(xx, ys))
    across = pearson([r["pred"][key] for r in rows], [r["truth"][key] for r in rows])
    return {
        "within_r": round(obs, 3),
        "p_perm": round(sum(n >= obs for n in null) / perms, 4),
        "pages": len(groups),
        "ads": len(xs),
        "across_r": round(across, 3),
        "mae": round(st.mean(abs(r["pred"][key] - r["truth"][key]) for r in rows), 3),
    }


def half(page_id: str) -> str:
    return "A" if int(hashlib.sha256(page_id.encode()).hexdigest(), 16) % 2 == 0 else "B"


def dev_pages() -> set[str]:
    return {
        str(it["page_id"])
        for path in glob.glob(str(DATA / "raw" / "ad_library" / "*.json"))
        for it in json.loads(Path(path).read_text(encoding="utf-8")).get("data") or []
    }


async def run(args: argparse.Namespace) -> None:
    if args.holdout:
        seen_pages = dev_pages()
        ads = [a for a in load_ads(DATA / "raw" / "holdout") if a["page_id"] not in seen_pages]
    else:
        ads = load_ads()
    if args.limit:
        random.Random(1).shuffle(ads)
        ads = ads[: args.limit]
    per_ad = 0.0007 * max(1, args.personas // 20)
    log.info(f"{len(ads)} anuncios de {len({a['page_id'] for a in ads})} páginas · costo estimado US$ {len(ads) * per_ad:.2f}")
    if not args.yes:
        log.info("No se llamó a la API. Repite con --yes para gastar.")
        return
    client = ModelClient.from_env(concurrency=args.concurrency)
    client.effort = "low"
    async with httpx.AsyncClient(follow_redirects=True) as http:
        if args.personas:
            preds = await asyncio.gather(*(predict_population(client, http, a, args.personas) for a in ads))
        else:
            preds = await asyncio.gather(*(predict(client, http, a) for a in ads))
    await client.aclose()
    rows = [a | {"pred": p} for a, p in zip(ads, preds) if p]
    if args.holdout:
        # Primero solo las predicciones y su hash: se commitea antes de mirar las etiquetas (--score las lee).
        preds_only = {r["ad_id"]: {k: round(r["pred"][k], 4) for k in TARGETS} for r in rows}
        blob = json.dumps(preds_only, sort_keys=True)
        digest = hashlib.sha256(blob.encode()).hexdigest()
        (RESULTS / "holdout_predictions.json").write_text(blob, encoding="utf-8")
        (RESULTS / "holdout_predictions.sha256").write_text(f"{digest}\n", encoding="utf-8")
        log.info(f"{len(rows)} predicciones · SHA-256 {digest}. Commitea y después corre --score.")
        return
    summary = {k: within_page(rows, k) for k in TARGETS}
    for h in "AB":
        part = [r for r in rows if half(r["page_id"]) == h]
        summary[f"half_{h}"] = {k: within_page(part, k, perms=1000) for k in TARGETS}
    out = {"model": MODEL, "personas": args.personas, "ads": len(rows), "failed": len(ads) - len(rows), "summary": summary, "rows": rows}
    path = RESULTS / f"audience_validation{'_' + args.tag if args.tag else ''}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info(json.dumps(summary, indent=1))
    log.info(f"Guardado {path.name}")


def score_holdout() -> None:
    preds = json.loads((RESULTS / "holdout_predictions.json").read_text(encoding="utf-8"))
    ads = {a["ad_id"]: a for a in load_ads(DATA / "raw" / "holdout")}
    rows = [ads[k] | {"pred": v} for k, v in preds.items() if k in ads]
    summary = {k: within_page(rows, k) for k in TARGETS}
    passed = sum(1 for k in TARGETS if summary[k].get("within_r", 0) > 0 and summary[k].get("p_perm", 1) < 0.05)
    summary["rule"] = {"passed_metrics": passed, "validated": passed >= 2}
    out = {"model": MODEL, "ads": len(rows), "summary": summary, "rows": rows}
    (RESULTS / "holdout_scored.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info(json.dumps(summary, indent=1))


def main() -> None:
    load_dotenv(".env")
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--concurrency", type=int, default=32)
    p.add_argument("--tag", default="")
    p.add_argument("--personas", type=int, default=0, help="usar la población sintética (personas por anuncio)")
    p.add_argument("--yes", action="store_true")
    p.add_argument("--holdout", action="store_true", help="marcas nuevas de data/raw/holdout/: solo predice y escribe el hash")
    p.add_argument("--score", action="store_true", help="puntuar results/holdout_predictions.json contra las etiquetas")
    args = p.parse_args()
    if args.score:
        score_holdout()
        return
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
