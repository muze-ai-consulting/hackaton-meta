"""Pruebas con datos de ejemplo: población, lotes, sellado y métricas."""

import hashlib
import json
from datetime import date

from ensayo import batches, metrics, population


def ad(i: int, page: str = "p1", start: str = "2026-09-15", reach: int | None = 1000, bodies: list[str] | None = None, **extra) -> dict:
    return {
        "id": f"{page}-{i}",
        "page_id": page,
        "page_name": f"Página {page}",
        "ad_delivery_start_time": f"{start}T10:00:00+0000",
        "ad_creative_bodies": bodies if bodies is not None else [f"texto {i}"],
        "ad_creative_link_titles": [f"título {i}"],
        "eu_total_reach": None if reach is None else str(reach),
        "ad_snapshot_url": f"https://www.facebook.com/ads/archive/render_ad/?id={page}-{i}&access_token=SECRETO",
        **extra,
    }


# Población


def test_population_is_deterministic_and_respects_target() -> None:
    spec = population.TargetSpec(age_min=25, age_max=44, genders=("female",), countries=("DE", "FR"))
    a = population.build_population(spec, n=300, seed=3)
    b = population.build_population(spec, n=300, seed=3)
    assert a == b
    assert all(25 <= p.age <= 44 for p in a)
    assert {p.gender for p in a} == {"female"}
    assert {p.country for p in a} == {"DE", "FR"}
    assert {p.age_bucket for p in a} == {"25-34", "35-44"}
    assert population.build_population(spec, n=300, seed=4) != a


def test_population_65_plus_and_describe() -> None:
    people = population.build_population(population.TargetSpec(age_min=60, age_max=65), n=200)
    assert any(p.age >= 65 for p in people) and all(p.age >= 60 for p in people)
    assert "años" in people[0].describe()


def test_spec_from_ad_reads_targeting() -> None:
    spec = population.spec_from_ad(
        {
            "target_ages": ["18", "65+"],
            "target_gender": "Women",
            "target_locations": [
                {"name": "DE", "type": "countries", "excluded": False},
                {"name": "AT", "type": "countries", "excluded": True},
                {"name": "Berlin", "type": "cities", "excluded": False},
            ],
        }
    )
    assert (spec.age_min, spec.age_max, spec.genders, spec.countries) == (18, 65, ("female",), ("DE",))
    assert population.spec_from_ad({}).countries == ("GB",)


def test_calibrate_age_weights_from_breakdown() -> None:
    dev = [{"age_country_gender_reach_breakdown": [{"country": "DE", "age_gender_breakdowns": [
        {"age_range": "18-24", "male": 30, "female": 10, "unknown": 0},
        {"age_range": "25-34", "male": 40, "female": 20, "unknown": 0},
    ]}]}]
    w = population.calibrate_age_weights(dev)
    assert round(w["18-24"], 2) == 0.4 and round(w["25-34"], 2) == 0.6 and w["65+"] == 0


# Lotes


def test_build_batches_applies_rules() -> None:
    ads = [ad(i, reach=1000 * (i + 1)) for i in range(4)]
    ads += [ad(10, start="2026-08-30")]  # antes del corte
    ads += [ad(11, reach=None)]  # sin alcance UE
    ads += [ad(12, bodies=["v1", "v2"])]  # varias versiones
    ads += [ad(13, bodies=["texto 0"]) | {"ad_creative_link_titles": ["título 0"]}]  # duplicado
    ads += [ad(i, page="p2") for i in range(2)]  # lote demasiado chico
    out = batches.build_batches(ads, today=date(2026, 10, 27))
    assert len(out) == 1
    b = out[0]
    assert b["batch_id"] == "p1-2026W38"
    assert [v["ad_id"] for v in b["variants"]] == ["p1-0", "p1-1", "p1-2", "p1-3"]
    assert b["labels"]["p1-3"]["reach_share"] == 0.4
    assert all("SECRETO" not in (v["snapshot_url"] or "") for v in b["variants"])


def test_longevity_only_for_finished_ads() -> None:
    finished = ad(1) | {"ad_delivery_stop_time": "2026-09-25T00:00:00+0000"}
    running = ad(2) | {"ad_delivery_stop_time": "2026-12-01T00:00:00+0000"}
    today = date(2026, 10, 27)
    assert batches.longevity_days(finished, today) == 10
    assert batches.longevity_days(running, today) is None


def test_sealed_split_hides_labels_and_hashes_them(tmp_path) -> None:
    ads = [ad(i, page=f"p{p}", reach=100 * (i + 1)) for p in range(30) for i in range(3)]
    out = batches.build_batches(ads, today=date(2026, 10, 27))
    counts = batches.write_split(out, out_dir=tmp_path / "batches", hash_path=tmp_path / "hash.txt")
    assert counts["sealed"] > 0 and counts["dev"] > 0
    sealed_inputs = json.loads((tmp_path / "batches" / "sealed_inputs.json").read_text())
    assert all("labels" not in b for b in sealed_inputs)
    labels = (tmp_path / "sealed" / "labels.json").read_text()
    assert (tmp_path / "hash.txt").read_text().startswith(hashlib.sha256(labels.encode()).hexdigest())
    # El sellado depende solo del id del lote: estable entre corridas.
    assert [b["sealed"] for b in out] == [b["sealed"] for b in batches.build_batches(ads, today=date(2026, 11, 1))]


# Métricas


def test_metrics_perfect_and_reversed() -> None:
    truth = {"a": 300.0, "b": 200.0, "c": 100.0}
    assert metrics.score_batch(["a", "b", "c"], truth) == {"pairwise": 1.0, "top1": 1.0, "spearman": 1.0}
    assert metrics.score_batch(["c", "b", "a"], truth) == {"pairwise": 0.0, "top1": 0.0, "spearman": -1.0}


def test_metrics_ties_are_skipped() -> None:
    assert metrics.pairwise_accuracy(["a", "b"], {"a": 1.0, "b": 1.0}) is None
    assert metrics.top1_hit(["a", "b"], {"a": 1.0, "b": 1.0}) is None


def test_random_baseline_is_near_chance() -> None:
    bs = [{"labels": {f"{j}-{i}": {"reach": 100 * i} for i in range(1, 5)}} for j in range(200)]
    s = metrics.random_baseline(bs)
    assert abs(s["pairwise"]["mean"] - 0.5) < 0.05
    assert abs(s["top1"]["mean"] - 0.25) < 0.05
    lo, hi = s["pairwise"]["ci95"]
    assert lo <= s["pairwise"]["mean"] <= hi
