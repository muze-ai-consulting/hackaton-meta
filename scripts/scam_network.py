"""Alerta temprana: repite día a día los casos públicos de Reddit como si hubieran llegado a Second Look.

Una campaña es una marca imitada dentro de una familia. Se marca cuando junta MIN_REPORTS reportes en WINDOW_DAYS días;
los reportes posteriores son los que un aviso habría alcanzado a anticipar. Es una repetición descriptiva, no una
prueba preregistrada: el umbral se fijó mirando estos mismos datos y nadie recibió un aviso. No usa el modelo: sale de
data/scams/{described,assigned}.json. Escribe results/scam_network.json.

    uv run python scripts/scam_network.py
"""

import json
import logging
import statistics
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ensayo import DATA, RESULTS
from ensayo.campaigns import CAMPAIGNS, scrub
from scripts.scam_campaigns import scam_posts

log = logging.getLogger(__name__)

OUT = RESULTS / "scam_network.json"
MIN_REPORTS = 3
WINDOW_DAYS = 14
SHOWN = 6


def flag_index(days: list[date]) -> int | None:
    """Posición del reporte que completa MIN_REPORTS dentro de WINDOW_DAYS días, si existe."""
    for i in range(MIN_REPORTS - 1, len(days)):
        if (days[i] - days[i - MIN_REPORTS + 1]).days <= WINDOW_DAYS:
            return i
    return None


def replay(rows: list[dict[str, Any]], families: dict[str, dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        if r["brand"] and r["family"] != "other":
            groups[(r["family"], r["brand"].lower())].append(r)
    found, leads = [], []
    for (family, _), reports in groups.items():
        reports.sort(key=lambda r: r["date"])
        days = [date.fromisoformat(r["date"]) for r in reports]
        at = flag_index(days)
        if at is None:
            continue
        later = [(d - days[at]).days for d in days[at + 1:]]
        leads += later
        fam = families[family]
        found.append({
            "id": f"{family}:{reports[0]['brand'].lower()}",
            "name": f"Fake {reports[0]['brand']} messages",
            "family": fam["name"],
            "what": fam["what"],
            "spot": fam["spot"],
            "do": fam["do"],
            "flagged_on": reports[at]["date"],
            "flag_index": at,
            "warned": len(later),
            "reports": [{"date": r["date"], "hook": r["hook"], "channel": r["channel"], "url": r["url"]} for r in reports],
        })
    found.sort(key=lambda c: (-c["warned"], -len(c["reports"])))
    branded = sum(len(v) for v in groups.values())
    return {
        "source": "public Reddit reports, replayed by date",
        "rule": {"min_reports": MIN_REPORTS, "window_days": WINDOW_DAYS},
        "reports": len(rows),
        "branded_reports": branded,
        "flagged": len(found),
        "warned": sum(c["warned"] for c in found),
        "median_days_ahead": statistics.median(leads) if leads else 0,
        "campaigns": [c for c in found if c["warned"] > 0][:SHOWN],
    }


def main() -> None:
    described = json.loads((DATA / "scams" / "described.json").read_text(encoding="utf-8"))
    assigned = json.loads((DATA / "scams" / "assigned.json").read_text(encoding="utf-8"))
    families = {f["id"]: f for f in json.loads(CAMPAIGNS.read_text(encoding="utf-8"))["families"]}
    rows = [{"date": p["created"][:10], "family": assigned[p["id"]], "brand": (described[p["id"]].get("brand") or "").strip(),
             "hook": scrub(described[p["id"]].get("hook") or ""), "channel": described[p["id"]].get("channel") or "unknown",
             "url": p.get("url")}
            for p in scam_posts() if p["id"] in assigned and p["id"] in described]
    out = replay(rows, families)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info(f"{out['flagged']} campañas · {out['warned']} reportes posteriores · mediana {out['median_days_ahead']} días")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
