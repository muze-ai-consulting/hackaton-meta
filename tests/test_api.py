"""Pruebas de la API del demo, siempre con el servidor falso."""

from fastapi.testclient import TestClient

from ensayo import api, llm

PIXEL = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="


def client(tmp_path, monkeypatch) -> TestClient:
    monkeypatch.setattr(llm, "RESULTS", tmp_path)  # el medidor falso escribe en tmp, no en results/
    return TestClient(api.app)


def request(**extra) -> dict:
    return {
        "brand": "Prueba",
        "variants": [{"title": "Uno", "body": "Texto uno"}, {"title": "Dos", "body": "Texto dos", "image_url": PIXEL}],
        "target": {"age_min": 25, "age_max": 44, "gender": "Women", "countries": ["de", "FR"]},
        "personas": 40,
        **extra,
    }


def test_simulate_mock_with_image(tmp_path, monkeypatch) -> None:
    res = client(tmp_path, monkeypatch).post("/api/simulate", json=request())
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "mock" and data["personas"] == 40
    assert sorted(data["population"]["ranking"]) == ["v1", "v2"]
    assert sorted(data["single_call"]["ranking"]) == ["v1", "v2"]
    assert 0 < len(data["population"]["sample_reactions"]) <= 8
    assert data["usd"] > 0  # costo hipotético, incluye los tokens de la imagen


def test_real_mode_blocked_without_flag(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("ENSAYO_REAL", raising=False)
    res = client(tmp_path, monkeypatch).post("/api/simulate", json=request(mode="real"))
    assert res.status_code == 403


def test_validation_and_pages(tmp_path, monkeypatch) -> None:
    c = client(tmp_path, monkeypatch)
    assert c.post("/api/simulate", json=request(variants=[{"title": "solo una"}])).status_code == 422
    assert c.get("/health").json() == {"status": "ok"}
    assert "Second Look" in c.get("/").text
    assert c.get("/api/config").json()["real_allowed"] in (True, False)


def test_to_batch_shape() -> None:
    batch = api.to_batch(api.SimulateIn(**request()))
    assert batch["target"]["target_ages"] == ["25", "44"]
    assert [loc["name"] for loc in batch["target"]["target_locations"]] == ["DE", "FR"]
    assert batch["variants"][1]["image_url"] == PIXEL


def test_examples_only_dev_with_reach(tmp_path, monkeypatch) -> None:
    import json

    dev = [
        {
            "batch_id": "b1",
            "page_name": "Marca",
            "week": "2026-09-14",
            "target": {"target_ages": ["25", "65+"], "target_gender": "Women", "target_locations": [{"name": "DE", "excluded": False}]},
            "variants": [{"ad_id": "1", "title": "T", "body": "x", "image_url": "https://img/1"}, {"ad_id": "2", "title": "", "body": "y", "image_url": None}],
            "labels": {"1": {"reach": 900}, "2": {"reach": 100}},
        },
        {"batch_id": "s1", "sealed": True, "variants": [], "labels": {}},
    ]
    path = tmp_path / "dev.json"
    path.write_text(json.dumps(dev), encoding="utf-8")
    monkeypatch.setattr(api, "DEV_BATCHES", path)
    out = client(tmp_path, monkeypatch).get("/api/examples").json()
    assert [e["batch_id"] for e in out] == ["b1"]
    assert out[0]["target"] == {"age_min": 25, "age_max": 65, "gender": "Women", "countries": ["DE"]}
    assert out[0]["reach"] == {"1": 900, "2": 100}


def test_examples_empty_without_batches(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(api, "DEV_BATCHES", tmp_path / "missing.json")
    assert client(tmp_path, monkeypatch).get("/api/examples").json() == []


def test_real_daily_limit(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ENSAYO_REAL", "1")
    monkeypatch.setitem(api.REAL_DAILY_LIMITS, "simulate", 0)
    res = client(tmp_path, monkeypatch).post("/api/simulate", json=request(mode="real"))
    assert res.status_code == 429


def test_examples_carry_real_dev_prediction(tmp_path, monkeypatch) -> None:
    import json

    dev = [
        {
            "batch_id": "b1",
            "page_name": "Marca",
            "week": "2026W40",
            "target": {"target_ages": ["18", "65+"], "target_gender": "All", "target_locations": [{"name": "FR"}]},
            "variants": [{"ad_id": "1", "body": "x", "image_url": None}, {"ad_id": "2", "body": "y", "image_url": None}],
            "labels": {"1": {"reach": 10}, "2": {"reach": 20}},
        }
    ]
    (tmp_path / "dev.json").write_text(json.dumps(dev), encoding="utf-8")
    stats = {"1": {"stop_rate": 0.2, "click_rate": 0.05, "click_reasons": []}, "2": {"stop_rate": 0.4, "click_rate": 0.1, "click_reasons": []}}
    run = {"mock": False, "config": {"model": "muse-spark-1.3-contributor", "personas": 1000}, "batches": [
        {"batch_id": "b1", "population": {"ranking": ["2", "1"], "stats": stats}, "single_call": {"ranking": ["1", "2"]}}
    ]}
    (tmp_path / "backtest_dev.json").write_text(json.dumps(run), encoding="utf-8")
    (tmp_path / "backtest_dev_mock.json").write_text(json.dumps({**run, "mock": True}), encoding="utf-8")
    monkeypatch.setattr(api, "DEV_BATCHES", tmp_path / "dev.json")
    monkeypatch.setattr(api, "RESULTS", tmp_path)
    pred = client(tmp_path, monkeypatch).get("/api/examples").json()[0]["prediction"]
    assert pred["ranking"] == ["2", "1"] and pred["single_call"] == ["1", "2"] and pred["personas"] == 1000
    assert pred["stats"]["2"] == {"stop_rate": 0.4, "click_rate": 0.1}


def test_local_ad_images(tmp_path, monkeypatch) -> None:
    images = tmp_path / "images"
    images.mkdir()
    (images / "123.jpg").write_bytes(b"\xff\xd8jpeg")
    monkeypatch.setattr(api, "AD_IMAGES", images)
    c = client(tmp_path, monkeypatch)
    assert c.get("/api/ad-image/123").status_code == 200
    assert c.get("/api/ad-image/999").status_code == 404
    assert c.get("/api/ad-image/..%2F..%2Fetc").status_code == 404
    assert api.ad_image_url("123", "https://x") == "api/ad-image/123"
    assert api.ad_image_url("999", "https://x") == "https://x"
