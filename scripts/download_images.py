"""Descarga las imágenes de los anuncios de los lotes a data/images/<ad_id>.jpg (máx. 720 px, JPEG).

Las URLs de fbcdn que trae la Ad Library vencen (oe=…): las del 1-nov vencían el 6-nov, en plena evaluación.
Decisión de Mark (2-nov): guardar una copia para el demo y para correr el set sellado aunque venzan.
Ya descargadas se saltan. Las imágenes no se versionan (data/ está en .gitignore).

Uso: uv run python scripts/download_images.py
"""

import asyncio
import io
import json
import logging
from pathlib import Path

import httpx
from PIL import Image, UnidentifiedImageError

from ensayo import DATA

log = logging.getLogger("images")

IMAGES = DATA / "images"
MAX_SIDE = 720
SOURCES = [DATA / "batches" / "dev.json", DATA / "batches" / "sealed_inputs.json"]


def wanted() -> dict[str, str]:
    """ad_id → URL de la imagen, de todos los lotes que existan."""
    out: dict[str, str] = {}
    for path in SOURCES:
        if not path.exists():
            continue
        for batch in json.loads(path.read_text(encoding="utf-8")):
            for v in batch["variants"]:
                if v.get("image_url"):
                    out[str(v["ad_id"])] = v["image_url"]
    return out


def to_jpeg(raw: bytes) -> bytes:
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82, optimize=True)
    return buf.getvalue()


async def fetch(client: httpx.AsyncClient, ad_id: str, url: str, sem: asyncio.Semaphore) -> bool:
    dest = IMAGES / f"{ad_id}.jpg"
    if dest.exists():
        return True
    async with sem:
        try:
            res = await client.get(url)
            res.raise_for_status()
            dest.write_bytes(to_jpeg(res.content))
            return True
        except (httpx.HTTPError, UnidentifiedImageError, OSError) as exc:
            log.warning(f"{ad_id}: {exc}")
            return False


async def run() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    todo = wanted()
    sem = asyncio.Semaphore(6)
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        ok = await asyncio.gather(*(fetch(client, ad, url, sem) for ad, url in todo.items()))
    log.info(f"{sum(ok)} de {len(todo)} imágenes en {IMAGES.relative_to(DATA.parent)}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    asyncio.run(run())


if __name__ == "__main__":
    main()
