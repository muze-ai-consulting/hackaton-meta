# Second Look

**A scam lands in your WhatsApp. An agent flags it, checks it and steps in, right there in the chat.**

Second Look is a scam-stopping agent built on Meta's models. The home page is a **concept prototype** of how it could work inside WhatsApp: the message arrives, its link is locked, the verdict appears in the chat, and if you try to open the link anyway the agent alerts someone you trust. The verdict, checks and agent's choices are real model output; the phone and its actions are simulated, and Second Look is not a WhatsApp feature.

**What works today:** a bot on the WhatsApp Cloud API (forward the text, screenshot or voice note) and a web check. Every answer comes in layers:

1. **A verdict that was measured before it was shipped.** It is "Likely a scam", "Be careful" or "No clear signs of a scam", with a one-line reason and the next step. The prompt is the one that passed a preregistered test on 945 real cases.
2. **An agent that investigates.** Muse Spark 1.3 with function calling chooses its own checks: it follows links without opening the page and looks up who registered the domain (RDAP). It reads links inside screenshots and points at the exact words in the message that give the scam away.
3. **"You're not the first."** The message is matched against 20 families built from 1,902 scams that people asked about on Reddit and that the community confirmed. For example: "Delivery Fee Texts: 39 people reported this since September, rising."
4. **An agent that prepares what to do next.** Function calling again: it decides whether to alert a trusted contact, write a report to the bank or the imitated company, block the sender and warn others. If the person says they already paid, the report goes to their bank's fraud team. Every action waits for approval, except alerting the trusted contact when the person already paid or shared their details. **In this demo the actions are simulated and labeled as such: nothing is sent, blocked or published.** The written report is real: the person copies it and sends it themselves.

And one screen shows where this goes: **Early warning**, a simulation that replays real public reports day by day, as if they had reached Second Look, to show how a network would flag a campaign and warn people first. That network doesn't exist yet.

- **Live demo:** https://labs.muze.cl/ensayo/ (real mode; capped per visitor)
- **WhatsApp:** runs on the WhatsApp Cloud API test number, so only verified recipients can message it. The video shows it.
- **Track:** Startup · Meta Global AI Developer Hackathon 2026 · built by [Muze AI](https://muze.cl) (Chile)

## Why trust it: the test

We wanted a scam checker we could prove, not one that only sounds confident. On Reddit (r/Scams, r/isthisascam, r/IsThisAScamIndia, r/ScamCenter, r/scamsUK), people post a message, screenshot or call and ask "is this a scam?", and the community answers in the replies. We used that as ground truth.

- **No memorization.** Only posts published **after 3 September 2026**, when Muse Spark 1.3 was released.
- **Separate answer key.** The label is the community's verdict, extracted from the replies only. Unclear threads were dropped. Second Look sees only the post (title, text, up to 3 screenshots), never the replies.
- **Rule written first.** Pass = balanced accuracy ≥ 0.80, beats a keyword filter by ≥ 0.10 with the 95% interval above zero, false alarms on genuine cases ≤ 30%, and at least 30 genuine cases.
- **Preregistered.** The SHA-256 of all predictions was committed **before** scoring.
- **Two baselines.** A keyword filter and "always say scam".

| | Attempt 1 (2 Nov) | Attempt 2 (3 Nov) |
|---|---|---|
| Cases (scam / genuine) | 1,137 (968 / 169) | 945 (823 / 122) |
| Balanced accuracy | 0.787: **did not pass** | **0.801** (95% CI 0.759–0.839): **passed** |
| Scams caught | 78.6% | **84.0%** |
| False alarms on genuine cases | 21.3% | 23.8% |
| Keyword filter, balanced accuracy | 0.505 | 0.517 (catches 48.5% of scams) |
| Predictions hash | `1665740b…d898`, commit `4de2c5f` | `38b435bb…b2c`, commit `be7ec95` |

**What happened between the attempts.** Attempt 1 asked whether the *post* was deceptive, when the community answers whether *what the person ran into* was a scam. We fixed the question, wrote the rule again and ran it on **new** posts, without touching attempt 1's data. Both attempts are published, including the one that failed.

**What each answer means (attempt 2):**

| Answer | Share that were scams |
|---|---|
| "Likely a scam" (≥ 50%) | 96% of 720 |
| "Be careful" (20–49%) | 70% of 120 |
| "No clear signs" (< 20%) | 46% of 105 |

The lowest band never says "safe". People post when something already worries them, so even there about half were scams.

**Limits.** 0.80 sits inside the confidence interval, so we claim "about 8 in 10", not more. The answer key is a Reddit community, not fraud investigators, and the posts are mostly English, from the UK, US and India. About 1 in 4 genuine cases got a false alarm, mostly consumer disputes that people already call scams. Voice notes were not part of the test: they are transcribed and judged like text. The product adds one line to the tested prompt so it answers in the person's language. The agent and the families are shown as clues apart from the score, and they never change it.

Code: [`scripts/validate_scams.py`](scripts/validate_scams.py) · results in [`results/scam_scored.json`](results/scam_scored.json), [`results/scam_scored2.json`](results/scam_scored2.json), [`results/scam_bands.json`](results/scam_bands.json).

## Meta models and APIs used

| What | Where |
|---|---|
| **Muse Spark 1.3** (standard endpoint) | The verdict, the investigating agent (function calling with our own tools) and family matching for user messages. User data only goes through the standard endpoint. |
| **Muse Spark 1.3 contributor** | Public data only: labeling Reddit threads, running the preregistered tests and building the scam families. |
| **Muse Voice Transcribe 1.0** | Voice notes and recorded calls (`POST /v1/asr/transcribe`, WAV; ffmpeg converts anything else). |
| **WhatsApp Cloud API** | The bot: webhook with signature check, then the verdict, the agent's clues and family, and the prepared actions as reply buttons (simulated). |

| **Function calling (response agent)** | `alert_contact`, `draft_report`, `block_sender` and `share_pattern`. The model really chooses and writes them; running them is simulated. |

The Model API has function calling but no web search, so the agent's tools are ours. `inspect_link` follows redirects without downloading the page; it only allows http(s) on ports 80/443 and never private or reserved addresses, checked at every hop. `domain_registration` reads public RDAP records.

**Cost:** about US$ 0.02 per check, with the verdict, investigation, family match and prepared actions. The whole project, including both tests and the families, cost under US$ 10 of model credits.

## Architecture

```
WhatsApp / web ──▶ FastAPI (ensayo/api.py)
                    ├─ /api/check        ensayo/shield.py       verdict (validated prompt) · voice → Muse Voice Transcribe
                    ├─ /api/investigate  ensayo/investigate.py  agent: Spark 1.3 + inspect_link + domain_registration
                    │                    ensayo/campaigns.py    nearest scam family
                    ├─ /api/act          ensayo/act.py          response agent: prepares actions (simulated)
                    ├─ /api/campaigns    results/scam_campaigns.json
                    ├─ /api/network      results/scam_network.json  early warning replay
                    ├─ /api/evidence     results/scam_bands.json
                    └─ /api/whatsapp     ensayo/whatsapp.py     Cloud API webhook
```

- **Cost and safety rails.** Every model call goes through `ensayo/costs.py:Ledger` (per-phase caps, logged to `results/costs.jsonl`). Real mode has a daily quota per IP and per WhatsApp number. User messages are not stored on disk, and WhatsApp logs keep only a hash of the number. Prepared actions stay in memory for one hour to answer the WhatsApp buttons.
- **Front end.** React + Vite + Tailwind in `frontend/`, built into `web/`.
- **Deploy.** Docker Compose behind nginx on a VPS.

### Scam families

[`scripts/scam_campaigns.py`](scripts/scam_campaigns.py) works in three steps:

1. Spark 1.3 describes each confirmed case: channel, brand used as bait, what the scammer wanted, whether AI was involved, and a hook rewritten without names, numbers or links.
2. It groups the descriptions into about 20 families.
3. It assigns every case to one family.

The trend compares September with October as a share of all reports, and it is only shown for families with at least 30 cases. Brands count as a "campaign" from 3 cases. One finding we did **not** expect: only 46 of the 1,902 cases (2.4%) say AI was used. The other numbers: 16% of cases with a known channel reached people on WhatsApp, Instagram, Facebook, Messenger or Marketplace, and fake job offers grew 35% in October.

### Early warning (simulation)

[`scripts/scam_network.py`](scripts/scam_network.py) replays the cases by date, with no model calls. A campaign is one imitated brand within one family, flagged at 3 reports in 14 days. Result: 15 campaigns flagged from 478 reports that name a brand, and 34 later reports that came after the flag (median 22.5 days later). This is an illustration, not a test: we chose the rule while looking at these same reports, and nobody received an alert. A few Reddit communities are a tiny sample, so we don't claim what a real network would catch.

## What's next

**The hard part of going native is privacy.** WhatsApp chats are end-to-end encrypted, so a server can't read them. A native version would have to be opt-in and work without breaking that promise, for example with the first check on the device and the deeper check only when the person allows it. We haven't built or tested that.

- Make the actions real, with consent: alerts to a trusted contact and direct reports to banks and platforms.
- Build the opt-in network from forwards, sharing only anonymous descriptions of each scam.
- A public weekly scoreboard: score new cases every week, commit the hash first, and publish the result even in bad weeks.
- Business verification with Meta, so anyone can message the WhatsApp number.

## Run it

```bash
uv sync --group dev
uv run --group dev pytest                      # 75 tests, mock server, no network
uv run uvicorn ensayo.api:app --port 8040      # mock mode (no key needed)
ENSAYO_REAL=1 uv run uvicorn ensayo.api:app --port 8041   # real mode: needs MODEL_API_KEY in .env
cd frontend && npm install && npm run build    # rebuilds web/
```

`.env.example` lists the variables: `MODEL_API_KEY`, plus `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN` and `WHATSAPP_APP_SECRET` for the bot.

Reproduce the test: `uv run python scripts/validate_scams.py --round 2 --label|--predict|--score --yes`. Rebuild the families: `uv run python scripts/scam_campaigns.py --describe|--taxonomy|--assign --yes`, then run it without flags to aggregate.

## Data and tools we declare

- **Reddit posts.** Public, from the [Arctic Shift](https://arctic-shift.photon-reddit.com) archive and, for the first pilot, the Apify Reddit scraper. Only post text, public image links and reply text are used. The families page shows model-written summaries without names, numbers or links, plus links to the original threads.
- **Earlier pivot.** The repo also contains **Ensayo**, our first idea: synthetic audiences predicting which ad variant wins, with Meta Ad Library data via Apify. In its backtest the synthetic audience beat neither chance nor a single prompt. A narrower follow-up, predicting which gender Meta delivers an ad to, passed an out-of-sample test (within-brand r = 0.385 on 133 new ads), but we moved to the scam shield for impact. Its code and results stay in the repo (`ensayo/simulate.py`, `results/holdout_*`).
- **Coding tools.** Built with **Claude Code** (Anthropic) as the coding assistant. The product itself runs only on Meta's models.
- **Fraud figures in the video.** FTC Consumer Sentinel 2025: US$ 15.9 billion reported lost, with social media the contact method with the highest losses.

## Team

[Muze AI](https://muze.cl), Chile.
