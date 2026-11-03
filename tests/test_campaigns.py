"""Pruebas de las familias de estafas y del agente investigador, siempre con el servidor falso (sin red)."""

import asyncio
import json

import httpx
from fastapi.testclient import TestClient

from ensayo import api, campaigns, llm
from ensayo.investigate import domain_registration, inspect_link, registrable

FAMILIES = {"families": [
    {"id": "parcel_fee", "name": "Parcel fee texts", "what": "A fake courier asks for a small fee.", "spot": ["a"], "do": "Ignore.",
     "reports": 40, "trend": "rising", "top_brands": [{"brand": "Evri", "reports": 9}]},
    {"id": "other", "name": "Other scams", "what": "Anything else.", "spot": [], "do": "Check.", "reports": 5},
]}


def client(tmp_path, monkeypatch, data: dict | None = FAMILIES) -> TestClient:
    monkeypatch.setattr(llm, "RESULTS", tmp_path)
    path = tmp_path / "scam_campaigns.json"
    if data:
        path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(campaigns, "CAMPAIGNS", path)
    return TestClient(api.app)


def test_scrub_removes_contact_details() -> None:
    out = campaigns.scrub("Call +44 7700 900123 or mail bob@x.com, see https://evri-fee.top/pay now")
    assert "7700" not in out and "bob@" not in out and "evri-fee" not in out and "now" in out


def test_registrable_domain() -> None:
    assert registrable("www.amazon.co.uk") == "amazon.co.uk"
    assert registrable("pay.evri-redelivery.com") == "evri-redelivery.com"


def test_inspect_link_refuses_private_addresses() -> None:
    async def go() -> dict:
        async with httpx.AsyncClient() as http:
            return await inspect_link(http, "http://127.0.0.1:80/admin")
    out = asyncio.run(go())
    assert "error" in out and not out["hops"]


def test_inspect_link_refuses_other_ports() -> None:
    async def go() -> dict:
        async with httpx.AsyncClient() as http:
            return await inspect_link(http, "http://example.com:8080/")
    assert "error" in asyncio.run(go())


def test_domain_registration_reads_rdap() -> None:
    rdap = {"events": [{"eventAction": "registration", "eventDate": "2026-10-30T10:00:00Z"}],
            "entities": [{"roles": ["registrar"], "vcardArray": ["vcard", [["fn", {}, "text", "Cheap Names Ltd"]]]}]}

    async def go() -> dict:
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json=rdap))
        async with httpx.AsyncClient(transport=transport) as http:
            return await domain_registration(http, "pay.evri-fee.co.uk")
    out = asyncio.run(go())
    assert out["domain"] == "evri-fee.co.uk" and out["registered_on"] == "2026-10-30" and out["registrar"] == "Cheap Names Ltd"


def test_investigate_matches_family_and_skips_without_links(tmp_path, monkeypatch) -> None:
    res = client(tmp_path, monkeypatch).post("/api/investigate", json={"text": "Mum, new number, send money today"})
    assert res.status_code == 200
    data = res.json()
    assert data["family"]["id"] == "parcel_fee" and data["family"]["reports"] == 40
    assert data["investigation"]["skipped"] is True


def test_investigate_runs_agent_with_links(tmp_path, monkeypatch) -> None:
    res = client(tmp_path, monkeypatch).post("/api/investigate", json={"text": "Pay £1.45 at https://evri-fee.top/pay"})
    assert res.status_code == 200
    assert res.json()["investigation"]["clues"][0]["signal"] == "neutral"


def test_investigate_without_campaign_data(tmp_path, monkeypatch) -> None:
    res = client(tmp_path, monkeypatch, data=None).post("/api/investigate", json={"text": "hello"})
    assert res.status_code == 200 and res.json()["family"] is None
    assert client(tmp_path, monkeypatch, data=None).get("/api/campaigns").status_code == 404


def test_investigate_real_mode_blocked(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("ENSAYO_REAL", raising=False)
    res = client(tmp_path, monkeypatch).post("/api/investigate", json={"text": "hi", "mode": "real"})
    assert res.status_code == 403
