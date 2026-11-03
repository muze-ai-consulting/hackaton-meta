"""Baja preguntas de estafas de Reddit desde Arctic Shift (archivo público, gratis), con el mismo formato que
scripts/scam_reddit.py (Apify), para que scripts/validate_scams.py los lea igual.

Solo publicaciones entre el corte de contaminación y --before (para que los comentarios ya estén archivados),
con texto o imagen y al menos dos comentarios.

    uv run --with httpx python scripts/scam_arctic.py --per-sub 600
"""

import argparse
import asyncio
import json
import logging
import pathlib
from datetime import UTC, datetime
from typing import Any

import httpx

log = logging.getLogger(__name__)

API = "https://arctic-shift.photon-reddit.com/api"
CUTOFF = "2026-09-03"
SUBS = ("Scams", "isthisascam", "IsThisAScamIndia")
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw" / "scams"
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def images(p: dict[str, Any]) -> list[str]:
    urls = [p["url"]] if str(p.get("url", "")).lower().endswith(IMAGE_EXT) else []
    for m in (p.get("media_metadata") or {}).values():
        src = (m.get("s") or {}).get("u")
        if src:
            urls.append(src.replace("&amp;", "&"))
    return urls[:3]


async def get(http: httpx.AsyncClient, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    for attempt in range(4):
        try:
            r = await http.get(f"{API}{path}", params=params, timeout=60)
            if r.status_code == 429:
                await asyncio.sleep(5 * (attempt + 1))
                continue
            r.raise_for_status()
            return r.json().get("data") or []
        except httpx.HTTPError as exc:
            log.warning(f"{path}: {exc}")
            await asyncio.sleep(3)
    return []


async def posts(http: httpx.AsyncClient, sub: str, after: str, before: str, want: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    while len(out) < want:
        page = await get(http, "/posts/search", {"subreddit": sub, "after": after, "before": before, "limit": 100, "sort": "asc"})
        if not page:
            break
        after = str(int(page[-1]["created_utc"]) + 1)
        for p in page:
            body = (p.get("selftext") or "").strip()
            removed = body in ("[removed]", "[deleted]") or p.get("removed_by_category")
            if removed or int(p.get("num_comments") or 0) < 2 or not (body or images(p)):
                continue
            out.append(p)
    return out[:want]


async def comments(http: httpx.AsyncClient, sem: asyncio.Semaphore, post_id: str) -> list[dict[str, Any]]:
    async with sem:
        return await get(http, "/comments/search", {"link_id": post_id, "limit": 50})


async def run(args: argparse.Namespace) -> None:
    out_dir = OUT.parent / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(4)
    async with httpx.AsyncClient(headers={"User-Agent": "ensayo-research/0.1 (hackathon validation)"}) as http:
        for sub in args.subs or SUBS:
            found = await posts(http, sub, max(args.after, CUTOFF), args.before, args.per_sub)
            threads = await asyncio.gather(*(comments(http, sem, p["id"]) for p in found))
            items: list[dict[str, Any]] = []
            for p, com in zip(found, threads):
                items.append({"dataType": "post", "id": f"t3_{p['id']}", "communityName": f"r/{sub}", "title": p.get("title"),
                              "body": p.get("selftext"), "imageUrls": images(p), "createdAt": iso(p["created_utc"]),
                              "url": f"https://www.reddit.com{p.get('permalink', '')}", "numberOfComments": p.get("num_comments")})
                for c in com:
                    top = str(c.get("parent_id", "")).startswith("t3_")
                    items.append({"dataType": "comment", "postId": f"t3_{p['id']}", "username": c.get("author"),
                                  "body": c.get("body"), "upVotes": c.get("score") or 0, "depth": "0" if top else "1"})
            path = out_dir / f"arctic_{sub}.json"
            path.write_text(json.dumps(items), encoding="utf-8")
            log.info(f"r/{sub}: {len(found)} publicaciones → {path}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-sub", type=int, default=600)
    ap.add_argument("--before", default="2026-10-28")
    ap.add_argument("--after", default=CUTOFF)
    ap.add_argument("--subs", nargs="*")
    ap.add_argument("--out-dir", default="scams", help="carpeta dentro de data/raw/ (scams2 = intento 2)")
    asyncio.run(run(ap.parse_args()))


if __name__ == "__main__":
    main()
