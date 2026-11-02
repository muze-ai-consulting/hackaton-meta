# Estado del proyecto: traspaso al 1-nov-2026 (actualizado: Muse Image, chat con personas, diseño estilo Zenith y demo desplegado)

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
- `ensayo/api.py` + `web/`: demo (FastAPI + HTML/CSS/JS sin build). Pestañas "Ensayar anuncios" y "Prueba del modelo". Modo real solo con `ENSAYO_REAL=1` (Spark estándar, fase `demo`, máx. 300 personas). Preview: `.claude/launch.json` → `ensayo` (puerto 8040).
- `ensayo/images.py` + `POST /api/variants`: variantes con Muse Image. Una llamada a Spark escribe un ángulo por variante (título, texto, prompt de imagen; ve la foto del producto si la hay) y `muse-image-1.0` genera una imagen por variante (`ModelClient.image`, US$0,01 cada una, pasa por el `Ledger`). En el demo, el bloque "Generar variantes con Muse Image" llena el formulario. Modo falso: degradado PNG de relleno sin red, costo hipotético en `results/costs_mock.jsonl` (~US$0,03 por 3 variantes). Supuestos sin verificar hasta la sonda: que `/images/generations` acepte `size` y devuelva `b64_json` o `url` (se manejan los dos), y que no haya edición desde foto (por eso la foto pasa por Spark y no por Muse Image).
- `ensayo/chat.py` + `POST /api/chat`: conversar con una persona de la audiencia. Cada tarjeta de "Algunas personas" tiene "Conversar": la persona responde en primera persona con su descripción, los anuncios (mismas letras del demo, con imagen) y su reacción como contexto, y puede discutir. Una llamada a Spark por pregunta (fase `demo`); el historial lo manda el navegador (máx. 10 mensajes). Modo falso con respuesta de relleno.
- Diseño del demo basado en zenith.chat: fondo `#ebedf1`, Inter, tarjetas blancas translúcidas con sombra, botón primario `#353536`, acento cian → violeta → verde, portada con los cuatro pasos. Verificado en escritorio y a 375 px.
- `scripts/probe_model_api.py` (sonda del día 0) y `scripts/eu_advertisers.py` (descarga y ranking de anunciantes), ambos sin correr: faltan credenciales.
- 31 pruebas: `uv run --group dev pytest -q`.

## Bloqueado en Mark
1. Verificación de identidad en facebook.com/ID, app de desarrollador y token de la Ad Library (`META_ACCESS_TOKEN` en `.env`).
2. Key de la Model API (`MODEL_API_KEY` en `.env`) y confirmar que los 150 créditos son US$ y valen en el contributor.
3. Leer las Official Rules y preguntar en el Discord: herramientas de IA para programar, modelos que no son de Meta, código previo (no hay; el repo parte el 27-oct).
4. ~~OK para desplegar el demo~~ dado y desplegado el 1-nov: https://labs.muze.cl/ensayo/ (solo modo prueba). Falta el OK para encender el modo real en el VPS cuando haya key.
5. Ruta sin datos: si el token no llega el lunes 2-nov al mediodía, se entrega como protocolo preregistrado + motor reproducible + demo, sin métrica de precisión.

## Pendiente (en orden sugerido)
1. ~~Variantes con Muse Image~~ hecho (1-nov). Con la key: probarlo una vez en real con `ENSAYO_REAL=1`.
2. ~~Despliegue del demo~~ hecho (1-nov): https://labs.muze.cl/ensayo/. Detalles y comando de redespliegue en `CLAUDE.md` § Deployment.
3. **Con la key:** `probe_model_api.py` → actualizar `IMAGE_TOKENS` en `simulate.py` y precios/caché medidos → piloto de 1 lote con 200 personas.
4. **Con el token:** `eu_advertisers.py` → `python -m ensayo.batches` → commit de `results/sealed_labels.sha256` → calibración en dev (pesos de edad, puntaje) → corrida sellada → hash de rankings en commit antes del 3-nov 23:59.
5. **README** con la declaración de Claude Code, el protocolo y cómo correr todo. Video y formulario de entrega (Mark los envía).
6. Actualizar `site/roadmap.json` (editar con reemplazo de texto, no con `json.dump`) y publicar con el rsync del CLAUDE.md.

## Fechas
Entrega interna: miércoles 4-nov 18:00 Chile (cierre oficial 23:00 Chile). Hash de la prueba en vivo: antes del 3-nov 23:59.
