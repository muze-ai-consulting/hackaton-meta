"""Cuántas estafas y cuántos casos legítimos caen en cada banda del escudo (las que muestra el producto).

Lee las predicciones ya puntuadas de los dos intentos y escribe results/scam_bands.json, que alimenta la página
"How we measured it". No llama a ningún modelo.

    uv run python scripts/scam_bands.py
"""

import json
import logging

from ensayo import DATA, RESULTS
from ensayo.shield import BANDS, band

log = logging.getLogger(__name__)

ROUNDS = {1: ("labels.json", "scam_predictions.json", "scam_scored.json"), 2: ("labels2.json", "scam_predictions2.json", "scam_scored2.json")}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    out = {}
    for rnd, (labels_file, preds_file, scored_file) in ROUNDS.items():
        labels = json.loads((DATA / "scams" / labels_file).read_text(encoding="utf-8"))
        preds = json.loads((RESULTS / preds_file).read_text(encoding="utf-8"))
        counts = {name: {"scam": 0, "legit": 0} for _, name in BANDS}
        for pid, pred in preds.items():
            if labels.get(pid) in ("scam", "legit"):
                counts[band(pred["p"])][labels[pid]] += 1
        out[f"round{rnd}"] = {
            "scored": json.loads((RESULTS / scored_file).read_text(encoding="utf-8")),
            "sha256": (RESULTS / preds_file).with_suffix(".sha256").read_text(encoding="utf-8").strip(),
            "bands": counts,
        }
    (RESULTS / "scam_bands.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    log.info(json.dumps({k: v["bands"] for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
