"""Pruebas del medidor de gasto."""

import pytest

from ensayo import costs


def test_chat_cost_uses_cached_price() -> None:
    usage = {"prompt_tokens": 1_000_000, "completion_tokens": 1_000_000, "prompt_tokens_details": {"cached_tokens": 500_000}}
    assert costs.chat_cost("muse-spark-1.3", usage) == pytest.approx(0.5 * 1.25 + 0.5 * 0.15 + 4.25)


def test_ledger_stops_at_phase_and_total_caps(tmp_path) -> None:
    ledger = costs.Ledger(path=tmp_path / "c.jsonl", total_budget=10, caps={"calibracion": 5, "demo": 8})
    ledger.record("calibracion", "muse-spark-1.3-contributor", 4.9)
    ledger.check("calibracion", 0.05)
    with pytest.raises(costs.BudgetExceeded):
        ledger.check("calibracion", 0.2)
    ledger.record("demo", "muse-spark-1.3", 5.0)
    with pytest.raises(costs.BudgetExceeded):
        ledger.check("demo", 0.5)  # la fase aguanta, el total no
    with pytest.raises(ValueError):
        ledger.check("otra")
    assert ledger.report()["total"] == 9.9


def test_contributor_with_grouping_fits_budget() -> None:
    per_batch = costs.estimate_batch_usd("muse-spark-1.3-contributor", variants=5)
    assert per_batch < 0.5
    assert costs.estimate_batch_usd("muse-spark-1.3", variants=5, per_call=1) > 30
