"""Pruebas del agente de respuesta (acciones simuladas), con el modelo falso."""

import asyncio

from fastapi.testclient import TestClient

from ensayo import act, api, llm
from ensayo.llm import ModelClient

SCAM = {"band": "scam", "probability": 0.97, "reason": "Fake fee.", "action": "Don't pay."}
FAMILY = {"name": "Delivery Fee Texts", "reports": 39, "spot": ["Odd link"]}


def run(verdict: dict, tmp_path, monkeypatch) -> dict:
    monkeypatch.setattr(llm, "RESULTS", tmp_path)

    async def go() -> dict:
        client = ModelClient.from_env(mock=True)
        try:
            return await act.respond(client, model="muse-spark-1.3", phase="demo", verdict=verdict, text="Pay now", family=FAMILY)
        finally:
            await client.aclose()
    return asyncio.run(go())


def test_scam_prepares_simulated_actions(tmp_path, monkeypatch) -> None:
    out = run(SCAM, tmp_path, monkeypatch)
    assert out["simulated"] is True
    assert [a["tool"] for a in out["actions"]] == ["alert_contact", "draft_report", "share_pattern"]
    share = out["actions"][-1]
    assert share["report_number"] == 40 and "Odd link" in share["heads_up"]


def test_genuine_does_not_call_the_model(tmp_path, monkeypatch) -> None:
    out = run({"band": "genuine", "probability": 0.05}, tmp_path, monkeypatch)
    assert out["actions"] == [] and out["skipped"]
    assert not (tmp_path / "costs_mock.jsonl").exists()


def test_alert_never_carries_a_live_link() -> None:
    a = act.to_action("alert_contact", {"message": "It asks to pay at https://royalmail-redelivery-uk.com/pay now", "why": "x"}, None)
    assert "royalmail-redelivery-uk[.]com/pay" in a["body"] and "https://" not in a["body"]


def test_shared_pattern_is_scrubbed() -> None:
    a = act.to_action("share_pattern", {"pattern": "Call +44 7700 900123 or see https://x.top", "why": "x"}, None)
    assert "7700" not in a["body"] and "x.top" not in a["body"]


def test_only_an_explicit_urgent_runs_by_itself() -> None:
    assert act.to_action("alert_contact", {"message": "m", "why": "w", "urgent": True}, None)["auto"] is True
    assert act.to_action("alert_contact", {"message": "m", "why": "w", "urgent": "yes"}, None)["auto"] is False
    assert act.to_action("alert_contact", {"message": "m", "why": "w"}, None)["auto"] is False


def test_unknown_or_empty_tool_is_dropped() -> None:
    assert act.to_action("wire_money", {"amount": 1}, None) is None
    assert act.to_action("alert_contact", {"why": "x"}, None) is None


def test_endpoint_mock(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(llm, "RESULTS", tmp_path)
    r = TestClient(api.app).post("/api/act", json={"text": "Pay now", "verdict": SCAM, "mode": "mock"})
    assert r.status_code == 200 and r.json()["simulated"] is True and len(r.json()["actions"]) == 3
