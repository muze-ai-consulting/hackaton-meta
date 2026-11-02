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
    assert "Ensayo" in c.get("/").text
    assert c.get("/api/config").json()["real_allowed"] in (True, False)


def test_to_batch_shape() -> None:
    batch = api.to_batch(api.SimulateIn(**request()))
    assert batch["target"]["target_ages"] == ["25", "44"]
    assert [loc["name"] for loc in batch["target"]["target_locations"]] == ["DE", "FR"]
    assert batch["variants"][1]["image_url"] == PIXEL
