# Ensayo: probar el anuncio antes de pagarlo

Versión visual de este plan: https://claude.ai/artifact/QLNs68p9s2JJEpou72BfH3

| | |
|---|---|
| Evento | Meta Global AI Developer Hackathon 2026 |
| Entrega | Miércoles 4-nov, 18:00 Chile (cierre oficial 21:00 ET = 23:00 Chile) |
| Track y tema | Startup · Push the Frontier |
| Premios | US$1.000.000 entre los tracks Indie y Startup |
| Jurado | 4 al 8-nov; ceremonia de cierre el 9-nov |

## Qué vamos a construir

El anunciante sube la foto de su producto. Ensayo genera las variantes del anuncio, las muestra a mil personas sintéticas en un feed simulado y devuelve un ranking con la razón de cada lugar. Solo las ganadoras salen a pauta.

1. **Genera:** Muse Image crea unas 20 variantes del anuncio a partir de la foto del producto.
2. **Simula:** mil personas sintéticas, con la edad, el género y el país del público objetivo, ven cada variante con Muse Spark 1.3.
3. **Ordena:** ranking de variantes con la explicación de por qué gana la primera y qué segmento reacciona a cada una.
4. **Lanza:** solo las variantes ganadoras van a pauta.

## Por qué Meta lo elegiría

- **Habla el idioma del patrocinador.** A YC, que invierte, le hablan los inversionistas sintéticos. Meta vive de la publicidad y su plan reportado es que la IA arme campañas completas a partir de una foto y un presupuesto. Ensayo resuelve la pieza que falta: saber si el creativo funciona antes de gastar.
- **Pone el stack de 2026 en el centro.** Muse Image genera, Muse Spark 1.3 simula y razona, Voice Transcribe lee el audio de los anuncios en video.
- **El jurado puede comprobarlo.** Publicamos los pronósticos con un hash antes de entregar; durante la evaluación cualquier juez puede consultar la Ad Library y ver si acertamos.

Que Meta quiera audiencias sintéticas es inferencia nuestra. El jurado probablemente es gente de la Model API: el pitch tiene que lucir el stack tanto como el negocio.

## Cómo probamos que funciona

- **Backtest con datos de Meta:** anuncios comerciales entregados en la UE con inicio después del 2-sep (lanzamiento de Spark 1.3). Comparación dentro de cada marca: entre sus variantes de la misma semana, cuál se llevó más alcance en la UE (`eu_total_reach`) y cuál siguió activa más tiempo.
- **Prueba en vivo:** ranking de anuncios lanzados entre el 27-oct y el 1-nov; hash publicado el 3-nov; se resuelve entre el 4 y el 8-nov volviendo a consultar alcance y estado.
- **Rivales a batir:** el azar y una sola llamada a Spark 1.3 sin población.

Para anuncios comerciales la Ad Library no entrega gasto ni impresiones. Sí entrega, en la UE: alcance estimado, desglose por edad, país y género, segmentación y fechas.

## Arquitectura

| Capa | Qué hace | Tecnología |
|---|---|---|
| Ingesta | Anuncios de la UE, alcance y segmentación; creativo renderizado de a un anuncio | Ad Library API (`ads_archive`, `ad_snapshot_url`) |
| Variantes | Unas 20 variantes desde la foto del producto | Muse Image |
| Población | Mil personas ponderadas por la segmentación declarada y el alcance de anuncios anteriores de la marca | Motor propio, semillas fijas y caché |
| Feed simulado | Cada persona ve las variantes en cuatro órdenes distintos y reacciona | Muse Spark 1.3 con imagen y video |
| Audio | Transcripción de la locución de anuncios en video | Muse Voice Transcribe |
| Ranking | Orden de variantes, explicación y segmentos que reaccionan | Muse Spark 1.3, salida estructurada |
| Despliegue | Web en vivo con health check; costo y latencia por corrida | Docker en el VPS de Muze |

## Roadmap día a día

| Día | Fecha | Entregable | Corte |
|---|---|---|---|
| 0 | Mar 27-oct | Mark verifica identidad en facebook.com/ID y crea la app de desarrollador. Aceptación y track confirmados. Key de la Model API activa. Spark 1.3 probado con una imagen y un video. Lista de 30 a 50 anunciantes de la UE con muchas variantes simultáneas. | Si Spark 1.3 no acepta imagen por la API: escalar a Discord y evaluar un modelo de pesos abiertos de Meta con visión. |
| 1 | Mié 28-oct | Con acceso: primeras consultas a `ads_archive`, filtro de activos y límite real de llamadas, lotes armados y etiquetas selladas. Sin acceso: motor de población y 10 a 15 lotes registrados a mano desde la web de la Ad Library. | Si el jueves a mediodía no hay acceso ni set manual usable: plan B. |
| 2 | Jue 29-oct | **Punto de decisión.** Corrida sobre el set de calibración contra el azar y la llamada única. | Si la población no le gana a la llamada única: un rediseño con plazo al viernes a mediodía; si sigue sin ganar, pivote a crowdfunding o Parche. |
| 3 | Vie 30-oct | Corrida única sobre el set sellado, métricas congeladas. Seguimiento diario de anunciantes para capturar lotes del 27-oct al 1-nov. | No se toca el modelo después de abrir el set sellado. |
| 4 | Sáb 31-oct | Interfaz: subida de foto, grilla de variantes, feed simulado con mil puntos, tablero con explicación, vista de evidencia. | Flujo completo en menos de 3 minutos. |
| 5 | Dom 1-nov | Despliegue en el VPS con health check, costo y latencia, Voice Transcribe en anuncios de video. Extras solo si todo está en verde. | Si algo opcional falla, se saca. |
| 6 | Lun 2-nov | Captura final de lotes en vivo. Dos o tres pymes o agencias prueban Ensayo con autorización grabada. Manejo de errores y README. | Sin usuarios reales: productos propios de Muze, dicho con honestidad. |
| 7 | Mar 3-nov | Rankings de la prueba en vivo y hash SHA-256 en un commit público. Guía de verificación para el jurado. Video de 3 minutos. | Hash publicado antes de las 23:59. |
| 8 | Mié 4-nov | **Entrega a más tardar a las 18:00 de Chile.** | Se envía aunque falte pulido. |

## Lo que Mark hace hoy

- [ ] Confirmar el correo de aceptación y el track asignado (las postulaciones cerraron el 25-oct).
- [ ] Verificar identidad y ubicación en facebook.com/ID con documento oficial.
- [ ] Crear la app de desarrollador de Meta y generar el token.
- [ ] Activar la key de la Meta Model API desde Chile.

## Costo estimado

Estimación propia con las tarifas publicadas de Meta y un supuesto de 1.500 tokens por imagen (se mide el día 0).

| | Tarifa estándar | Tarifa contributor |
|---|---|---|
| Un test de demo | ~US$9,30 | ~US$0,50 |
| Backtest completo (150 lotes × 200 personas) | ~US$130 | ~US$5 |

En la tarifa contributor Meta usa los datos para mejorar sus productos: solo para datos públicos.

## Riesgos y qué falta verificar

- Si Muse Spark 1.3 acepta imagen y video por la API, y cuántos tokens consume.
- Cuánto tarda Meta en aprobar el acceso a la Ad Library API.
- Si los términos permiten abrir `ad_snapshot_url` desde un script (no hay descarga en lote).
- Cada cuánto se actualiza `eu_total_reach`; si se demora, la prueba en vivo podría no resolverse a tiempo.
- El límite real de llamadas (los 200 por hora vienen de una fuente de terceros).
- Las reglas oficiales: duración del video, código preexistente, propiedad intelectual.

## Plan B

Si la Ad Library no da acceso o la población no le gana a la llamada única: Ensayo sobre campañas de crowdfunding (`reports/Hackatón de Meta ideas en grande v1 crowdfunding.md`) o Parche, un enjambre de agentes de Muse Code que mantiene vivas las integraciones de API.

## Fuentes

- [Meta Global AI Developer Hackathon](https://dev.meta.ai/events/global-hackathon)
- [Ad Library API: campos de ArchivedAd](https://developers.facebook.com/docs/graph-api/reference/archived-ad/)
- [Meta Model API: modelos y precios](https://dev.meta.ai/products/meta-model-api/)
- [Simile, Serie B de US$200M (TechCrunch)](https://techcrunch.com/?p=3148353)
