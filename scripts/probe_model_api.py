"""Prueba del día 0 de la Meta Model API: modelos, texto, imagen, video, Muse Image y tier contributor.

Lee MODEL_API_KEY desde .env. Guarda el resultado en results/probe_model_api.json.

Uso: uv run python scripts/probe_model_api.py
"""

import base64
import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
from io import BytesIO
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

from ensayo.costs import IMAGE_PRICE, PRICES, Ledger

ROOT = Path(__file__).resolve().parent.parent
BASE = os.environ.get("MODEL_API_BASE", "https://api.meta.ai/v1")
SPARK = "muse-spark-1.3"
SPARK_CONTRIB = "muse-spark-1.3-contributor"
IMAGE_MODEL = "muse-image-1.0"
SECRET_WORD = "ENSAYO 42"
LEDGER = Ledger()

log = logging.getLogger("probe")


def test_image_png() -> bytes:
    """Imagen sintética con contenido verificable: texto, un círculo rojo a la izquierda, un cuadrado azul a la derecha."""
    img = Image.new("RGB", (640, 400), "white")
    draw = ImageDraw.Draw(img)
    draw.ellipse((40, 120, 200, 280), fill="red")
    draw.rectangle((440, 120, 600, 280), fill="blue")
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 48)
    except OSError:
        font = ImageFont.load_default()
    draw.text((200, 30), SECRET_WORD, fill="black", font=font)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_video_mp4() -> bytes | None:
    """Video de 4 s: 2 s rojo y 2 s verde. Sirve para ver si el modelo percibe el orden temporal."""
    if not shutil.which("ffmpeg"):
        return None
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "v.mp4"
        cmd = [
            "ffmpeg", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "color=c=red:s=320x240:d=2:r=10",
            "-f", "lavfi", "-i", "color=c=green:s=320x240:d=2:r=10",
            "-filter_complex", "[0:v][1:v]concat=n=2:v=1[v]", "-map", "[v]",
            "-pix_fmt", "yuv420p", str(out),
        ]
        subprocess.run(cmd, check=True)
        return out.read_bytes()


def call(client: httpx.Client, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    t0 = time.monotonic()
    try:
        r = client.request(method, f"{BASE}{path}", json=payload)
    except httpx.HTTPError as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "secs": round(time.monotonic() - t0, 2)}
    secs = round(time.monotonic() - t0, 2)
    try:
        body = r.json()
    except json.JSONDecodeError:
        body = {"raw": r.text[:500]}
    return {"ok": r.is_success, "status": r.status_code, "secs": secs, "body": body}


def chat(client: httpx.Client, model: str, content: Any, max_tokens: int = 200) -> dict[str, Any]:
    res = call(client, "POST", "/chat/completions", {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max_tokens,
    })
    if res.get("ok"):
        body = res.pop("body")
        res["answer"] = body["choices"][0]["message"].get("content")
        res["usage"] = body.get("usage")
        if model in PRICES and res["usage"]:
            res["usd"] = round(LEDGER.record_chat("pruebas", model, res["usage"], note="probe_model_api"), 6)
    return res


def summarize(res: dict[str, Any]) -> dict[str, Any]:
    """Recorta cuerpos de error largos para el JSON de salida."""
    if "body" in res:
        res["body"] = json.dumps(res["body"])[:600]
    return res


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    load_dotenv(ROOT / ".env")
    key = os.environ.get("MODEL_API_KEY") or os.environ.get("META_API_KEY")
    if not key:
        raise SystemExit("Falta MODEL_API_KEY (o META_API_KEY) en .env (ver .env.example).")

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    out: dict[str, Any] = {"base": BASE, "ran_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}

    with httpx.Client(headers=headers, timeout=120) as client:
        models = call(client, "GET", "/models")
        if models.get("ok"):
            ids = sorted(m.get("id", "") for m in models["body"].get("data", []))
            out["models"] = {"ok": True, "secs": models["secs"], "ids": ids}
        else:
            out["models"] = summarize(models)
        log.info(f"models: {out['models'].get('ids') or out['models']}")

        out["text"] = chat(client, SPARK, "Responde solo con la palabra: listo")
        log.info(f"text: {out['text'].get('answer') or out['text']}")

        out["text_contributor"] = chat(client, SPARK_CONTRIB, "Responde solo con la palabra: listo")
        log.info(f"contributor: {out['text_contributor'].get('answer') or out['text_contributor']}")

        img_b64 = base64.b64encode(test_image_png()).decode()
        question = (
            "Describe esta imagen en una línea: qué texto aparece, qué figura hay a la izquierda "
            "y de qué color, y qué figura hay a la derecha y de qué color."
        )
        out["image"] = chat(client, SPARK, [
            {"type": "text", "text": question},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
        ])
        answer = (out["image"].get("answer") or "").upper()
        out["image"]["passes"] = all(w in answer for w in ("ENSAYO", "42", "ROJ", "AZUL"))
        log.info(f"image: {out['image'].get('answer') or out['image']}")

        # Tokens por imagen y caché: de estos dos números depende el costo por lote (ensayo.costs.estimate_batch_usd).
        text_tokens = ((out["text"].get("usage") or {}).get("prompt_tokens")) or 0
        img_tokens = ((out["image"].get("usage") or {}).get("prompt_tokens")) or 0
        out["image_tokens_approx"] = img_tokens - text_tokens - 40 if img_tokens else None
        long_prefix = "Instrucciones de simulación. " * 300  # ~1.800 tokens, sobre el mínimo típico para cachear
        cache_runs = []
        for _ in range(2):
            res = chat(client, SPARK_CONTRIB, [
                {"type": "text", "text": long_prefix},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                {"type": "text", "text": "Responde solo: ok"},
            ], max_tokens=5)
            cache_runs.append((res.get("usage") or {}).get("prompt_tokens_details", {}).get("cached_tokens"))
        out["cache"] = {"cached_tokens_second_call": cache_runs[-1], "works": bool(cache_runs[-1])}
        log.info(f"tokens por imagen ≈ {out['image_tokens_approx']} · caché: {out['cache']}")

        video = test_video_mp4()
        if video is None:
            out["video"] = {"ok": False, "error": "ffmpeg no disponible"}
        else:
            vid_b64 = base64.b64encode(video).decode()
            vq = "Este video cambia de color. ¿Qué color aparece primero y cuál después? Responde en una línea."
            # El formato de video no está documentado: se prueban las dos formas más comunes.
            attempts = {
                "video_url": {"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{vid_b64}"}},
                "file": {"type": "file", "file": {"filename": "v.mp4", "file_data": f"data:video/mp4;base64,{vid_b64}"}},
            }
            out["video"] = {}
            for name, part in attempts.items():
                res = chat(client, SPARK, [{"type": "text", "text": vq}, part])
                ans = (res.get("answer") or "").upper()
                res["passes"] = ans.find("ROJ") != -1 and ans.find("VERD") > ans.find("ROJ")
                out["video"][name] = summarize(res)
                log.info(f"video[{name}]: {res.get('answer') or res}")
                if res["passes"]:
                    break

        gen = call(client, "POST", "/images/generations", {
            "model": IMAGE_MODEL,
            "prompt": "Foto de producto: una botella de agua de acero sobre una mesa de madera, luz natural",
            "n": 1,
            "size": "1024x1024",
        })
        if gen.get("ok"):
            item = gen["body"]["data"][0]
            results = ROOT / "results"
            results.mkdir(exist_ok=True)
            if item.get("b64_json"):
                (results / "probe_muse_image.png").write_bytes(base64.b64decode(item["b64_json"]))
                saved = "results/probe_muse_image.png"
            else:
                saved = item.get("url")
            out["image_generation"] = {"ok": True, "secs": gen["secs"], "saved": saved}
            LEDGER.record("pruebas", IMAGE_MODEL, IMAGE_PRICE[IMAGE_MODEL], note="probe_model_api")
        else:
            out["image_generation"] = summarize(gen)
        log.info(f"image_generation: {out['image_generation']}")

    for k in ("text", "text_contributor", "image"):
        summarize(out[k])
    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    (results / "probe_model_api.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info(f"Guardado en results/probe_model_api.json · gasto: {LEDGER.report()}")


if __name__ == "__main__":
    main()
