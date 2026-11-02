"""Conversar con una persona de la audiencia: preguntarle por qué frenó, hizo clic o pasó de largo.

La persona responde en primera persona, con su descripción, los anuncios que vio (mismas letras que el demo) y
su reacción en la simulación como contexto, y puede discutir. Cada pregunta es una llamada a Spark 1.3 que pasa
por el `Ledger`. Es para el demo: va por el endpoint estándar, nunca por el contributor.
"""

import logging
from typing import Any

from ensayo.llm import ModelClient, estimate_call_usd
from ensayo.simulate import IMAGE_TOKENS, LETTERS, _content

log = logging.getLogger(__name__)

MAX_TURNS = 10  # mensajes previos que se reenvían
MAX_REPLY_TOKENS = 300

SYSTEM_PERSONA = (
    "Eres una persona real que navega su feed de Facebook o Instagram, no un asistente ni un experto en marketing. "
    "Respondes en primera persona, en el idioma de la pregunta, con 80 palabras como máximo, con tu forma de "
    "hablar y tus prioridades. Si un anuncio no te interesó, lo dices sin rodeos y explicas por qué; no intentas "
    "agradar a quien pregunta ni cambias de opinión solo porque te insistan. No menciones que eres simulada."
)


def _letters(ids: list[str], variants: list[dict[str, Any]]) -> str:
    pos = {v["ad_id"]: LETTERS[i] for i, v in enumerate(variants)}
    picked = [pos[i] for i in ids if i in pos]
    return ", ".join(picked) or "ninguno"


def persona_messages(
    *,
    brand: str,
    persona: str,
    variants: list[dict[str, Any]],
    stopped: list[str],
    clicked: list[str],
    reason: str,
    history: list[dict[str, str]],
    question: str,
) -> list[dict[str, Any]]:
    ads = [(LETTERS[i], v) for i, v in enumerate(variants)]
    header = (
        "Tarea: conversar\n"
        f"Quién eres: {persona}\n"
        f"Hace un rato viste estos anuncios de {brand or 'una marca'} en tu feed:"
    )
    footer = (
        f"\nTe detuviste a mirar: {_letters(stopped, variants)}. Hiciste clic en: {_letters(clicked, variants)}."
        + (f" Lo que pensaste en el momento: «{reason}»." if reason else "")
        + "\nAhora alguien de la marca te hace preguntas sobre esos anuncios."
    )
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PERSONA},
        {"role": "user", "content": _content(header, ads, footer)},
        {"role": "assistant", "content": "Dale, pregúntame."},
    ]
    for turn in history[-MAX_TURNS:]:
        role = "assistant" if turn.get("role") == "persona" else "user"
        messages.append({"role": role, "content": str(turn.get("text") or "")})
    messages.append({"role": "user", "content": question})
    return messages


async def ask_persona(client: ModelClient, *, model: str, phase: str, **kwargs: Any) -> str:
    messages = persona_messages(**kwargs)
    n_images = sum(1 for v in kwargs["variants"] if v.get("image_url"))
    upcoming = estimate_call_usd(model, len(str(messages)), MAX_REPLY_TOKENS, n_images * IMAGE_TOKENS)
    res = await client.chat(
        model, messages, phase=phase, max_tokens=MAX_REPLY_TOKENS, upcoming_usd=upcoming, note="chat persona"
    )
    return res.text.strip()
