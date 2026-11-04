# Guion del video: Second Look (2:55, máximo 3:00)

## De dónde sale esta estructura

No encontré transcripciones publicadas de videos ganadores. Lo que sí hay coincide entre fuentes:

- **El juez decide en la primera frase.** En eventos grandes, el video suele ser lo único que ve el jurado. Los equipos que abren con contexto de mercado o con una historia personal pierden al juez antes de mostrar el producto (Kurbaitaev, notas de un año como juez; Ray Deck, cinco hackatones ganadas; ambas en `reports/Hackatón de Meta qué buscan jueces.md`).
- **Mostrar el producto funcionando, no diapositivas.** Que se entienda en menos de 30 s y que el momento wow llegue en el primer minuto (HackerEarth; reskilll, "pitch in 3 minutes").
- **Un usuario concreto y una cifra de impacto con fuente.** Así lo hizo CrossBeam, ganador del Built with Opus 4.6: "más del 90 % de los permisos reciben correcciones", "de semanas a 15 minutos por ~US$3".
- **Uso visible de la tecnología del patrocinador.** Las rúbricas lo puntúan como criterio propio: más allá de "una integración básica".
- **Debe funcionar sin audio.** Los jueces ven muchos videos seguidos, a veces en silencio, así que los textos en pantalla cuentan la historia solos.

Estructura: **gancho con el producto (0–15 s) → problema con cifra → demo del agente → el agente actúa → red → evidencia → negocio → cierre.**

---

## Antes de grabar (checklist)

1. **Confirmar que el bot de WhatsApp responde**: reenviar un mensaje al +1 555-165-2559, recibir las 3 respuestas y tocar un botón de acción. Si no responde, la toma 1 se graba en la web, con el teléfono animado de la portada.
2. Teléfono en "No molestar", con batería y hora limpias; en lo posible, idioma del teléfono en inglés.
3. Tener listos para reenviar, desde otro chat (por ejemplo, un chat contigo mismo):
   - el SMS de Royal Mail (texto del ejemplo "Parcel fee text");
   - la nota de voz `frontend/public/static/examples/bank-call.wav`, enviada como audio;
   - el pantallazo `frontend/public/static/examples/marketplace-chat.png`.
4. **Probar cada toma una vez antes de grabarla.** El modelo puede variar: si una respuesta sale rara, repetir.
5. Pantalla del computador a 1920×1080 y zoom del navegador al 125 %, para que se lea en un celular.
6. Grabación: teléfono con la grabación de pantalla de iOS o Android; web con QuickTime u OBS. Se edita en CapCut o iMovie.

**Voz:** en inglés, idealmente la tuya, con calma. Si prefieres no grabar voz, los textos en pantalla (columna "En pantalla") cuentan todo y se agrega música suave.

---

## Guion

### 1 · Gancho (0:00–0:15) — producto primero
| Imagen | En pantalla | Voz (inglés) |
|---|---|---|
| Teléfono en WhatsApp. Llega el SMS de Royal Mail: "unpaid shipping fee of £1.45". Mantener presionado → **Reenviar** → **Second Look**. | — | "You get this text. It looks real. Before you tap anything…" |
| A los 4–6 s aparece: **🔴 Likely a scam · 99%**, el porqué y qué hacer. | **Forward it. Get a second look.** | "…forward it to Second Look on WhatsApp. Seconds later, you know." |

### 2 · El problema, con cifra (0:15–0:27)
| Imagen | En pantalla | Voz |
|---|---|---|
| Fondo simple con la cifra grande, o la pantalla "What's going around" haciendo scroll. | **$15.9B lost to scams in 2025 (US, FTC)** · **Social media: the costliest way scams reach people** | "Americans alone reported losing nearly sixteen billion dollars to scams last year, and social media was where the losses were biggest. Most people face these alone, inside a chat, in the moment." |

### 3 · El agente investiga (0:27–0:55) — el momento wow
| Imagen | En pantalla | Voz |
|---|---|---|
| Teléfono: llega el **segundo mensaje** de Second Look: "🔎 What I checked", con el enlace seguido, el dominio sin registro, que imita a Royal Mail y "👥 Seen before: Delivery Fee Texts · 39 people reported this". | **An agent on Muse Spark 1.3 picks its own tools** | "Then an agent built on Muse Spark 1.3 investigates. It decides which tools to use: it follows the link without opening the page, and looks up who registered the domain. Here, the domain doesn't even exist, and it imitates Royal Mail." |
| Reenviar la **nota de voz** del "banco". Aparece el veredicto con "I heard: …". | **Voice notes → Muse Voice Transcribe** | "Scam calls and voice notes work too: Muse Voice Transcribe turns them into text first." |
| Web: botón de ejemplo **"Marketplace buyer"** (pantallazo) → resultado → "What we checked" muestra que leyó el enlace **dentro de la imagen** y lo revisó. | **It reads links inside screenshots** | "Screenshots too: it found the payment link inside this Marketplace chat and checked it." |
| Web: ejemplo **"Remote job offer"** → el mensaje con frases subrayadas en rojo y numeradas. | **Every red flag, pointed out in the message** | "And it points at the exact words that give it away." |

### 3b · El agente actúa, con tu aprobación (0:55–1:15) — **simulado, y se dice**
| Imagen | En pantalla | Voz |
|---|---|---|
| Teléfono: llega el **tercer mensaje** con botones. Tocar **Alert Ana**: aparece la respuesta "Simulated: Ana would get this". El agente decide qué ofrece y a veces no ofrece esa acción con el mensaje del paquete; para esta toma, reenviar el texto del ejemplo "Already paid" junto con su nota. | **It prepares what to do. You approve. · Demo: simulated, nothing is sent** | "Then a second agent prepares what to do next: alert someone you trust, write the report, warn others. You approve each step. In this demo the actions are simulated." |
| Web: ejemplo **"Already paid"** → tarjeta "What the agent prepared": el informe va al equipo de fraude del banco. Botón **Copy report**. | **Already paid? It writes to your bank's fraud team** | "If you already paid, it changes its plan and writes to your bank's fraud team. That report is real. You copy it and send it." |

### 4 · No eres el primero (1:15–1:27)
| Imagen | En pantalla | Voz |
|---|---|---|
| "What's going around": scroll por las familias. Detenerse en **Fake Jobs and Tasks · Rising 35%**. | **1,902 confirmed scams · 20 families · since Sept 2026** | "We grouped nearly two thousand confirmed scams from Reddit into twenty families. So Second Look can tell you: you're not the first, and here's how this one works." |

### 4b · Alerta temprana (1:27–1:42) — **simulación, y se dice**
| Imagen | En pantalla | Voz |
|---|---|---|
| Pantalla **Early warning**, campaña "Fake Apple messages": la repetición avanza, aparece **Campaign flagged** y las filas siguientes se ponen verdes. Se ve el aviso a la derecha. | **Simulation: real public reports, replayed by date. No alerts were sent.** | "Here's where this goes. We replayed real reports by date. After three reports about Apple, a network could flag the campaign, and the next eleven people could have been warned first. It's a simulation today: the network is what we build next." |

### 5 · Por qué creerle (1:42–2:15) — lo que nadie más tiene
| Imagen | En pantalla | Voz |
|---|---|---|
| "How we measured it": tabla del intento 2 y la regla con ✓. | **Rule written before any result · 945 real cases posted after the model's release** | "We didn't want another AI that just sounds confident. We wrote the pass rule before seeing a single result, and tested on 945 real 'is this a scam?' posts published after the model came out, so it couldn't have memorized them." |
| Zoom a la fila de Second Look frente al filtro de palabras clave. | **Catches 84% of scams · keyword filter: 48%** | "It agrees with the community eight times out of ten and catches 84% of scams. A keyword filter catches 48." |
| Zoom al hash SHA-256 y a la tarjeta "Attempt 1 · Did not pass". | **Predictions hashed before scoring · the failed attempt is published too** | "We published the hash of every prediction before scoring, and we published the attempt that failed." |
| Tabla de bandas. | **"Likely a scam" → 96% were scams** | "When it says 'likely a scam', it was right 96% of the time. And it never says 'safe'." |

### 6 · Negocio y stack (2:15–2:42) — track Startup
| Imagen | En pantalla | Voz |
|---|---|---|
| Diagrama simple o lista: WhatsApp Cloud API → Muse Voice Transcribe → Muse Spark 1.3 (veredicto) + agente con function calling → familias (Spark 1.3, datos públicos). | **About 2 cents per check, agents included** | "A check costs about two cents, agents included. Banks, telcos and insurers already pay for fraud. They can offer Second Look inside WhatsApp, where scams arrive. Next: real alerts with consent, and a public scoreboard every week." |

### 7 · Cierre (2:42–2:55)
| Imagen | En pantalla | Voz |
|---|---|---|
| Volver al teléfono: la conversación completa. Logo de Second Look. | **Second Look · Forward it before you act.** · labs.muze.cl/ensayo · github.com/muze-ai-consulting/hackaton-meta | "Second Look. Forward it before you act." |

---

## Lo que no hay que decir (no está respaldado)

- **Que las acciones o la red ya funcionan de verdad.** Las alertas, el bloqueo y la red son simulados, y se dice en voz y en pantalla. Lo real: el agente las elige y las redacta con Muse Spark, y el informe sirve para copiar y enviar.
- **"Habríamos protegido a N personas."** La repetición es una ilustración: el umbral se eligió mirando estos datos. Se dice "could have been warned".
- **"La IA fabrica las estafas."** En nuestros datos, solo 46 de 1.902 casos (2,4 %) dicen que se usó IA.
- **"Seguro" o "safe."** La banda baja dice "no clear signs".
- **Que está disponible en WhatsApp para cualquiera.** Corre en el número de prueba de la Cloud API (5 destinatarios verificados). Si alguien pregunta: "running on the WhatsApp Cloud API; opening it publicly needs Meta's business verification".
- **"Detecta 8 de cada 10 estafas."** Es *coincide con la comunidad* 8 de cada 10 veces (exactitud balanceada 0,80) y *detecta el 84 %*.
- **Un tiempo de respuesta de Reddit como gancho.** La comunidad responde en una mediana de 7,4 minutos, así que no sirve.

## Fuentes de las cifras

| Cifra | Fuente |
|---|---|
| US$15,9 mil millones perdidos en estafas en 2025; redes sociales como el canal de contacto con más pérdidas (más de US$2 mil millones) | FTC, Consumer Sentinel 2025, vía [Spokesman-Review](https://www.spokesman.com/stories/2026/apr/03/americans-lost-a-record-159-billion-to-scams-in-20) y [Techwalla](https://www.techwalla.com/13779374/ftc-social-media-scams-2025-21-billion-in-us-losses) |
| 945 casos, 0,801, 84 %, palabras clave 48 %, 96 % en "Likely a scam" | `results/scam_scored2.json`, `results/scam_bands.json` |
| 1.902 casos, 20 familias, trabajos falsos +35 % | `results/scam_campaigns.json` |
| ~2 centavos por consulta | `results/costs.jsonl` (veredicto, investigación, familia y acciones) |
| Alerta temprana: 15 campañas, 34 reportes posteriores, Apple 11 de 14 | `results/scam_network.json` |
