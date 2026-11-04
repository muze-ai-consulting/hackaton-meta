"""The script judges run to check our numbers has to catch a wrong number, not only confirm a right one."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("verify_results", ROOT / "scripts" / "verify_results.py")
assert spec and spec.loader
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def test_score_uses_the_test_threshold() -> None:
    rows = [("scam", 0.9), ("scam", 0.5), ("scam", 0.49), ("scam", 0.1), ("legit", 0.6), ("legit", 0.2)]
    assert verify.score(rows) == {"balanced_accuracy": 0.5, "recall_scam": 0.5, "false_alarm_legit": 0.5}


def test_bands_cover_every_case_once() -> None:
    rows = [("scam", 1.0), ("legit", 0.5), ("scam", 0.49), ("legit", 0.2), ("scam", 0.19), ("legit", 0.0)]
    assert verify.bands(rows) == [("Likely a scam", 2, 1), ("Be careful", 2, 1), ("No clear signs", 2, 1)]


def test_published_results_match() -> None:
    for number, round_spec in verify.ROUNDS.items():
        assert verify.check_round(number, round_spec) == []


def test_a_changed_prediction_is_caught(tmp_path: Path, monkeypatch) -> None:
    predictions = json.loads((ROOT / "results" / "scam_predictions2.json").read_text(encoding="utf-8"))
    first = next(iter(predictions))
    predictions[first]["p"] = 1.0 - predictions[first]["p"]
    (tmp_path / "results").mkdir()
    (tmp_path / "results" / "scam_predictions2.json").write_text(json.dumps(predictions), encoding="utf-8")
    (tmp_path / "results" / "scam_predictions2.sha256").write_bytes((ROOT / "results" / "scam_predictions2.sha256").read_bytes())
    (tmp_path / "results" / "scam_scored2.json").write_bytes((ROOT / "results" / "scam_scored2.json").read_bytes())
    (tmp_path / "data" / "scams").mkdir(parents=True)
    (tmp_path / "data" / "scams" / "labels2.json").write_bytes((ROOT / "data" / "scams" / "labels2.json").read_bytes())
    monkeypatch.setattr(verify, "ROOT", tmp_path)
    assert any("hash" in problem for problem in verify.check_round(2, verify.ROUNDS[2]))
