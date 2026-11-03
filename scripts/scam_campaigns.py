"""Familias de estafas a partir de los casos de Reddit que la comunidad calificó de estafa (intentos 1 y 2).

    --label      veredicto de la comunidad para los casos nuevos (data/raw/scams3 → data/scams/labels3.json), con el
                 mismo etiquetador de la validación: lee solo las respuestas
    --describe   canal, marca imitada, pago, uso de IA, tipo y gancho de cada caso (data/scams/described.json)
    --taxonomy   ~20 familias a partir de los tipos (data/scams/families.json)
    --assign     cada caso a una familia (data/scams/assigned.json)
    --aggregate  números por familia, canal y mes, sin datos personales (results/scam_campaigns.json)

Los datos son públicos, así que van por muse-spark-1.3-contributor. Cada paso guarda lo hecho y no repite casos.

    uv run python scripts/scam_campaigns.py --describe --yes
"""

import argparse
import asyncio
import json
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ensayo import DATA
from ensayo.campaigns import (AI_USE, CHANNELS, META_CHANNELS, PAYMENTS, describe_messages, match_messages, save, scrub,
                              taxonomy_messages)
from ensayo.llm import ModelClient, estimate_call_usd, extract_json
from scripts.validate_scams import label_one, load_posts

log = logging.getLogger(__name__)

MODEL = "muse-spark-1.3-contributor"
PHASE = "campanas"
OUT = DATA / "scams"
DESCRIBED, FAMILIES, ASSIGNED = OUT / "described.json", OUT / "families.json", OUT / "assigned.json"
MIN_TREND = 30
RAW_DIRS = [DATA / "raw" / d for d in ("scams", "scams2", "scams3")]


def all_labels() -> dict[str, str]:
    labels: dict[str, str] = {}
    for path in sorted(OUT.glob("labels*.json")):
        labels.update(json.loads(path.read_text(encoding="utf-8")))
    return labels


def all_posts() -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for d in RAW_DIRS:
        if d.exists():
            seen.update({p["id"]: p for p in load_posts(d)})
    return sorted(seen.values(), key=lambda p: p["id"])


def scam_posts() -> list[dict[str, Any]]:
    labels = all_labels()
    return [p for p in all_posts() if labels.get(p["id"]) == "scam"]


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def pick(value: Any, allowed: tuple[str, ...], fallback: str) -> str:
    v = str(value or "").strip().lower()
    return v if v in allowed else fallback


async def describe_one(client: ModelClient, post: dict[str, Any]) -> dict[str, Any] | None:
    try:
        res = await client.chat(MODEL, describe_messages(post), phase=PHASE, max_tokens=120,
                                upcoming_usd=estimate_call_usd(MODEL, 3500, 300), note=f"describe {post['id']}")
        d = extract_json(res.text)
    except (RuntimeError, ValueError, KeyError) as exc:
        log.warning(f"{post['id']}: {exc}")
        return None
    brand = d.get("brand")
    return {
        "channel": pick(d.get("channel"), CHANNELS, "unknown"),
        "brand": str(brand).strip() if brand and str(brand).lower() not in ("null", "none", "") else None,
        "payment": pick(d.get("payment"), PAYMENTS, "unknown"),
        "ai": pick(d.get("ai"), AI_USE, "none"),
        "kind": str(d.get("kind") or "").strip().lower()[:80],
        "hook": scrub(str(d.get("hook") or ""))[:160],
    }


async def assign_one(client: ModelClient, families: list[dict[str, Any]], pid: str, d: dict[str, Any]) -> str | None:
    ids = {f["id"] for f in families}
    try:
        res = await client.chat(MODEL, match_messages(families, d["kind"] or "unknown", d["hook"]), phase=PHASE,
                                max_tokens=40, upcoming_usd=estimate_call_usd(MODEL, 4000, 100), note=f"assign {pid}")
        fam = extract_json(res.text).get("family")
    except (RuntimeError, ValueError, KeyError) as exc:
        log.warning(f"{pid}: {exc}")
        return None
    return fam if fam in ids else "other"


def aggregate(posts: list[dict[str, Any]], described: dict[str, Any], families: list[dict[str, Any]],
              assigned: dict[str, str]) -> dict[str, Any]:
    rows = [{**described[p["id"]], "id": p["id"], "month": p["created"][:7], "url": p.get("url"), "family": assigned[p["id"]]}
            for p in posts if p["id"] in described and p["id"] in assigned]
    months = sorted({r["month"] for r in rows})
    per_month = Counter(r["month"] for r in rows)
    # La tendencia compara los dos últimos meses completos (el mes en curso trae solo unos días).
    end = max(p["created"][:10] for p in posts)
    full = [m for m in months if m < end[:7]] or months
    n = len(rows)
    by_fam: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_fam[r["family"]].append(r)
    out_fams = []
    for f in families:
        rs = by_fam.get(f["id"], [])
        if not rs:
            continue
        monthly = {m: sum(r["month"] == m for r in rs) for m in months}
        # Tendencia como parte del total de cada mes: la cantidad de casos bajados cambia de un mes a otro.
        share = {m: monthly[m] / per_month[m] for m in months if per_month[m]}
        last, prev = (full[-1], full[-2]) if len(full) >= 2 else (full[-1], full[-1])
        change = (share.get(last, 0) - share.get(prev, 0)) / share[prev] if share.get(prev) else 0.0
        brands = Counter(r["brand"] for r in rs if r["brand"])
        examples = [{"hook": r["hook"], "channel": r["channel"], "url": r["url"]} for r in rs if r["hook"]][:4]
        out_fams.append({
            **f,
            "reports": len(rs),
            "share": round(len(rs) / n, 4),
            "monthly": monthly,
            # Con pocos casos el cambio es ruido: tendencia solo desde MIN_TREND casos.
            "trend": "steady" if len(rs) < MIN_TREND else "rising" if change >= 0.25 else "falling" if change <= -0.25 else "steady",
            "trend_change": round(change, 3),
            "channels": dict(Counter(r["channel"] for r in rs).most_common(5)),
            "payments": dict(Counter(r["payment"] for r in rs).most_common(4)),
            # "Campaña" = al menos 3 casos de la misma familia que imitan a la misma marca.
            "top_brands": [{"brand": b, "reports": c} for b, c in brands.most_common(5) if c >= 3],
            "meta_share": round(sum(r["channel"] in META_CHANNELS for r in rs) / len(rs), 3),
            "ai_share": round(sum(r["ai"] != "none" for r in rs) / len(rs), 3),
            "examples": examples,
        })
    out_fams.sort(key=lambda f: -f["reports"])
    channels = Counter(r["channel"] for r in rows)
    return {
        "source": "Reddit posts (r/Scams, r/isthisascam, r/IsThisAScamIndia, r/ScamCenter, r/scamsUK) the community judged to be scams",
        "window": [min(p["created"][:10] for p in posts), max(p["created"][:10] for p in posts)],
        "reports": n,
        "months": {m: per_month[m] for m in months},
        "trend_months": full[-2:],
        "channels": dict(channels.most_common()),
        "meta_share": round(sum(channels[c] for c in META_CHANNELS) / n, 3),
        "known_channel_meta_share": round(sum(channels[c] for c in META_CHANNELS) / max(1, n - channels["unknown"]), 3),
        "ai": dict(Counter(r["ai"] for r in rows if r["ai"] != "none").most_common()),
        "ai_share": round(sum(r["ai"] != "none" for r in rows) / n, 3),
        "families": out_fams,
    }


async def run(args: argparse.Namespace) -> None:
    if args.label:
        labels = all_labels()
        todo = [p for p in all_posts() if p["id"] not in labels]
        log.info(f"{len(todo)} casos sin etiqueta · costo estimado US$ {len(todo) * 0.0006:.2f}")
        if not (args.yes and todo):
            return
        client = ModelClient.from_env(concurrency=args.concurrency)
        client.effort = "low"
        verdicts = await asyncio.gather(*(label_one(client, p) for p in todo))
        await client.aclose()
        path = OUT / "labels3.json"
        new = {**read(path), **{p["id"]: v for p, v in zip(todo, verdicts) if v}}
        path.write_text(json.dumps(new, indent=1), encoding="utf-8")
        log.info(f"etiquetas: {json.dumps(Counter(new.values()))}")
        return
    posts = scam_posts()
    described, assigned = read(DESCRIBED), read(ASSIGNED)
    if args.describe:
        todo = [p for p in posts if p["id"] not in described]
        log.info(f"{len(posts)} casos de estafa · {len(todo)} por describir · costo estimado US$ {len(todo) * 0.0004:.2f}")
        if not (args.yes and todo):
            return
        client = ModelClient.from_env(concurrency=args.concurrency)
        client.effort = "low"
        res = await asyncio.gather(*(describe_one(client, p) for p in todo))
        await client.aclose()
        described.update({p["id"]: r for p, r in zip(todo, res) if r})
        DESCRIBED.write_text(json.dumps(described, indent=1, ensure_ascii=False), encoding="utf-8")
        log.info(f"{len(described)} descritos")
        return
    if args.taxonomy:
        kinds = Counter(d["kind"] for d in described.values() if d["kind"])
        log.info(f"{len(kinds)} tipos distintos de {sum(kinds.values())} casos")
        if not args.yes:
            return
        client = ModelClient.from_env(concurrency=1)
        client.effort = "medium"
        messages = taxonomy_messages(kinds.most_common())
        res = await client.chat(MODEL, messages, phase=PHASE, max_tokens=4000,
                                upcoming_usd=estimate_call_usd(MODEL, len(str(messages)), 6000), note="taxonomia")
        await client.aclose()
        fams = extract_json(res.text)["families"]
        if not any(f["id"] == "other" for f in fams):
            fams.append({"id": "other", "name": "Other scams", "what": "Scams that do not fit a common pattern.",
                         "spot": [], "do": "Stop and check with someone you trust."})
        FAMILIES.write_text(json.dumps(fams, indent=1, ensure_ascii=False), encoding="utf-8")
        log.info("\n".join(f"{f['id']}: {f['name']}" for f in fams))
        return
    families = json.loads(FAMILIES.read_text(encoding="utf-8"))
    if args.assign:
        todo = [(pid, d) for pid, d in described.items() if pid not in assigned]
        log.info(f"{len(todo)} por asignar · costo estimado US$ {len(todo) * 0.0004:.2f}")
        if not (args.yes and todo):
            return
        client = ModelClient.from_env(concurrency=args.concurrency)
        client.effort = "low"
        res = await asyncio.gather(*(assign_one(client, families, pid, d) for pid, d in todo))
        await client.aclose()
        assigned.update({pid: f for (pid, _), f in zip(todo, res) if f})
        ASSIGNED.write_text(json.dumps(assigned, indent=1), encoding="utf-8")
        log.info(json.dumps(Counter(assigned.values()).most_common(), indent=0))
        return
    data = aggregate(posts, described, families, assigned)
    save(data)
    log.info(f"{data['reports']} casos · {len(data['families'])} familias · Meta {data['meta_share']:.0%} · IA {data['ai_share']:.0%}")
    for f in data["families"]:
        log.info(f"{f['reports']:4d} {f['trend']:8s} {f['name']} · {[b['brand'] for b in f['top_brands']]}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    ap = argparse.ArgumentParser()
    for step in ("label", "describe", "taxonomy", "assign"):
        ap.add_argument(f"--{step}", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--concurrency", type=int, default=8)
    asyncio.run(run(ap.parse_args()))


if __name__ == "__main__":
    main()
