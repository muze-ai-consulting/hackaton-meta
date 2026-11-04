# Textos para el formulario de entrega

Listos para copiar. Los textos del producto van en inglés.

**No vi el formulario ni las Official Rules:** están detrás del inicio de sesión de Cerebral Valley. Los campos reales pueden llamarse distinto o tener otros límites de largo. Para cada campo, usa la versión que más se acerque.

**Cierre oficial:** 4-nov, 21:00 ET (23:00 Chile). Nuestra entrega interna: 18:00 Chile.

## Comprobar en el formulario antes de enviar

| Qué | Por qué |
|---|---|
| ¿Piden repo público o basta con dar acceso? | El repo hoy es privado y el plan era abrirlo el 5-nov. Ninguna fuente pública lo aclara. |
| Largo máximo del video | No está confirmado. El guion dura ~2:55, por debajo de los 3 minutos que otros equipos planifican. |
| Tema | Abajo propongo "Build for Your World". `CLAUDE.md` dice "Push the Frontier", pero eso venía de la idea anterior. Decides tú. |
| Herramientas permitidas | Declaramos Claude Code para programar. Un blog que resume las reglas habla de "plataformas permitidas" para construir (Meta). El producto corre solo con modelos de Meta, pero léelo en las reglas. |
| Licencia sobre lo entregado | El mismo blog dice que los organizadores reciben una licencia perpetua e irrevocable. No lo pude confirmar. Léelo antes de aceptar. |

---

## Datos básicos

- **Project name:** Second Look
- **Track:** Startup
- **Theme:** Build for Your World
- **Team / company:** Muze AI, Chile (https://muze.cl)
- **Live demo:** https://labs.muze.cl/ensayo/
- **Repository:** https://github.com/muze-ai-consulting/hackaton-meta
- **Video:** [pegar el enlace cuando esté subido]
- **Tags:** scams, fraud, WhatsApp, agents, function calling, Muse Spark

## Tagline

**Corta (hasta 60 caracteres)**

> The agent that stops scams inside the chat.

**Larga**

> A scam lands in your WhatsApp. An agent flags it, checks it and steps in, right there in the chat.

## Short description (una frase)

> Second Look is a scam-stopping agent on Meta's models: it gives a verdict tested on 945 real cases, investigates links on its own, and prepares what to do next, on a working WhatsApp bot and in a concept of how it could work natively.

## Summary (unas 150 palabras)

> People lost US$ 15.9 billion to reported fraud in the US in 2025 (FTC), and social media was the contact method with the highest losses. Most scam checkers make you stop, copy the message and paste it into a website, which is exactly what people don't do under pressure.
>
> Second Look is an agent built on Muse Spark 1.3. Forward a text, screenshot or voice note to our WhatsApp bot and it gives a verdict, investigates links and domains with tools it chooses itself, matches the message against 20 scam families, and prepares a report, a warning to someone you trust and other next steps.
>
> Before shipping the verdict, we tested it on real Reddit cases, committing a hash of the predictions before scoring. The first attempt failed and is published. The second passed: 84% of 823 scams caught, 0.801 balanced accuracy, against 0.517 for a keyword filter.
>
> Our home page shows the next step: the same agent inside WhatsApp, as a labeled concept.

## Long description

> ### The problem
>
> Scams work because they create pressure. A parcel fee, a bank alert or a job offer asks you to act now, and that is the moment nobody opens a separate website to check. We think protection has to happen where the message arrives, and it has to do more than label it.
>
> ### What it does
>
> **Works today:** a bot on the WhatsApp Cloud API and a web check, live in production on Meta's models.
>
> 1. **Verdict.** "Likely a scam", "Be careful" or "No clear signs of a scam", with a one-line reason and the next step. It reads text and screenshots, and transcribes voice notes.
> 2. **Investigating agent.** Using function calling, Muse Spark 1.3 picks its own checks: it follows links without opening the page and looks up who registered the domain. It also points at the words in the message that give the scam away.
> 3. **"You're not the first."** The message is matched against 20 families built from 1,902 scams that people asked about on Reddit and the community confirmed.
> 4. **Response agent.** Using function calling again, the model decides what would protect this person and writes it: an alert to a trusted contact, a report to their bank or the imitated company, blocking the sender, an anonymous warning for others. Actions are simulated and labeled as such. The written report is real: the person can copy and send it. If they say they already paid, the contact alert goes out right away instead of waiting for a tap, and the report goes to their bank's fraud team.
>
> **Concept prototype (home page):** how this could work if WhatsApp offered it natively. The message arrives, the link is locked, the verdict appears in the chat, and if you try to open the link anyway, the agent alerts someone you trust. The model output is real and live. The phone and its actions are simulated, and the page says so.
>
> **Early warning (simulation):** a replay of real public reports, day by day, that shows how a network could flag a campaign and warn people first. It flagged 15 campaigns from 478 reports naming a brand, with 34 later reports after the flag. The threshold was chosen on the same data, so this is an illustration and not a test. That network doesn't exist yet.
>
> ### Why you can trust the number
>
> We wanted a scam checker we could prove. On Reddit, people post what they received and ask whether it's a scam, and the community answers in the replies. Second Look sees only the post, never the replies. We used only posts from after Muse Spark 1.3 came out, wrote the pass rule first, and committed the SHA-256 of all predictions before scoring.
>
> - **Attempt 1 (1,137 cases): did not pass.** Balanced accuracy 0.787 against a required 0.80. It is published.
> - **Attempt 2 (945 new cases): passed.** Balanced accuracy 0.801 (95% CI 0.759 to 0.839). It caught 84% of scams, with false alarms on 23.8% of genuine cases. A keyword filter scored 0.517.
> - When it says "Likely a scam", 96% of 720 cases were scams.
>
> The limits are stated too. The 0.80 bar sits inside the confidence interval, so we claim about 8 in 10. The answer key is a Reddit community, not fraud investigators. About 1 in 4 genuine cases gets a false alarm. Voice notes were not part of the test.
>
> ### Production
>
> It runs live in Docker behind nginx, in real mode, at about US$ 0.02 per check. Every model call goes through a ledger with spending caps per phase, with daily quotas per IP and per WhatsApp number. User messages are not stored on disk, WhatsApp logs keep only a hash of the number, and user data only goes through the standard Model API endpoint, never the contributor one. The webhook checks signatures, and the link tool only allows http(s) on ports 80 and 443 and rejects private addresses at every redirect.
>
> ### What we haven't solved
>
> WhatsApp chats are end-to-end encrypted, so a server can't read them. A native version would have to be opt-in and keep that promise, for example by running the first check on the device. We haven't built or tested that. The bot also runs on the Cloud API test number, so only verified recipients can message it for now.

## How we used Meta's models

> - **Muse Spark 1.3 (standard):** the verdict, including screenshots; both agents, through function calling with our own tools; and family matching. All user data goes through this endpoint.
> - **Muse Spark 1.3 contributor:** public data only. It labeled Reddit threads, ran the preregistered tests and built the scam families.
> - **Muse Voice Transcribe 1.0:** voice notes and recorded calls.
> - **WhatsApp Cloud API:** the bot, with reply buttons for the actions the agent prepares.
>
> The product runs only on Meta's models.

## Challenges

> Our first idea failed. Ensayo used synthetic audiences to predict which ad would win, and in its backtest it beat neither chance nor a single prompt. We pivoted and kept the code and the result in the repo.
>
> Second Look's first test then failed too, at 0.787 against a 0.80 bar. It asked whether the post was deceptive, when the community answers whether what the person ran into was a scam. We fixed the question, wrote the rule again and ran it on new posts, without touching the first attempt's data.
>
> The Model API has function calling but no web search, so we built the agent's tools ourselves and had to make following a scammer's link safe.

## What's next

> - Make the actions real, with consent: alerts to a trusted contact and direct reports to banks and platforms.
> - Solve the privacy design for a native, opt-in version that keeps end-to-end encryption.
> - Build the opt-in network from forwards, sharing only anonymous descriptions of each scam.
> - Publish a weekly scoreboard: score new cases, commit the hash first, and publish even the bad weeks.
> - Complete business verification with Meta, so anyone can message the WhatsApp number.

## Tools and data we declare

> Built with Claude Code (Anthropic) as the coding assistant. Reddit posts come from the Arctic Shift public archive and, for the first pilot, an Apify scraper. The earlier ad idea used Meta Ad Library data via Apify. Fraud figures: FTC Consumer Sentinel 2025.

## Si piden instrucciones para el jurado

> Open https://labs.muze.cl/ensayo/ and pick a scenario, or write your own message. The phone is a concept prototype; the verdict, checks and agent output are live. For a scam that already got someone, use "Check a message" and tell it you already paid. The WhatsApp bot runs on a test number that only reaches verified recipients, so the video shows it working. Real mode has a daily quota per visitor.
