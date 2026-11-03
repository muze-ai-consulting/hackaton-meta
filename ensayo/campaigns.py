"""Familias de estafas: qué está circulando, armado con los casos públicos de Reddit que la comunidad llamó estafa.

Tres pasos (scripts/scam_campaigns.py): cada caso se describe (canal, marca imitada, pago, si usa IA), con esas
descripciones se arma una lista de ~20 familias, y cada caso se asigna a una. El producto usa la misma asignación
(`match_messages`) para decirle a la persona a qué familia se parece lo que recibió; ese paso va aparte del
veredicto, que sigue saliendo solo del prompt validado (ensayo/shield.py).
"""

import json
import re
from pathlib import Path
from typing import Any

from ensayo import RESULTS
from ensayo.llm import ModelClient, estimate_call_usd, extract_json

CAMPAIGNS = RESULTS / "scam_campaigns.json"

CHANNELS = ("sms", "whatsapp", "instagram", "facebook", "messenger", "marketplace", "email", "phone_call", "website",
            "dating_app", "telegram", "other_app", "in_person", "unknown")
META_CHANNELS = {"whatsapp", "instagram", "facebook", "messenger", "marketplace"}
PAYMENTS = ("gift_card", "crypto", "bank_transfer", "card", "payment_app", "upfront_fee", "personal_data", "account_access",
            "none", "unknown")
AI_USE = ("none", "deepfake_video", "voice_clone", "ai_image", "ai_chatbot", "ai_other")

# Teléfonos, correos y enlaces fuera de lo que se publica: lo que se muestra describe la estafa, no a personas.
_PII = re.compile(r"\+?\d[\d\s().-]{5,}\d|[\w.+-]+@[\w-]+\.[\w.]+|https?://\S+|www\.\S+")


def scrub(text: str) -> str:
    return _PII.sub("…", text or "").strip()


def describe_messages(post: dict[str, Any]) -> list[dict[str, Any]]:
    text = (
        "Below is a post where someone describes something an online community later judged to be a scam. "
        "Describe the scam itself, not the person.\n\n"
        f"Title: {post['title']}\n\n{(post['body'] or '(no text)')[:2500]}\n\n"
        f"channel: where it reached them, one of {', '.join(CHANNELS)}.\n"
        "brand: the company, platform or public figure being impersonated or used as bait, or null.\n"
        f"payment: what the scammer wanted, one of {', '.join(PAYMENTS)}.\n"
        f"ai: one of {', '.join(AI_USE)}; only if the post says or clearly shows AI was used, else none.\n"
        "kind: a generic 3-6 word name for this type of scam (e.g. 'parcel redelivery fee text', "
        "'task-based remote job').\n"
        "hook: max 15 words on how it looked to the person, with no names, numbers or links.\n"
        'Format: {"channel": "...", "brand": null, "payment": "...", "ai": "none", "kind": "...", "hook": "..."}'
    )
    return [{"role": "user", "content": text}]


def taxonomy_messages(kinds: list[tuple[str, int]], n_families: int = 20) -> list[dict[str, Any]]:
    lines = "\n".join(f"{k} ({c})" for k, c in kinds)
    text = (
        f"These are short names for {sum(c for _, c in kinds)} scams people reported, with counts. Group them into "
        f"about {n_families} families that an ordinary person would recognise, plus one 'other' family. Each family "
        "must be a clear pattern someone can learn to spot.\n\n"
        f"{lines}\n\n"
        "For each family give: id (snake_case), name (max 5 words), what (one sentence, max 25 words, how it works), "
        "spot (three short signs, max 10 words each), and do (the one thing to do, max 12 words).\n"
        'Format: {"families": [{"id": "...", "name": "...", "what": "...", "spot": ["...", "...", "..."], "do": "..."}]}'
    )
    return [{"role": "user", "content": text}]


def family_menu(families: list[dict[str, Any]]) -> str:
    return "\n".join(f"- {f['id']}: {f['name']}. {f['what']}" for f in families)


def match_messages(families: list[dict[str, Any]], kind: str, hook: str = "", text: str = "") -> list[dict[str, Any]]:
    """Asigna un caso a una familia. Con `kind`/`hook` para los casos de Reddit y con `text` para lo que llega al producto."""
    case = f"Kind: {kind}\nHow it looked: {hook}" if kind else f"Message or situation:\n{text[:3000]}"
    content = (
        f"Scam families:\n{family_menu(families)}\n\n{case}\n\n"
        "Which family does this belong to? Use 'other' if none fits well, and say how close the match is.\n"
        'Format: {"family": "id", "fit": "strong|partial|none"}'
    )
    return [{"role": "user", "content": content}]


def load() -> dict[str, Any] | None:
    return json.loads(CAMPAIGNS.read_text(encoding="utf-8")) if CAMPAIGNS.exists() else None


async def match(client: ModelClient, data: dict[str, Any], *, model: str, phase: str, text: str,
                images: list[str] | None = None) -> dict[str, Any] | None:
    """La familia más parecida a lo que la persona reenvió, con sus números. None si no se parece a ninguna."""
    families = data["families"]
    messages = match_messages(families, "", text=text or "(see the screenshots)")
    chars = len(messages[0]["content"])
    if images:
        messages[0]["content"] = [{"type": "text", "text": messages[0]["content"]}] + [
            {"type": "image_url", "image_url": {"url": u}} for u in images]
    res = await client.chat(model, messages, phase=phase, max_tokens=40,
                            upcoming_usd=estimate_call_usd(model, chars, 60, 800 * len(images or [])),
                            note="familia")
    try:
        out = extract_json(res.text)
    except ValueError:
        return None
    fam = next((f for f in families if f["id"] == out.get("family")), None)
    if not fam or fam["id"] == "other" or out.get("fit") not in ("strong", "partial"):
        return None
    return {**{k: fam[k] for k in ("id", "name", "what", "spot", "do", "reports", "trend", "top_brands") if k in fam},
            "fit": out["fit"]}


def save(data: dict[str, Any], path: Path = CAMPAIGNS) -> None:
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
