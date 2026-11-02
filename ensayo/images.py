"""Variantes de un anuncio con Muse Image: de una descripción (y una foto opcional) a 2-4 variantes con imagen.

1. Una llamada a Spark 1.3 escribe un ángulo creativo por variante: título, texto y un prompt de imagen. Si hay
   foto del producto, la ve para describir el producto tal como es.
2. Una llamada a `muse-image-1.0` (/images/generations, US$0,01 por imagen) por variante.

Las dos pasan por el `Ledger`. Es para el demo: datos de clientes, así que va por el endpoint estándar y nunca
por el contributor. En modo falso, `ensayo.mock` responde las dos sin red con una imagen de relleno.
"""

import asyncio
import base64
import logging
from typing import Any

from ensayo.llm import ModelClient, estimate_call_usd, extract_json

log = logging.getLogger(__name__)

IMAGE_MODEL = "muse-image-1.0"
IMAGE_SIZE = "1024x1024"
MAX_VARIANTS = 4

SYSTEM_CREATIVE = (
    "You are a creative director for Facebook and Instagram ads. You propose versions that truly differ in angle "
    "(benefit, social proof, price, emotion, curiosity), not just in wording. Reply with valid JSON only."
)


def creative_prompt(brand: str, brief: str, n: int, has_photo: bool) -> str:
    photo = (
        "The attached image is the product photo: describe the product exactly as it looks in every image prompt.\n"
        if has_photo
        else ""
    )
    return (
        "Task: creative_variants\n"
        f"Brand: {brand or '(no brand)'}\n"
        f"Product or idea: {' '.join(brief.split()) or '(no description)'}\n"
        f"Count: {n}\n"
        f"{photo}"
        f"Propose {n} ad versions, each with a different angle. For each one: a headline of up to 40 characters, "
        "primary text of up to 125 characters in the same language as the description, and an image prompt in "
        "English for an image generator (square advertising photo, no written text in the image).\n"
        'Format: {"variants": [{"angle": "...", "headline": "...", "text": "...", "image_prompt": "..."}]}'
    )


def _image_src(item: dict[str, Any]) -> str:
    """La imagen como data URL si viene en base64, o la URL que entregue la API."""
    if item.get("b64_json"):
        base64.b64decode(item["b64_json"], validate=True)  # falla aquí si no es base64
        return f"data:image/png;base64,{item['b64_json']}"
    if item.get("url"):
        return item["url"]
    raise ValueError("La respuesta de imagen no trae b64_json ni url")


async def generate_image(client: ModelClient, prompt: str, *, phase: str, note: str = "") -> str:
    body = await client.image(IMAGE_MODEL, prompt, phase=phase, size=IMAGE_SIZE, note=note)
    return _image_src(body["data"][0])


async def generate_variants(
    client: ModelClient,
    *,
    brand: str,
    brief: str,
    n: int = 3,
    photo_url: str | None = None,
    model: str = "muse-spark-1.3",
    phase: str = "demo",
) -> list[dict[str, Any]]:
    """n variantes con título, texto e imagen generada."""
    n = max(2, min(n, MAX_VARIANTS))
    text = creative_prompt(brand, brief, n, bool(photo_url))
    content: str | list[dict[str, Any]] = text
    if photo_url:
        content = [{"type": "text", "text": text}, {"type": "image_url", "image_url": {"url": photo_url}}]
    messages = [{"role": "system", "content": SYSTEM_CREATIVE}, {"role": "user", "content": content}]
    upcoming = estimate_call_usd(model, len(str(messages)), 250 * n, 1200 if photo_url else 0)
    res = await client.chat(model, messages, phase=phase, max_tokens=300 * n, upcoming_usd=upcoming, note="variantes")
    body = extract_json(res.text)
    ideas = (body.get("variants") or body.get("variantes") or [])[:n]
    if len(ideas) < 2:
        raise ValueError(f"El modelo propuso {len(ideas)} variantes; se necesitan al menos 2")

    images = await asyncio.gather(
        *(generate_image(client, idea.get("image_prompt") or idea.get("prompt_imagen") or brief, phase=phase, note="variantes") for idea in ideas)
    )
    return [
        {
            "angle": str(idea.get("angle") or idea.get("angulo") or ""),
            "title": str(idea.get("headline") or idea.get("titulo") or "")[:200],
            "body": str(idea.get("text") or idea.get("texto") or "")[:2000],
            "image_prompt": str(idea.get("image_prompt") or idea.get("prompt_imagen") or ""),
            "image_url": src,
        }
        for idea, src in zip(ideas, images)
    ]
