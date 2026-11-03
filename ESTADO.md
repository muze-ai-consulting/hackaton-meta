# Estado del proyecto (actualizado 3-nov: el producto es Second Look, el escudo antiestafas; lo de Ensayo queda como historia)

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

## Hipótesis nueva: a quién le muestra Meta cada anuncio (2-nov)
- Con segmentación amplia, Meta reparte cada anuncio a audiencias muy distintas (mujeres alcanzadas: 5 % a 99 %; dentro de una marca, ±10–20 puntos según el creativo).
- `scripts/validate_audience.py`: 294 anuncios de 24 marcas (posteriores al 2-sep, segmentación amplia). Métrica: correlación dentro de cada marca, con nulo por permutación.
- Llamada única (US$ 0,2): mujeres r 0,14 (p 0,004), 18–34 r 0,19 (p 0,001), 55+ r 0,17 (p 0,003). Primera señal del proyecto.
- Población de 200 personas (US$ 1,5): mujeres r 0,17 (p 0,004), 18–34 r 0,03 (n.s.), 55+ r 0,09 (p 0,07). Iguala en género y empeora en edad: la señal está en cómo el modelo lee el creativo, no en la población.
- **Prueba fuera de muestra (regla fijada el 2-nov ~19:10, antes de bajar los datos):** 29 marcas nuevas (`data/holdout_candidates.csv`), ninguna página de dev. Método congelado: `validate_audience.py` tal cual está en este commit (llamada única, Spark 1.3 contributor, effort low, mismo prompt, mismos filtros). Se predice, se commitea `results/holdout_predictions.sha256` y recién después `--score`. **Validado si al menos 2 de las 3 métricas (mujeres, 18–34, 55+) tienen correlación dentro de marca > 0 con p < 0,05.** Si no, se descarta la hipótesis.
- **Resultado fuera de muestra (2-nov ~20:00):** 133 anuncios de 12 marcas nuevas (Apify US$ ~2, modelo US$ 0,1). Hash de las predicciones `30d88295…` commiteado en `de4425e` antes de puntuar. Mujeres r **0,385** (p < 0,001); 18–34 r 0,154 (p 0,17, n.s.); 55+ r 0,417 (p 0,0495). **Regla cumplida (2 de 3).**
- Robustez (hecha después): género es sólido. Quitando cualquier marca sigue entre 0,32 y 0,42, y 9 de 12 marcas dan positivo. El 55+ depende de una sola marca (sin Junglück da −0,07). Conclusión honesta: **el modelo anticipa hacia qué género empuja Meta cada creativo; la edad no está demostrada.** El producto y el pitch se apoyan en género; la edad se muestra como exploratoria.

## Pivote: escudo antiestafas (2-nov, decisión de Mark; regla fijada antes de correr)
Investigación de ganadores 2026 en `reports/Ganadores hackathons 2026.md`. Mark eligió el escudo antiestafas: reenvías un mensaje, pantallazo o llamada y te dice si es estafa, por qué y qué hacer.
- **Datos:** preguntas reales de r/Scams, r/isthisascam y r/IsThisAScamIndia posteriores al 3-sep-2026 (después de Spark 1.3), bajadas sobre todo de Arctic Shift, archivo público y gratis (`scripts/scam_arctic.py`, publicaciones hasta el 28-oct para que los comentarios estén archivados), más un piloto con Apify (`scripts/scam_reddit.py`; cuatro de las cinco cuentas quedaron sin cupo). Todo en `data/raw/scams/`, que no se versiona.
- **Etiqueta:** el veredicto de la comunidad, que Spark extrae leyendo solo los comentarios (scam/legit/unclear). Se descartan los "unclear". Se auditan a mano 30 etiquetas al azar antes de puntuar.
- **Predicción:** Spark 1.3 contributor lee solo la publicación (título, texto, hasta 3 imágenes), nunca los comentarios. Predicciones y SHA-256 se commitean antes de puntuar (`scripts/validate_scams.py`).
- **Rivales:** regla de palabras clave (≥3 términos típicos de estafa = estafa) y "siempre estafa".
- **Regla de éxito (todas):** al menos 30 casos legítimos; exactitud balanceada del escudo ≥ 0,80; supera a la regla de palabras clave por ≥ 0,10 con el IC 95 % bootstrap sobre cero; falsas alarmas sobre casos legítimos ≤ 30 %. Si falla, se pasa a "Ojos por voz" (VizWiz).
- **Etiquetas (3-nov, antes de predecir):** 1.547 publicaciones → 969 scam, 169 legit, 407 unclear, 2 fallidas. Auditoría a mano de 30 (15 legit + 15 scam, semilla 30): 13/15 legit claras (2 dudosas: producto defectuoso, yogur de larga duración), 15/15 scam correctas. Muchos "legit" son quejas de consumo que la gente llama estafa: casos difíciles a propósito.
- **Resultado preregistrado (3-nov, hash 1665740b…): NO PASA.** 1.137 casos (968 scam, 169 legit). Escudo: exactitud balanceada **0,787** (regla ≥ 0,80), detecta 78,6 % de las estafas, falsa alarma 21,3 % (regla ≤ 30 %, pasa), AUC 0,85. Regla de palabras clave: 0,505; siempre estafa: 0,50. Ventaja sobre palabras clave +0,28 (IC 95 % 0,23–0,33, pasa). Cumple 3 de 4 condiciones.
- **Diagnóstico posterior (exploratorio, no cambia el resultado):** muchas estafas perdidas son publicaciones donde la persona cuenta lo que le pasó ("me sacaron US$200 del cajero", "cómo bloqueo a un estafador") y el modelo juzgó si la *publicación* era engañosa, no si la *situación* era una estafa. Es un problema de cómo se formuló la pregunta.
- **Intento 2 (decisión de Mark, 3-nov; regla fijada antes de bajar etiquetas y predecir):**
  - **Datos nuevos, nunca vistos:** r/Scams del 24-sep al 28-oct (el intento 1 solo llegó al 23-sep) más r/scamsUK y r/ScamCenter del 3-sep al 28-oct, en `data/raw/scams2/`. Se excluye todo id del intento 1.
  - **Único cambio:** la pregunta. Ahora se le pide juzgar la situación que la persona describe (mensaje, llamada, sitio, vendedor, cobro), aunque ya haya pasado, y se aclara que mal servicio, disputas o spam comercial cuentan como legítimos (constante `SITUATION` en `scripts/validate_scams.py`, `--round 2`). Mismo modelo, mismas etiquetas de la comunidad, misma auditoría de 30, mismo umbral 0,5.
  - **Misma regla:** ≥ 30 legítimos; exactitud balanceada ≥ 0,80; ventaja ≥ 0,10 sobre palabras clave con IC 95 % sobre cero; falsas alarmas ≤ 30 %. Si falla, se pasa a "Ojos por voz" sin otro intento. El 0,787 del intento 1 se publica igual en el README.
  - **Etiquetas (antes de predecir):** 1.189 publicaciones → 823 scam, 122 legit, 244 unclear. Auditoría a mano de 30 (semilla 30): 12/15 legit claras (3 dudosas: un bróker que "robó", un aviso de Barclays, un cheque de Capital One), 15/15 scam correctas.
  - **Resultado (3-nov, hash 38b435bb…): PASA, justo en el borde.** 945 casos (823 scam, 122 legit). Exactitud balanceada **0,801** (IC 95 % 0,759–0,839, o sea que el piso de 0,80 queda dentro del intervalo), detecta 84 % de las estafas, falsa alarma 23,8 %, AUC 0,88. Palabras clave: 0,517; ventaja +0,28 (IC 0,22–0,34). Cumple las 4 condiciones. Cómo contarlo: "en 945 preguntas reales posteriores al modelo, el escudo coincide con la comunidad 8 de cada 10 veces y detecta 84 % de las estafas, contra 48 % de un filtro de palabras clave". El intento 1 (0,787) se cuenta igual.

## Producto: Second Look (3-nov, Mark: "Sí, construye")
- **Qué hace:** pegas un mensaje, agregas hasta 3 pantallazos (también pegándolos) o una nota de voz (grabada en el navegador o subida: opus, m4a, webm, wav) y en 4–7 s responde *Likely a scam* / *Be careful* / *No clear signs of a scam*, con la razón, lo único que hay que hacer y un botón "Warn someone" (hoja de compartir del teléfono o WhatsApp). Responde en el idioma de la persona (probado en español). Cuatro ejemplos inventados (SMS de Royal Mail, llamada del "banco" en audio, oferta de trabajo, recordatorio del médico, que es legítimo).
- **Motor:** `ensayo/shield.py`. El prompt es el validado en el intento 2 (`scripts/validate_scams.py` lo importa desde ahí; mensajes idénticos, verificado por hash); el producto solo agrega `LANGUAGE_LINE`. Spark 1.3 **estándar** (datos de usuarios), fase `demo`. Costo medido: ~US$ 0,003 por consulta, ~US$ 0,004 con voz.
- **Voz:** Muse Voice Transcribe en `POST /v1/asr/transcribe` (no está en `/audio/transcriptions`): multipart con una parte `request` (JSON `{"model": "muse-voice-transcribe-1.0", "audioEncoding": "WAV"}`) y una parte `audio`. Solo acepta `WAV` (MP3, OGG_OPUS, WEBM_OPUS, FLAC, M4A dan "Malformed request"), así que ffmpeg convierte todo a WAV mono de 16 kHz (`to_wav`; en el Dockerfile). Detecta el idioma sin `languageCode`. US$ 0,18/hora, anotado en el `Ledger` (`ModelClient.transcribe`).
- **Bandas:** ≥ 0,5 *Likely a scam* (en el intento 2, 96 % de 720 eran estafas), 0,2–0,49 *Be careful* (70 % de 120), < 0,2 *No clear signs* (46 % de 105: por eso nunca dice "seguro"). `scripts/scam_bands.py` → `results/scam_bands.json`.
- **API:** `POST /api/check` (texto, nota, imágenes, audio en base64; cupo de 30 por IP y día en modo real) y `GET /api/evidence`. Los endpoints de Ensayo siguen, sin uso en el front.
- **Front:** `frontend/src/screens/Check.tsx` y `Evidence.tsx` ("How we measured it": los dos intentos con su regla, hashes, bandas y límites). Las pantallas de Ensayo quedan en el repo sin usar. Verificado en el navegador en modo real (la llamada del banco: 99 %, razón y acción correctas) y a 375 px sin scroll horizontal. Preview en modo real: `shield-real` (puerto 8041) en `.claude/launch.json`.
- **Desplegado (3-nov, OK de Mark) en https://labs.muze.cl/ensayo/ con el modo real encendido:** `/opt/ensayo/.env` (600) con `MODEL_API_KEY` y `ENSAYO_REAL=1`; `results/scam_bands.json` subido (el volumen tapa el de la imagen; cada vez que cambie, se vuelve a subir); nginx ya tenía `client_max_body_size 25m` en `/ensayo/`, no se tocó. ffmpeg 7.1 dentro del contenedor. Verificado: consulta real de texto ("hi mum", 95 %, US$ 0,0024) y la llamada del banco en audio desde el navegador (99 %). Gasto del VPS en su propio `results/costs.jsonl` (tope fase `demo`: US$ 30). Con voz, en el VPS tarda 10–20 s (local, 7 s).
- **Falta:** README en inglés (Claude Code, Arctic Shift, Apify, los dos intentos), guion del video, `site/roadmap.json`.

## Second Look: familias de estafas y agente investigador (3-nov, plan aprobado por Mark)
Relato: "la IA ya fabrica las estafas, y la IA de Meta las desarma". El veredicto **no cambia**: sigue saliendo solo del prompt validado. Lo nuevo va aparte, como pistas.
- **Qué está circulando** (`ensayo/campaigns.py`, `scripts/scam_campaigns.py`): los casos de Reddit que la comunidad llamó estafa (intentos 1 y 2, más los del 28-oct al 2-nov bajados de Arctic Shift a `data/raw/scams3` y etiquetados con el mismo etiquetador en `data/scams/labels3.json`). Spark 1.3 contributor (datos públicos, fase `campanas`, tope US$ 8):
  1. describe cada caso (canal, marca usada de cebo, pago, uso de IA, tipo y gancho sin nombres, números ni enlaces);
  2. arma ~20 familias;
  3. asigna cada caso a una.
  `results/scam_campaigns.json` trae, por familia, casos, tendencia (parte del total en los dos últimos meses completos), canales, marcas con ≥ 3 casos ("campañas") y ejemplos. Pantalla "What's going around".
- **Agente investigador** (`ensayo/investigate.py`): la Model API acepta function calling (probado) pero **no** búsqueda web (`web_search`, `web_search_options` dan 400). Spark 1.3 estándar decide qué revisar con dos herramientas nuestras:
  - `inspect_link`: sigue redirecciones sin descargar la página; solo http(s) a los puertos 80/443 y nunca a IP privadas, revisando cada salto.
  - `domain_registration`: fecha de registro y registrador por RDAP (rdap.org).
  Lee también enlaces dentro de pantallazos. Si no hay enlaces ni imágenes, no se llama. ~13 s con enlaces.
- **API:** `POST /api/investigate` (familia + agente en paralelo, cupo de 30 por IP y día) y `GET /api/campaigns`. El front lanza la investigación en paralelo con el veredicto; con nota de voz, después, con la transcripción. Lo que la gente revisa **no** se agrega a las familias.
- **Desplegado (3-nov, OK de Mark)** en https://labs.muze.cl/ensayo/: `results/scam_campaigns.json` subido aparte a `/opt/ensayo/results/` (chown 1000). Verificado en vivo: familia correcta y el agente usó las dos herramientas (9 s, US$ 0,007).
- **Bot de WhatsApp** (`ensayo/whatsapp.py`, desplegado el 3-nov con OK de Mark). Webhook `https://labs.muze.cl/ensayo/api/whatsapp`:
  - GET verifica el verify token. POST exige la firma `X-Hub-Signature-256` (App Secret).
  - Responde 200 de inmediato y revisa en segundo plano.
  - Manda dos mensajes: el veredicto validado (citando el mensaje original) y después lo que revisó el agente más la familia.
  - Acepta texto, pantallazos y notas de voz; 30 consultas por número y día; los registros solo guardan un hash del número.
  - **Funciona de punta a punta (3-nov, probado por Mark desde su WhatsApp).** `WHATSAPP_APP_SECRET` está en `/opt/ensayo/.env`. El panel tiene la Callback URL, el verify token y el campo `messages` suscrito.
- **Portada para el jurado (3-nov, desplegado con OK de Mark):**
  - Un teléfono animado (`PhoneDemo.tsx`) muestra el flujo en WhatsApp con las respuestas reales del ejemplo del paquete.
  - Las pistas del agente traen la cita exacta y la web la marca en el mensaje. El agente ahora corre también sin enlaces, si el texto tiene 40 caracteres o más.
  - Ejemplo nuevo con pantallazo de un chat de Marketplace (`frontend/example-sources/` → PNG).
- `ModelClient.chat_message` devuelve el mensaje completo (con `tool_calls`); `chat` lo usa por dentro.

## WhatsApp Cloud API (3-nov, OK de Mark)
Activo y probado con mensajes reales (el bot está descrito arriba, en "Bot de WhatsApp"):
- App **Second Look**: tipo Business, solo con el caso de uso WhatsApp y **publicada**. Pertenece al portfolio **Muze SPA Marketing**, que no está verificado.
  - App ID: `2398768447629662`
  - Business ID: `1079571729304625`
  - Política de privacidad e instrucciones para borrar datos: https://labs.muze.cl/hackaton-meta/privacy.html (fuente: `site/privacy.html`).
- Número de prueba de Meta: +1 555-165-2559. Phone Number ID: `1378053318730517`.
- Meta ahora separa la cuenta en dos:
  - **Messaging account** `2694084821039382`: maneja plantillas y pagos, y es donde va la suscripción del webhook (`/subscribed_apps`).
  - **WhatsApp account** `2492142621276501`: maneja el número.
- System User `second-look-bot` (ID `61596325586076`, rol Employee).
  - Tiene control total de la app y de las dos cuentas.
  - Su token tiene los permisos `whatsapp_business_messaging` y `whatsapp_business_management` y vence en 60 días (~2-ene-2027).
- Webhook `https://labs.muze.cl/ensayo/api/whatsapp`, con el campo `messages` suscrito.
- Valores en `.env` local y en `/opt/ensayo/.env`, nunca en el repo: `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN` y `WHATSAPP_APP_SECRET`.

Lecciones (para no perder otra hora):
- Una app sin publicar solo recibe webhooks de prueba del panel, no mensajes reales.
- Guardar el webhook en el panel **no** suscribe la app a la cuenta. Hay que hacer `POST /2694084821039382/subscribed_apps` con el token del bot. Antes de eso, la cuenta solo tenía suscrita la app interna de Meta "WA DevX Webhook Events".

Pendiente:
- El log de acceso de uvicorn guarda la URL de verificación, que lleva el verify token en claro. El riesgo es bajo, pero conviene sacar esa ruta del log o rotar el token después de la hackatón.
- Modo de prueba: solo se puede escribir a los 5 destinatarios verificados. Para un número real hace falta verificar el negocio.

## Fechas
Entrega interna: miércoles 4-nov 18:00 Chile (cierre oficial 23:00 Chile). Hash de la prueba en vivo: antes del 3-nov 23:59.
