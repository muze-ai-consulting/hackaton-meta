# hackaton-meta — Ensayo para anuncios

Proyecto Labs de Muze para la **Meta Global AI Developer Hackathon** (26-oct al 4-nov-2026, US$1M, track Startup, tema "Push the Frontier").
**Entrega: miércoles 4-nov-2026 a las 18:00 de Chile** (cierre oficial 21:00 ET = 23:00 Chile). Jurado 4–8 nov, cierre 9 nov.

**Producto: Ensayo para anuncios.** Audiencias sintéticas de Instagram y Facebook que ven las variantes de un anuncio y predicen cuál rinde, antes de que el anunciante gaste. Plan y roadmap: `PLAN.md` (versión visual: https://claude.ai/artifact/QLNs68p9s2JJEpou72BfH3). Investigación detrás: `reports/` y `research_notes/`.

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
- **Ad Library:** solo anuncios entregados en la UE/UK (los comerciales de otros países no salen en la API). EE.UU. descartado (27-oct): sin la DSA, Meta no publica alcance de anuncios comerciales allá; los políticos quedan fuera por decisión de Mark. Criterio: ir donde haya más datos; se suman marcas de EE.UU. que pautan en UK y se baja cada página con `ad_reached_countries=ALL`. Sin descarga en lote; `ad_snapshot_url` de a un anuncio, para análisis, respetando los términos de almacenamiento de Meta.
- **Datos de clientes** van por el endpoint estándar de la Model API, nunca por el `contributor` (Meta usa esos datos). El contributor solo para datos públicos de la Ad Library.
- Credenciales (token de Meta, key de la Model API) solo en `.env`, nunca en el repo.

## Arquitectura
Placeholder hasta el día 1. Capas previstas: ingesta (Ad Library) → variantes (Muse Image) → población (1.000 personas, semillas fijas, caché) → feed simulado (Spark 1.3, cuatro órdenes) → ranking con explicación → tablero. Intermedios en `data/`, resultados en `results/`.

## Deployment
- **Web del plan (equipo):** https://labs.muze.cl/hackaton-meta/ — estática y pública por decisión de Mark (solo `noindex`). Fuente en `site/`; el avance vive en `site/roadmap.json` (estados: `pendiente`, `en-curso`, `hecho`, `bloqueado`; riesgos `abierto`/`resuelto`). Informes HTML: `uv run --python 3.12 --with markdown scripts/build_site.py` → `site/informes/`. Publicar: `rsync -az site/ root@185.205.244.85:/var/www/hackaton-meta/` (sin `--delete`). Ruta nginx en `/etc/nginx/sites-enabled/labs.muze.cl` (bloque `location /hackaton-meta/`); respaldos en `/root/nginx-backups/`.
- **Producto (Ensayo):** Docker Compose con `restart: unless-stopped` y health check en el VPS, en `labs.muze.cl/ensayo` vía nginx. Deploy solo con OK de Mark.

## Mistakes Log
<!-- formato: - AAAA-MM-DD — qué pasó — regla que lo evita -->
