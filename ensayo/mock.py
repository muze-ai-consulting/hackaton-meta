"""Servidor falso de la Model API: responde /chat/completions sin red y sin gastar créditos.

Lee los mismos prompts que arma `ensayo.simulate` y devuelve JSON con la forma esperada. Las reacciones son
pseudoaleatorias pero deterministas (dependen del texto de cada persona y anuncio), así que las pruebas son
repetibles. No tiene ninguna señal real: en el backtest debe rendir como el azar. El uso de tokens se estima
con 4 caracteres por token y 1.200 tokens por imagen, para que el medidor muestre el costo de la corrida real.
"""

import hashlib
import json
import re
from typing import Any

import httpx

IMAGE_TOKENS = 1200
AD_LINE = re.compile(r"^Anuncio ([A-H]):(.*)$", re.MULTILINE)
PERSONA_LINE = re.compile(r"^P(\d+):(.*)$", re.MULTILINE)


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
        out.append({"p": int(num), "frena": stops, "clic": clicks, "motivo": "respuesta de prueba del servidor falso"})
    return {"reacciones": out}


def _ranking(prompt: str) -> dict[str, Any]:
    letters = [letter for letter, _ in AD_LINE.findall(prompt)]
    return {"ranking": sorted(letters, key=lambda x: _unit(prompt, x)), "motivo": "orden de prueba del servidor falso"}


def respond(payload: dict[str, Any]) -> dict[str, Any]:
    prompt, images = _flatten(payload.get("messages") or [])
    body = _simulation(prompt) if "reacciones" in prompt else _ranking(prompt)
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
    return httpx.Response(404, json={"error": {"message": f"El servidor falso no implementa {request.url.path}"}})


def transport() -> httpx.MockTransport:
    return httpx.MockTransport(_handler)
