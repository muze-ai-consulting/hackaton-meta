"""Lotes del backtest: anuncios de un mismo anunciante lanzados la misma semana, y el sellado de sus etiquetas.

Reglas (CLAUDE.md):
- Solo anuncios con ad_delivery_start_time posterior al 2-sep-2026.
- Se compara dentro del anunciante y la semana de lanzamiento: el alcance bruto depende del presupuesto.
- Solo anuncios de una versión con eu_total_reach: con varias versiones el alcance mezcla variantes.
- El set sellado se separa por hash del lote; sus etiquetas van a un archivo aparte y su SHA-256 se commitea.

Uso: uv run python -m ensayo.batches
"""

import hashlib
import json
import logging
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from ensayo import DATA, RESULTS

log = logging.getLogger(__name__)

CUTOFF = date(2026, 9, 2)
MIN_BATCH = 3
MAX_BATCH = 8  # más variantes encarecen la simulación sin aportar mucho
SEALED_SHARE = 0.3
RAW = DATA / "raw" / "ad_library"


def start_date(ad: dict[str, Any]) -> date:
    return datetime.fromisoformat(ad["ad_delivery_start_time"][:10]).date()


def reach(ad: dict[str, Any]) -> int | None:
    try:
        return int(ad["eu_total_reach"]) if ad.get("eu_total_reach") is not None else None
    except (TypeError, ValueError):
        return None


def is_single_version(ad: dict[str, Any]) -> bool:
    return len(ad.get("ad_creative_bodies") or []) <= 1 and len(ad.get("ad_creative_link_titles") or []) <= 1


def eligible(ad: dict[str, Any]) -> bool:
    return bool(ad.get("ad_delivery_start_time")) and start_date(ad) > CUTOFF and reach(ad) is not None and is_single_version(ad)


def longevity_days(ad: dict[str, Any], today: date) -> int | None:
    """Días al aire, solo si el anuncio ya terminó (la fecha de término de un anuncio activo es la planeada)."""
    stop = ad.get("ad_delivery_stop_time")
    if not stop:
        return None
    stop_d = datetime.fromisoformat(stop[:10]).date()
    return (stop_d - start_date(ad)).days if stop_d < today else None


def strip_token(url: str | None) -> str | None:
    """ad_snapshot_url trae el access_token en la query: no se guarda."""
    if not url:
        return None
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query) if k != "access_token"]
    return urlunsplit(parts._replace(query=urlencode(query)))


def is_sealed(batch_id: str) -> bool:
    return int(hashlib.sha256(batch_id.encode()).hexdigest(), 16) % 100 < SEALED_SHARE * 100


def load_raw_ads(raw_dir: Path = RAW) -> list[dict[str, Any]]:
    """Todos los anuncios de las respuestas cacheadas de ads_archive, sin duplicados por id."""
    ads: dict[str, dict[str, Any]] = {}
    for path in sorted(raw_dir.glob("*.json")):
        for row in json.loads(path.read_text(encoding="utf-8")).get("data", []):
            if row.get("id") and row.get("ad_delivery_start_time"):
                ads[row["id"]] = row
    return list(ads.values())


def build_batches(ads: list[dict[str, Any]], today: date) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ad in ads:
        if not eligible(ad):
            continue
        iso = start_date(ad).isocalendar()
        groups[f"{ad['page_id']}-{iso.year}W{iso.week:02d}"].append(ad)

    batches: list[dict[str, Any]] = []
    for batch_id, members in sorted(groups.items()):
        # Sin duplicados de texto: dos anuncios idénticos no son variantes distintas.
        seen: set[str] = set()
        unique = []
        for ad in sorted(members, key=lambda a: a["id"]):
            body = " ".join(ad.get("ad_creative_bodies") or []) + "|" + " ".join(ad.get("ad_creative_link_titles") or [])
            if body not in seen:
                seen.add(body)
                unique.append(ad)
        if len(unique) < MIN_BATCH:
            continue
        unique = unique[:MAX_BATCH]
        total = sum(reach(a) or 0 for a in unique)
        variants = [
            {
                "ad_id": a["id"],
                "body": " ".join(a.get("ad_creative_bodies") or []),
                "title": " ".join(a.get("ad_creative_link_titles") or []),
                "platforms": a.get("publisher_platforms") or [],
                "snapshot_url": strip_token(a.get("ad_snapshot_url")),
            }
            for a in unique
        ]
        labels = {
            a["id"]: {
                "reach": reach(a),
                "reach_share": round((reach(a) or 0) / total, 4) if total else None,
                "longevity_days": longevity_days(a, today),
            }
            for a in unique
        }
        batches.append(
            {
                "batch_id": batch_id,
                "page_id": unique[0]["page_id"],
                "page_name": unique[0].get("page_name"),
                "week": batch_id.rsplit("-", 1)[1],
                "target": {k: unique[0].get(k) for k in ("target_ages", "target_gender", "target_locations")},
                "variants": variants,
                "labels": labels,
                "sealed": is_sealed(batch_id),
            }
        )
    return batches


def write_split(batches: list[dict[str, Any]], out_dir: Path = DATA / "batches", hash_path: Path = RESULTS / "sealed_labels.sha256") -> dict[str, int]:
    """dev.json lleva etiquetas; sealed_inputs.json no. Las etiquetas selladas van a data/sealed/ con su hash en results/."""
    out_dir.mkdir(parents=True, exist_ok=True)
    dev = [b for b in batches if not b["sealed"]]
    sealed = [b for b in batches if b["sealed"]]
    (out_dir / "dev.json").write_text(json.dumps(dev, ensure_ascii=False, indent=1), encoding="utf-8")
    (out_dir / "sealed_inputs.json").write_text(
        json.dumps([{k: v for k, v in b.items() if k != "labels"} for b in sealed], ensure_ascii=False, indent=1), encoding="utf-8"
    )
    sealed_labels = json.dumps({b["batch_id"]: b["labels"] for b in sealed}, sort_keys=True, ensure_ascii=False)
    sealed_dir = out_dir.parent / "sealed"
    sealed_dir.mkdir(parents=True, exist_ok=True)
    (sealed_dir / "labels.json").write_text(sealed_labels, encoding="utf-8")
    hash_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(sealed_labels.encode()).hexdigest()
    hash_path.write_text(f"{digest}  data/sealed/labels.json  ({len(sealed)} lotes)\n", encoding="utf-8")
    return {"dev": len(dev), "sealed": len(sealed), "dev_variants": sum(len(b["variants"]) for b in dev)}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ads = load_raw_ads()
    batches = build_batches(ads, today=date.today())
    counts = write_split(batches)
    log.info(f"{len(ads)} anuncios crudos → {len(batches)} lotes: {counts}")


if __name__ == "__main__":
    main()
