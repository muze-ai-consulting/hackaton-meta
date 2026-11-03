"""Agente investigador: Spark 1.3 con herramientas revisa los enlaces y dominios de lo que la persona reenvió.

Va aparte del veredicto (ensayo/shield.py), que sale solo del prompt validado: esto agrega pistas comprobables, no
cambia el puntaje. La Model API acepta function calling pero no búsqueda web, así que las herramientas son nuestras:

- inspect_link: sigue las redirecciones de un enlace sin descargar la página. Solo http(s) a puertos 80/443 y nunca a
  direcciones privadas, de loopback o reservadas (se revisa cada salto), con tiempo límite.
- domain_registration: fecha de registro y registrador del dominio por RDAP (registro público, sin clave).
"""

import asyncio
import ipaddress
import json
import logging
import re
import socket
import time
from typing import Any
from urllib.parse import urljoin, urlsplit

import httpx

from ensayo.llm import ModelClient, estimate_call_usd, extract_json

log = logging.getLogger(__name__)

MAX_TURNS = 4
MAX_HOPS = 5
TIMEOUT = 6.0
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly", "rb.gy", "ow.ly", "shorturl.at", "t.ly",
              "rebrand.ly", "tiny.cc", "s.id", "lnkd.in"}
# Sufijos de dos niveles más comunes en los casos (sin depender de la lista pública de sufijos).
LINKISH = re.compile(r"https?://|www\.|\b[a-z0-9-]+\.(?:com|net|org|co|uk|in|io|info|xyz|top|shop|site|online|app|me|ly|cc)\b", re.I)
TWO_LEVEL = {"co.uk", "org.uk", "gov.uk", "ac.uk", "com.au", "net.au", "co.in", "net.in", "org.in", "com.br", "co.nz",
             "co.za", "com.mx", "com.sg", "com.my", "co.jp", "com.tr", "com.ar", "com.co", "com.pk", "com.ng", "co.ke"}

INVESTIGATOR = (
    "You are the investigator inside a scam shield. Someone forwarded a message, screenshot or call. Find every link, "
    "website or domain in it (also inside screenshots) and check them with your tools before concluding. Watch for "
    "domains that imitate a real brand, link shorteners, very new domains and redirects to unrelated sites. Also point "
    "out the warning signs in the wording (pressure, payment requests, odd sender) and anything reassuring. Never "
    "guess facts you did not check. When you are done, answer only with your report. "
)
FINISH = (
    "Report only what you found, at most 5 clues. In quote, copy the exact words from the forwarded text that show "
    "the clue (max 12 words, character for character), or null if it comes from a screenshot or a tool. Format: "
    '{"clues": [{"label": "max 8 words", "detail": "max 25 words", "signal": "risky|reassuring|neutral", '
    '"quote": "exact words or null"}], "summary": "max 20 words"}. Write label, detail and summary in the language '
    "the person wrote in."
)

TOOLS = [
    {"type": "function", "function": {
        "name": "inspect_link",
        "description": "Follow a link's redirects without opening the page. Returns each hop's domain, the final domain and HTTP status.",
        "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {
        "name": "domain_registration",
        "description": "Public registration record (RDAP) of a domain: when it was registered and by which registrar.",
        "parameters": {"type": "object", "properties": {"domain": {"type": "string"}}, "required": ["domain"]}}},
]


def registrable(host: str) -> str:
    parts = host.lower().strip(".").split(".")
    n = 3 if ".".join(parts[-2:]) in TWO_LEVEL else 2
    return ".".join(parts[-n:])


async def _public_host(host: str) -> bool:
    try:
        infos = await asyncio.get_running_loop().getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except (socket.gaierror, UnicodeError):
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global or ip.is_multicast:
            return False
    return bool(infos)


async def inspect_link(http: httpx.AsyncClient, url: str) -> dict[str, Any]:
    url = url.strip()
    if not re.match(r"^https?://", url, re.I):
        url = "http://" + url
    hops: list[dict[str, Any]] = []
    for _ in range(MAX_HOPS):
        parts = urlsplit(url)
        host = parts.hostname or ""
        if parts.scheme not in ("http", "https") or (parts.port or 0) not in (0, 80, 443):
            return {"error": "Only normal web links are checked.", "hops": hops}
        if not host or not await _public_host(host):
            return {"error": f"{host or url} does not resolve to a public website.", "hops": hops}
        try:
            async with http.stream("GET", url, follow_redirects=False) as r:
                status, location = r.status_code, r.headers.get("location")
        except httpx.HTTPError as exc:
            hops.append({"domain": host, "error": type(exc).__name__})
            return {"hops": hops, "final_domain": host, "reachable": False}
        hops.append({"domain": host, "https": parts.scheme == "https", "status": status,
                     "shortener": registrable(host) in SHORTENERS})
        if status in (301, 302, 303, 307, 308) and location:
            url = urljoin(url, location)
            continue
        break
    final = hops[-1]["domain"] if hops else ""
    return {"hops": hops, "final_domain": final, "final_registrable": registrable(final), "reachable": True,
            "redirected_to_other_site": len({registrable(h["domain"]) for h in hops}) > 1}


async def domain_registration(http: httpx.AsyncClient, domain: str) -> dict[str, Any]:
    domain = registrable(urlsplit(domain).hostname or domain) if "/" in domain else registrable(domain)
    try:
        r = await http.get(f"https://rdap.org/domain/{domain}", follow_redirects=True)
    except httpx.HTTPError as exc:
        return {"domain": domain, "error": f"registry lookup failed ({type(exc).__name__})"}
    if r.status_code == 404:
        return {"domain": domain, "registered": False, "note": "No registration record found."}
    if r.status_code != 200:
        return {"domain": domain, "error": f"registry answered {r.status_code}"}
    body = r.json()
    events = {e.get("eventAction"): e.get("eventDate", "")[:10] for e in body.get("events", [])}
    registrar = next((
        next((v[3] for v in (ent.get("vcardArray") or [None, []])[1] if v and v[0] == "fn"), None)
        for ent in body.get("entities", []) if "registrar" in (ent.get("roles") or [])), None)
    created = events.get("registration")
    age = None
    if created:
        age = int((time.time() - time.mktime(time.strptime(created, "%Y-%m-%d"))) // 86400)
    return {"domain": domain, "registered": True, "registered_on": created, "age_days": age, "registrar": registrar}


async def investigate(
    client: ModelClient,
    *,
    model: str,
    phase: str,
    text: str = "",
    images: list[str] | None = None,
    http: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Pistas comprobadas sobre los enlaces y dominios, con el rastro de cada herramienta usada."""
    content: list[dict[str, Any]] = [{"type": "text", "text": f"Forwarded content:\n{text[:3000] or '(only screenshots)'}"}]
    content += [{"type": "image_url", "image_url": {"url": u}} for u in (images or [])]
    # Sin enlaces el agente igual marca las señales del texto (una sola llamada, sin herramientas); muy corto, no.
    if not images and not LINKISH.search(text) and len(text.strip()) < 40:
        return {"clues": [], "summary": "", "steps": [], "skipped": True}
    messages: list[dict[str, Any]] = [{"role": "system", "content": INVESTIGATOR + FINISH}, {"role": "user", "content": content}]
    steps: list[dict[str, Any]] = []
    final = ""
    chars = len(INVESTIGATOR + FINISH) + len(text[:3000])
    own = http is None
    http = http or httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0 (SecondLook link check)"})
    try:
        for _ in range(MAX_TURNS):
            msg = await client.chat_message(model, messages, phase=phase, tools=TOOLS, max_tokens=300,
                                            upcoming_usd=estimate_call_usd(model, chars + 1500 * len(steps), 400, 800 * len(images or [])),
                                            note="investiga")
            calls = msg.get("tool_calls") or []
            if not calls:
                final = msg.get("content") or ""
                break
            messages.append({"role": "assistant", "content": msg.get("content") or "", "tool_calls": calls})
            results = await asyncio.gather(*(_run_tool(http, c) for c in calls))
            for call, (name, args, result) in zip(calls, results):
                steps.append({"tool": name, "input": args, "result": result})
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result)})
        if not final:
            messages.append({"role": "user", "content": FINISH})
            res = await client.chat(model, messages, phase=phase, max_tokens=400,
                                    upcoming_usd=estimate_call_usd(model, chars + 1500 * len(steps), 500, 800 * len(images or [])), note="investiga cierre")
            final = res.text
    finally:
        if own:
            await http.aclose()
    try:
        out = extract_json(final)
    except ValueError:
        out = {"clues": [], "summary": ""}
    clues = [{"label": str(c.get("label") or ""), "detail": str(c.get("detail") or ""),
              "signal": c.get("signal") if c.get("signal") in ("risky", "reassuring", "neutral") else "neutral",
              # Solo citas que aparecen tal cual en el texto: así el front puede marcarlas sin inventar.
              "quote": quote if (quote := str(c.get("quote") or "").strip()) and quote.lower() in text.lower() else None}
             for c in (out.get("clues") or [])[:5] if isinstance(c, dict)]
    return {"clues": clues, "summary": str(out.get("summary") or ""), "steps": steps}


async def _run_tool(http: httpx.AsyncClient, call: dict[str, Any]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    name = call["function"]["name"]
    try:
        args = json.loads(call["function"].get("arguments") or "{}")
    except json.JSONDecodeError:
        args = {}
    if name == "inspect_link" and args.get("url"):
        return name, args, await inspect_link(http, str(args["url"]))
    if name == "domain_registration" and args.get("domain"):
        return name, args, await domain_registration(http, str(args["domain"]))
    return name, args, {"error": "unknown tool or missing argument"}
