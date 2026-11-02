"""Pruebas del feed simulado, la llamada única y el cliente, todo contra el servidor falso (sin red ni créditos)."""

import asyncio
import json
from collections import Counter

import httpx
import pytest

from ensayo import mock
from ensayo.costs import Ledger
from ensayo.fixtures import demo_batches
from ensayo.llm import ModelClient, extract_json, mock_ledger
from ensayo.population import build_population, spec_from_ad
from ensayo.simulate import LETTERS, feed_orders, simulate_batch, simulation_messages, single_call_ranking


def mock_client(tmp_path) -> ModelClient:
    ledger = mock_ledger()
    ledger.path = tmp_path / "costs.jsonl"
    return ModelClient(ledger, base="https://mock.local/v1", transport=mock.transport())


def test_feed_orders_balance_positions() -> None:
    for n in range(3, 9):
        orders = feed_orders(n, 4)
        assert len(orders) == 4 and all(sorted(o) == list(range(n)) for o in orders)
        firsts = Counter(o[0] for o in orders)
        assert len(firsts) == min(4, n)  # el feed lo abren variantes distintas
    assert len(feed_orders(3, 4)) == 4


def test_extract_json_tolerates_fences() -> None:
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json('Claro: {"ranking": ["A"]} listo') == {"ranking": ["A"]}
    with pytest.raises(ValueError):
        extract_json("sin json")


def test_prompt_hides_ids_and_labels() -> None:
    batch = demo_batches(1)[0]
    people = build_population(spec_from_ad(batch["target"]), n=3)
    text = json.dumps(simulation_messages(batch, list(range(len(batch["variants"]))), people), ensure_ascii=False)
    assert all(v["ad_id"] not in text for v in batch["variants"])
    assert "reach" not in text and "alcance" not in text
    assert "P3:" in text and "Anuncio A:" in text


def test_simulate_batch_with_mock(tmp_path) -> None:
    batch = demo_batches(1)[0]
    people = build_population(spec_from_ad(batch["target"]), n=60)
    client = mock_client(tmp_path)

    async def go():
        try:
            return await simulate_batch(client, batch, people, model="muse-spark-1.3-contributor", phase="pruebas")
        finally:
            await client.aclose()

    out = asyncio.run(go())
    ids = [v["ad_id"] for v in batch["variants"]]
    assert sorted(out["ranking"]) == sorted(ids)
    assert out["calls"] == 3 and out["failed_calls"] == 0
    assert all(out["stats"][ad]["seen"] == 60 for ad in ids)
    assert all(0 <= out["stats"][ad]["click_rate"] <= out["stats"][ad]["stop_rate"] <= 1 for ad in ids)
    entries = client.ledger.entries()
    assert len(entries) == 3 and all(e["usd"] > 0 for e in entries)


def test_single_call_returns_full_ranking(tmp_path) -> None:
    batch = demo_batches(2)[1]
    client = mock_client(tmp_path)

    async def go():
        try:
            return await single_call_ranking(client, batch, model="muse-spark-1.3", phase="pruebas")
        finally:
            await client.aclose()

    out = asyncio.run(go())
    assert sorted(out["ranking"]) == sorted(v["ad_id"] for v in batch["variants"])
    assert not out["incomplete"]


def test_client_retries_rate_limit_and_respects_budget(tmp_path, monkeypatch) -> None:
    real_sleep = asyncio.sleep
    monkeypatch.setattr("ensayo.llm.asyncio.sleep", lambda *_: real_sleep(0))
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, json={"error": {"message": "lento"}})
        return httpx.Response(200, json=mock.respond(json.loads(request.content)))

    ledger = Ledger(path=tmp_path / "c.jsonl", total_budget=1.0, caps={"pruebas": 0.5})
    client = ModelClient(ledger, base="https://mock.local/v1", transport=httpx.MockTransport(handler))
    messages = [{"role": "user", "content": "Anuncio A: x\nAnuncio B: y\nranking"}]

    async def go():
        try:
            ok = await client.chat("muse-spark-1.3", messages, phase="pruebas")
            with pytest.raises(Exception, match="Fase pruebas"):
                await client.chat("muse-spark-1.3", messages, phase="pruebas", upcoming_usd=0.6)
            return ok
        finally:
            await client.aclose()

    res = asyncio.run(go())
    assert calls["n"] == 2 and extract_json(res.text)["ranking"]
    assert len(ledger.entries()) == 1


def test_letters_cover_max_batch() -> None:
    from ensayo.batches import MAX_BATCH

    assert len(LETTERS) >= MAX_BATCH
