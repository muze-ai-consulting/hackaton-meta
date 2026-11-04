"""Validación del escudo antiestafas con preguntas reales de Reddit ("¿esto es estafa?"), posteriores al corte.

Tres pasos, en orden, con commit entre el segundo y el tercero (preregistro en ESTADO.md):

    --label    Lee solo los comentarios de cada publicación y extrae el veredicto de la comunidad (scam/legit/unclear).
    --predict  Lee solo la publicación (título, texto e imágenes) y predice. Guarda las predicciones y su SHA-256,
               sin puntuar.
    --score    Cruza predicciones y etiquetas, con los rivales (regla de palabras clave y "siempre estafa").

Los datos son públicos (Reddit), así que van por muse-spark-1.3-contributor.

    uv run python scripts/validate_scams.py --label --yes
"""

import argparse
import asyncio
import base64
import hashlib
import io
import json
import logging
import random
import re
from pathlib import Path
from typing import Any

import httpx
from PIL import Image, UnidentifiedImageError

from ensayo import DATA, RESULTS
from ensayo.llm import ModelClient, estimate_call_usd, extract_json
from ensayo.shield import shield_messages  # el mismo prompt que usa el producto

log = logging.getLogger(__name__)

MODEL = "muse-spark-1.3-contributor"
CUTOFF = "2026-09-03"
RAW = DATA / "raw" / "scams"
IMAGES = DATA / "images" / "scams"
LABELS = DATA / "scams" / "labels.json"
PREDICTIONS = RESULTS / "scam_predictions.json"
MAX_IMAGES = 3

# Rival clásico: lo que un filtro de reglas marcaría como estafa.
KEYWORDS = re.compile(
    r"gift ?card|crypto|bitcoin|usdt|wire|western union|zelle|cash ?app|venmo|paypal|verify|verification|"
    r"suspend|locked|urgent|immediately|click|link|code|otp|password|refund|prize|won|winner|lottery|"
    r"invest|profit|job offer|work from home|telegram|whatsapp|deposit|fee|kyc|parcel|package|toll|customs",
    re.I,
)


def load_posts(raw: Path = RAW) -> list[dict[str, Any]]:
    """Publicaciones posteriores al corte, con sus comentarios humanos (sin AutoModerator)."""
    posts: dict[str, dict[str, Any]] = {}
    comments: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(raw.glob("*.json")):
        for it in json.loads(path.read_text(encoding="utf-8")):
            if it.get("dataType") == "post" and it.get("createdAt", "") >= CUTOFF:
                posts[it["id"]] = it
            elif it.get("dataType") == "comment" and it.get("username") != "AutoModerator" and (it.get("body") or "").strip():
                comments.setdefault(it["postId"], []).append(it)
    out = []
    for pid, p in posts.items():
        com = comments.get(pid, [])
        if not com:
            continue
        images = p.get("imageUrls")
        if isinstance(images, str):
            images = re.findall(r"https?://[^'\"\]\s,]+", images)
        out.append({
            "id": pid, "community": p.get("communityName"), "created": p["createdAt"], "title": p.get("title") or "",
            "body": (p.get("body") or "").strip(), "images": (images or [])[:MAX_IMAGES], "url": p.get("url"),
            "comments": [{"body": c["body"].strip()[:600], "up": int(c.get("upVotes") or 0), "depth": c.get("depth")}
                         for c in com if str(c.get("depth")) in ("0", "None")][:8],
        })
    return sorted(out, key=lambda r: r["id"])


def label_messages(post: dict[str, Any]) -> list[dict[str, Any]]:
    lines = "\n".join(f"- ({c['up']} upvotes) {c['body']}" for c in sorted(post["comments"], key=lambda c: -c["up"]))
    text = (
        "Someone asked an online community whether a message, call, website or offer was a scam. Below are the "
        "community's replies only (you do not see the original post). What is the community's verdict?\n"
        f"Replies:\n{lines}\n\n"
        'Answer "scam" if replies agree it is a scam or fraud attempt, "legit" if they agree it is genuine or harmless, '
        '"unclear" if they disagree, do not say, or only give generic advice.\n'
        'Format: {"verdict": "scam|legit|unclear"}'
    )
    return [{"role": "user", "content": text}]


async def image_uri(http: httpx.AsyncClient, url: str, key: str) -> str | None:
    path = IMAGES / f"{key}.jpg"
    if not path.exists():
        try:
            r = await http.get(url, timeout=30)
            r.raise_for_status()
            img = Image.open(io.BytesIO(r.content)).convert("RGB")
        except (httpx.HTTPError, UnidentifiedImageError, OSError) as exc:
            log.warning(f"{key}: sin imagen ({exc})")
            return None
        img.thumbnail((1024, 1024))
        IMAGES.mkdir(parents=True, exist_ok=True)
        img.save(path, "JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


async def label_one(client: ModelClient, post: dict[str, Any]) -> str | None:
    try:
        res = await client.chat(MODEL, label_messages(post), phase="pruebas", max_tokens=40,
                                upcoming_usd=estimate_call_usd(MODEL, 3000, 300), note=f"etiqueta {post['id']}")
        return extract_json(res.text)["verdict"]
    except (RuntimeError, ValueError, KeyError) as exc:
        log.warning(f"{post['id']}: {exc}")
        return None


async def predict_one(client: ModelClient, http: httpx.AsyncClient, post: dict[str, Any], round_: int = 1) -> dict[str, Any] | None:
    images = [u for i, url in enumerate(post["images"]) if (u := await image_uri(http, url, f"{post['id']}_{i}"))]
    try:
        res = await client.chat(MODEL, shield_messages(post, images, round_), phase="pruebas", max_tokens=150,
                                upcoming_usd=estimate_call_usd(MODEL, 4000, 400, 800 * len(images)), note=f"escudo {post['id']}")
        body = extract_json(res.text)
        return {"p": float(body["scam_probability"]) / 100, "verdict": body.get("verdict"), "reason": body.get("reason"),
                "action": body.get("action"), "images": len(images)}
    except (RuntimeError, ValueError, KeyError, TypeError) as exc:
        log.warning(f"{post['id']}: {exc}")
        return None


def keyword_score(post: dict[str, Any]) -> float:
    return min(1.0, len(KEYWORDS.findall(f"{post['title']} {post['body']}")) / 3)


def auc(pos: list[float], neg: list[float]) -> float:
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def metrics(rows: list[dict[str, Any]], score: str, threshold: float = 0.5) -> dict[str, float]:
    pos = [r[score] for r in rows if r["label"] == "scam"]
    neg = [r[score] for r in rows if r["label"] == "legit"]
    recall = sum(s >= threshold for s in pos) / len(pos)
    false_alarm = sum(s >= threshold for s in neg) / len(neg)
    return {"balanced_accuracy": round((recall + 1 - false_alarm) / 2, 4), "recall_scam": round(recall, 4),
            "false_alarm_legit": round(false_alarm, 4), "auc": round(auc(pos, neg), 4)}


def bootstrap_gap(rows: list[dict[str, Any]], a: str, b: str, n: int = 2000) -> list[float]:
    """IC 95 % de la diferencia de exactitud balanceada a − b, remuestreando dentro de cada clase."""
    rng = random.Random(7)
    pos = [r for r in rows if r["label"] == "scam"]
    neg = [r for r in rows if r["label"] == "legit"]
    gaps = []
    for _ in range(n):
        sample = [rng.choice(pos) for _ in pos] + [rng.choice(neg) for _ in neg]
        gaps.append(metrics(sample, a)["balanced_accuracy"] - metrics(sample, b)["balanced_accuracy"])
    gaps.sort()
    return [round(gaps[int(0.025 * n)], 4), round(gaps[int(0.975 * n)], 4)]


async def run(args: argparse.Namespace) -> None:
    global LABELS, PREDICTIONS
    scored = RESULTS / "scam_scored.json"
    if args.round == 2:
        # Datos nuevos (data/raw/scams2) y archivos aparte; fuera todo lo que ya pasó por el intento 1.
        used = set(json.loads(LABELS.read_text(encoding="utf-8")))
        LABELS, PREDICTIONS = DATA / "scams" / "labels2.json", RESULTS / "scam_predictions2.json"
        scored = RESULTS / "scam_scored2.json"
        posts = [p for p in load_posts(DATA / "raw" / "scams2") if p["id"] not in used]
    else:
        posts = load_posts()
    if not posts and (args.label or args.predict):
        log.error("No hay publicaciones en data/raw: bájalas primero. No se sobrescribe nada.")
        return
    if args.label:
        log.info(f"{len(posts)} publicaciones con comentarios · costo estimado US$ {len(posts) * 0.0006:.2f}")
        if not args.yes:
            return
        client = ModelClient.from_env(concurrency=args.concurrency)
        client.effort = "low"
        verdicts = await asyncio.gather(*(label_one(client, p) for p in posts))
        await client.aclose()
        LABELS.parent.mkdir(parents=True, exist_ok=True)
        LABELS.write_text(json.dumps({p["id"]: v for p, v in zip(posts, verdicts) if v}, indent=1), encoding="utf-8")
        log.info(f"etiquetas: {json.dumps({v: verdicts.count(v) for v in set(verdicts)})}")
        return
    labels = json.loads(LABELS.read_text(encoding="utf-8"))
    posts = [p for p in posts if labels.get(p["id"]) in ("scam", "legit")]
    if args.predict:
        log.info(f"{len(posts)} publicaciones con veredicto claro · costo estimado US$ {len(posts) * 0.0015:.2f}")
        if not args.yes:
            return
        client = ModelClient.from_env(concurrency=args.concurrency)
        client.effort = "low"
        async with httpx.AsyncClient(follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as http:
            preds = await asyncio.gather(*(predict_one(client, http, p, args.round) for p in posts))
        await client.aclose()
        blob = json.dumps({p["id"]: r for p, r in zip(posts, preds) if r}, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(blob.encode()).hexdigest()
        PREDICTIONS.write_text(blob, encoding="utf-8")
        PREDICTIONS.with_suffix(".sha256").write_text(f"{digest}\n", encoding="utf-8")
        log.info(f"{blob.count('\"p\"')} predicciones · SHA-256 {digest}. Commitea y después corre --score.")
        return
    preds = json.loads(PREDICTIONS.read_text(encoding="utf-8"))
    rows = [{"id": p["id"], "community": p["community"], "label": labels[p["id"]], "shield": preds[p["id"]]["p"],
             "keywords": keyword_score(p), "always_scam": 1.0} for p in posts if p["id"] in preds]
    out = {
        "n": len(rows), "scam": sum(r["label"] == "scam" for r in rows), "legit": sum(r["label"] == "legit" for r in rows),
        "shield": metrics(rows, "shield"), "keywords": metrics(rows, "keywords"), "always_scam": metrics(rows, "always_scam"),
        "gap_vs_keywords_ci95": bootstrap_gap(rows, "shield", "keywords"),
    }
    s = out["shield"]
    out["rule"] = {
        "enough_legit": out["legit"] >= 30,
        "ba_at_least_0.80": s["balanced_accuracy"] >= 0.80,
        "beats_keywords_by_0.10": s["balanced_accuracy"] - out["keywords"]["balanced_accuracy"] >= 0.10 and out["gap_vs_keywords_ci95"][0] > 0,
        "false_alarm_at_most_0.30": s["false_alarm_legit"] <= 0.30,
    }
    out["rule"]["validated"] = all(out["rule"].values())
    scored.write_text(json.dumps(out, indent=1), encoding="utf-8")
    log.info(json.dumps(out, indent=1))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", action="store_true")
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--round", type=int, default=1, choices=(1, 2))
    ap.add_argument("--concurrency", type=int, default=6)
    asyncio.run(run(ap.parse_args()))


if __name__ == "__main__":
    main()
