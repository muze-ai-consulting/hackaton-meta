"""Pruebas del bot de WhatsApp, con el modelo falso y una Graph API de mentira (sin red)."""

import asyncio
import hashlib
import hmac
import json

import httpx
from fastapi.testclient import TestClient

from ensayo import api, llm, whatsapp
from ensayo.llm import ModelClient

SECRET = "test-secret"


def sign(body: bytes) -> str:
    return "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()


def env(monkeypatch) -> None:
    for k, v in {"WHATSAPP_TOKEN": "t", "WHATSAPP_PHONE_NUMBER_ID": "123", "WHATSAPP_VERIFY_TOKEN": "v", "WHATSAPP_APP_SECRET": SECRET}.items():
        monkeypatch.setenv(k, v)


def fake_graph(sent: list[dict]) -> httpx.AsyncClient:
    def handler(r: httpx.Request) -> httpx.Response:
        if r.method == "POST":
            sent.append(json.loads(r.content))
            return httpx.Response(200, json={"messages": [{"id": "out"}]})
        return httpx.Response(404)
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def run(message: dict, tmp_path, monkeypatch) -> list[dict]:
    monkeypatch.setattr(llm, "RESULTS", tmp_path)
    sent: list[dict] = []

    async def go() -> None:
        async with fake_graph(sent) as http:
            await whatsapp.handle(message, client=ModelClient.from_env(mock=True), http=http)
    asyncio.run(go())
    return [s for s in sent if s.get("type") == "text"]


def test_verify_handshake(monkeypatch) -> None:
    env(monkeypatch)
    c = TestClient(api.app)
    ok = c.get("/api/whatsapp", params={"hub.mode": "subscribe", "hub.verify_token": "v", "hub.challenge": "42"})
    assert ok.status_code == 200 and ok.text == "42"
    assert c.get("/api/whatsapp", params={"hub.mode": "subscribe", "hub.verify_token": "x", "hub.challenge": "42"}).status_code == 403


def test_webhook_rejects_unsigned(monkeypatch) -> None:
    env(monkeypatch)
    body = json.dumps({"entry": []}).encode()
    c = TestClient(api.app)
    assert c.post("/api/whatsapp", content=body, headers={"x-hub-signature-256": "sha256=bad"}).status_code == 401
    monkeypatch.setenv("ENSAYO_REAL", "1")
    assert c.post("/api/whatsapp", content=body, headers={"x-hub-signature-256": sign(body)}).status_code == 200


def test_text_gets_verdict_then_clues(tmp_path, monkeypatch) -> None:
    env(monkeypatch)
    msg = {"from": "447700900123", "id": "wamid.1", "type": "text",
           "text": {"body": "URGENT your bank account is locked, verify now at https://secure-bank-verify.top"}}
    sent = run(msg, tmp_path, monkeypatch)
    assert len(sent) == 2
    assert sent[0]["to"] == "447700900123" and sent[0]["context"]["message_id"] == "wamid.1"
    assert "Why:" in sent[0]["text"]["body"] and "Do now:" in sent[0]["text"]["body"]
    assert "What I checked" in sent[1]["text"]["body"]


def test_scam_offers_actions_and_button_answers(tmp_path, monkeypatch) -> None:
    env(monkeypatch)
    monkeypatch.setattr(llm, "RESULTS", tmp_path)
    number = "447700900124"
    sent: list[dict] = []

    async def go() -> None:
        async with fake_graph(sent) as http:
            client = ModelClient.from_env(mock=True)
            await whatsapp.handle({"from": number, "id": "wamid.a", "type": "text", "text": {
                "body": "URGENT your bank account is locked, verify now at https://secure-bank-verify.top"}}, client=client, http=http)
            await whatsapp.handle({"from": number, "id": "wamid.b", "type": "interactive", "interactive": {
                "type": "button_reply", "button_reply": {"id": "act:0", "title": "Alert Ana"}}}, client=client, http=http)
    asyncio.run(go())
    buttons = [s for s in sent if s.get("type") == "interactive"]
    assert len(buttons) == 1 and "simulated" in buttons[0]["interactive"]["body"]["text"]
    assert len(buttons[0]["interactive"]["action"]["buttons"]) == 3
    assert "Simulated" in sent[-1]["text"]["body"] and "Nothing was sent" in sent[-1]["text"]["body"]


def test_expired_button(tmp_path, monkeypatch) -> None:
    env(monkeypatch)
    sent = run({"from": "9", "id": "wamid.c", "type": "interactive", "interactive": {"button_reply": {"id": "act:0"}}}, tmp_path, monkeypatch)
    assert "expired" in sent[0]["text"]["body"]


def test_short_hello_gets_welcome(tmp_path, monkeypatch) -> None:
    env(monkeypatch)
    sent = run({"from": "1", "id": "wamid.2", "type": "text", "text": {"body": "hi"}}, tmp_path, monkeypatch)
    assert len(sent) == 1 and "Second Look" in sent[0]["text"]["body"]


def test_unsupported_type(tmp_path, monkeypatch) -> None:
    env(monkeypatch)
    sent = run({"from": "1", "id": "wamid.3", "type": "sticker", "sticker": {"id": "s"}}, tmp_path, monkeypatch)
    assert len(sent) == 1 and "text, screenshots and voice notes" in sent[0]["text"]["body"]


def test_duplicates_ignored() -> None:
    assert whatsapp.first_time("wamid.dup") and not whatsapp.first_time("wamid.dup")


def test_clues_text_formats_steps() -> None:
    inv = {"steps": [{"tool": "domain_registration", "input": {"domain": "x.top"},
                      "result": {"domain": "x.top", "registered": True, "registered_on": "2026-10-30", "age_days": 4}}],
           "clues": [{"label": "New domain", "detail": "Registered 4 days ago.", "signal": "risky"}]}
    fam = {"name": "Delivery Fee Texts", "what": "Fake fee.", "reports": 39, "trend": "rising", "spot": ["Odd link"],
           "top_brands": [{"brand": "FedEx", "reports": 3}], "fit": "strong"}
    out = whatsapp.clues_text(fam, inv)
    assert "x.top was registered on 2026-10-30, 4 days ago" in out and "⚠️ *New domain.*" in out
    assert "39 people" in out and "*rising*" in out and "FedEx" in out
