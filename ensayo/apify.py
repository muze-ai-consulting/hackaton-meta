"""Ad Library vía Apify (actor memo23/facebook-ads-library-scraper-cheerio), mientras no haya token de la API oficial.

El actor lee la Biblioteca de anuncios pública (incluido el panel de transparencia de la UE) y devuelve, por
anuncio, el alcance en la UE y la segmentación. `to_ads_archive` lo deja con los mismos campos que pide
scripts/eu_advertisers.py a ads_archive, así ensayo.batches y el resto no cambian. Diferencias con la API oficial:

- La transparencia UE viene en data_reach.ad_library_main.ad_details.transparency_by_location.eu_transparency
  (no donde dice el README del actor) y con los números como texto.
- Los países de la segmentación pueden venir con el nombre en el idioma del proxy del actor ("Njemačka"): se usan
  los códigos ISO del desglose de alcance y, si no hay desglose, el nombre tal cual.
- En el modo por página el actor no respeta startDateMin: trae anuncios anteriores al corte. ensayo.batches los
  descarta (regla de contaminación), pero gastan parte del tope de anuncios.
- El género viene traducido ("Svi" = todos): se reconocen mujeres y hombres en varios idiomas; lo demás es All.
- Trae la URL de la imagen (`image_url`). Es de fbcdn y vence en días: sirve para simular al poco tiempo de bajarla.
  No se descargan las imágenes (términos de almacenamiento de Meta).

Costo: desde US$0,30 por 1.000 anuncios, con el alcance incluido. Lo paga la cuenta de Apify, no los créditos de Meta.
El token va en APIFY_TOKEN (.env) y viaja en la cabecera, nunca en la URL. Con más cuentas (APIFY_TOKEN_2, _3…),
scripts/eu_advertisers.py pasa a la siguiente cuando una se queda sin crédito (decisión de Mark, 1-nov).
"""

import logging
import time
from datetime import UTC, datetime
from typing import Any

import httpx

log = logging.getLogger(__name__)

API = "https://api.apify.com/v2"
ACTOR = "memo23~facebook-ads-library-scraper-cheerio"
USD_PER_AD = 0.0005  # techo del precio por anuncio, para estimar antes de correr
USD_PER_RUN = 0.06  # medido el 1-nov: cada corrida cuesta ~US$0,06 aunque traiga solo 30 anuncios
POLL_SECONDS = 10
RUN_TIMEOUT = 3600

WOMEN = {"women", "female", "žene", "zene", "frauen", "femmes", "mujeres", "donne", "vrouwen", "kobiety", "mulheres", "kvinder", "kvinnor"}
MEN = {"men", "male", "muškarci", "muskarci", "männer", "maenner", "hommes", "hombres", "uomini", "mannen", "mężczyźni", "homens", "mænd", "män"}


def _num(value: Any) -> int | None:
    """El actor entrega muchos números como texto ("567391"); None si no es un número."""
    try:
        return int(value) if value is not None and str(value) != "None" else None
    except (TypeError, ValueError):
        return None


def _true(value: Any) -> bool:
    return value is True or str(value).lower() == "true"


def _eu_info(item: dict[str, Any]) -> dict[str, Any]:
    """El bloque de transparencia UE. Las corridas reales lo traen en
    data_reach.ad_library_main.ad_details.transparency_by_location.eu_transparency; el ejemplo del README,
    en data_reach.aaa_info."""
    reach = item.get("data_reach") or {}
    details = (reach.get("ad_library_main") or {}).get("ad_details") or {}
    candidates = [
        ((details.get("transparency_by_location") or {}).get("eu_transparency")),
        details.get("aaa_info"),
        reach.get("aaa_info"),
    ]
    for block in candidates:
        if isinstance(block, dict) and ("eu_total_reach" in block or "age_audience" in block):
            return block
    return {}


def _breakdown(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "country": str(c.get("country") or "").upper(),
            "age_gender_breakdowns": [
                {"age_range": r.get("age_range"), **{k: _num(r.get(k)) for k in ("male", "female", "unknown")}}
                for r in c.get("age_gender_breakdowns") or []
            ],
        }
        for c in rows or []
        if c.get("country")
    ]


def _iso_date(ts: Any) -> str | None:
    try:
        return datetime.fromtimestamp(int(ts), tz=UTC).strftime("%Y-%m-%dT%H:%M:%S+0000")
    except (TypeError, ValueError, OverflowError):
        return None


def _gender(raw: Any) -> str:
    value = str(raw or "").strip().lower()
    if value in WOMEN:
        return "Women"
    if value in MEN:
        return "Men"
    return "All"


def _texts(snapshot: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Textos y títulos del anuncio. Más de uno = varias versiones (creatividad dinámica o carrusel)."""
    body = ((snapshot.get("body") or {}).get("text") or "").strip()
    bodies = [body] if body else []
    titles = [snapshot["title"].strip()] if (snapshot.get("title") or "").strip() else []
    for extra in snapshot.get("extra_texts") or []:
        text = (extra.get("text") if isinstance(extra, dict) else str(extra or "")).strip()
        if text and text not in bodies:
            bodies.append(text)
    for card in snapshot.get("cards") or []:
        if (card.get("body") or "").strip() and card["body"].strip() not in bodies:
            bodies.append(card["body"].strip())
        if (card.get("title") or "").strip() and card["title"].strip() not in titles:
            titles.append(card["title"].strip())
    return bodies, titles


def _image(snapshot: dict[str, Any]) -> str | None:
    for img in snapshot.get("images") or []:
        url = img.get("resized_image_url") or img.get("original_image_url")
        if url:
            return url
    for video in snapshot.get("videos") or []:
        if video.get("video_preview_image_url"):
            return video["video_preview_image_url"]
    return None


def to_ads_archive(item: dict[str, Any]) -> dict[str, Any] | None:
    """Un anuncio del actor con los campos de ads_archive; None si no trae id o fecha de inicio."""
    ad_id = str(item.get("ad_archive_id") or "")
    start = _iso_date(item.get("start_date"))
    if not ad_id or not start:
        return None
    snapshot = item.get("snapshot") or {}
    aaa = _eu_info(item)
    breakdown = _breakdown(aaa.get("age_country_gender_reach_breakdown") or [])
    ages = aaa.get("age_audience") or {}
    age_min, age_max = _num(ages.get("min")), _num(ages.get("max"))
    codes = sorted({c["country"] for c in breakdown})
    included = [loc for loc in aaa.get("location_audience") or [] if not _true(loc.get("excluded"))]
    locations = (
        [{"name": c, "type": "countries", "excluded": False} for c in codes]
        if codes
        else [{"name": loc.get("name"), "type": loc.get("type"), "excluded": False} for loc in included]
    )
    bodies, titles = _texts(snapshot)
    return {
        "id": ad_id,
        "page_id": str(item.get("page_id") or snapshot.get("page_id") or ""),
        "page_name": item.get("page_name") or snapshot.get("page_name"),
        "ad_delivery_start_time": start,
        # Para un anuncio activo, end_date es la fecha planeada: no es una fecha de término.
        "ad_delivery_stop_time": None if _true(item.get("is_active")) else _iso_date(item.get("end_date")),
        "ad_creative_bodies": bodies,
        "ad_creative_link_titles": titles,
        "publisher_platforms": [str(p).lower() for p in item.get("publisher_platform") or []],
        "eu_total_reach": _num(aaa.get("eu_total_reach")),
        "target_ages": [str(age_min), "65+" if (age_max or 0) >= 65 else str(age_max)] if age_min and age_max else [],
        "target_gender": _gender(aaa.get("gender_audience")),
        "target_locations": locations,
        "target_locations_raw": [loc.get("name") for loc in included],
        "age_country_gender_reach_breakdown": breakdown,
        "ad_snapshot_url": item.get("FB AD Link") or f"https://www.facebook.com/ads/library/?id={ad_id}",
        "image_url": _image(snapshot) or next(iter(item.get("imageUrls") or []), None),
        "source": "apify",
    }


class OutOfCredit(RuntimeError):
    """La cuenta de Apify no tiene crédito o llegó a su límite de uso."""


CREDIT_WORDS = ("limit", "usage", "credit", "exceed", "payment", "insufficient")


def _is_credit_problem(text: str) -> bool:
    text = text.lower()
    return any(w in text for w in CREDIT_WORDS)


def run_actor(client: httpx.Client, run_input: dict[str, Any]) -> list[dict[str, Any]]:
    """Lanza el actor, espera a que termine y devuelve los ítems de su dataset."""
    r = client.post(f"{API}/acts/{ACTOR}/runs", json=run_input)
    if r.status_code == 402 or (r.status_code == 403 and _is_credit_problem(r.text)):
        raise OutOfCredit(f"Apify {r.status_code}: {r.text[:200]}")
    if not r.is_success:
        raise RuntimeError(f"Apify {r.status_code}: {r.text[:300]}")
    run = r.json()["data"]
    deadline = time.monotonic() + RUN_TIMEOUT
    while run["status"] in ("READY", "RUNNING"):
        if time.monotonic() > deadline:
            raise RuntimeError(f"Apify: la corrida {run['id']} no terminó en {RUN_TIMEOUT} s")
        time.sleep(POLL_SECONDS)
        run = client.get(f"{API}/actor-runs/{run['id']}").json()["data"]
    if run["status"] != "SUCCEEDED":
        message = str(run.get("statusMessage") or "")
        error = OutOfCredit if _is_credit_problem(message) else RuntimeError
        raise error(f"Apify: la corrida {run['id']} terminó en {run['status']}: {message[:200]}")
    items = client.get(f"{API}/datasets/{run['defaultDatasetId']}/items", params={"clean": "true", "format": "json"})
    items.raise_for_status()
    usd = (run.get("usageTotalUsd") or 0) or (run.get("stats") or {}).get("costUsd") or 0
    log.info(f"Apify: corrida {run['id']}, {len(items.json())} ítems, US$ {usd:.3f}")
    return items.json()


def client_from_token(token: str) -> httpx.Client:
    return httpx.Client(headers={"Authorization": f"Bearer {token}"}, timeout=120)


def page_ads_input(page_id: str, start_min: str, max_items: int) -> dict[str, Any]:
    """Todos los anuncios de una página que empezaron desde start_min, con alcance UE."""
    return {
        "advertisers": [page_id],
        "adActiveStatus": "all",
        "startDateMin": start_min,
        "includeAdReach": True,
        "maxItems": max_items,
    }


def search_input(query: str, country: str, start_min: str, max_items: int = 50) -> dict[str, Any]:
    """Búsqueda por nombre de marca en un país, para encontrar el page_id."""
    return {
        "searchTerms": [query],
        "searchCountries": [country],
        "adActiveStatus": "all",
        "startDateMin": start_min,
        "searchMode": "keyword_unordered",
        "maxItems": max_items,
    }
