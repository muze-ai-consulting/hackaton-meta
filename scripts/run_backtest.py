"""Backtest: población simulada contra la llamada única y el azar, lote por lote.

Fuentes de lotes:
- fixtures: lotes inventados de ensayo.fixtures (para desarrollar).
- dev: data/batches/dev.json (con etiquetas; para calibrar).
- sealed: data/batches/sealed_inputs.json. Escribe los rankings y su SHA-256 antes de mirar etiquetas;
  solo con --score se leen data/sealed/labels.json. Después de abrir el sellado no se toca el modelo.

Sin --mock gasta créditos: primero muestra el costo estimado y solo corre con --yes.

Uso:
  uv run python scripts/run_backtest.py --source fixtures --mock
  uv run python scripts/run_backtest.py --source dev --limit 2 --personas 200          # muestra el costo
  uv run python scripts/run_backtest.py --source dev --limit 2 --personas 200 --yes    # gasta
"""

import argparse
import asyncio
import base64
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any

from ensayo import DATA, RESULTS
from ensayo.costs import estimate_batch_usd
from ensayo.fixtures import demo_batches
from ensayo.llm import ModelClient
from ensayo.metrics import random_baseline, score_batch, summarize
from ensayo.population import load_or_build, spec_from_ad
from ensayo.simulate import IMAGE_TOKENS, simulate_batch, single_call_ranking

log = logging.getLogger("backtest")


def use_local_images(batches: list[dict[str, Any]], images: Path = DATA / "images") -> int:
    """Cambia las URLs de fbcdn (vencen) por la copia local en data URI, igual en dev y en sellado."""
    swapped = 0
    for b in batches:
        for v in b["variants"]:
            path = images / f"{v['ad_id']}.jpg"
            if v.get("image_url") and path.exists():
                v["image_url"] = "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()
                swapped += 1
    return swapped


def load_batches(source: str) -> list[dict[str, Any]]:
    if source == "fixtures":
        return demo_batches()
    path = DATA / "batches" / ("dev.json" if source == "dev" else "sealed_inputs.json")
    if not path.exists():
        raise SystemExit(f"Falta {path}. Corre antes: uv run python -m ensayo.batches")
    batches = json.loads(path.read_text(encoding="utf-8"))
    log.info(f"{use_local_images(batches)} imágenes desde data/images (scripts/download_images.py)")
    return batches


def attach_labels(batches: list[dict[str, Any]], path: Path = DATA / "sealed" / "labels.json") -> None:
    labels = json.loads(path.read_text(encoding="utf-8"))
    for b in batches:
        b["labels"] = labels[b["batch_id"]]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--source", choices=["fixtures", "dev", "sealed"], default="fixtures")
    p.add_argument("--mock", action="store_true", help="servidor falso: no gasta créditos")
    p.add_argument("--model", default="muse-spark-1.3-contributor", help="contributor solo con datos públicos")
    p.add_argument("--phase", default="calibracion")
    p.add_argument("--personas", type=int, default=1000)
    p.add_argument("--per-call", type=int, default=20)
    p.add_argument("--orders", type=int, default=4)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--limit", type=int, default=0, help="solo los primeros N lotes")
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--no-single", action="store_true", help="sin el rival de llamada única")
    p.add_argument("--score", action="store_true", help="sealed: leer las etiquetas selladas y puntuar")
    p.add_argument("--yes", action="store_true", help="confirmar el gasto real")
    p.add_argument("--tag", default="")
    return p.parse_args()


async def run(args: argparse.Namespace) -> None:
    batches = load_batches(args.source)
    if args.limit:
        batches = batches[: args.limit]
    if not batches:
        raise SystemExit("No hay lotes.")

    # orders=1: cada grupo de personas ve un solo orden del feed (ensayo.simulate).
    estimate = sum(
        estimate_batch_usd(
            args.model,
            len(b["variants"]),
            personas=args.personas,
            per_call=args.per_call,
            orders=1,
            image_tokens=IMAGE_TOKENS if any(v.get("image_url") for v in b["variants"]) else 0,
        )
        for b in batches
    )
    log.info(f"{len(batches)} lotes · {args.personas} personas · modelo {args.model} · costo estimado US$ {estimate:.2f}")
    if not args.mock and not args.yes:
        log.info("No se llamó a la API. Para gastar, repite con --yes (o usa --mock para probar gratis).")
        return

    client = ModelClient.from_env(mock=args.mock, concurrency=args.concurrency)
    spent_before = client.ledger.spent()
    t0 = time.monotonic()
    per_batch = []
    try:
        for b in batches:
            people = load_or_build(spec_from_ad(b.get("target") or {}), n=args.personas, seed=args.seed)
            sim = await simulate_batch(
                client, b, people, model=args.model, phase=args.phase, per_call=args.per_call, orders=args.orders
            )
            single = None if args.no_single else await single_call_ranking(client, b, model=args.model, phase=args.phase)
            per_batch.append({"batch_id": b["batch_id"], "population": sim, "single_call": single})
            log.info(f"{b['batch_id']}: {sim['calls']} llamadas, {sim['failed_calls']} fallidas · ranking {sim['ranking']}")
    finally:
        await client.aclose()
    spent = client.ledger.spent() - spent_before

    name = f"backtest_{args.source}{'_mock' if args.mock else ''}{'_' + args.tag if args.tag else ''}"
    RESULTS.mkdir(exist_ok=True)
    out: dict[str, Any] = {
        "source": args.source,
        "mock": args.mock,
        "config": {k: v for k, v in vars(args).items() if k not in ("yes",)},
        "ran_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "secs": round(time.monotonic() - t0, 1),
        "usd": round(spent, 4),
        "usd_note": "hipotético: lo que costaría en la API real" if args.mock else "gasto real",
        "batches": per_batch,
    }

    if args.source == "sealed":
        rankings = json.dumps({r["batch_id"]: r["population"]["ranking"] for r in per_batch}, sort_keys=True)
        digest = hashlib.sha256(rankings.encode()).hexdigest()
        (RESULTS / f"{name}_rankings.sha256").write_text(f"{digest}\n", encoding="utf-8")
        out["rankings_sha256"] = digest
        log.info(f"SHA-256 de los rankings sellados: {digest}")
        if not args.score:
            (RESULTS / f"{name}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
            log.info("Rankings guardados sin puntuar. Commitea el hash y después corre con --score.")
            return
        attach_labels(batches)

    truth = {b["batch_id"]: {ad: float(lab["reach"]) for ad, lab in b["labels"].items()} for b in batches}
    pop_scores = [score_batch(r["population"]["ranking"], truth[r["batch_id"]]) for r in per_batch]
    out["summary"] = {"population": summarize(pop_scores), "random": random_baseline(batches)}
    if not args.no_single:
        single_scores = [score_batch(r["single_call"]["ranking"], truth[r["batch_id"]]) for r in per_batch]
        out["summary"]["single_call"] = summarize(single_scores)
    for r, s in zip(per_batch, pop_scores):
        r["population_score"] = s

    path = RESULTS / f"{name}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for rival, s in out["summary"].items():
        pw = s.get("pairwise", {})
        log.info(f"{rival:12s} pares bien ordenados {pw.get('mean')} IC95 {pw.get('ci95')}")
    log.info(f"Guardado {path.relative_to(RESULTS.parent)} · costo {out['usd_note']}: US$ {spent:.4f}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    asyncio.run(run(parse_args()))


if __name__ == "__main__":
    main()
