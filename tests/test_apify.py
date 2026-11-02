"""Pruebas del adaptador de Apify con la forma de salida documentada del actor, sin red."""

import json
from datetime import date

import httpx

from ensayo import apify, batches
from ensayo.population import spec_from_ad


def item(ad_id: str = "554396010944539", body: str = "Be 137% more productive.", start: int = 1789084800, **extra) -> dict:
    """Un anuncio como lo entrega el actor (ejemplo del README, con el proxy en croata)."""
    return {
        "FB AD Link": f"https://www.facebook.com/ads/library/?id={ad_id}",
        "ad_archive_id": ad_id,
        "page_id": "103598131567301",
        "page_name": "Motion",
        "is_active": False,
        "start_date": start,  # 2026-09-11
        "end_date": start + 10 * 86400,
        "publisher_platform": ["FACEBOOK", "INSTAGRAM"],
        "snapshot": {
            "body": {"text": body},
            "title": "AI Project Management",
            "cards": [],
            "extra_texts": [],
            "images": [{"original_image_url": "https://x/orig.jpg", "resized_image_url": "https://x/600.jpg"}],
            "videos": [],
        },
        "data_reach": {
            "aaa_info": {
                "targets_eu": True,
                "location_audience": [
                    {"name": "Nizozemska", "num_obfuscated": 0, "type": "countries", "excluded": False},
                    {"name": "Njemačka", "num_obfuscated": 0, "type": "countries", "excluded": False},
                ],
                "gender_audience": "Svi",
                "age_audience": {"min": 18, "max": 65},
                "eu_total_reach": 16,
                "age_country_gender_reach_breakdown": [
                    {"country": "NL", "age_gender_breakdowns": [{"age_range": "35-44", "male": 1, "female": 1, "unknown": None}]},
                    {"country": "DE", "age_gender_breakdowns": [{"age_range": "18-24", "male": 1, "female": 3, "unknown": None}]},
                ],
            }
        },
        **extra,
    }


def test_to_ads_archive_maps_fields() -> None:
    ad = apify.to_ads_archive(item())
    assert ad["id"] == "554396010944539" and ad["page_id"] == "103598131567301"
    assert ad["ad_delivery_start_time"].startswith("2026-09-11")
    assert ad["ad_delivery_stop_time"].startswith("2026-09-21")
    assert ad["ad_creative_bodies"] == ["Be 137% more productive."]
    assert ad["ad_creative_link_titles"] == ["AI Project Management"]
    assert ad["publisher_platforms"] == ["facebook", "instagram"]
    assert ad["eu_total_reach"] == 16
    assert ad["target_ages"] == ["18", "65+"] and ad["target_gender"] == "All"
    assert [loc["name"] for loc in ad["target_locations"]] == ["DE", "NL"]
    assert ad["target_locations_raw"] == ["Nizozemska", "Njemačka"]
    assert ad["image_url"] == "https://x/600.jpg"
    spec = spec_from_ad(ad)
    assert spec.countries == ("DE", "NL") and spec.age_min == 18


def test_to_ads_archive_edge_cases() -> None:
    active = apify.to_ads_archive(item(is_active=True))
    assert active["ad_delivery_stop_time"] is None  # end_date de un activo es la planeada
    women = item()
    women["data_reach"]["aaa_info"]["gender_audience"] = "Frauen"
    assert apify.to_ads_archive(women)["target_gender"] == "Women"
    dynamic = item()
    dynamic["snapshot"]["cards"] = [{"body": "otra versión", "title": "otro título"}]
    assert len(apify.to_ads_archive(dynamic)["ad_creative_bodies"]) == 2  # batches lo descarta
    no_reach = item()
    no_reach["data_reach"] = None
    ad = apify.to_ads_archive(no_reach)
    assert ad["eu_total_reach"] is None and ad["target_ages"] == [] and ad["target_locations"] == []
    assert apify.to_ads_archive({"ad_archive_id": "1"}) is None


def test_converted_ads_make_a_batch() -> None:
    week = 1789084800  # viernes 11-sep-2026: los tres en la misma semana ISO
    ads = [apify.to_ads_archive(item(ad_id=str(i), body=f"Texto {i}", start=week + i * 3600)) for i in range(3)]
    ads.append(apify.to_ads_archive(item(ad_id="old", body="Anterior al corte", start=1788000000)))  # 29-ago
    out = batches.build_batches(ads, today=date(2026, 11, 1))
    assert len(out) == 1 and len(out[0]["variants"]) == 3
    assert out[0]["variants"][0]["image_url"] == "https://x/600.jpg"
    assert out[0]["target"]["target_locations"][0]["name"] == "DE"


def test_run_actor_polls_and_reads_dataset(monkeypatch) -> None:
    monkeypatch.setattr(apify, "POLL_SECONDS", 0)
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(f"{request.method} {request.url.path}")
        assert request.headers["Authorization"] == "Bearer secreto" and "token" not in str(request.url)
        if request.method == "POST":
            assert json.loads(request.content)["includeAdReach"] is True
            return httpx.Response(201, json={"data": {"id": "r1", "status": "RUNNING"}})
        if request.url.path.endswith("/actor-runs/r1"):
            return httpx.Response(200, json={"data": {"id": "r1", "status": "SUCCEEDED", "defaultDatasetId": "d1", "usageTotalUsd": 0.01}})
        return httpx.Response(200, json=[item()])

    client = httpx.Client(headers={"Authorization": "Bearer secreto"}, transport=httpx.MockTransport(handler))
    items = apify.run_actor(client, apify.page_ads_input("103598131567301", "2026-09-03", 10))
    assert len(items) == 1
    assert calls == [
        f"POST /v2/acts/{apify.ACTOR}/runs",
        "GET /v2/actor-runs/r1",
        "GET /v2/datasets/d1/items",
    ]


def test_real_run_shape() -> None:
    """Forma de las corridas reales (1-nov): transparencia en ad_library_main y números como texto."""
    raw = item()
    eu = raw.pop("data_reach")["aaa_info"]
    eu = {
        **eu,
        "eu_total_reach": "567391",
        "gender_audience": "Women",
        "age_audience": {"min": "18", "max": "65"},
        "location_audience": [{"name": "Austria", "num_obfuscated": "0", "type": "countries", "excluded": "False"}],
        "age_country_gender_reach_breakdown": [
            {"country": "AT", "age_gender_breakdowns": [{"age_range": "25-34", "male": "None", "female": "1200", "unknown": "3"}]}
        ],
    }
    raw["data_reach"] = {"ad_library_main": {"ad_details": {"transparency_by_location": {"eu_transparency": eu, "uk_transparency": None}}}}
    raw["is_active"] = "False"
    ad = apify.to_ads_archive(raw)
    assert ad["eu_total_reach"] == 567391 and ad["target_gender"] == "Women"
    assert ad["target_ages"] == ["18", "65+"] and [loc["name"] for loc in ad["target_locations"]] == ["AT"]
    assert ad["target_locations_raw"] == ["Austria"] and ad["ad_delivery_stop_time"] is not None
    assert ad["age_country_gender_reach_breakdown"][0]["age_gender_breakdowns"][0] == {
        "age_range": "25-34", "male": None, "female": 1200, "unknown": 3,
    }


def test_out_of_credit_is_detected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(402, json={"error": {"type": "not-enough-usage-to-run-paid-actor", "message": "Monthly usage limit exceeded"}})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        apify.run_actor(client, {"advertisers": ["1"]})
    except apify.OutOfCredit:
        pass
    else:
        raise AssertionError("debía avisar que la cuenta no tiene crédito")
