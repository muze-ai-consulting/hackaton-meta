"""Métricas del backtest y rival al azar.

Un ranking predicho es una lista de ad_id del mejor al peor. La verdad es el alcance UE de cada anuncio
dentro de su lote. Métricas por lote, promediadas con intervalo de confianza por bootstrap sobre lotes:
- pairwise: fracción de pares bien ordenados (azar = 0,5).
- top1: si el primero predicho es el de más alcance (azar = 1/n).
- spearman: correlación de rangos.
"""

import random
from itertools import combinations
from statistics import mean
from typing import Any


def pairwise_accuracy(ranking: list[str], truth: dict[str, float]) -> float | None:
    pos = {ad: i for i, ad in enumerate(ranking)}
    pairs = [(a, b) for a, b in combinations(truth, 2) if truth[a] != truth[b] and a in pos and b in pos]
    if not pairs:
        return None
    good = sum(1 for a, b in pairs if (pos[a] < pos[b]) == (truth[a] > truth[b]))
    return good / len(pairs)


def top1_hit(ranking: list[str], truth: dict[str, float]) -> float | None:
    best = max(truth.values())
    winners = [ad for ad, v in truth.items() if v == best]
    if len(winners) == len(truth):
        return None
    return 1.0 if ranking and ranking[0] in winners else 0.0


def spearman(ranking: list[str], truth: dict[str, float]) -> float | None:
    ads = [ad for ad in ranking if ad in truth]
    n = len(ads)
    if n < 3:
        return None
    true_order = sorted(ads, key=lambda a: -truth[a])
    true_rank = {ad: i for i, ad in enumerate(true_order)}
    d2 = sum((i - true_rank[ad]) ** 2 for i, ad in enumerate(ads))
    return 1 - 6 * d2 / (n * (n**2 - 1))


def score_batch(ranking: list[str], truth: dict[str, float]) -> dict[str, float | None]:
    return {"pairwise": pairwise_accuracy(ranking, truth), "top1": top1_hit(ranking, truth), "spearman": spearman(ranking, truth)}


def bootstrap_ci(values: list[float], iters: int = 2000, seed: int = 11) -> tuple[float, float, float]:
    """Media e intervalo del 95 % remuestreando lotes."""
    rng = random.Random(seed)
    means = sorted(mean(rng.choices(values, k=len(values))) for _ in range(iters))
    return mean(values), means[int(0.025 * iters)], means[int(0.975 * iters)]


def summarize(per_batch: list[dict[str, float | None]]) -> dict[str, Any]:
    out: dict[str, Any] = {"batches": len(per_batch)}
    for metric in ("pairwise", "top1", "spearman"):
        vals = [s[metric] for s in per_batch if s[metric] is not None]
        if vals:
            m, lo, hi = bootstrap_ci(vals)
            out[metric] = {"mean": round(m, 3), "ci95": [round(lo, 3), round(hi, 3)], "n": len(vals)}
    return out


def random_ranking(ad_ids: list[str], seed: int | str) -> list[str]:
    """Rival al azar con semilla fija."""
    order = list(ad_ids)
    random.Random(seed).shuffle(order)
    return order


def random_baseline(batches: list[dict[str, Any]], seeds: range = range(20)) -> dict[str, Any]:
    """Promedio de 20 sorteos para que el rival al azar no dependa de una semilla con suerte."""
    per_batch: list[dict[str, float | None]] = []
    for i, b in enumerate(batches):
        truth = {ad: float(lab["reach"]) for ad, lab in b["labels"].items()}
        # Semilla por lote: con la misma semilla todos los lotes recibirían la misma permutación.
        runs = [score_batch(random_ranking(list(truth), f"{i}-{s}"), truth) for s in seeds]
        per_batch.append(
            {
                k: (mean(v for r in runs if (v := r[k]) is not None) if any(r[k] is not None for r in runs) else None)
                for k in ("pairwise", "top1", "spearman")
            }
        )
    return summarize(per_batch)
