"""Verifica la lista de anunciantes candidatos contra la Meta Ad Library API y los ordena por utilidad para el backtest.

Para cada candidato de data/advertisers_candidates.csv:
1. Resuelve su página (page_id) buscando por nombre en el país indicado.
2. Baja sus anuncios entregados en cualquier país de la UE o UK desde el 3-sep-2026 y se queda con los que partieron después del 2-sep (regla de contaminación).
3. Mide cuántas creatividades distintas tiene y cuántos grupos comparables (misma semana de lanzamiento,
   3+ anuncios de una sola versión con alcance UE).

Lee META_ACCESS_TOKEN desde .env. Respuestas crudas en data/raw/ad_library/ (fuera del repo).
Salida: results/eu_advertisers.csv.

Uso: uv run --python 3.12 --with httpx --with python-dotenv scripts/eu_advertisers.py [--limit N]
"""

import argparse
import csv
import hashlib
import json
import logging
import os
import time
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
GRAPH = "https://graph.facebook.com/v26.0/ads_archive"
CUTOFF = date(2026, 9, 2)  # lanzamiento de Muse Spark 1.3
DELIVERY_MIN = "2026-09-03"
RAW = ROOT / "data" / "raw" / "ad_library"
FIELDS = ",".join([
    "id", "page_id", "page_name", "ad_delivery_start_time", "ad_delivery_stop_time",
    "ad_creative_bodies", "ad_creative_link_titles", "publisher_platforms", "eu_total_reach",
])
MIN_GROUP = 3  # anuncios por semana de lanzamiento para que el grupo sirva de comparación

log = logging.getLogger("eu_advertisers")


def get(client: httpx.Client, params: dict[str, Any]) -> dict[str, Any]:
    """GET con caché en disco y reintento ante el límite de tasa (error 613)."""
    key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:16]
    cache = RAW / f"{key}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    for attempt in range(5):
        r = client.get(GRAPH, params=params)
        body = r.json()
        err = body.get("error", {})
        if err.get("code") in (4, 17, 613):
            wait = 60 * (attempt + 1)
            log.warning(f"Límite de tasa (código {err.get('code')}), espero {wait} s")
            time.sleep(wait)
            continue
        if err:
            raise RuntimeError(f"Ad Library API: {err.get('code')} {err.get('message')}")
        cache.write_text(json.dumps(body), encoding="utf-8")
        return body
    raise RuntimeError("Límite de tasa persistente")


def paginate(client: httpx.Client, params: dict[str, Any], max_pages: int = 10) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page = get(client, params)
    for _ in range(max_pages):
        rows.extend(page.get("data", []))
        after = page.get("paging", {}).get("cursors", {}).get("after")
        if not page.get("paging", {}).get("next") or not after:
            break
        page = get(client, {**params, "after": after})
    return rows


def resolve_page(client: httpx.Client, token: str, query: str, country: str) -> tuple[str, str] | None:
    """La página con más anuncios cuyo nombre contiene el término buscado."""
    rows = paginate(client, {
        "access_token": token, "search_terms": query, "ad_reached_countries": json.dumps([country]),
        "ad_type": "ALL", "ad_active_status": "ALL", "ad_delivery_date_min": DELIVERY_MIN,
        "fields": "page_id,page_name", "limit": 500,
    }, max_pages=2)
    needle = query.lower().split()[0]
    counts = Counter((r["page_id"], r["page_name"]) for r in rows if needle in r.get("page_name", "").lower())
    return counts.most_common(1)[0][0] if counts else None


def reach_value(ad: dict[str, Any]) -> int | None:
    val = ad.get("eu_total_reach")
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def score_page(ads: list[dict[str, Any]]) -> dict[str, Any]:
    fresh = [a for a in ads if datetime.fromisoformat(a["ad_delivery_start_time"][:10]).date() > CUTOFF]
    bodies = [" ".join(a.get("ad_creative_bodies") or [""]).strip() for a in fresh]
    distinct = len(set(bodies))
    top_share = Counter(bodies).most_common(1)[0][1] / len(bodies) if bodies else 0.0
    weeks: dict[str, int] = defaultdict(int)
    with_reach = 0
    single = 0
    for a in fresh:
        if reach_value(a) is None:
            continue
        with_reach += 1
        # Con varias versiones (creatividad dinámica) el alcance mezcla variantes: no sirve para comparar.
        if len(a.get("ad_creative_bodies") or []) > 1 or len(a.get("ad_creative_link_titles") or []) > 1:
            continue
        single += 1
        iso = datetime.fromisoformat(a["ad_delivery_start_time"][:10]).isocalendar()
        weeks[f"{iso.year}-W{iso.week:02d}"] += 1
    groups = [w for w, n in weeks.items() if n >= MIN_GROUP]
    return {
        "ads_after_cutoff": len(fresh),
        "with_eu_reach": with_reach,
        "single_version": single,
        "distinct_bodies": distinct,
        "catalog_share": round(top_share, 2),  # alto = mismo texto en casi todo: probable catálogo
        "comparable_weeks": len(groups),
        "ads_in_comparable_weeks": sum(weeks[w] for w in groups),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="procesar solo los primeros N candidatos")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    load_dotenv(ROOT / ".env")
    token = os.environ.get("META_ACCESS_TOKEN")
    if not token:
        raise SystemExit("Falta META_ACCESS_TOKEN en .env (ver .env.example).")
    RAW.mkdir(parents=True, exist_ok=True)

    with open(ROOT / "data" / "advertisers_candidates.csv", encoding="utf-8") as f:
        candidates = list(csv.DictReader(f))
    if args.limit:
        candidates = candidates[: args.limit]

    out: list[dict[str, Any]] = []
    with httpx.Client(timeout=60) as client:
        for c in candidates:
            page = resolve_page(client, token, c["query"], c["country"])
            if not page:
                log.info(f"{c['brand']}: sin página en {c['country']}")
                out.append({**c, "page_id": "", "page_name": "", "note": "sin página"})
                continue
            page_id, page_name = page
            ads = paginate(client, {
                "access_token": token, "search_page_ids": json.dumps([page_id]),
                # ALL = todo país con datos; para anuncios comerciales eso es UE y UK. Maximiza anuncios por página.
                "ad_reached_countries": json.dumps(["ALL"]), "ad_type": "ALL",
                "ad_active_status": "ALL", "ad_delivery_date_min": DELIVERY_MIN, "fields": FIELDS, "limit": 500,
            })
            stats = score_page(ads)
            note = "probable catálogo" if stats["catalog_share"] >= 0.6 else ""
            out.append({**c, "page_id": page_id, "page_name": page_name, **stats, "note": note})
            log.info(f"{c['brand']}: {stats['ads_after_cutoff']} anuncios, {stats['comparable_weeks']} semanas comparables {note}")

    out.sort(key=lambda r: (r.get("note") == "", r.get("ads_in_comparable_weeks", 0)), reverse=True)
    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    cols = ["brand", "country", "category", "page_id", "page_name", "ads_after_cutoff", "with_eu_reach",
            "single_version", "distinct_bodies", "catalog_share", "comparable_weeks", "ads_in_comparable_weeks", "note", "why"]
    with open(results / "eu_advertisers.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(out)
    log.info(f"Guardado results/eu_advertisers.csv ({len(out)} anunciantes)")


if __name__ == "__main__":
    main()
