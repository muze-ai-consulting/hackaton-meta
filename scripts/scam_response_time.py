"""Cuánto esperó la gente una respuesta de la comunidad, en los casos de Reddit que la comunidad llamó estafa.

Para cada publicación, la hora de la primera respuesta humana de primer nivel (sin AutoModerator ni el autor) desde
Arctic Shift (archivo público). Solo se guardan tiempos, no textos. Escribe results/scam_response_time.json.

    uv run python scripts/scam_response_time.py
"""

import asyncio
import json
import logging
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ensayo import DATA, RESULTS
from scripts.scam_campaigns import scam_posts

log = logging.getLogger(__name__)

API = "https://arctic-shift.photon-reddit.com/api"
CACHE = DATA / "scams" / "first_reply.json"
OUT = RESULTS / "scam_response_time.json"


async def first_reply(http: httpx.AsyncClient, sem: asyncio.Semaphore, post_id: str) -> dict[str, Any] | None:
    pid = post_id.removeprefix("t3_")
    async with sem:
        for attempt in range(3):
            try:
                r = await http.get(f"{API}/posts/ids", params={"ids": pid, "fields": "created_utc,author"})
                post = (r.raise_for_status().json().get("data") or [None])[0]
                r = await http.get(f"{API}/comments/search", params={
                    "link_id": pid, "limit": 100, "fields": "created_utc,author,parent_id"})
                coms = r.raise_for_status().json().get("data") or []
                break
            except (httpx.HTTPError, ValueError) as exc:
                log.warning(f"{pid}: {exc}")
                await asyncio.sleep(2 * (attempt + 1))
        else:
            return None
    if not post:
        return None
    human = [c for c in coms if c.get("parent_id") == f"t3_{pid}" and c.get("author") not in ("AutoModerator", post.get("author"), "[deleted]")
             and not str(c.get("author", "")).lower().endswith("modteam")]
    if not human:
        return None
    first = min(c["created_utc"] for c in human)
    return {"minutes": round((first - post["created_utc"]) / 60, 1)}


async def run() -> None:
    posts = scam_posts()
    cache: dict[str, Any] = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    todo = [p for p in posts if p["id"] not in cache]
    log.info(f"{len(posts)} casos · {len(todo)} por consultar")
    sem = asyncio.Semaphore(6)
    async with httpx.AsyncClient(timeout=30) as http:
        res = await asyncio.gather(*(first_reply(http, sem, p["id"]) for p in todo))
    cache.update({p["id"]: r for p, r in zip(todo, res) if r})
    CACHE.write_text(json.dumps(cache), encoding="utf-8")
    mins = sorted(v["minutes"] for v in cache.values() if v["minutes"] >= 0)
    q = statistics.quantiles(mins, n=4)
    out = {
        "cases": len(mins),
        "median_minutes": round(statistics.median(mins), 1),
        "p25_minutes": round(q[0], 1),
        "p75_minutes": round(q[2], 1),
        "over_1h": round(sum(m > 60 for m in mins) / len(mins), 3),
        "over_3h": round(sum(m > 180 for m in mins) / len(mins), 3),
        "computed": datetime.now().strftime("%Y-%m-%d"),
    }
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    log.info(json.dumps(out))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    asyncio.run(run())
