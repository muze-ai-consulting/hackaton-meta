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
IMAGE_TOKENS = 300  # medido por scripts/probe_model_api.py el 2-nov: ~296 tokens por imagen

# Prompts en inglés desde el 2-nov (decisión de Mark: todo el producto en inglés). Se cambió antes del backtest
# de dev y del sellado; después de abrir el sellado no se tocan.
SYSTEM_SIM = (
    "You simulate real people scrolling their Facebook or Instagram feed. Ads appear between posts from friends "
    "and each person reacts the way they really would: most ads get scrolled past without a look. You are not a "
    "marketing expert; you are each of these people. Reply with valid JSON only."
)
SYSTEM_RANK = (
    "You are a Facebook and Instagram advertising strategist. Reply with valid JSON only."
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


VIEWS = ("full", "feed")
FEED_CUT = 125  # caracteres del texto principal que el feed muestra antes de "… more"
FEED_NOTE = (
    "Each ad is shown as the feed shows it: the first line of text, then the image, then the headline under the "
    "image. Long text is cut with \"… more\" and almost nobody taps it; people decide in about a second, mostly "
    "from the image."
)


def _feed_text(body: str) -> str:
    return body if len(body) <= FEED_CUT else body[:FEED_CUT].rsplit(" ", 1)[0] + "… more"


def _ad_lines(letter: str, v: dict[str, Any], view: str) -> tuple[str, str]:
    """Texto antes y después de la imagen. "full" es el formato original; "feed" imita el feed (desde el 2-nov)."""
    title = (v.get("title") or "").strip()
    body = " ".join((v.get("body") or "").split())
    if view == "feed":
        before = f"Ad {letter}: {_feed_text(body) or '(no text)'}"
        return before, f"Ad {letter} headline under the image: {title or '(none)'}"
    return f"Ad {letter}: headline: {title or '(no headline)'} · text: {body or '(no text)'}", ""


def _content(
    header: str, ads: list[tuple[str, dict[str, Any]]], footer: str, view: str = "full"
) -> str | list[dict[str, Any]]:
    """Texto plano, o partes con imagen después de cada anuncio cuando las variantes traen image_url."""
    lines = [_ad_lines(letter, v, view) for letter, v in ads]
    if not any(v.get("image_url") for _, v in ads):
        return "\n".join([header, *(x for pair in lines for x in pair if x), footer])
    parts: list[dict[str, Any]] = [{"type": "text", "text": header}]
    for (before, after), (_, v) in zip(lines, ads):
        parts.append({"type": "text", "text": before})
        if v.get("image_url"):
            parts.append({"type": "image_url", "image_url": {"url": v["image_url"]}})
        if after:
            parts.append({"type": "text", "text": after})
    parts.append({"type": "text", "text": footer})
    return parts


def simulation_messages(
    batch: dict[str, Any], order: list[int], people: list[Persona], view: str = "full"
) -> list[dict[str, Any]]:
    variants = batch["variants"]
    ads = [(LETTERS[pos], variants[idx]) for pos, idx in enumerate(order)]
    header = f"Advertiser: {batch.get('page_name') or 'a brand'}.\n{FEED_NOTE + chr(10) if view == 'feed' else ''}Feed, in this order:"
    personas = "\n".join(f"P{i + 1}: {p.describe()}" for i, p in enumerate(people))
    footer = (
        f"\nPeople:\n{personas}\n\n"
        "For each person, list the ads they would stop to look at (\"stop\") and the ones they would click "
        "(\"click\", only if they also stopped). Use the letters. An empty list is a valid and common answer. "
        "Add a reason of 12 words at most.\n"
        'Format: {"reactions": [{"p": 1, "stop": ["A"], "click": [], "reason": "..."}]}'
    )
    return [{"role": "system", "content": SYSTEM_SIM}, {"role": "user", "content": _content(header, ads, footer, view)}]


def _target_text(batch: dict[str, Any]) -> str:
    t = batch.get("target") or {}
    ages = t.get("target_ages") or ["18", "65+"]
    countries = [loc.get("name") for loc in t.get("target_locations") or [] if not loc.get("excluded")]
    return f"age {ages[0]} to {ages[-1]}, gender {t.get('target_gender') or 'All'}, countries {', '.join(countries) or 'GB'}"


def ranking_messages(batch: dict[str, Any], view: str = "full") -> list[dict[str, Any]]:
    ads = [(LETTERS[i], v) for i, v in enumerate(batch["variants"])]
    header = (
        f"Advertiser: {batch.get('page_name') or 'a brand'}. Targeting: {_target_text(batch)}.\n"
        f"{FEED_NOTE + chr(10) if view == 'feed' else ''}"
        "These ads ran the same week with the same targeting:"
    )
    footer = (
        "\nRank them from the one that will reach the most people to the one that will reach the fewest. Use every letter.\n"
        'Format: {"ranking": ["B", "A", "C"], "reason": "..."}'
    )
    return [{"role": "system", "content": SYSTEM_RANK}, {"role": "user", "content": _content(header, ads, footer, view)}]


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
    view: str = "full",
) -> dict[str, Any]:
    variants = batch["variants"]
    if len(variants) > len(LETTERS):
        raise ValueError(f"Lote {batch['batch_id']}: máximo {len(LETTERS)} variantes")
    feed = feed_orders(len(variants), orders)
    chunks = [population[i : i + per_call] for i in range(0, len(population), per_call)]
    n_images = sum(1 for v in variants if v.get("image_url"))

    async def run(i: int, people: list[Persona]) -> tuple[list[int], list[Persona], dict[str, Any] | None]:
        order = feed[i % len(feed)]
        messages = simulation_messages(batch, order, people, view)
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
        for r in body.get("reactions") or body.get("reacciones") or []:
            try:
                person = people[int(r.get("p")) - 1]
            except (TypeError, ValueError, IndexError):
                continue
            segment = f"{person.age_bucket} · {person.platform}"
            seen_by_segment[segment] += 1
            stopped = {letter_to_idx[x] for x in r.get("stop") or r.get("frena") or [] if x in letter_to_idx}
            clicked = {letter_to_idx[x] for x in r.get("click") or r.get("clic") or [] if x in letter_to_idx} & stopped
            why = str(r.get("reason") or r.get("motivo") or "")
            for idx in range(len(variants)):
                seen[idx] += 1
            for idx in stopped:
                stops[idx] += 1
                stops_by_segment[idx][segment] += 1
            for idx in clicked:
                clicks[idx] += 1
                if len(reasons[idx]) < 5 and why:
                    reasons[idx].append(why)
            if len(sample) < sample_size:
                sample.append(
                    {
                        "persona": person.describe(),
                        "segment": segment,
                        "stopped": [variants[i]["ad_id"] for i in sorted(stopped)],
                        "clicked": [variants[i]["ad_id"] for i in sorted(clicked)],
                        "reason": why,
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


async def single_call_ranking(
    client: ModelClient, batch: dict[str, Any], *, model: str, phase: str, view: str = "full"
) -> dict[str, Any]:
    """Rival obligatorio: una sola llamada a Spark 1.3, sin población. Ve los anuncios igual que la población."""
    messages = ranking_messages(batch, view)
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
    return {"ranking": ranking + missing, "incomplete": bool(missing), "reason": body.get("reason") or body.get("motivo")}


def short_text_ranking(batch: dict[str, Any]) -> list[str]:
    """Rival sin modelo (desde el 2-nov): gana el texto más corto. En dev ordenó bien el 63 % de los pares."""
    size = {v["ad_id"]: len((v.get("body") or "").strip()) + len((v.get("title") or "").strip()) for v in batch["variants"]}
    return sorted(size, key=lambda ad: (size[ad], ad))
