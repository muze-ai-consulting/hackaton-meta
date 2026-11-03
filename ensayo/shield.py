"""Escudo antiestafas: la persona reenvía un mensaje, pantallazos o una nota de voz y recibe veredicto, razón y qué hacer.

El prompt es el mismo que pasó la validación preregistrada del intento 2 (scripts/validate_scams.py importa de aquí,
así no se separan). El producto le agrega una sola línea, LANGUAGE_LINE, para responder en el idioma de la persona.
Las notas de voz pasan primero por Muse Voice Transcribe (/asr/transcribe, solo WAV: se convierte con ffmpeg).
Los datos de usuarios van por el endpoint estándar (muse-spark-1.3), nunca por el contributor.
"""

import asyncio
import base64
import io
import logging
import shutil
from typing import Any

from PIL import Image, UnidentifiedImageError

from ensayo.llm import ModelClient, estimate_call_usd, extract_json

log = logging.getLogger(__name__)

MAX_IMAGES = 3
MAX_TEXT = 3000
IMAGE_TOKENS = 800
# Bandas para mostrar el resultado. 0,5 es el umbral medido; las otras dos se describen con su tasa real en
# results/scam_bands.json (página "How we measured it").
BANDS = ((0.5, "scam"), (0.2, "careful"), (0.0, "genuine"))

SHIELD_SYSTEM = (
    "You are a scam shield inside a messaging app. People forward you a message, screenshot, call description or "
    "offer and ask whether it is a scam. Judge it carefully: many real banks, couriers, employers and platforms send "
    "messages that look alarming, and calling a genuine message a scam also hurts people."
)

# Intento 2 (3-nov): el intento 1 juzgaba si la publicación era engañosa; aquí se juzga la situación que la
# persona describe, que es lo que responde la comunidad (y lo que hace el producto).
SITUATION = (
    "The person below describes something they ran into: a message, call, website, seller, job offer, charge or "
    "transaction, sometimes with screenshots, sometimes after it already happened. Decide whether what they ran "
    "into is a scam or fraud (someone deliberately deceiving them to take money, data or an account) or legitimate "
    "(a genuine company or person, even if it is bad service, a mistake, a dispute or ordinary marketing spam)."
)

LANGUAGE_LINE = "Write reason and action in the language the person wrote or spoke in."


def shield_messages(post: dict[str, Any], images: list[str], round_: int = 1, language: bool = False) -> list[dict[str, Any]]:
    intro = f"{SITUATION}\n\n" if round_ == 2 else ""
    question = "Is what they ran into a scam?" if round_ == 2 else "Is this a scam?"
    content: list[dict[str, Any]] = [{"type": "text", "text": f"{intro}Title: {post['title']}\n\n{post['body'][:MAX_TEXT] or '(no text)'}"}]
    content += [{"type": "image_url", "image_url": {"url": u}} for u in images]
    content.append({"type": "text", "text": (
        f"{question} Give the probability that it is a scam (0-100), a verdict and the one thing the person "
        'should do now.\nFormat: {"scam_probability": 85, "verdict": "scam|legit", "reason": "max 20 words", '
        '"action": "max 15 words"}'
    ) + (f"\n{LANGUAGE_LINE}" if language else "")})
    return [{"role": "system", "content": SHIELD_SYSTEM}, {"role": "user", "content": content}]


def band(p: float) -> str:
    return next(name for floor, name in BANDS if p >= floor)


def shrink_image(data_url: str) -> str:
    """Pantallazo del usuario a JPEG de 1024 px como máximo (el mismo tamaño que en la validación)."""
    try:
        raw = base64.b64decode(data_url.split(",", 1)[-1])
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except (ValueError, UnidentifiedImageError, OSError) as exc:
        raise ValueError("One of the images could not be read.") from exc
    img.thumbnail((1024, 1024))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(out.getvalue()).decode()


async def to_wav(audio: bytes) -> bytes:
    """Cualquier audio (nota de voz de WhatsApp, grabación del navegador, m4a) a WAV mono de 16 kHz."""
    if audio[:4] == b"RIFF":
        return audio
    if not shutil.which("ffmpeg"):
        raise ValueError("This server cannot convert audio; upload a WAV file.")
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-t", "600", "-ac", "1", "-ar", "16000", "-f", "wav", "pipe:1",
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate(audio)
    if proc.returncode != 0 or not out:
        log.warning(f"ffmpeg: {err.decode(errors='replace')[:300]}")
        raise ValueError("The audio could not be read.")
    return out


async def check(
    client: ModelClient,
    *,
    model: str,
    phase: str,
    text: str = "",
    note: str = "",
    images: list[str] | None = None,
    audio: bytes | None = None,
) -> dict[str, Any]:
    """Veredicto del escudo para lo que la persona reenvió. `note` es lo que cuenta ella; `text`, el mensaje."""
    transcript = ""
    if audio:
        transcript = (await client.transcribe(await to_wav(audio), phase=phase, note="escudo voz")).strip()
    body = "\n\n".join(part for part in (
        text.strip(),
        f"Transcript of the voice note or call:\n{transcript}" if transcript else "",
    ) if part)
    post = {"title": note.strip() or "Is this a scam?", "body": body}
    pics = [shrink_image(u) for u in (images or [])[:MAX_IMAGES]]
    if not body and not pics:
        raise ValueError("Paste a message, add a screenshot or a voice note.")
    messages = shield_messages(post, pics, round_=2, language=True)
    upcoming = estimate_call_usd(model, len(str(post)) + 2000, 400, IMAGE_TOKENS * len(pics))
    res = await client.chat(model, messages, phase=phase, max_tokens=200, upcoming_usd=upcoming, note="escudo")
    try:
        out = extract_json(res.text)
        p = max(0.0, min(1.0, float(out["scam_probability"]) / 100))
    except (ValueError, KeyError, TypeError) as exc:
        # RuntimeError: es falla del modelo, no del pedido (la API la responde como 502, no 422).
        raise RuntimeError(f"unreadable answer: {res.text[:200]!r}") from exc
    return {
        "probability": round(p, 3),
        "band": band(p),
        "verdict": "scam" if p >= 0.5 else "legit",
        "reason": str(out.get("reason") or ""),
        "action": str(out.get("action") or ""),
        "transcript": transcript,
        "images": len(pics),
    }
