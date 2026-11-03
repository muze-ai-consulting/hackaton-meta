"""Baja publicaciones de r/Scams (y afines) con sus comentarios vía Apify (actor trudax/reddit-scraper-lite).

Es la materia prima del set de validación del escudo antiestafas: gente que pregunta "¿esto es estafa?" con el
mensaje o el pantallazo, y la comunidad que responde. Solo publicaciones posteriores al corte de contaminación.

    uv run --with httpx python scripts/scam_reddit.py --out data/raw/scams/pilot.json --posts 20
"""

import argparse
import json
import logging
import pathlib
import time

import httpx

log = logging.getLogger(__name__)

API = "https://api.apify.com/v2"
ACTOR = "trudax~reddit-scraper-lite"
CUTOFF = "2026-09-03"
ROOT = pathlib.Path(__file__).resolve().parent.parent


def tokens() -> list[str]:
    """Las cuentas de Apify de .env, en orden (APIFY_TOKEN, APIFY_TOKEN_2…)."""
    env = {}
    for line in (ROOT / ".env").read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip('"')
    return [env[k] for k in sorted(env) if k.startswith("APIFY_TOKEN") and env[k]]


def run(url: str, posts: int, comments: int) -> list[dict]:
    payload = {
        "startUrls": [{"url": url}], "maxItems": posts * (comments + 1), "maxPostCount": posts,
        "maxComments": comments, "includeMediaLinks": True, "skipUserPosts": True, "skipCommunity": True,
        "postDateLimit": CUTOFF, "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
    }
    for token in tokens():
        head = {"Authorization": f"Bearer {token}"}
        started = httpx.post(f"{API}/acts/{ACTOR}/runs?timeout=2400&memory=2048", json=payload, headers=head, timeout=60).json()
        if "data" not in started:
            log.warning("cuenta sin cupo: %s", started.get("error", {}).get("message"))
            continue
        run_id = started["data"]["id"]
        while True:
            state = httpx.get(f"{API}/actor-runs/{run_id}", headers=head, timeout=60).json().get("data") or {}
            if state.get("status") not in (None, "READY", "RUNNING"):
                break
            time.sleep(10)
        items = httpx.get(f"{API}/datasets/{state['defaultDatasetId']}/items", headers=head, timeout=300).json()
        log.info("%s: %s, %d ítems, US$ %s", url, state["status"], len(items), state.get("usageTotalUsd"))
        return items
    raise RuntimeError("ninguna cuenta de Apify tiene cupo")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", action="append", default=None)
    ap.add_argument("--posts", type=int, default=20)
    ap.add_argument("--comments", type=int, default=8)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()
    items: list[dict] = []
    for url in args.url or ["https://www.reddit.com/r/Scams/new/"]:
        items += run(url, args.posts, args.comments)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(items))
    log.info("guardado %s (%d ítems)", args.out, len(items))


if __name__ == "__main__":
    main()
