"""Second Look en WhatsApp: la persona reenvía el mensaje, pantallazo o nota de voz al número y recibe la respuesta ahí.

Webhook de la WhatsApp Cloud API (Graph API). Dos respuestas por consulta:
1. el veredicto del escudo (ensayo.shield, el prompt validado), apenas está;
2. las pistas del agente investigador y la familia a la que se parece (ensayo.investigate y ensayo.campaigns).

Los mensajes son datos de usuarios: van por muse-spark-1.3 estándar (fase "demo") y no se guardan ni se registran;
en los logs solo queda un hash del número. Cada aviso de Meta se verifica con la firma X-Hub-Signature-256 (App
Secret). Variables en .env: WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_VERIFY_TOKEN, WHATSAPP_APP_SECRET.
"""

import asyncio
import base64
import hashlib
import hmac
import logging
import os
import time
from collections import OrderedDict, defaultdict
from typing import Any

import httpx
from dotenv import load_dotenv

from ensayo import ROOT, campaigns
from ensayo.costs import BudgetExceeded
from ensayo.investigate import investigate
from ensayo.llm import ModelClient
from ensayo.shield import check

log = logging.getLogger(__name__)
load_dotenv(ROOT / ".env")  # en el VPS las variables llegan por env_file; esto es para correrlo en local

GRAPH = "https://graph.facebook.com/v23.0"
MODEL = "muse-spark-1.3"
DAILY_LIMIT = 30
MAX_MEDIA_BYTES = 10 * 1024 * 1024
BAND_LINE = {"scam": "🔴 *Likely a scam*", "careful": "🟠 *Be careful*", "genuine": "🟢 *No clear signs of a scam*"}
SIGNAL = {"risky": "⚠️", "reassuring": "✅", "neutral": "•"}
WELCOME = (
    "👋 This is *Second Look*.\n\nForward me a message, screenshot or voice note that feels off and I'll tell you if "
    "it looks like a scam, why, and the one thing to do now. I also check the links in it."
)

_seen: OrderedDict[str, None] = OrderedDict()  # ids ya procesados: Meta reintenta los avisos
_usage: dict[tuple[str, str], int] = defaultdict(int)


def env(name: str) -> str:
    return os.environ.get(name, "")


def configured() -> bool:
    return all(env(k) for k in ("WHATSAPP_TOKEN", "WHATSAPP_PHONE_NUMBER_ID", "WHATSAPP_VERIFY_TOKEN", "WHATSAPP_APP_SECRET"))


def valid_signature(body: bytes, header: str | None) -> bool:
    secret = env("WHATSAPP_APP_SECRET")
    if not secret or not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


def who(number: str) -> str:
    return hashlib.sha256(number.encode()).hexdigest()[:10]


def first_time(message_id: str) -> bool:
    if message_id in _seen:
        return False
    _seen[message_id] = None
    while len(_seen) > 2000:
        _seen.popitem(last=False)
    return True


def messages_in(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Los mensajes entrantes de un aviso (los avisos de estado de entrega se ignoran)."""
    out = []
    for entry in payload.get("entry") or []:
        for change in entry.get("changes") or []:
            out += (change.get("value") or {}).get("messages") or []
    return out


# --- Graph API ---------------------------------------------------------------------------------------------------

def graph() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=30, headers={"Authorization": f"Bearer {env('WHATSAPP_TOKEN')}"})


async def send_text(http: httpx.AsyncClient, to: str, text: str, reply_to: str | None = None) -> None:
    payload: dict[str, Any] = {"messaging_product": "whatsapp", "to": to, "type": "text",
                               "text": {"body": text[:4000], "preview_url": False}}
    if reply_to:
        payload["context"] = {"message_id": reply_to}
    r = await http.post(f"{GRAPH}/{env('WHATSAPP_PHONE_NUMBER_ID')}/messages", json=payload)
    if r.status_code >= 400:
        log.error(f"WhatsApp send {r.status_code}: {r.text[:300]}")


async def mark_read(http: httpx.AsyncClient, message_id: str) -> None:
    """Marca como leído y muestra "escribiendo…" mientras se revisa."""
    await http.post(f"{GRAPH}/{env('WHATSAPP_PHONE_NUMBER_ID')}/messages", json={
        "messaging_product": "whatsapp", "status": "read", "message_id": message_id, "typing_indicator": {"type": "text"}})


async def download(http: httpx.AsyncClient, media_id: str) -> tuple[bytes, str]:
    meta = (await http.get(f"{GRAPH}/{media_id}")).raise_for_status().json()
    if int(meta.get("file_size") or 0) > MAX_MEDIA_BYTES:
        raise ValueError("That file is too large (10 MB max).")
    r = (await http.get(meta["url"])).raise_for_status()
    return r.content, meta.get("mime_type") or "application/octet-stream"


# --- Respuestas ----------------------------------------------------------------------------------------------------

def verdict_text(out: dict[str, Any]) -> str:
    lines = [f"{BAND_LINE[out['band']]} · {round(out['probability'] * 100)}%", "", f"*Why:* {out['reason']}",
             f"*Do now:* {out['action']}"]
    if out["band"] == "genuine":
        lines += ["", "_This doesn't mean it's safe. If it asks for money, codes or passwords, contact the company "
                      "through its official app or number._"]
    if out.get("transcript"):
        lines += ["", f"_I heard:_ \"{out['transcript'][:300]}\""]
    lines += ["", "_Second Look · Muse Spark 1.3 · tested on 945 real cases: 96% of \"Likely a scam\" answers were scams._"]
    return "\n".join(lines)


def step_line(step: dict[str, Any]) -> str:
    r, tool = step["result"], step["tool"]
    if tool == "inspect_link":
        if r.get("error"):
            return f"🔗 Followed {step['input'].get('url')}: {r['error']}"
        return "🔗 Followed the link without opening it: " + " → ".join(h["domain"] for h in r.get("hops", []))
    if tool == "domain_registration":
        if r.get("error"):
            return f"🌐 Couldn't read the registration of {r.get('domain')}"
        if r.get("registered") is False:
            return f"🌐 {r['domain']} has no public registration record"
        age = r.get("age_days")
        when = "" if age is None else f", {age} days ago" if age < 60 else f", {round(age / 365)} years ago"
        return f"🌐 {r['domain']} was registered on {r.get('registered_on')}{when}"
    return f"• {tool}"


def clues_text(family: dict[str, Any] | None, inv: dict[str, Any] | None) -> str:
    parts = []
    if inv and not inv.get("skipped") and (inv.get("steps") or inv.get("clues")):
        lines = ["🔎 *What I checked*"] + [step_line(s) for s in inv.get("steps", [])]
        lines += [f"{SIGNAL.get(c['signal'], '•')} *{c['label']}.* {c['detail']}" for c in inv.get("clues", [])]
        parts.append("\n".join(lines))
    if family:
        trend = f", *{family['trend']}* last month" if family.get("trend") in ("rising", "falling") else ""
        brands = family.get("top_brands") or []
        posing = f" Often posing as {', '.join(b['brand'] for b in brands[:3])}." if brands else ""
        spot = "\n".join(f"  – {s}" for s in family.get("spot", []))
        head = "Seen before" if family.get("fit") == "strong" else "Looks similar to"
        parts.append(f"👥 *{head}: {family['name']}*\n{family['what']}\n{family['reports']} people reported this "
                     f"kind of scam on Reddit since September{trend}.{posing}\n{spot}".rstrip())
    return "\n\n".join(parts)


async def handle(message: dict[str, Any], client: ModelClient | None = None, http: httpx.AsyncClient | None = None) -> None:
    """Responde un mensaje entrante. Nunca levanta: los errores se le cuentan a la persona."""
    sender, mid, kind = message.get("from", ""), message.get("id", ""), message.get("type")
    own_http = http is None
    http = http or graph()
    own_client = client is None
    client = client or ModelClient.from_env()
    client.effort = "low"
    spent_before = client.ledger.spent()
    try:
        text, images, audio = "", [], None
        if kind == "text":
            text = (message.get("text") or {}).get("body", "")
        elif kind == "image":
            raw, mime = await download(http, message["image"]["id"])
            images = [f"data:{mime};base64,{base64.b64encode(raw).decode()}"]
            text = message["image"].get("caption", "")
        elif kind in ("audio", "voice"):
            audio, _ = await download(http, message[kind]["id"])
        else:
            await send_text(http, sender, "I can check text, screenshots and voice notes. Forward one of those to me.", mid)
            return
        if not audio and not images and len(text.strip()) < 15:
            await send_text(http, sender, WELCOME)
            return
        day = (time.strftime("%Y-%m-%d"), who(sender))
        if _usage[day] >= DAILY_LIMIT:
            await send_text(http, sender, "You've reached today's limit for this demo. Come back tomorrow.", mid)
            return
        _usage[day] += 1
        await mark_read(http, mid)
        verdict = await check(client, model=MODEL, phase="demo", text=text, images=images, audio=audio)
        await send_text(http, sender, verdict_text(verdict), mid)
        content = "\n\n".join(p for p in (text, verdict.get("transcript", "")) if p.strip())
        data = campaigns.load()
        family, inv = await asyncio.gather(
            campaigns.match(client, data, model=MODEL, phase="demo", text=content, images=images) if data else _none(),
            investigate(client, model=MODEL, phase="demo", text=content, images=images),
            return_exceptions=True,
        )
        extra = clues_text(None if isinstance(family, BaseException) else family, None if isinstance(inv, BaseException) else inv)
        if extra:
            await send_text(http, sender, extra)
        log.info(f"whatsapp {who(sender)} {kind} → {verdict['band']} (US$ {client.ledger.spent() - spent_before:.4f})")
    except BudgetExceeded:
        await send_text(http, sender, "The demo has reached its spending cap. Try again tomorrow.", mid)
    except (ValueError, httpx.HTTPError) as exc:
        log.warning(f"whatsapp {who(sender)} {kind}: {exc}")
        await send_text(http, sender, f"Sorry, I couldn't read that. {exc if isinstance(exc, ValueError) else ''}".strip(), mid)
    except (RuntimeError, KeyError, TypeError) as exc:
        log.exception(f"whatsapp {who(sender)} falló: {exc!r}")
        await send_text(http, sender, "Sorry, something went wrong on my side. Please try again in a minute.", mid)
    finally:
        if own_client:
            await client.aclose()
        if own_http:
            await http.aclose()


async def _none() -> None:
    return None
