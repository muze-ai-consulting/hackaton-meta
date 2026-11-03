"""Servidor falso de la Model API: responde /chat/completions e /images/generations sin red y sin gastar créditos.

Lee los mismos prompts que arma `ensayo.simulate` y devuelve JSON con la forma esperada. Las reacciones son
pseudoaleatorias pero deterministas (dependen del texto de cada persona y anuncio), así que las pruebas son
repetibles. No tiene ninguna señal real: en el backtest debe rendir como el azar. El uso de tokens se estima
con 4 caracteres por token y 1.200 tokens por imagen, para que el medidor muestre el costo de la corrida real.
Las imágenes generadas son un degradado de relleno cuyos colores dependen del prompt.
"""

import base64
import hashlib
import json
import re
import struct
import zlib
from typing import Any

import httpx

IMAGE_TOKENS = 1200
AD_LINE = re.compile(r"^Ad ([A-H]):(.*)$", re.MULTILINE)
PERSONA_LINE = re.compile(r"^P(\d+):(.*)$", re.MULTILINE)
COUNT_LINE = re.compile(r"^Count: (\d+)$", re.MULTILINE)
BRIEF_LINE = re.compile(r"^Product or idea: (.*)$", re.MULTILINE)
ANGLES = ["benefit", "social proof", "price", "curiosity"]
PLACEHOLDER_SIDE = 256


def _unit(*parts: str) -> float:
    """Número estable en [0, 1) a partir de un texto."""
    return int(hashlib.sha256("|".join(parts).encode()).hexdigest()[:8], 16) / 0x100000000


def _flatten(messages: list[dict[str, Any]]) -> tuple[str, int]:
    texts, images = [], 0
    for m in messages:
        content = m.get("content")
        if isinstance(content, str):
            texts.append(content)
            continue
        for part in content or []:
            if part.get("type") == "text":
                texts.append(part["text"])
            elif part.get("type") == "image_url":
                images += 1
    return "\n".join(texts), images


def _simulation(prompt: str) -> dict[str, Any]:
    ads = AD_LINE.findall(prompt)
    out = []
    for num, persona in PERSONA_LINE.findall(prompt):
        stops = [letter for letter, ad in ads if _unit(persona, ad, "frena") < 0.35]
        clicks = [letter for letter, ad in ads if letter in stops and _unit(persona, ad, "clic") < 0.3]
        out.append({"p": int(num), "stop": stops, "click": clicks, "reason": "placeholder answer from the mock server"})
    return {"reactions": out}


def _ranking(prompt: str) -> dict[str, Any]:
    letters = [letter for letter, _ in AD_LINE.findall(prompt)]
    return {"ranking": sorted(letters, key=lambda x: _unit(prompt, x)), "reason": "placeholder order from the mock server"}


def _creative(prompt: str) -> dict[str, Any]:
    n = int(COUNT_LINE.search(prompt).group(1)) if COUNT_LINE.search(prompt) else 3
    brief = (BRIEF_LINE.search(prompt).group(1) if BRIEF_LINE.search(prompt) else "the product").strip()
    short = brief[:60]
    return {
        "variants": [
            {
                "angle": ANGLES[i % len(ANGLES)],
                "headline": f"Test {i + 1}: {ANGLES[i % len(ANGLES)]}",
                "text": f"Placeholder copy from the mock server about {short}.",
                "image_prompt": f"Advertising photo, angle {ANGLES[i % len(ANGLES)]}: {short}",
            }
            for i in range(n)
        ]
    }


def placeholder_png(seed: str, side: int = PLACEHOLDER_SIDE) -> bytes:
    """PNG con un degradado diagonal entre dos colores derivados de seed, sin dependencias."""
    h = hashlib.sha256(seed.encode()).digest()
    a, b = h[:3], h[3:6]
    rows = []
    for y in range(side):
        row = bytearray([0])
        for x in range(side):
            t = (x + y) / (2 * (side - 1))
            row += bytes(round(a[c] + (b[c] - a[c]) * t) for c in range(3))
        rows.append(bytes(row))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    header = struct.pack(">IIBBBBB", side, side, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(b"".join(rows))) + chunk(b"IEND", b"")


def respond_image(payload: dict[str, Any]) -> dict[str, Any]:
    png = placeholder_png(str(payload.get("prompt") or ""))
    return {"created": 0, "data": [{"b64_json": base64.b64encode(png).decode()}]}


def _conversation(messages: list[dict[str, Any]]) -> str:
    question = str(messages[-1].get("content") or "")[:80]
    return f"(Placeholder answer from the mock server.) You're asking me \"{question}\". What I remember is how I reacted in the feed."


SCAM_HINTS = re.compile(r"gift ?card|crypto|code|verify|urgent|locked|fee|prize|won|click|link|password|bank", re.I)


def _shield(prompt: str) -> dict[str, Any]:
    """Probabilidad de relleno según palabras sospechosas: el servidor falso no juzga nada de verdad."""
    hits = len(SCAM_HINTS.findall(prompt.split("Title:", 1)[-1]))
    p = min(95, 10 + 20 * hits)
    return {"scam_probability": p, "verdict": "scam" if p >= 50 else "legit",
            "reason": "Placeholder from the mock server, based only on suspicious words.",
            "action": "Turn on real mode for a real verdict."}


def respond(payload: dict[str, Any]) -> dict[str, Any]:
    messages = payload.get("messages") or []
    prompt, images = _flatten(messages)
    if "You are a scam shield" in prompt:
        text = json.dumps(_shield(prompt))
    elif "Task: conversation" in prompt:
        text = _conversation(messages)
    else:
        if "Task: creative_variants" in prompt:
            body = _creative(prompt)
        else:
            body = _simulation(prompt) if '"reactions"' in prompt else _ranking(prompt)
        text = json.dumps(body, ensure_ascii=False)
    usage = {
        "prompt_tokens": len(prompt) // 4 + images * IMAGE_TOKENS,
        "completion_tokens": len(text) // 4,
        "prompt_tokens_details": {"cached_tokens": 0},
    }
    return {
        "id": "mock",
        "object": "chat.completion",
        "model": payload.get("model"),
        "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        "usage": usage,
    }


def _handler(request: httpx.Request) -> httpx.Response:
    if request.url.path.endswith("/chat/completions"):
        return httpx.Response(200, json=respond(json.loads(request.content)))
    if request.url.path.endswith("/asr/transcribe"):
        # WAV de 16 kHz mono: la duración sale del tamaño. El texto es de relleno.
        seconds = max(0, len(request.content) - 44) / 32_000
        return httpx.Response(200, json={"transcript": "Hello, this is your bank. Please read me the code we just sent you.",
                                         "audioDurationMs": int(seconds * 1000), "turns": []})
    if request.url.path.endswith("/images/generations"):
        return httpx.Response(200, json=respond_image(json.loads(request.content)))
    return httpx.Response(404, json={"error": {"message": f"El servidor falso no implementa {request.url.path}"}})


def transport() -> httpx.MockTransport:
    return httpx.MockTransport(_handler)
