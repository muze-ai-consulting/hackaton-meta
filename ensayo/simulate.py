"""Feed simulado y ranking: la población ve las variantes de un lote y se cuenta quién frena y quién hace clic.

- Cada llamada lleva 20 personas (regla de presupuesto) y las variantes en un orden del feed.
- Cuatro órdenes rotados se reparten entre las llamadas: cada orden lo ve una parte de la población, así el sesgo
  de posición se cancela sin multiplicar el costo por cuatro.
- El modelo solo ve letras (A, B, C…), nunca los ad_id ni el alcance.
- Puntaje de una variante = tasa de frenado + tasa de clic. Es un supuesto: se ajusta con el set de desarrollo.

El rival "llamada única" pide a Spark 1.3, en una sola llamada y sin población, que ordene las variantes.
"""

import asyncio
import logging
from collections import defaultdict
from typing import Any

from ensayo.llm import ModelClient, estimate_call_usd, extract_json
from ensayo.population import Persona

log = logging.getLogger(__name__)

LETTERS = "ABCDEFGH"
IMAGE_TOKENS = 1200  # se reemplaza por lo que mida scripts/probe_model_api.py

SYSTEM_SIM = (
    "Simulas a personas reales que navegan su feed de Facebook o Instagram. Los anuncios aparecen intercalados "
    "con publicaciones de amigos y cada persona reacciona como lo haría de verdad: la mayoría de los anuncios se "
    "pasan de largo sin mirarlos. No eres un experto en marketing; eres cada una de estas personas. "
    "Responde solo con JSON válido."
)
SYSTEM_RANK = (
    "Eres un estratega de publicidad en Facebook e Instagram. Responde solo con JSON válido."
)


def feed_orders(n: int, orders: int = 4) -> list[list[int]]:
    """Órdenes distintos de n variantes: rotaciones repartidas y, si faltan, rotaciones del orden inverso."""
    base = list(range(n))
    candidates = [base[i:] + base[:i] for i in range(n)]
    rev = base[::-1]
    candidates += [rev[i:] + rev[:i] for i in range(n)]
    if orders <= n:
        picked = [candidates[round(k * n / orders)] for k in range(orders)]
    else:
        picked = candidates[:orders]
    unique: list[list[int]] = []
    for order in picked:
        if order not in unique:
            unique.append(order)
    return unique


def _ad_line(letter: str, v: dict[str, Any]) -> str:
    title = (v.get("title") or "").strip()
    body = " ".join((v.get("body") or "").split())
    return f"Anuncio {letter}: título: {title or '(sin título)'} · texto: {body or '(sin texto)'}"


def _content(header: str, ads: list[tuple[str, dict[str, Any]]], footer: str) -> str | list[dict[str, Any]]:
    """Texto plano, o partes con imagen después de cada anuncio cuando las variantes traen image_url."""
    lines = [_ad_line(letter, v) for letter, v in ads]
    if not any(v.get("image_url") for _, v in ads):
        return "\n".join([header, *lines, footer])
    parts: list[dict[str, Any]] = [{"type": "text", "text": header}]
    for line, (_, v) in zip(lines, ads):
        parts.append({"type": "text", "text": line})
        if v.get("image_url"):
            parts.append({"type": "image_url", "image_url": {"url": v["image_url"]}})
    parts.append({"type": "text", "text": footer})
    return parts


def simulation_messages(batch: dict[str, Any], order: list[int], people: list[Persona]) -> list[dict[str, Any]]:
    variants = batch["variants"]
    ads = [(LETTERS[pos], variants[idx]) for pos, idx in enumerate(order)]
    header = f"Anunciante: {batch.get('page_name') or 'una marca'}.\nFeed, en este orden:"
    personas = "\n".join(f"P{i + 1}: {p.describe()}" for i, p in enumerate(people))
    footer = (
        f"\nPersonas:\n{personas}\n\n"
        "Para cada persona, indica en qué anuncios se detendría a mirar (\"frena\") y en cuáles haría clic "
        "(\"clic\", solo si también frena). Usa las letras. Una lista vacía es una respuesta válida y frecuente. "
        "Agrega un motivo de 12 palabras como máximo.\n"
        'Formato: {"reacciones": [{"p": 1, "frena": ["A"], "clic": [], "motivo": "..."}]}'
    )
    return [{"role": "system", "content": SYSTEM_SIM}, {"role": "user", "content": _content(header, ads, footer)}]


def _target_text(batch: dict[str, Any]) -> str:
    t = batch.get("target") or {}
    ages = t.get("target_ages") or ["18", "65+"]
    countries = [loc.get("name") for loc in t.get("target_locations") or [] if not loc.get("excluded")]
    return f"edad {ages[0]} a {ages[-1]}, género {t.get('target_gender') or 'todos'}, países {', '.join(countries) or 'GB'}"


def ranking_messages(batch: dict[str, Any]) -> list[dict[str, Any]]:
    ads = [(LETTERS[i], v) for i, v in enumerate(batch["variants"])]
    header = (
        f"Anunciante: {batch.get('page_name') or 'una marca'}. Segmentación: {_target_text(batch)}.\n"
        "Estos anuncios salieron la misma semana con la misma segmentación:"
    )
    footer = (
        "\nOrdénalos del que llegará a más personas al que llegará a menos. Usa todas las letras.\n"
        'Formato: {"ranking": ["B", "A", "C"], "motivo": "..."}'
    )
    return [{"role": "system", "content": SYSTEM_RANK}, {"role": "user", "content": _content(header, ads, footer)}]


def score(stats: dict[str, Any]) -> float:
    return stats["stop_rate"] + stats["click_rate"]


async def simulate_batch(
    client: ModelClient,
    batch: dict[str, Any],
    population: list[Persona],
    *,
    model: str,
    phase: str,
    per_call: int = 20,
    orders: int = 4,
    sample_size: int = 0,
) -> dict[str, Any]:
    variants = batch["variants"]
    if len(variants) > len(LETTERS):
        raise ValueError(f"Lote {batch['batch_id']}: máximo {len(LETTERS)} variantes")
    feed = feed_orders(len(variants), orders)
    chunks = [population[i : i + per_call] for i in range(0, len(population), per_call)]
    n_images = sum(1 for v in variants if v.get("image_url"))

    async def run(i: int, people: list[Persona]) -> tuple[list[int], list[Persona], dict[str, Any] | None]:
        order = feed[i % len(feed)]
        messages = simulation_messages(batch, order, people)
        upcoming = estimate_call_usd(model, len(str(messages)), per_call * 40, n_images * IMAGE_TOKENS)
        res = await client.chat(
            model, messages, phase=phase, max_tokens=per_call * 60, upcoming_usd=upcoming, note=f"sim {batch['batch_id']}"
        )
        try:
            return order, people, extract_json(res.text)
        except ValueError as exc:
            log.warning(f"{batch['batch_id']} llamada {i}: {exc}")
            return order, people, None

    results = await asyncio.gather(*(run(i, people) for i, people in enumerate(chunks)))

    seen = defaultdict(int)
    stops: dict[int, int] = defaultdict(int)
    clicks: dict[int, int] = defaultdict(int)
    stops_by_segment: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    seen_by_segment: dict[str, int] = defaultdict(int)
    reasons: dict[int, list[str]] = defaultdict(list)
    sample: list[dict[str, Any]] = []  # algunas personas con su reacción completa, para mostrar en el demo
    failed = 0
    for order, people, body in results:
        if body is None:
            failed += 1
            continue
        letter_to_idx = {LETTERS[pos]: idx for pos, idx in enumerate(order)}
        for r in body.get("reacciones") or []:
            try:
                person = people[int(r.get("p")) - 1]
            except (TypeError, ValueError, IndexError):
                continue
            segment = f"{person.age_bucket} · {person.platform}"
            seen_by_segment[segment] += 1
            stopped = {letter_to_idx[x] for x in r.get("frena") or [] if x in letter_to_idx}
            clicked = {letter_to_idx[x] for x in r.get("clic") or [] if x in letter_to_idx} & stopped
            for idx in range(len(variants)):
                seen[idx] += 1
            for idx in stopped:
                stops[idx] += 1
                stops_by_segment[idx][segment] += 1
            for idx in clicked:
                clicks[idx] += 1
                if len(reasons[idx]) < 5 and r.get("motivo"):
                    reasons[idx].append(str(r["motivo"]))
            if len(sample) < sample_size:
                sample.append(
                    {
                        "persona": person.describe(),
                        "segment": segment,
                        "stopped": [variants[i]["ad_id"] for i in sorted(stopped)],
                        "clicked": [variants[i]["ad_id"] for i in sorted(clicked)],
                        "reason": str(r.get("motivo") or ""),
                    }
                )

    stats = {}
    for idx, v in enumerate(variants):
        n = seen[idx] or 1
        stats[v["ad_id"]] = {
            "seen": seen[idx],
            "stop_rate": round(stops[idx] / n, 4),
            "click_rate": round(clicks[idx] / n, 4),
            "stop_rate_by_segment": {
                s: round(stops_by_segment[idx][s] / c, 3) for s, c in sorted(seen_by_segment.items()) if c
            },
            "click_reasons": reasons[idx],
        }
        stats[v["ad_id"]]["score"] = round(score(stats[v["ad_id"]]), 4)
    ranking = sorted(stats, key=lambda ad: (-stats[ad]["score"], ad))
    return {
        "ranking": ranking,
        "stats": stats,
        "calls": len(chunks),
        "failed_calls": failed,
        "orders": feed,
        "sample_reactions": sample,
    }


async def single_call_ranking(client: ModelClient, batch: dict[str, Any], *, model: str, phase: str) -> dict[str, Any]:
    """Rival obligatorio: una sola llamada a Spark 1.3, sin población."""
    messages = ranking_messages(batch)
    ids = [v["ad_id"] for v in batch["variants"]]
    upcoming = estimate_call_usd(model, len(str(messages)), 200)
    res = await client.chat(model, messages, phase=phase, max_tokens=400, upcoming_usd=upcoming, note=f"única {batch['batch_id']}")
    try:
        body = extract_json(res.text)
    except ValueError as exc:
        log.warning(f"{batch['batch_id']} llamada única: {exc}")
        body = {}
    ranking: list[str] = []
    for letter in body.get("ranking") or []:
        idx = LETTERS.find(str(letter).strip().upper()[:1]) if letter else -1
        if 0 <= idx < len(ids) and ids[idx] not in ranking:
            ranking.append(ids[idx])
    missing = [ad for ad in ids if ad not in ranking]
    return {"ranking": ranking + missing, "incomplete": bool(missing), "reason": body.get("motivo")}
