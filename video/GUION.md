# Guion del video: Second Look (2:45, máximo 3:00)

## De dónde sale esta estructura

No encontré transcripciones publicadas de videos ganadores. Lo que sí hay coincide entre fuentes:

- **El juez decide en la primera frase.** En eventos grandes, el video suele ser lo único que ve el jurado. Los equipos que abren con contexto de mercado o con una historia personal pierden al juez antes de mostrar el producto (Kurbaitaev, notas de un año como juez; Ray Deck, cinco hackatones ganadas; ambas en `reports/Hackatón de Meta qué buscan jueces.md`).
- **Mostrar el producto funcionando, no diapositivas.** Que se entienda en menos de 30 s y que el momento wow llegue en el primer minuto (HackerEarth; reskilll, "pitch in 3 minutes").
- **Un usuario concreto y una cifra de impacto con fuente.** Así lo hizo CrossBeam, ganador del Built with Opus 4.6: "más del 90 % de los permisos reciben correcciones", "de semanas a 15 minutos por ~US$3".
- **Uso visible de la tecnología del patrocinador.** Las rúbricas lo puntúan como criterio propio: más allá de "una integración básica".
- **Debe funcionar sin audio.** Los jueces ven muchos videos seguidos, a veces en silencio, así que los textos en pantalla cuentan la historia solos.

Estructura: **gancho con el producto (0–15 s) → problema con cifra → demo del agente → evidencia → negocio → cierre.**

---

## Antes de grabar (checklist)

1. **Confirmar que el bot de WhatsApp responde**: reenviar un mensaje al +1 555-165-2559 y recibir las 2 respuestas. Si no responde, la toma 1 se graba en la web, con el teléfono animado de la portada.
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

### 2 · El problema, con cifra (0:15–0:30)
| Imagen | En pantalla | Voz |
|---|---|---|
| Fondo simple con la cifra grande, o la pantalla "What's going around" haciendo scroll. | **$15.9B lost to scams in 2025 (US, FTC)** · **Social media: the costliest way scams reach people** | "Americans alone reported losing nearly sixteen billion dollars to scams last year, and social media was where the losses were biggest. Most people face these alone, inside a chat, in the moment." |

### 3 · El agente investiga (0:30–1:05) — el momento wow
| Imagen | En pantalla | Voz |
|---|---|---|
| Teléfono: llega el **segundo mensaje** de Second Look: "🔎 What I checked", con el enlace seguido, el dominio sin registro, que imita a Royal Mail y "👥 Seen before: Delivery Fee Texts · 39 people reported this". | **An agent on Muse Spark 1.3 picks its own tools** | "Then an agent built on Muse Spark 1.3 investigates. It decides which tools to use: it follows the link without opening the page, and looks up who registered the domain. Here, the domain doesn't even exist, and it imitates Royal Mail." |
| Reenviar la **nota de voz** del "banco". Aparece el veredicto con "I heard: …". | **Voice notes → Muse Voice Transcribe** | "Scam calls and voice notes work too: Muse Voice Transcribe turns them into text first." |
| Web: botón de ejemplo **"Marketplace buyer"** (pantallazo) → resultado → "What we checked" muestra que leyó el enlace **dentro de la imagen** y lo revisó. | **It reads links inside screenshots** | "Screenshots too: it found the payment link inside this Marketplace chat and checked it." |
| Web: ejemplo **"Remote job offer"** → el mensaje con frases subrayadas en rojo y numeradas. | **Every red flag, pointed out in the message** | "And it points at the exact words that give it away." |

### 4 · No eres el primero (1:05–1:25)
| Imagen | En pantalla | Voz |
|---|---|---|
| "What's going around": scroll por las familias. Detenerse en **Fake Jobs and Tasks · Rising 35%**. | **1,902 confirmed scams · 20 families · since Sept 2026** | "We grouped nearly two thousand scams that people asked about on Reddit, and that the community confirmed, into twenty families. So Second Look can tell you: you're not the first, and here's how this one works. Fake job offers grew 35% in October." |

### 5 · Por qué creerle (1:25–2:05) — lo que nadie más tiene
| Imagen | En pantalla | Voz |
|---|---|---|
| "How we measured it": tabla del intento 2 y la regla con ✓. | **Rule written before any result · 945 real cases posted after the model's release** | "We didn't want another AI that just sounds confident. We wrote the pass rule before seeing a single result, and tested on 945 real 'is this a scam?' posts published after the model came out, so it couldn't have memorized them." |
| Zoom a la fila de Second Look frente al filtro de palabras clave. | **Catches 84% of scams · keyword filter: 48%** | "It agrees with the community eight times out of ten and catches 84% of scams. A keyword filter catches 48." |
| Zoom al hash SHA-256 y a la tarjeta "Attempt 1 · Did not pass". | **Predictions hashed before scoring · the failed attempt is published too** | "We published the hash of every prediction before scoring, and we published the attempt that failed." |
| Tabla de bandas. | **"Likely a scam" → 96% were scams** | "When it says 'likely a scam', it was right 96% of the time. And it never says 'safe'." |

### 6 · Negocio y stack (2:05–2:30) — track Startup
| Imagen | En pantalla | Voz |
|---|---|---|
| Diagrama simple o lista: WhatsApp Cloud API → Muse Voice Transcribe → Muse Spark 1.3 (veredicto) + agente con function calling → familias (Spark 1.3, datos públicos). | **About 1 cent per check, agent included** | "A check costs about one cent, agent included. Banks, telcos and insurers already pay for fraud. They can offer Second Look to their customers inside WhatsApp, where scams actually arrive." |

### 7 · Cierre (2:30–2:45)
| Imagen | En pantalla | Voz |
|---|---|---|
| Volver al teléfono: la conversación completa. Logo de Second Look. | **Second Look · Forward it before you act.** · labs.muze.cl/ensayo · github.com/muze-ai-consulting/hackaton-meta | "Second Look. Forward it before you act." |

---

## Lo que no hay que decir (no está respaldado)

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
| ~1 centavo por consulta | `results/costs.jsonl` (veredicto US$ 0,003–0,009 + agente ~US$ 0,007) |
