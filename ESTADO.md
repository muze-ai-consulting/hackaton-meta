# Estado del proyecto: traspaso al 1-nov-2026 (actualizado: front en React con el flujo de 3 pasos y el anuncio real)

Para retomar sin perder contexto. Las reglas duras están en `CLAUDE.md`; el plan, en `PLAN.md`; la investigación, en `reports/` (la última es `reports/Hackatón de Meta apuesta final.md`).

## Decisiones tomadas
- **La idea se mantiene: Ensayo para anuncios.** Audiencias sintéticas que ven las variantes de un anuncio en un feed simulado y predicen cuál rinde, validadas con un backtest contra la Meta Ad Library (UE/UK).
- **Por qué:** el ganador de la hackatón de Anthropic y Forum Ventures (NYC, sept-2025), Zenith de Affaan Mustafa y David Rodriguez, hizo *clientes* sintéticos (no inversionistas) y ganó por cerrar el ciclo con datos reales: personas → simulación → contraste con la realidad → recalibración. Ese ciclo es lo que hay que mostrar en el video. Su sitio es https://zenith.chat/: idea → perfil de cliente → chatear con personas sintéticas que «responden y discuten como prospectos reales» → validar con encuestas a clientes reales → las personas se recalibran con lo validado. Diferencia a favor nuestro: validamos contra resultados reales (alcance en la Ad Library, backtest preregistrado con rivales), no contra encuestas. Lo que ellos tenían y nosotros no: conversar con una persona (ya agregado, 1-nov) y ver el ciclo de aprendizaje en pantalla (pendiente: "antes y después de calibrar" en Prueba del modelo, cuando haya datos). Su repo "Everything Claude Code" es configuración de Claude Code para programar, no arquitectura del producto: **no se instala** (choca con la poda del CLAUDE.md global y suma contexto).
- **Datos:** UE/UK más marcas de EE.UU. que pautan en UK. EE.UU. descartado (sin DSA no hay alcance comercial); sin anuncios políticos.
- **Créditos de Meta (150):** se usan solo para validar: sonda (<US$1), piloto, calibración, set sellado, hash en vivo y demo. Todo lo demás se desarrolla con el servidor falso. Gasto esperado ~US$30, tope US$68.
- **Herramientas:** el producto corre solo con modelos de Meta (Spark 1.3, Muse Image). Claude Code se usa para programar y se declara en el README. Falta confirmarlo en las Official Rules y en el Discord.
- **Claude Code:** el plan Ultra iba en 50 % semanal el 1-nov; se reinicia el 5-nov (después de la entrega). Sesiones cortas, `/clear` entre tareas, nada de investigación con muchos agentes salvo que haga falta.

## Lo construido (rama `dia-0`, sin merge a `main`)
- `ensayo/population.py`, `batches.py`, `metrics.py`, `costs.py`: población, lotes con sellado, métricas y medidor de gasto.
- `ensayo/llm.py`: cliente async; toda llamada pasa por el `Ledger`. Con `mock=True` usa `ensayo/mock.py` (sin red) y anota el costo hipotético en `results/costs_mock.jsonl`.
- `ensayo/simulate.py`: feed simulado (20 personas por llamada, 4 órdenes repartidos entre llamadas, solo letras en el prompt), puntaje = frenado + clic (supuesto a calibrar), muestra de reacciones, y el rival de llamada única.
- `ensayo/fixtures.py`: lotes inventados.
- `scripts/run_backtest.py`: población vs llamada única vs azar. Sin `--mock` solo muestra el costo; gasta con `--yes`. El sellado escribe los rankings y su SHA-256 antes de mirar etiquetas (`--score` después).
- `frontend/` (React 18 + Vite 5 + Tailwind 4 + componentes estilo shadcn) compila a `web/` (`cd frontend && npm run build`; el build se versiona, así el Dockerfile no cambia). Flujo de producto: 1) tus versiones (subir fotos o generarlas con Muse Image), 2) tu audiencia (6 presets + ajuste de edad, género y países), 3) resultado (ganadora, 3 razones, barras, rival de llamada única y chat con la audiencia). Más "Ejemplos reales": un lanzamiento real del set de desarrollo, Ensayo predice y después se revela el alcance UE. Tokens de zenith.chat en `src/index.css`. `ensayo/api.py` sirve `web/index.html` en `/` y `web/static/` en `/static`; `GET /api/examples` entrega hasta 12 lotes de `data/batches/dev.json` (nunca del sellado). Modo real solo con `ENSAYO_REAL=1` (Spark estándar, fase `demo`, máx. 300 personas). Preview: `ensayo` en `.claude/launch.json`.
- `ensayo/images.py` + `POST /api/variants`: variantes con Muse Image. Una llamada a Spark escribe un ángulo por variante (título, texto, prompt de imagen; ve la foto del producto si la hay) y `muse-image-1.0` genera una imagen por variante (`ModelClient.image`, US$0,01 cada una, pasa por el `Ledger`). En el demo, el bloque "Generar variantes con Muse Image" llena el formulario. Modo falso: degradado PNG de relleno sin red, costo hipotético en `results/costs_mock.jsonl` (~US$0,03 por 3 variantes). Supuestos sin verificar hasta la sonda: que `/images/generations` acepte `size` y devuelva `b64_json` o `url` (se manejan los dos), y que no haya edición desde foto (por eso la foto pasa por Spark y no por Muse Image).
- `ensayo/chat.py` + `POST /api/chat`: conversar con una persona de la audiencia. Cada tarjeta de "Algunas personas" tiene "Conversar": la persona responde en primera persona con su descripción, los anuncios (mismas letras del demo, con imagen) y su reacción como contexto, y puede discutir. Una llamada a Spark por pregunta (fase `demo`); el historial lo manda el navegador (máx. 10 mensajes). Modo falso con respuesta de relleno.
- Diseño del demo basado en zenith.chat: fondo `#ebedf1`, Inter, tarjetas blancas translúcidas con sombra, botón primario `#353536`, acento cian → violeta → verde, portada con los cuatro pasos. Verificado en escritorio y a 375 px.
- `ensayo/apify.py` + `scripts/eu_advertisers.py --apify`: Ad Library vía el actor de Apify `memo23/facebook-ads-library-scraper-cheerio`. Convierte cada anuncio a los campos de `ads_archive` (alcance UE, edad, género, países con código ISO desde el desglose de alcance, textos, plataformas) y además trae la URL de la imagen, que pasa a las variantes de los lotes. Respuestas cacheadas en `data/raw/apify/`; sin `--yes` solo muestra el costo. Probado contra Apify real el 1-nov con Snocks y Holy Energy: 4 corridas, ~US$0,25; 58 de 60 anuncios con alcance UE y segmentación, 60/60 con imagen, 24 elegibles (después del 2-sep, una versión) y 2 lotes de 3 variantes. Notas: el actor no respeta `startDateMin` en el modo por página (trae anuncios anteriores al corte, que `batches` descarta) y el plan gratis corta cada corrida en 30 anuncios.
- `scripts/probe_model_api.py` (sonda del día 0) y `scripts/eu_advertisers.py` (descarga y ranking de anunciantes), ambos sin correr: faltan credenciales.
- 39 pruebas: `uv run --group dev pytest -q`.

## Bloqueado en Mark
1. ~~Token de la Ad Library~~ Mark no alcanzó a obtenerlo (1-nov). Reemplazo: Apify (ver abajo). Falta que Mark cree la cuenta en apify.com y ponga `APIFY_TOKEN` en `.env`. El plan gratis limita cada corrida a 30 anuncios y a un objetivo: sirve para validar; para el set completo conviene un plan pagado (máx. ~US$14 por los 79 anunciantes con 300 anuncios cada uno).
2. Key de la Model API (`MODEL_API_KEY` en `.env`) y confirmar que los 150 créditos son US$ y valen en el contributor.
3. Leer las Official Rules y preguntar en el Discord: herramientas de IA para programar, modelos que no son de Meta, código previo (no hay; el repo parte el 27-oct).
4. ~~OK para desplegar el demo~~ dado y desplegado el 1-nov: https://labs.muze.cl/ensayo/ (solo modo prueba). Falta el OK para encender el modo real en el VPS cuando haya key.
5. Ruta sin datos: si tampoco hay datos de Apify el lunes 2-nov al mediodía, se entrega como protocolo preregistrado + motor reproducible + demo, sin métrica de precisión.

## Pendiente (en orden sugerido)
1. ~~Variantes con Muse Image~~ hecho (1-nov). Con la key: probarlo una vez en real con `ENSAYO_REAL=1`.
2. ~~Despliegue del demo~~ hecho (1-nov): https://labs.muze.cl/ensayo/. Detalles y comando de redespliegue en `CLAUDE.md` § Deployment.
3. **Con la key:** `probe_model_api.py` → actualizar `IMAGE_TOKENS` en `simulate.py` y precios/caché medidos → piloto de 1 lote con 200 personas.
4. **Datos:** ~~validar con 2 marcas~~ hecho. Siguiente: corrida completa `uv run python scripts/eu_advertisers.py --apify --yes` (máx. ~US$23 con plan pagado; con el gratis, cada página queda en 30 anuncios y los US$5 alcanzan para ~20 marcas) → `python -m ensayo.batches` → commit de `results/sealed_labels.sha256` → calibración en dev (pesos de edad, puntaje) → corrida sellada → hash de rankings en commit antes del 3-nov 23:59.
5. **README** con la declaración de Claude Code, el protocolo y cómo correr todo. Video y formulario de entrega (Mark los envía).
6. Actualizar `site/roadmap.json` (editar con reemplazo de texto, no con `json.dump`) y publicar con el rsync del CLAUDE.md.

7. ~~Redesplegar el front nuevo~~ hecho (2-nov) en https://labs.muze.cl/ensayo/, con los 19 lotes de desarrollo como ejemplos reales.
8. ~~Descarga de las 79 marcas~~ hecha (1-nov): 2.010 anuncios → 32 lotes (19 de desarrollo con 72 variantes, 13 sellados). Hash de las etiquetas selladas en `results/sealed_labels.sha256`. Apify ya no se usa.

## Críticos para el jurado (2-nov)
- **Hecho:** interfaz en inglés; `/api/examples` adjunta la predicción del último backtest real de dev (`results/backtest_dev*.json` sin `_mock`), así la pantalla del anuncio real muestra predicciones reales sin gastar por visita; cupo diario por IP en modo real (`REAL_DAILY_LIMITS`: 5 ensayos, 3 generaciones, 30 preguntas) además del tope de la fase `demo`; la línea de confianza se oculta mientras el backtest sea de prueba; si una imagen de fbcdn falla, enlace permanente al anuncio en la Biblioteca.
- **Imágenes:** ~~vencen el 6-nov~~ resuelto (2-nov, decisión de Mark): las 128 (dev y sellado) están en `data/images/`; el demo las sirve en `/api/ad-image/<ad_id>` y `run_backtest.py` las manda como data URI.
- **Hash público:** el repo se hace público el **5-nov** (decisión de Mark). Como el plazo del hash es el 3-nov 23:59 y la fecha de un commit se puede editar, conviene publicar también el hash el 3-nov en el Discord (o un gist público) para que haya un registro de terceros.
- **Idioma:** ~~motivos en español~~ resuelto (2-nov): prompts de simulación, rival, chat y variantes, descripciones de personas y servidor falso en inglés, antes del backtest de dev. Caché de poblaciones nueva (`*-en.json`).
- **Para encender el modo real en el VPS:** con la key, correr `scripts/run_backtest.py --source dev --personas 200 --yes`, subir el JSON a `/opt/ensayo/results/` y poner `ENSAYO_REAL=1` (con OK de Mark).

## Resultados con la key (2-nov)
- Sonda: modelos OK, contributor OK, Muse Image OK, ~296 tokens por imagen, caché funciona. Spark 1.3 razona y gasta max_tokens en eso: ahora `reasoning_effort=low` + margen (`ensayo/llm.py`). Key en `.env` como `META_API_KEY`.
- **Backtest de dev (19 lotes, 1.000 personas, contributor, low): US$ 0,63, 0 fallas. La audiencia NO le gana al azar ni a la llamada única.** Pares bien ordenados: audiencia 0,453 [0,30–0,59], llamada única 0,487, azar 0,522. Ganadora: 26 % vs 37 % vs 32 %. Puntuar solo frenado o solo clic no cambia nada. Las etiquetas son débiles: en la mayoría de los lotes la ganadora llega a 1,0–1,5 veces lo que llega la segunda.
- Decisión pendiente de Mark: qué contamos (ver mensaje del 2-nov). El sellado se corre igual antes del 3-nov 23:59.

## Rediseño acotado (2-nov, regla fijada antes de correr)
- Diagnóstico en dev, sin gastar: el texto más corto gana el 63 % de los pares, y la población prefiere el texto largo (lo lee completo; el feed real lo corta tras ~125 caracteres).
- Se prueban solo dos configuraciones nuevas en dev: `--view feed --effort low` y `--view feed --effort medium` (el anuncio como lo muestra el feed: primera línea cortada, imagen, título debajo). La llamada única ve lo mismo.
- Rival nuevo sin modelo: "gana el texto más corto" (`short_text`). Va también al sellado y su ranking entra en el hash.
- Regla: al sellado va la configuración con mayor promedio de pares bien ordenados de la población en dev, entre las tres (`full/low`, `feed/low`, `feed/medium`). No se prueba nada más. Se corre el sellado aunque no gane; se informa lo que salga.
- Resultado en dev (pares bien ordenados de la población / llamada única / texto corto / azar): `full/low` 0,453 / 0,487 / 0,64 / 0,522; `feed/low` **0,493** / 0,498 / 0,64 / 0,522 (US$ 0,64); `feed/medium` 0,484 / 0,484 / 0,64 / 0,522 (US$ 0,95). Por la regla, al sellado va `feed/low`. Ninguna configuración de modelo le gana al azar; la regla del texto corto sí (IC95 0,51–0,77).

## Fechas
Entrega interna: miércoles 4-nov 18:00 Chile (cierre oficial 23:00 Chile). Hash de la prueba en vivo: antes del 3-nov 23:59.
