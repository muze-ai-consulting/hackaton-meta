# hackaton-meta — Ensayo para anuncios

Proyecto Labs de Muze para la **Meta Global AI Developer Hackathon** (26-oct al 4-nov-2026, US$1M, track Startup, tema "Push the Frontier").
**Entrega: miércoles 4-nov-2026 a las 18:00 de Chile** (cierre oficial 21:00 ET = 23:00 Chile). Jurado 4–8 nov, cierre 9 nov.

**Producto (desde el 3-nov): Second Look, escudo antiestafas** (`ensayo/shield.py`; ver ESTADO.md). Antes fue Ensayo para anuncios: audiencias sintéticas que predecían qué anuncio rinde; no pasó su validación y su código queda en el repo. Plan y roadmap: `PLAN.md` (versión visual: https://claude.ai/artifact/QLNs68p9s2JJEpou72BfH3). Investigación detrás: `reports/` y `research_notes/`.

## Stack (propuesto, confirmar el día 0)
- Python 3.12 con `uv` para la ingesta, el motor de población, el backtest y la API (FastAPI).
- Front web simple para el demo (subir foto, grilla de variantes, feed simulado, tablero).
- Modelos de Meta vía Meta Model API (`https://api.meta.ai/v1`, compatible con los SDK de OpenAI y Anthropic): `muse-spark-1.3` (simulación y ranking), `muse-image-1.0` (variantes), `muse-voice-transcribe-1.0` (audio de anuncios en video).
- Datos: Meta Ad Library API (`ads_archive`). Campos verificados en `research_notes/Hackatón de Meta ideas en grande/ad_library_api_verificado.md`.

## Reglas duras
- **Contaminación:** el backtest usa solo anuncios con `ad_delivery_start_time` posterior a 2026-09-02 (lanzamiento de Spark 1.3).
- **Comparar solo dentro de cada anunciante** (misma página, misma semana de lanzamiento). El `eu_total_reach` bruto depende del presupuesto.
- **Set sellado:** después de abrir el set de evaluación sellado no se toca el modelo.
- **Rivales obligatorios:** azar y una sola llamada a Spark 1.3 sin población. Si la población no le gana a la llamada única el jueves 29-oct, se pivota (ver PLAN.md).
- **Prueba en vivo:** el hash SHA-256 de los rankings se publica en un commit antes del 3-nov 23:59. No se cambian después.
- **Ad Library:** solo anuncios entregados en la UE/UK (los comerciales de otros países no salen en la API). EE.UU. descartado (27-oct): sin la DSA, Meta no publica alcance de anuncios comerciales allá; los políticos quedan fuera por decisión de Mark. Criterio: ir donde haya más datos; se suman marcas de EE.UU. que pautan en UK y se baja cada página con `ad_reached_countries=ALL`. Sin descarga en lote; `ad_snapshot_url` de a un anuncio, para análisis, respetando los términos de almacenamiento de Meta. **Fuente de datos desde el 1-nov (decisión de Mark):** Mark no alcanzó a obtener el token de la API oficial, así que la Ad Library se baja con el actor de Apify `memo23/facebook-ads-library-scraper-cheerio` (`ensayo/apify.py`, `scripts/eu_advertisers.py --apify`, `APIFY_TOKEN` en `.env`). Se declara en el README y en el video. Imágenes: desde el 2-nov (decisión de Mark) se guarda una copia de 720 px en `data/images/` (`scripts/download_images.py`, no se versiona) porque las URLs de fbcdn vencen; el demo y el backtest usan la copia. Al VPS solo van las de dev. Si llega el token oficial, se vuelve a la API.
- **Datos de clientes** van por el endpoint estándar de la Model API, nunca por el `contributor` (Meta usa esos datos). El contributor solo para datos públicos de la Ad Library.
- Credenciales (token de Meta, key de la Model API) solo en `.env`, nunca en el repo.
- **Presupuesto: 150 créditos para toda la hackatón** (asumimos US$; confirmar al tener la key).
  - Calibración, set sellado y prueba en vivo van en `muse-spark-1.3-contributor`, con 20 personas por llamada: unos US$ 0,25 por lote, frente a ~US$ 34 en estándar con una persona por llamada.
  - El estándar se usa solo para el demo y para cualquier dato de cliente.
  - Toda llamada pasa por `ensayo.costs.Ledger`, que tiene tope por fase y registra en `results/costs.jsonl`.
  - Si agrupar personas empeora la calidad, primero se bajan a 200 personas; recién después se pasa a una por llamada.

## Arquitectura
Capas previstas: ingesta (Ad Library) → variantes (Muse Image) → población (1.000 personas, semillas fijas, caché) → feed simulado (Spark 1.3, cuatro órdenes) → ranking con explicación → tablero. Intermedios en `data/`, resultados en `results/`.
- Paquete `ensayo/` (`uv run --group dev pytest`):
  - `population.py`: personas deterministas desde la segmentación del anuncio (nunca desde su alcance). Los pesos de edad y de plataforma son supuestos hasta calibrarlos con el set de desarrollo.
  - `batches.py`: lotes por página y semana con anuncios de una versión. Separa el sellado por hash del lote y escribe el SHA-256 de las etiquetas en `results/sealed_labels.sha256`.
  - `metrics.py`: pares bien ordenados, top-1, Spearman, bootstrap y rival al azar.
  - `costs.py`: precios, medidor con topes por fase y estimación de costo por lote.
  - `llm.py`: cliente async de la Model API; toda llamada pasa por el `Ledger`. `--mock` usa `mock.py` (sin red; el costo hipotético va a `results/costs_mock.jsonl`).
  - `simulate.py`: feed simulado (20 personas por llamada, 4 órdenes repartidos entre llamadas, solo letras en el prompt) y el rival de llamada única. Puntaje = frenado + clic (supuesto a calibrar en dev).
  - `fixtures.py`: lotes inventados para desarrollar sin Ad Library.
  - `api.py` + `web/`: demo (FastAPI). `web/` es el build de `frontend/` (React + Vite + Tailwind; `cd frontend && npm run build`) y se versiona. Todo el producto en inglés (interfaz, prompts, personas; decisión de Mark del 2-nov). `GET /api/examples` adjunta la predicción del último backtest real de dev; en modo real hay cupo diario por IP. `uv run uvicorn ensayo.api:app --port 8040`. Por defecto modo falso; el modo real usa Spark 1.3 estándar (fase `demo`) y solo se habilita con `ENSAYO_REAL=1`.
- Scripts: `scripts/run_backtest.py` (población vs llamada única vs azar; sin `--mock` muestra el costo y solo gasta con `--yes`), `scripts/probe_model_api.py` (día 0) y `scripts/eu_advertisers.py` (descarga a `data/raw/ad_library/`, que alimenta `python -m ensayo.batches`; con `--apify` usa Apify y sin `--yes` solo muestra el costo).

## Deployment
- **Web del plan (equipo):** https://labs.muze.cl/hackaton-meta/ — estática y pública por decisión de Mark (solo `noindex`). Fuente en `site/`; el avance vive en `site/roadmap.json` (estados: `pendiente`, `en-curso`, `hecho`, `bloqueado`; riesgos `abierto`/`resuelto`). Informes HTML: `uv run --python 3.12 --with markdown scripts/build_site.py` → `site/informes/`. Publicar: `rsync -az site/ root@185.205.244.85:/var/www/hackaton-meta/` (sin `--delete`). Ruta nginx en `/etc/nginx/sites-enabled/labs.muze.cl` (bloque `location /hackaton-meta/`); respaldos en `/root/nginx-backups/`.
- **Producto (Ensayo):** https://labs.muze.cl/ensayo/ (desplegado el 1-nov con OK de Mark). Contenedor `ensayo` en `/opt/ensayo` del VPS (Docker Compose, `restart: unless-stopped`, health check en `/health`), publicado en `127.0.0.1:8040`; nginx `location /ensayo/` en el mismo archivo que `/hackaton-meta/` (respaldo `*-pre-ensayo` en `/root/nginx-backups/`). `./results` del VPS montado en el contenedor (uid 1000) con `backtest_fixtures_mock.json` para la pestaña Prueba del modelo. Modo real apagado: encenderlo (`ENSAYO_REAL=1` + `MODEL_API_KEY` en `/opt/ensayo/.env`) solo con OK de Mark. Los ejemplos reales salen de `/opt/ensayo/data/batches/dev.json` (volumen de solo lectura; subirlo con `rsync -az data/batches/dev.json root@185.205.244.85:/opt/ensayo/data/batches/` cada vez que cambien los lotes; el sellado nunca se sube). Redesplegar (también con su OK): `rsync -az --exclude __pycache__ Dockerfile docker-compose.yml .dockerignore pyproject.toml uv.lock ensayo web root@185.205.244.85:/opt/ensayo/` y `ssh root@185.205.244.85 'cd /opt/ensayo && docker compose up -d --build'`.

## Mistakes Log
<!-- formato: - AAAA-MM-DD — qué pasó — regla que lo evita -->
