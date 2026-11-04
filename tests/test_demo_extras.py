"""Pruebas de las variantes con Muse Image y del chat con una persona, siempre con el servidor falso."""

import asyncio
import base64

import pytest
from fastapi.testclient import TestClient

from ensayo import api, llm, mock
from ensayo.costs import IMAGE_PRICE, BudgetExceeded, Ledger
from ensayo.images import IMAGE_MODEL, generate_variants
from tests.test_api import PIXEL


def test_placeholder_png_is_valid_and_depends_on_prompt() -> None:
    a, b = mock.placeholder_png("uno", side=8), mock.placeholder_png("dos", side=8)
    assert a.startswith(b"\x89PNG\r\n\x1a\n") and a.endswith(b"IEND\xaeB`\x82")
    assert a != b and a == mock.placeholder_png("uno", side=8)


def test_generate_variants_mock_records_image_cost(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(llm, "RESULTS", tmp_path)
    client = llm.ModelClient.from_env(mock=True)

    async def run() -> list[dict]:
        try:
            return await generate_variants(client, brand="Café", brief="café tostado a mano", n=3, photo_url=PIXEL)
        finally:
            await client.aclose()

    out = asyncio.run(run())
    assert len(out) == 3 and len({v["angle"] for v in out}) == 3
    for v in out:
        assert v["title"] and v["body"] and "café tostado" in v["image_prompt"]
        assert base64.b64decode(v["image_url"].removeprefix("data:image/png;base64,")).startswith(b"\x89PNG")
    entries = client.ledger.entries()
    images = [e for e in entries if e["model"] == IMAGE_MODEL]
    assert len(images) == 3 and all(e["usd"] == IMAGE_PRICE[IMAGE_MODEL] and e["phase"] == "demo" for e in images)
    assert (tmp_path / "costs_mock.jsonl").exists()


def test_image_respects_budget(tmp_path) -> None:
    ledger = Ledger(path=tmp_path / "costs.jsonl", caps={"demo": 0.005})
    client = llm.ModelClient(ledger, base="https://mock.local/v1", transport=mock.transport())

    async def run() -> None:
        try:
            await client.image(IMAGE_MODEL, "algo", phase="demo")
        finally:
            await client.aclose()

    with pytest.raises(BudgetExceeded):
        asyncio.run(run())
    assert ledger.entries() == []


def test_variants_endpoint(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(llm, "RESULTS", tmp_path)
    monkeypatch.delenv("ENSAYO_REAL", raising=False)
    c = TestClient(api.app)
    res = c.post("/api/variants", json={"brand": "Café", "brief": "café tostado", "n": 2})
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "mock" and len(data["variants"]) == 2
    assert data["usd"] >= 2 * IMAGE_PRICE[IMAGE_MODEL]
    assert c.post("/api/variants", json={"brief": "   "}).status_code == 422
    assert c.post("/api/variants", json={"brief": "x", "n": 5}).status_code == 422
    assert c.post("/api/variants", json={"brief": "x", "mode": "real"}).status_code == 403


def test_generated_variants_feed_the_simulation(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(llm, "RESULTS", tmp_path)
    c = TestClient(api.app)
    variants = c.post("/api/variants", json={"brief": "zapatillas de trail", "n": 3}).json()["variants"]
    body = {"variants": [{k: v[k] for k in ("title", "body", "image_url")} for v in variants], "personas": 40}
    res = c.post("/api/simulate", json=body)
    assert res.status_code == 200 and sorted(res.json()["population"]["ranking"]) == ["v1", "v2", "v3"]


def test_chat_with_persona(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(llm, "RESULTS", tmp_path)
    monkeypatch.delenv("ENSAYO_REAL", raising=False)
    c = TestClient(api.app)
    body = {
        "brand": "Café",
        "persona": "Mujer de 31 años en GB.",
        "variants": [{"title": "Uno", "body": "a"}, {"title": "Dos", "body": "b", "image_url": PIXEL}],
        "stopped": ["v2"],
        "clicked": [],
        "reason": "me gustó la foto",
        "history": [{"role": "user", "text": "hola"}, {"role": "persona", "text": "hola"}],
        "question": "¿Por qué no hiciste clic?",
    }
    res = c.post("/api/chat", json=body)
    assert res.status_code == 200 and "¿Por qué no hiciste clic?" in res.json()["answer"]
    assert res.json()["usd"] > 0
    assert c.post("/api/chat", json={**body, "question": ""}).status_code == 422
    assert c.post("/api/chat", json={**body, "mode": "real"}).status_code == 403


def test_persona_messages_use_demo_letters() -> None:
    from ensayo.chat import persona_messages

    variants = [{"ad_id": "v1", "title": "Uno"}, {"ad_id": "v2", "title": "Dos"}]
    msgs = persona_messages(
        brand="X", persona="P", variants=variants, stopped=["v2"], clicked=[], reason="",
        history=[{"role": "persona", "text": "antes"}], question="¿y?",
    )
    assert "Ad B: headline: Dos" in msgs[1]["content"] and "stopped to look at: B" in msgs[1]["content"]
    assert msgs[-2] == {"role": "assistant", "content": "antes"} and msgs[-1]["content"] == "¿y?"


def test_spoofed_forwarded_for_does_not_reset_the_quota(monkeypatch) -> None:
    from fastapi import HTTPException
    from starlette.requests import Request

    from ensayo import api

    monkeypatch.setenv("ENSAYO_REAL", "1")
    monkeypatch.setitem(api.REAL_DAILY_LIMITS, "check", 3)
    api._real_usage.clear()

    def call(forwarded: str) -> None:
        scope = {"type": "http", "headers": [(b"x-forwarded-for", forwarded.encode())], "client": ("10.0.0.1", 1)}
        api.guard_real(Request(scope), "check")

    for fake in ("1.1.1.1, 9.9.9.9", "2.2.2.2, 9.9.9.9", "3.3.3.3, 9.9.9.9"):
        call(fake)
    try:
        call("4.4.4.4, 9.9.9.9")
    except HTTPException as exc:
        assert exc.status_code == 429
    else:
        raise AssertionError("a made-up address got past the quota")
    api._real_usage.clear()


def test_missing_key_is_a_503_not_a_crash(monkeypatch) -> None:
    from fastapi import HTTPException

    from ensayo import api
    from ensayo.llm import ModelClient

    def no_key(**_: object) -> None:
        raise SystemExit("no key")

    monkeypatch.setattr(ModelClient, "from_env", no_key)
    try:
        api.model_client(False)
    except HTTPException as exc:
        assert exc.status_code == 503
    else:
        raise AssertionError("expected a 503")
