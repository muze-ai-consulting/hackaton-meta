"""Agente de respuesta: después del veredicto, Spark 1.3 decide qué acciones preparar para la persona.

Las herramientas son reales para el modelo (function calling), pero ejecutarlas está simulado: nada se envía, se bloquea
ni se publica. Cada acción espera la aprobación de la persona y el producto la muestra como simulada. El borrador de
denuncia sí sirve tal cual: la persona lo copia y lo envía por su cuenta.

Va aparte del veredicto (ensayo/shield.py): usa su resultado, no lo cambia. Si no hay señales de estafa no se llama
al modelo. Lo que la persona reenvió va por el modelo estándar y no se guarda.
"""

import json
import re
from typing import Any

from ensayo.campaigns import scrub
from ensayo.llm import ModelClient, estimate_call_usd

MAX_TURNS = 2
CONTACT = "Ana"
# Solo el dominio entero: "royalmail-redelivery-uk.com" pasa a "royalmail-redelivery-uk[.]com", para que no sea un enlace.
_DOMAIN = re.compile(r"(?:https?://)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/\S*)?", re.I)

RESPONDER = (
    "You are the response agent inside a scam shield. The verdict below is final: do not judge it again. Prepare the "
    "actions that would protect this person, by calling your tools. Nothing runs until the person approves it.\n"
    f"- alert_contact: their trusted contact is {CONTACT}. Use it only if money, codes or an account are at risk, or the "
    "person is about to act or already acted.\n"
    "- draft_report: if they already paid or shared card, bank or login details, write to their bank's fraud team and ask "
    "to block the card or account. Otherwise write to the company being imitated, or to the platform where it arrived. "
    "Use [brackets] for anything you don't know. Never invent phone numbers, emails, references or amounts.\n"
    "- block_sender: only if the message shows who sent it.\n"
    "- share_pattern: describe how this scam works so others can be warned, without names, numbers or links.\n"
    "Call each tool at most once. If the verdict is 'careful', prepare only what helps them verify before acting. In each "
    "tool's why, say in plain words why this helps this person. Write everything in the language the person wrote in."
)

TOOLS = [
    {"type": "function", "function": {
        "name": "alert_contact",
        "description": f"Prepare a message to {CONTACT}, the person's trusted contact, about what arrived and what to do.",
        "parameters": {"type": "object", "required": ["message", "why"], "properties": {
            "message": {"type": "string", "description": "Max 40 words, plain and calm."},
            "why": {"type": "string", "description": "Max 15 words."}}}}},
    {"type": "function", "function": {
        "name": "draft_report",
        "description": "Write a report the person can send to a bank, company or platform.",
        "parameters": {"type": "object", "required": ["recipient", "subject", "body", "why"], "properties": {
            "recipient": {"type": "string", "description": "Who it goes to, e.g. 'Your bank's fraud team' or 'Royal Mail'."},
            "subject": {"type": "string"},
            "body": {"type": "string", "description": "Max 90 words."},
            "why": {"type": "string", "description": "Max 15 words."}}}}},
    {"type": "function", "function": {
        "name": "block_sender",
        "description": "Block the sender on the channel where the message arrived.",
        "parameters": {"type": "object", "required": ["sender", "channel", "why"], "properties": {
            "sender": {"type": "string", "description": "As it appears in the message."},
            "channel": {"type": "string"},
            "why": {"type": "string", "description": "Max 15 words."}}}}},
    {"type": "function", "function": {
        "name": "share_pattern",
        "description": "Add an anonymous description of this scam to the shared network, so others can be warned.",
        "parameters": {"type": "object", "required": ["pattern", "why"], "properties": {
            "pattern": {"type": "string", "description": "Max 30 words, no names, numbers or links."},
            "why": {"type": "string", "description": "Max 15 words."}}}}},
]
ORDER = ["alert_contact", "draft_report", "block_sender", "share_pattern"]


def defang(text: str) -> str:
    return _DOMAIN.sub(lambda m: m.group(0).replace("https://", "").replace("http://", "").replace(".", "[.]"), text)


def heads_up(pattern: str, family: dict[str, Any] | None) -> str:
    """El aviso que recibirían otras personas si la red existiera."""
    spot = (family.get("spot") or [""])[0] if family else ""
    return f"Heads up: {pattern}" + (f" How to spot it: {spot}." if spot else "")


def to_action(name: str, args: dict[str, Any], family: dict[str, Any] | None) -> dict[str, Any] | None:
    """Una llamada del modelo, lista para mostrar. Devuelve None si le falta lo esencial."""
    why = str(args.get("why") or "")
    if name == "alert_contact" and args.get("message"):
        return {"tool": name, "title": f"Alert {CONTACT}", "why": why, "to": f"{CONTACT}, your trusted contact",
                "body": defang(str(args["message"]))}
    if name == "draft_report" and args.get("body"):
        recipient = str(args.get("recipient") or "The company being imitated")
        return {"tool": name, "title": f"Report to {recipient[0].lower() + recipient[1:] if recipient.startswith('Your ') else recipient}", "why": why, "to": recipient,
                "subject": str(args.get("subject") or "Report of a scam"), "body": defang(str(args["body"]))}
    if name == "block_sender" and args.get("sender"):
        channel = str(args.get("channel") or "this app")
        return {"tool": name, "title": f"Block {args['sender']}", "why": why, "to": channel,
                "body": f"Block {args['sender']} on {channel}."}
    if name == "share_pattern" and args.get("pattern"):
        pattern = scrub(str(args["pattern"]))
        return {"tool": name, "title": "Warn others", "why": why, "to": "Second Look network", "body": pattern,
                "heads_up": heads_up(pattern, family), "report_number": family["reports"] + 1 if family else None,
                "family": family["name"] if family else None}
    return None


async def respond(
    client: ModelClient,
    *,
    model: str,
    phase: str,
    verdict: dict[str, Any],
    text: str = "",
    images: list[str] | None = None,
    family: dict[str, Any] | None = None,
    clues: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Las acciones que el agente preparó. Ninguna se ejecuta: todas quedan marcadas como simuladas."""
    if verdict.get("band") == "genuine":
        return {"actions": [], "skipped": True, "simulated": True}
    facts = [f"Verdict: {verdict.get('band')} ({round(float(verdict.get('probability') or 0) * 100)}%). {verdict.get('reason', '')}",
             f"Advice already given: {verdict.get('action', '')}"]
    if family:
        facts.append(f"Scam family: {family.get('name')}")
    facts += [f"Clue: {c.get('label')}. {c.get('detail')}" for c in (clues or [])[:5]]
    content: list[dict[str, Any]] = [{"type": "text", "text": "\n".join(facts) + f"\n\nForwarded content:\n{text[:3000] or '(only screenshots)'}"}]
    content += [{"type": "image_url", "image_url": {"url": u}} for u in (images or [])]
    messages: list[dict[str, Any]] = [{"role": "system", "content": RESPONDER}, {"role": "user", "content": content}]
    chars = len(RESPONDER) + len(text[:3000]) + 800
    found: dict[str, dict[str, Any]] = {}
    for _ in range(MAX_TURNS):
        msg = await client.chat_message(model, messages, phase=phase, tools=TOOLS, max_tokens=700,
                                        upcoming_usd=estimate_call_usd(model, chars, 700, 800 * len(images or [])), note="responde")
        calls = msg.get("tool_calls") or []
        if not calls:
            break
        messages.append({"role": "assistant", "content": msg.get("content") or "", "tool_calls": calls})
        for call in calls:
            name = call["function"]["name"]
            try:
                args = json.loads(call["function"].get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            action = to_action(name, args, family) if name not in found else None
            if action:
                found[name] = action
            messages.append({"role": "tool", "tool_call_id": call["id"],
                             "content": json.dumps({"status": "prepared", "waits_for_approval": True})})
    return {"actions": [found[n] for n in ORDER if n in found], "simulated": True}

