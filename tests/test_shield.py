"""Pruebas del escudo antiestafas, siempre con el servidor falso."""

import base64
import struct

from fastapi.testclient import TestClient

from ensayo import api, llm
from ensayo.shield import LANGUAGE_LINE, band, shield_messages

PIXEL = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="


def wav(seconds: float = 2.0) -> bytes:
    data = b"\x00\x00" * int(16000 * seconds)
    header = b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 1, 1, 16000, 32000, 2, 16)
    return header + b"data" + struct.pack("<I", len(data)) + data


def client(tmp_path, monkeypatch) -> TestClient:
    monkeypatch.setattr(llm, "RESULTS", tmp_path)
    return TestClient(api.app)


def test_bands() -> None:
    assert band(0.5) == "scam" and band(0.49) == "careful" and band(0.2) == "careful" and band(0.19) == "genuine"


def test_product_prompt_only_adds_language_line() -> None:
    post = {"title": "Is this a scam?", "body": "Your parcel is held"}
    measured = shield_messages(post, [], round_=2)
    product = shield_messages(post, [], round_=2, language=True)
    assert product[0] == measured[0]
    assert product[1]["content"][-1]["text"] == measured[1]["content"][-1]["text"] + f"\n{LANGUAGE_LINE}"


def test_check_text(tmp_path, monkeypatch) -> None:
    res = client(tmp_path, monkeypatch).post("/api/check", json={"text": "URGENT: your bank account is locked, click the link and verify"})
    assert res.status_code == 200
    data = res.json()
    assert data["band"] == "scam" and data["verdict"] == "scam" and data["reason"] and data["action"]


def test_check_screenshot_and_voice(tmp_path, monkeypatch) -> None:
    audio = "data:audio/wav;base64," + base64.b64encode(wav()).decode()
    res = client(tmp_path, monkeypatch).post("/api/check", json={"images": [PIXEL], "audio": audio})
    assert res.status_code == 200
    data = res.json()
    assert data["images"] == 1 and "bank" in data["transcript"]


def test_check_empty_is_rejected(tmp_path, monkeypatch) -> None:
    assert client(tmp_path, monkeypatch).post("/api/check", json={"text": "  "}).status_code == 422


def test_check_bad_image_is_rejected(tmp_path, monkeypatch) -> None:
    res = client(tmp_path, monkeypatch).post("/api/check", json={"images": ["data:image/png;base64,bm90IGFuIGltYWdl"]})
    assert res.status_code == 422


def test_check_real_blocked_without_flag(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("ENSAYO_REAL", raising=False)
    assert client(tmp_path, monkeypatch).post("/api/check", json={"text": "hi", "mode": "real"}).status_code == 403
