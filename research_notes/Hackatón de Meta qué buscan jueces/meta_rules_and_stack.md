# Meta Global AI Developer Hackathon: Rules and Technology Stack

Research date: 2026-10-26. Sources are cited inline. Facts from pages I could only read through a summarizing fetch are marked "(summary fetch)"; verify them against the live page before relying on exact wording. Items marked UNCONFIRMED have only third-party or aggregator sources.

## Key findings at a glance

- **Application window has already closed, per the official pages.** Meta's page and the Cerebral Valley listing both say applications opened Oct 13 and closed Oct 25, 2026 at 11:59 PM ET, or earlier if the 20,000-applicant cap filled. The "Oct 26 to Nov 4" application window in the brief appears only in a third-party aggregator and a secondary email quote, and it conflicts with the primary pages. ([Meta event page](https://dev.meta.ai/events/global-hackathon); [Cerebral Valley](https://cerebralvalley.ai/e/meta-ai-developer-hackathon); [Course Joiner](https://coursejoiner.com/hackathon/meta-global-hackathon-2026-1/))
- **Official Rules are not published at the URLs I could reach.** Both Meta and Cerebral Valley say they will be published before Oct 26 and must be accepted by selected participants. No link was found. `dev.meta.ai/events/global-hackathon/rules` returned HTTP 404. The Cerebral Valley waiver page loaded only a "Loading..." placeholder.
- **Two tracks, one theme per project.** Indie (individuals and students) and Startup (teams and founders). $1,000,000 total cash across both tracks. No per-track, per-place, or sponsor-prize split is published.
- **Judging weights, judges, submission format, video length, repo/live-URL requirements, team size, and IP terms are not published** on any page I could read.
- **$150 participant API credit is unverified.** Only the aggregator Course Joiner and a German news article (Mindverse) say so. Meta's official page does not mention it. Cerebral Valley lists sponsor credits for "select participants" (Baseten $100 plus 2M TPM, Modal $100, Fireworks $25).
- **Newest model: Muse Spark 1.3** (released Sept 2, 2026 per secondary sources), with 1M context. Meta's own products page lists it at $1.25 input / $4.25 output per million tokens (standard) and $0.10 / $0.20 (contributor, data used to improve products).
- **Muze fit (inference):** Startup track requires a "real product" judged on production readiness, which matches an enterprise-agent build better than Indie. Theme 2 ("Push the Frontier") names manufacturing and energy. The Model API is drop-in compatible with the OpenAI and Anthropic SDKs, so the integration cost is low.

---

## 1. Official Rules, Terms, Eligibility, Prizes, Judging, Submission

### Takeaway
The official rules document is not reachable, and the primary pages leave the decisive items open: judging weights, prize split, submission format, team size, IP. The one hard fact that matters on day 0 is that the application deadline was Oct 25 at 11:59 PM ET.

### Cited Findings

**Dates and application window**
- Applications open Oct 13, 2026 9:00 AM ET (rolling review). Application deadline Oct 25, 2026 11:59 PM ET, or earlier if all 20,000 spots fill. Applicant notifications by Oct 26, 9:00 AM ET. Hackathon begins Oct 26 with a kickoff livestream. Workshops and Discord office hours Oct 27 to Nov 4. Submissions due Nov 4, 2026 9:00 PM ET. Judging Nov 4 to Nov 8. Closing ceremony Nov 9 with live finals and winner announcements. Meta may change dates at its sole discretion. ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch; same dates on [Cerebral Valley](https://cerebralvalley.ai/e/meta-ai-developer-hackathon), summary fetch)
- Cerebral Valley: "no later applications will be accepted or evaluated." Late entry appears unavailable. ([Cerebral Valley](https://cerebralvalley.ai/e/meta-ai-developer-hackathon), summary fetch)
- Conflicting: Course Joiner (dated Oct 13, 2026) says "applications run from October 26 through November 4th," while the same snippet says "apply by October 25." Treat as unreliable. ([Course Joiner](https://coursejoiner.com/hackathon/meta-global-hackathon-2026-1/))
- Cap: 20,000 accepted applicants. Entry is free if selected. ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch)

**Tracks and themes**
- Every project enters one track. Indie developer: "individual builders and students," judged on creativity, technical ambition, and whether it works. Startup: "teams and founders building a real product," judged on technical execution and production readiness. ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch)
- Themes (both tracks): Theme 1 "Build for Your World" (apply Meta's models to a problem you know firsthand). Theme 2 "Push the Frontier" (software, robotics, manufacturing, energy, materials, and similar fields, including giving machines new capabilities or accelerating experiments). ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch)

**Prizes**
- $1,000,000 total cash prize pool, shared across the two tracks. No per-track, per-place, per-theme, or special/sponsor prize amounts are listed. ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch; [Cerebral Valley](https://cerebralvalley.ai/e/meta-ai-developer-hackathon), summary fetch)
- Sponsor credits for "select participants": Baseten $100 in credits and 2M TPM rate limits; Modal $100; Fireworks $25 (plus a workshop led by Sinan Ozdemir). Not clear whether these are prizes or onboarding credits. ([Cerebral Valley](https://cerebralvalley.ai/e/meta-ai-developer-hackathon), summary fetch)
- UNCONFIRMED: "$150 in Meta Model API credits per participant." Sources: [Course Joiner](https://coursejoiner.com/hackathon/meta-global-hackathon-2026-1/), which attributes it to "Meta's official announcement" but cites no URL, and [Mindverse](https://www.mind-verse.de/news/meta-plant-globalen-ki-hackathon-fuer-entwickler), which says "150 US dollars in API credit" with no source. The official Meta page does not mention it. Credit terms (activation, validity, limits) are not published anywhere I could reach.

**Application review (separate from judging)**
- Applications are scored equally on two criteria using only form answers: (1) project idea clarity, feasibility, and theme fit; (2) demonstrated technical skill in an AI project. ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch; [Cerebral Valley](https://cerebralvalley.ai/e/meta-ai-developer-hackathon), summary fetch)

**Judging**
- Indie: creativity, technical ambition, whether it works. Startup: technical execution, production readiness. Weights: not published. ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch)
- Mindverse (published 25 Sep 2026) lists generic criteria (problem relevance, technical implementation, usability, reliability, responsibility, transferability, demonstrability) and explicitly says these are not official. ([Mindverse](https://www.mind-verse.de/news/meta-plant-globalen-ki-hackathon-fuer-entwickler), summary fetch)
- Judges: not listed on any page reached.

**Eligibility**
- Open worldwide where local law permits. Excluded: sanctions targets and persons located in or organized in Belarus, China, Russia, Ukraine, Syria, or comprehensively sanctioned regions (Crimea, Donetsk, Luhansk, Cuba, North Korea, Iran). Excluded: employees, contractors, interns of Meta and Cerebral Valley; government-affiliated individuals; immediate family and household. Duplicate applications, false identity, or spam disqualified at sponsor's discretion. Chile is not excluded. ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch)
- Age and country requirements: "not yet published" per Mindverse (25 Sep). ([Mindverse](https://www.mind-verse.de/news/meta-plant-globalen-ki-hackathon-fuer-entwickler), summary fetch)

**Team size**
- Not specified on any page. Indie is for individuals; Startup is for teams. ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch)

**Submission requirements**
- Deadline Nov 4, 2026 9:00 PM ET. Video length, public repo, live URL, deliverable format, and submission portal: not stated. Official rules and the Cerebral Valley waiver are referenced for terms. ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch)
- Required models/APIs: none marked mandatory. The page lists "the Muse Spark series, Muse Wonder, Muse Image and SAM 3.1 via Meta Model API," Meta open-weights models, and Muse Code, and does not say which are required. ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch)

**IP, licensing, disqualification**
- Not found. The page says Official Rules and the waiver contain terms. Cerebral Valley's waiver URL (https://cerebralvalley.ai/e/meta-ai-developer-hackathon/waiver) returned only "Loading..." in the summary fetch. Meta's footer links go to generic Facebook Terms and Privacy policies, not hackathon-specific terms. ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch; [waiver page](https://cerebralvalley.ai/e/meta-ai-developer-hackathon/waiver), empty)

**Pre-existing code**
- Not addressed on any page reached. The 2024 Llama 3 hackathon on Cerebral Valley barred previously built projects, but that is a different event and is not evidence for this one. (Source: [Cerebral Valley Llama hackathon listing, cited in search results](https://cerebralvalley.notion.site/Meta-Hackathon-Event-Details-Hackers-2732d46e36fc4f1dadb61f5ac422a239), not fetched.)

**Late registration**
- Not offered per Cerebral Valley (see above). Whether the 20,000 cap filled before Oct 25 is unknown.

### Inferences
- If Muze did not submit an application by Oct 25 at 11:59 PM ET, the official path to participation looks closed. Confirm directly with Meta or Cerebral Valley whether any late or waitlist path exists before building for it.
- Startup track is the realistic fit for a company team. Indie is for individuals and students, and the Startup track requires a real product judged on production readiness.
- Rules are not published, so anything about IP ownership (who owns the submitted code, and whether Meta gets a license) is unknown. Do not assume client-specific code or data can be submitted without reading the waiver.

### Gaps
- Official Rules text: not found at any URL tested. `dev.meta.ai/events/global-hackathon/rules` returned 404. Other URLs tried: Cerebral Valley waiver (empty), Meta footer terms (generic).
- Judging weights, judges, prize split per place, sponsor/special prizes beyond the three credit sponsors.
- Video length, repository, live URL, submission portal, mandatory vs optional stack.
- Team size limits, IP/license, pre-existing code policy, disqualification detail beyond eligibility.
- Whether the $150 API credit exists officially (only aggregator/secondary sources).
- Whether the 20,000 cap was reached.

---

## 2. Meta technology stack (as of 2026-10-26)

### Takeaway
The current flagship API model is Muse Spark 1.3, released Sept 2, 2026, with 1M context and tool/agent focus. Muse Spark 1.2 (Aug 5) is the coding model, and Muse Wonder 1.0 is in preview. Open weights are Muse Glimmer (30B, Apache 2.0) and Muse Spark Open. The Model API is OpenAI- and Anthropic-SDK compatible.

### Cited Findings

**Model API basics (Meta's own products page, summary fetch)**
- Base URL `https://api.meta.ai/v1`, bearer token `MODEL_API_KEY`. Drop-in compatible with the OpenAI SDK and the Anthropic SDK, and with OpenAI-compatible agent CLIs. Web search grounding available. Cookbooks: quick start, multi-agent orchestration, search grounding, computer use, a GitHub agent, browser-verified web design. ([Meta Model API](https://dev.meta.ai/products/meta-model-api/), summary fetch; [Meta Docs](https://dev.meta.ai/docs/), summary fetch)
- Rate limits and free credits: not on the products page or docs page. Linked "Pricing and rate limits" page (dev.meta.ai/docs/pricing-rate-limits) was not fetched; a search summary cites it, but I could not open it. ([Meta Docs](https://dev.meta.ai/docs/), summary fetch)
- Muse Code install (summary fetch of Meta Docs): `curl -fsSL https://dev.meta.ai/install.sh | sh` (macOS/Linux); `irm https://dev.meta.ai/install.ps1 | iex` (Windows). Launch with `muse`. A coding agent "for the terminal and CI, built for Muse Spark and powered by Model API." ([Meta Docs](https://dev.meta.ai/docs/), summary fetch)

**Model IDs and pricing (Meta products page, summary fetch; per million tokens unless noted)**
- `muse-spark-1.3`: 1M context, $1.25 input / $0.15 cached / $4.25 output. Note "Not used to improve our products." ([Meta Model API](https://dev.meta.ai/products/meta-model-api/), summary fetch)
- `muse-spark-1.3-contributor`: 1M, $0.10 / $0.002 / $0.20. "Used to improve our products." ([Meta Model API](https://dev.meta.ai/products/meta-model-api/), summary fetch)
- `muse-spark-1.2`: same price as 1.3 standard. `muse-spark-1.2-contributor`: same as 1.3 contributor. ([Meta Model API](https://dev.meta.ai/products/meta-model-api/), summary fetch; [Muse Spark 1.2 page](https://dev.meta.ai/models/muse-spark-1-2/), summary fetch)
- `muse-spark-1.1`: $1.25 / $0.15 / $4.25, 1M. ([Meta Model API](https://dev.meta.ai/products/meta-model-api/), summary fetch)
- `muse-wonder-1.0` (Muse Wonder, "in preview," 1M): $4.00 / $0.20 / $20.00. Available in Model API and Muse Code. `muse-wonder-full-1.0` is a Muse Code subscription only. ([Meta Model API](https://dev.meta.ai/products/meta-model-api/), summary fetch)
- Muse Image `muse-image-1.0`: $0.01 per image. ([Meta Model API](https://dev.meta.ai/products/meta-model-api/), summary fetch)
- Muse Voice Transcribe `muse-voice-transcribe-1.0`: $3.00 per 1,000 minutes ($0.18/hour). Streaming transcription and diarization announced. ([Meta Model API](https://dev.meta.ai/products/meta-model-api/), summary fetch; [Meta blog listing](https://dev.meta.ai/resources/blog/), summary fetch)
- SAM 3.1 `sam-3.1`: $2.50 per 1,000 images, or $0.20 per 1,000 video frames. ([Meta Model API](https://dev.meta.ai/products/meta-model-api/), summary fetch)
- Pricing corroborated by secondary sources for 1.3: [eesel.ai](https://www.eesel.ai/blog/muse-spark-1-3-pricing) (says standard rates held flat from 1.2). Contributor rate in eesel is described as approximate.

**Muse Spark 1.3 (newest, released Sept 2, 2026 per secondary sources)**
- Focus on agentic workflows and coding. Available via Muse Code and Model API first. Max reasoning mode delayed for safety testing; existing reasoning modes live. Facebook, Instagram, Meta AI access expected later. ([ProPakistani](https://propakistani.pk/2026/09/03/meta-launches-muse-spark-1-3-with-faster-coding-and-smarter-agents/); [Outlook Business](https://www.outlookbusiness.com/corporate/what-is-muse-spark-13-metas-new-ai-model-takes-on-openai-anthropic); both secondary)
- Meta-reported (company tests, not independently audited): about 20% fewer tool calls and about 25% fewer tokens vs. Muse Spark 1.2. Asks clarifying questions, confirms before consequential actions, better prompt-injection resistance. ([ProPakistani](https://propakistani.pk/2026/09/03/meta-launches-muse-spark-1-3-with-faster-coding-and-smarter-agents/); secondary)
- Artificial Analysis ranks the "max" variant 6th of 636 models on its Intelligence Index (secondary report). Alexandr Wang's competitive claims are his own. ([Siècle Digital](https://siecledigital.fr/2026/09/04/meta-affirme-avoir-rattrape-openai-et-anthropic-avec-son-nouveau-modele-dia/); secondary, French)
- Dedicated Meta page `dev.meta.ai/models/muse-spark-1-3/` returned 404. Specs come from secondary sources only.

**Muse Spark 1.2 (Aug 5, 2026 per secondary sources)**
- Coding and long-running tasks, shipped with Muse Code beta (macOS and Linux). 1M context. Meta's page: "more reliable tool calling"; cookbooks cover agent fan-out into isolated worktrees, computer use, GitHub agent, search grounding. Benchmarks shown as images only (TerminalBench, DeepSWE, Meta Internal Code Bench, GDPval). ([Muse Spark 1.2 page](https://dev.meta.ai/models/muse-spark-1-2/), summary fetch; launch date from [Gigazine](https://www.gigazine.net/gsc_news/en/20260807-muse-spark-1-2-benchmark) and [OODA Loop](https://oodaloop.com/briefs/technology/muse-spark-1-2-improved-agentic-performance-at-higher-cost-per-task/), secondary)
- Artificial Analysis index: 54 (1.2, xhigh), 51 (1.1), 43 (1.0). Secondary report. ([Muse Spark 1.2 search summary](https://www.gigazine.net/gsc_news/en/20260807-muse-spark-1-2-benchmark))

**Muse Spark 1.1 and the API launch**
- Public preview of Model API for Muse Spark 1.1 opened to US developers on July 9, 2026. New API accounts get $20 free credits, then pay-per-token. Input: text, images, video, PDFs; output: text; context 1,048,576 tokens. Features: adjustable reasoning effort per request, structured outputs, parallel tool calls, file handling, prompt caching, cited web search. Model ID `muse-spark-1.1`. Secondary coverage only. ([The Star](https://www.thestar.com.my/tech/tech-news/2026/07/09/meta-debuts-muse-spark-11-with-preview-open-to-developers); [Axios](https://www.axios.com/2026/07/09/meta-ai-spark-model-update-developer); [Let's Data Science](https://letsdatascience.com/news/meta-opens-muse-spark-11-to-developers-via-model-api-f9b336cb))
- WSJ reported Meta pushed back the developer release several times. ([The Standard](https://www.thestandard.com.hk/innovation/article/333768/Meta-repeatedly-pushes-back-new-AI-model-release-for-developers-WSJ-says))
- Caveat: the model is hosted, not downloadable, and cannot be fine-tuned. ([The Star](https://www.thestar.com.my/tech/tech-news/2026/07/09/meta-debuts-muse-spark-11-with-preview-open-to-developers))

**Consumer Muse Spark (April 2026, for context)**
- Launched April 8, 2026 in Meta AI app and meta.ai; Meta's post says WhatsApp, Instagram, Facebook, Messenger, and AI glasses would follow. Per search summary of Meta's post (not fetched directly): rollout reached WhatsApp, Instagram, Facebook, Messenger, Threads by May 12, 2026, and Ray-Ban Meta and Oakley Meta glasses in the US and Canada. ([Meta announcement](https://about.fb.com/news/2026/04/introducing-muse-spark/), search summary only; [Axios](https://www.axios.com/2026/04/08/meta-muse-alexandr-wang))

**Open-weight models**
- Muse Glimmer: 30B parameters, Apache 2.0 license, "small enough to run on a single consumer GPU or Mac," multimodal perception, text plus image per one outlet. Weights via Hugging Face (`huggingface.co/meta-models/Muse-Glimmer-30B`); runs on Ollama, LM Studio, llama.cpp, vLLM, Unsloth. Release date conflicts: about Aug 10 per several outlets, Aug 26 per Campus Technology. ([Muse Glimmer page](https://dev.meta.ai/models/muse-glimmer/), summary fetch; [Campus Technology](https://campustechnology.com/articles/2026/08/26/meta-releases-muse-glimmer-an-open-weight-ai-model-designed-to-run-on-consumer-hardware.aspx); [Crypto Briefing](https://cryptobriefing.com/meta-muse-glimmer-spark-release/))
- Muse Spark Open: open-weight agentic coding model, self-hostable, fine-tunable, also offered through hosted APIs (per Meta blog title "Build with Muse Spark Open"; date not shown). ([Meta blog](https://dev.meta.ai/resources/blog/), summary fetch)
- Muse Spark 1.2 open weights: Zuckerberg said they would follow. Status UNCONFIRMED. ([Crypto Briefing](https://cryptobriefing.com/meta-muse-glimmer-spark-release/), secondary)
- Muse Spark 1.3 open weights: Zuckerberg said an open-weights version is "coming soon." Not released as of the Sept 2 launch. ([Outlook Business](https://www.outlookbusiness.com/corporate/what-is-muse-spark-13-metas-new-ai-model-takes-on-openai-anthropic); secondary)

**Recent Meta blog posts (titles only; dates not shown on the listing page)**
- "Build with Muse Spark Open," "Build with Muse Wonder" (coding, long-running agents, computer use), "Muse Code: New plans and features" (Muse Code left beta), "Meet Muse Voice Transcribe" (streaming STT), "Build with Muse Image" (generation and editing), "Build with Muse Glimmer." ([Meta blog](https://dev.meta.ai/resources/blog/), summary fetch)

**Context and multimodal limits**
- Muse Spark 1.1 and 1.2 advertise 1,048,576-token context. Input types: text, images, video, PDFs (Muse Spark 1.1 per secondary coverage). Voice-in / voice-out is not listed for Muse Spark text models. ([Muse Spark 1.2 page](https://dev.meta.ai/models/muse-spark-1-2/), summary fetch; Star / Axios for 1.1)

### Inferences
- Newest-first build target: `muse-spark-1.3` standard endpoint, with 1.2 as fallback. Muse Code is the coding agent to showcase for "Push the Frontier" if the team builds a developer tool.
- For client data (banking, mining, salmon), use the standard endpoint, not the contributor variant. The contributor tier is priced lower but its data "used to improve our products." That is a data-governance point for enterprise clients.
- Drop-in OpenAI and Anthropic SDK compatibility means existing Muze agent code can point at `https://api.meta.ai/v1` with a new key and model ID. (Worth a quick test; not verified in code.)
- The $20 new-account credit is US-only at preview launch (per The Star/Axios). Whether Chilean accounts get it is UNCONFIRMED.

### Gaps
- Official rate limits and free-credit terms: the pricing and rate-limit page was not reachable.
- Muse Spark 1.3 official Meta page (404) and Meta's own announcement of the Sept 2 release: not fetched.
- Official Meta announcement of Muse Spark 1.2 (Aug 5): not fetched; date is from secondary coverage.
- SDK package names: not listed on the Meta docs page reached.
- Data retention and SLA for Model API: not stated on any page reached.
- Muse Spark 1.3 max-reasoning availability: "later," no date.

---

## 3. Workshop schedule (Oct 27 to Nov 4)

### Takeaway
Only the window and the format are published: live workshops by Meta and partners plus Discord office hours. No session titles or times were found. The one named session is a Fireworks workshop.

### Cited Findings
- Live workshops from Meta and partners Oct 27 to Nov 4, plus Discord office hours on the same dates. ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch)
- Fireworks workshop led by Sinan Ozdemir; no title or date listed. ([Cerebral Valley](https://cerebralvalley.ai/e/meta-ai-developer-hackathon), summary fetch)
- Meta's blog has model-focused "Build with..." posts (Muse Spark Open, Muse Wonder, Muse Glimmer, Muse Voice Transcribe, Muse Image), which read as the likely workshop subjects. ([Meta blog](https://dev.meta.ai/resources/blog/), summary fetch). This is an inference, not a published schedule.

### Inferences
- Meta is pushing agent workflows (tool calling, multi-agent, computer use, web search grounding) and the new model families (Muse Wonder, Muse Voice, Muse Image). Those are the capabilities the workshops are likely to cover.

### Gaps
- Session titles, times, speakers, and recordings: not found. Check the Discord and the Cerebral Valley event page once the Meta livestream starts.

---

## 4. Meta strategic messaging about the event

### Takeaway
Meta's public framing is "build with our newest models," with two themes and a broad frontier scope. No Meta executive keynote or press release about the hackathon was found. The Sept 24 date for a Meta announcement appears only in Mindverse and is not confirmed.

### Cited Findings
- Event description: "Ten-day, virtual, worldwide hackathon with Meta's newest models." Themes: "Build for Your World" and "Push the Frontier." ([Meta event page](https://dev.meta.ai/events/global-hackathon), summary fetch)
- Organizer named as Meta Superintelligence Labs by Course Joiner and by a search-result summary of the event; not stated on the Meta event page reached. ([Course Joiner](https://coursejoiner.com/hackathon/meta-global-hackathon-2026-1/))
- Mindverse says Meta's announcement is dated 24 September 2026, and that the article was published 25 Sept 2026. The 24 Sept Meta link was not opened. ([Mindverse](https://www.mind-verse.de/news/meta-plant-globalen-ki-hackathon-fuer-entwickler), summary fetch). A separate search did not confirm the Sept 24 date. (UNCONFIRMED)
- Mindverse's suggested use cases (internal knowledge assistants, business process automation, coding agents, multimodal apps, connectors) are the author's suggestions, not Meta's. ([Mindverse](https://www.mind-verse.de/news/meta-plant-globalen-ki-hackathon-fuer-entwickler), summary fetch)
- Meta's 2024 Llama hackathons (Montreal, San Francisco, Bengaluru) had "hands-on support from the Meta team" and in-person formats. This event is virtual, so that model does not directly carry over. ([Cerebral Valley newsletter, Oct 21, 2024](https://cerebralvalley.beehiiv.com/p/cerebral-valley-week-of-october-21st), summary fetch)

### Inferences
- The explicit themes ("manufacturing," "energy," "materials," "giving machines new capabilities") fit Muze's client base (salmon farming, mining, banking) better than the Indie framing. A project that solves a real industrial problem with an agent would match both themes.
- WhatsApp, Instagram, Messenger, and glasses integration are not named in any hackathon material found. Meta has said Muse Spark is rolling into those apps (April and May 2026 statements), but there is no evidence that hackathon projects get any special integration.

### Gaps
- No Meta executive quote, blog, or press release specifically about the hackathon was found. Meta's newsroom (about.fb.com/news) and ai.meta.com/blog were not searched directly.
- No signal on what Meta judges want beyond the stated criteria.

---

## 5. Participant chatter and rules clarifications

### Takeaway
No credible participant chatter or rules clarifications from Oct 2026 were found. Reddit and Discord searches returned nothing about this event.

### Cited Findings
- No Reddit or Discord threads about the 2026 hackathon surfaced. Search returned only Llama-era hackathons. ([search summary, no specific URL])
- A NodeSeek forum post (node seek ID 979727) came up in searches, but the fetch returned HTTP 403, so its content is unknown. ([NodeSeek](https://www.nodeseek.com/post-979727-1), 403)
- Course Joiner says the event is "relevant to developers and students in India," but it does not state this as an eligibility rule. Treat as unconfirmed. ([Course Joiner](https://coursejoiner.com/hackathon/meta-global-hackathon-2026-1/))

### Inferences
- The rules-clarification channel that matters is the Discord server linked from the Meta event page (office hours Oct 27 to Nov 4) and the Cerebral Valley event page. Neither was accessible to me.

### Gaps
- Discord server contents and any clarification posts: not accessible from here.
- X posts from @AIatMeta or Cerebral Valley staff: not searched (no X access in this session).
- LinkedIn posts from Meta DevRel: not searched.

---

## Discrepancies and unverified claims (summary for the report writer)

1. **Application window**: Meta and Cerebral Valley say Oct 13 to Oct 25 (11:59 PM ET). Brief and Course Joiner say Oct 26 to Nov 4. Primary sources win. Applications appear closed.
2. **$150 participant API credit**: only Course Joiner and Mindverse. Not on Meta's official page. UNCONFIRMED.
3. **Sponsor credits**: Baseten $100 (+2M TPM), Modal $100, Fireworks $25 are listed on Cerebral Valley for "select participants." Not clear whether these are distinct from the $150 claim.
4. **Muse Spark 1.3 pricing**: Meta's own products page lists $1.25 / $4.25 and $0.10 / $0.20. Confirmed on the primary page.
5. **Muse Spark 1.3 release date**: Sept 2, 2026 per secondary sources. Meta's model page 404'd. Secondary-only.
6. **Muse Glimmer release date**: about Aug 10 (several outlets) vs. Aug 26 (Campus Technology). Unresolved.
7. **Muse Spark 1.2 open weights**: promised, not confirmed as released.
8. **Meta hackathon announcement date**: Sept 24, 2026 (Mindverse) not confirmed by a second source.
9. **Model API free credit for new accounts**: $20 (July 2026 preview, US developers). Not on Meta's products page.
10. **Judging weights, prize split, team size, submission format, IP terms, judges**: not published on any reachable page.

## Source quality note

The two official pages (Meta event page, Cerebral Valley event page) and Meta's model/product pages were read through a summarizing fetch. The summaries are consistent with each other on dates, tracks, prizes, and eligibility. Exact wording of quoted lines in this file should be checked on the live pages. Pricing numbers on Meta's Model API page were consistent across two independent summaries and with a secondary source for 1.3.
