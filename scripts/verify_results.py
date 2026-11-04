"""Recompute every number we claim about the scam test, from the files in this repo.

No API key, no network and no dependencies beyond Python 3.12:

    python3 scripts/verify_results.py

It checks, for both attempts:
- that the predictions file still matches the SHA-256 written when it was created;
- that in git history, the commit with the predictions came before the commit with the score;
- balanced accuracy, scams caught, false alarms and the answer bands, from predictions + labels;
- the preregistered rule, and that the published score file says the same.

The keyword baseline needs the raw Reddit posts, which are not versioned, so its score is read from the score
file instead of being recomputed. Exits with 1 if anything doesn't match.
"""

import hashlib
import json
import logging
import random
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
ROUNDS = {
    1: {"labels": "data/scams/labels.json", "predictions": "results/scam_predictions.json",
        "scored": "results/scam_scored.json", "hash_commit": "4de2c5f", "score_commit": "d3da904", "validated": False},
    2: {"labels": "data/scams/labels2.json", "predictions": "results/scam_predictions2.json",
        "scored": "results/scam_scored2.json", "hash_commit": "be7ec95", "score_commit": "66d935b", "validated": True},
}
BANDS = (("Likely a scam", 0.5, 1.01), ("Be careful", 0.2, 0.5), ("No clear signs", 0.0, 0.2))

log = logging.getLogger("verify")


def load(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def score(rows: list[tuple[str, float]]) -> dict[str, float]:
    """Balanced accuracy, scams caught and false alarms at the threshold the test used (p >= 0.5)."""
    scams = [p for label, p in rows if label == "scam"]
    genuine = [p for label, p in rows if label == "legit"]
    recall = sum(p >= 0.5 for p in scams) / len(scams)
    false_alarm = sum(p >= 0.5 for p in genuine) / len(genuine)
    return {"balanced_accuracy": (recall + 1 - false_alarm) / 2, "recall_scam": recall, "false_alarm_legit": false_alarm}


def bootstrap_ci(rows: list[tuple[str, float]], n: int = 2000) -> tuple[float, float]:
    """95% interval for balanced accuracy, resampling within each class."""
    rng = random.Random(7)
    scams = [r for r in rows if r[0] == "scam"]
    genuine = [r for r in rows if r[0] == "legit"]
    runs = sorted(
        score([rng.choice(scams) for _ in scams] + [rng.choice(genuine) for _ in genuine])["balanced_accuracy"]
        for _ in range(n)
    )
    return runs[int(0.025 * n)], runs[int(0.975 * n)]


def bands(rows: list[tuple[str, float]]) -> list[tuple[str, int, int]]:
    """For each answer the product gives: how many cases got it, and how many of those were scams."""
    return [(name, sum(lo <= p < hi for _, p in rows), sum(lo <= p < hi and label == "scam" for label, p in rows))
            for name, lo, hi in BANDS]


def commit_order(first: str, second: str) -> str | None:
    """Commit times if `first` is an ancestor of `second`, or None if history is unavailable or says otherwise."""
    try:
        subprocess.run(["git", "merge-base", "--is-ancestor", first, second], cwd=ROOT, check=True, capture_output=True)
        times = subprocess.run(["git", "show", "-s", "--format=%cI", first, second], cwd=ROOT, check=True,
                               capture_output=True, text=True).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return f"{first} ({times[0]}) before {second} ({times[1]})"


def check_round(number: int, spec: dict[str, Any]) -> list[str]:
    """Print one attempt and return what failed."""
    failed: list[str] = []
    log.info(f"\nAttempt {number}")

    blob = (ROOT / spec["predictions"]).read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    recorded = (ROOT / spec["predictions"]).with_suffix(".sha256").read_text(encoding="utf-8").strip()
    log.info(f"  predictions SHA-256  {digest}")
    if digest != recorded:
        failed.append("the predictions don't match their recorded hash")

    order = commit_order(spec["hash_commit"], spec["score_commit"])
    log.info(f"  commit order         {order or 'not available'}")
    if order is None:
        failed.append("couldn't confirm that the predictions were committed before the score")

    labels = load(spec["labels"])
    predictions = json.loads(blob)
    rows = [(labels[i], float(pred["p"])) for i, pred in predictions.items() if labels.get(i) in ("scam", "legit")]
    scams = sum(label == "scam" for label, _ in rows)
    result = score(rows)
    low, high = bootstrap_ci(rows)
    log.info(f"  cases                {len(rows)} ({scams} scams, {len(rows) - scams} genuine)")
    log.info(f"  balanced accuracy    {result['balanced_accuracy']:.4f} (95% CI {low:.3f} to {high:.3f})")
    log.info(f"  scams caught         {result['recall_scam']:.1%}")
    log.info(f"  false alarms         {result['false_alarm_legit']:.1%}")
    for name, total, were_scams in bands(rows):
        log.info(f"  \"{name}\"{' ' * (19 - len(name))}{were_scams / total:.0%} of {total} were scams")

    published = load(spec["scored"])
    keywords = published["keywords"]["balanced_accuracy"]
    log.info(f"  keyword filter       {keywords:.4f} (read from the score file)")
    for key in result:
        if abs(result[key] - published["shield"][key]) > 0.0001:
            failed.append(f"{key} differs from {spec['scored']}")
    if (len(rows), scams) != (published["n"], published["scam"]):
        failed.append(f"the case count differs from {spec['scored']}")

    passed = (
        len(rows) - scams >= 30
        and result["balanced_accuracy"] >= 0.80
        and result["balanced_accuracy"] - keywords >= 0.10
        and published["gap_vs_keywords_ci95"][0] > 0
        and result["false_alarm_legit"] <= 0.30
    )
    log.info(f"  preregistered rule   {'PASSED' if passed else 'DID NOT PASS'}")
    if passed is not spec["validated"] or passed is not published["rule"]["validated"]:
        failed.append("the rule's outcome differs from what we publish")
    return failed


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    failed = [f"attempt {n}: {problem}" for n, spec in ROUNDS.items() for problem in check_round(n, spec)]
    if failed:
        log.error("\nFAILED\n" + "\n".join(f"- {problem}" for problem in failed))
        return 1
    log.info("\nAll checks match.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
