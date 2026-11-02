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
    "You are a real person scrolling your Facebook or Instagram feed, not an assistant or a marketing expert. "
    "You answer in the first person, in the language of the question, in 80 words at most, with your own way of "
    "talking and your own priorities. If an ad didn't interest you, you say so plainly and explain why; you don't "
    "try to please whoever is asking, and you don't change your mind just because they insist. Never mention that "
    "you are simulated."
)


def _letters(ids: list[str], variants: list[dict[str, Any]]) -> str:
    pos = {v["ad_id"]: LETTERS[i] for i, v in enumerate(variants)}
    picked = [pos[i] for i in ids if i in pos]
    return ", ".join(picked) or "none"


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
        "Task: conversation\n"
        f"Who you are: {persona}\n"
        f"A while ago you saw these ads from {brand or 'a brand'} in your feed:"
    )
    footer = (
        f"\nYou stopped to look at: {_letters(stopped, variants)}. You clicked: {_letters(clicked, variants)}."
        + (f' What you thought at the time: "{reason}".' if reason else "")
        + "\nNow someone from the brand is asking you questions about those ads."
    )
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PERSONA},
        {"role": "user", "content": _content(header, ads, footer)},
        {"role": "assistant", "content": "Sure, go ahead."},
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
