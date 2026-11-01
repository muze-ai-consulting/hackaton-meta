# Meta AI strategy, as of 1 Nov 2026

Scope: what Meta is betting on with AI tools and its app/developer ecosystem, Sept–Oct 2026, to help pick a hackathon product. Items before Sept 2026 are labeled background. Sourcing: "Primary" = Meta page (read via fetch; quotes below come from fetch summaries, not verified against the raw page). "Secondary" = press/aggregator/vendor. "Unverified" = single or conflicting source.

Important limits up front:
- The Q3 2026 call transcript is not verified verbatim. Meta's PDF transcript was unreadable (binary). The Motley Fool summary returned no verbatim quotes. Call quotes below are from the Meta release (via fetch) and from secondary coverage.
- No Meta developer blog, Connect 2026 recap, or dev.meta.ai case-study page for Sept–Oct 2026 was retrieved.

---

## 1. Q3 2026 earnings call (21 Oct 2026): what Meta said

### Takeaway
Meta framed Q3 2026 around the Muse agent family ("personal superintelligence for everyone") and tied AI spend to ad revenue and engagement. Ads grew 26%, and capex guidance rose to $135–145B. Advantage+ and business agents were not named in the release.

### Cited Findings
- Q3 2026 release dated 21 Oct 2026. Ad revenue $63.06B, +26% YoY; ad impressions +10%; average price per ad +14%. Primary: [Meta Q3 2026 release](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Third-Quarter-2026-Results/default.aspx) (via fetch summary). Corroborated by [Motley Fool summary](https://www.fool.com/earnings/call-transcripts/2026/10/21/meta-meta-q3-2026-earnings-call-transcript/) (ad revenue $63.1B, +26%).
- Zuckerberg, 21 Oct 2026: "launching Muse and Muse Wonder, our first frontier model" — Primary release, via fetch summary ([link](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Third-Quarter-2026-Results/default.aspx)). Unverified verbatim.
- Zuckerberg, 21 Oct 2026: framing "delivering personal superintelligence for everyone" — same release, via fetch summary.
- Susan Li (CFO), 21 Oct 2026: AI investments are "already delivering substantial incremental advertising revenue" — release via fetch summary; same phrasing reported by [Investing.com transcript coverage](https://www.investing.com/news/transcripts/earnings-call-transcript-meta-beats-q3-2026-estimates-as-ai-push-lifts-shares-93CH-4964260) (secondary).
- Release: MSL investments build technology for "significant new revenue opportunities," which "take longer to pay off" than core investments — same release.
- Capex: 2026 guided to $135–145B (narrowed from $130–145B). Q3 capex $34.9B. For 2027: "investing aggressively," budget still in development — release via fetch; Motley Fool confirms $135–145B and Q3 $34.9B.
- Reality Labs: 2026 loss guided to $18–19B (Motley Fool); release says losses narrow to about $15B in 2027, with investment shifted "primarily AI."
- Muse (per Motley Fool summary, secondary): more than 10M sign-ups in the US and Canada within about six weeks; roughly 25% active on a given day. Target: more than 10x compute-cost efficiency within a year. Monetization plans: free basic service with commerce-based fees, direct subscriptions, and business/enterprise offers. Meta also announced a personal-agent protocol with partners Stripe and Shopify.
- Partnership ads surpassed a $15B annual run rate, up over 97% (Motley Fool summary; secondary).
- Advantage+: NOT mentioned in the Q3 release (fetch check). Business AI agents / WhatsApp: NOT mentioned by name in the release.

### Inferences
- The AI story in the Q3 narrative is "Muse as a personal agent" plus "AI drives ad revenue." Ads automation is still a revenue story, but Meta did not put it in the release headline.
- Stripe and Shopify as agent-protocol partners points to commerce-agent integrations as a stated direction (secondary source, so treat as likely but not confirmed).

### Gaps
- No verbatim transcript quotes on Advantage+, business agents, glasses, or end-of-2026 ad automation. Meta's PDF transcript was unreadable and the Motley Fool summary returned none. Re-check the official transcript before quoting in any pitch.

---

## 2. Developer and AI launches, Sept–Oct 2026 (newest and most promoted first)

### Takeaway
The newest and most promoted items are the Muse agent models. Muse Wonder (12 Oct) is available through the Meta Model API and Muse Code. Muse Spark 1.3 (2 Sep) is also in the Model API. Meta's developer surface is agent-centric. Pricing, open-weights status, and several named models (SAM 3.1, Muse Voice Transcribe, Muse Glimmer) are unverified.

### Cited Findings

**Muse Wonder and Muse Wonder Full (12–13 Oct 2026) — newest, Primary**
- Muse Wonder: "state-of-the-art performance on personal and professional agentic tasks." Available today in the Meta Model API and for developers in Muse Code. Will power Muse experiences, rolling out first to subscribers. — [Meta blog](https://about.fb.com/news/2026/10/introducing-muse-wonder-models/)
- Muse Wonder Full: available only to Muse Code subscribers. — same source.
- No pricing, no open-weights statement, no named leaders quoted. — same source.

**Muse Spark 1.3 (2 Sep 2026) — Secondary, multiple outlets agree on date**
- Released 2 Sep 2026; fourth Muse Spark release in five months. Available via Muse Code and the Meta Model API. Facebook, Meta AI, and Instagram rollout reported as later. — [ProPakistani](https://propakistani.pk/2026/09/03/meta-launches-muse-spark-1-3-with-faster-coding-and-smarter-agents/), [Verdict](https://www.verdict.co.uk/?p=403613), [Siècle Digital](https://siecledigital.fr/2026/09/04/meta-affirme-avoir-rattrape-openai-et-anthropic-avec-son-nouveau-modele-dia/)
- Coding and agents: faster and more efficient than Spark 1.2. Internal comparisons: about 20% fewer tool calls, about 25% fewer tokens (secondary; source of the internal comparison not checked).
- Benchmarks compared against GPT-5.6 Sol and Opus 5. Meta's scorecard compares Spark 1.3 in max mode against Spark 1.2 in xhigh, which is not like-for-like. Max mode not yet broadly available pending safety testing. — [aitoolly coverage](https://aitoolly.com/zh/ai-news/article/2026-09-03-meta-launches-muse-spark-13-strategic-coding-upgrades-and-the-push-for-ai-dominance) (secondary)
- Pricing CONFLICTS: one source says same price as Spark 1.2; a Hebrew source gives $1.25 input / $4.25 output per million tokens. Unverified against Meta's pricing page.
- Note: 2 Sep 2026 is the same date the project's CLAUDE.md uses as the contamination cutoff for the backtest (Spark 1.3 launch).

**Muse Code (launched 5 Aug 2026) — Secondary (Reuters via The Star)**
- Terminal coding tool powered by Muse Spark 1.2. Splits large jobs into parallel sub-tasks across sub-agents. Positioned against Claude Code and OpenAI Codex, mainly on price. Described as preview/beta. — [The Star](https://www.thestar.com.my/tech/tech-news/2026/08/06/meta-launches-new-ai-coding-tool-powered-by-muse-spark-12), [Dealroom](https://app.dealroom.co/news/note/meta-launches-muse-code-coding-agent-undercutting-rivals-on-price)
- Pricing: standard pay-as-you-go $1.25 / $4.25 per million tokens ([Deccan Chronicle](https://www.deccanchronicle.com/technology/meta-launches-new-ai-coding-tool-muse-code-powered-by-muse-spark-12-1977049)). Discounted tier for users who allow Meta to train on prompts/completions, reported at $0.30 per million tokens and limited to select countries ([TNW](https://thenextweb.com/news/meta-muse-code-ai-coding-agent-launch), [tbreak](https://tbreak.com/meta-muse-code-muse-spark-1-2/)). Conflicting or unverified. A zero-data-retention option is mentioned by one low-quality source.
- Launch credit: one source credits Zuckerberg, others credit Meta and Superintelligence Labs leadership. Unresolved.

**Meta Model API — public preview (9 Jul 2026) — Primary, background**
- Launched with Muse Spark 1.1 as a public preview: "For the first time, developers can begin building with Muse Spark 1.1 via the new Meta Model API." — [Meta blog](https://ai.meta.com/blog/introducing-muse-spark-meta-model-api/)
- The Meta page gives no base URL, endpoints, or SDK-compatibility claim. "Clean OpenAI-compatible package" is a Replit CEO quote on the same page, not a Meta claim.
- Base URL https://api.meta.ai/v1 with Bearer auth is reported by secondary sources only. Consistent with the project's CLAUDE.md, but not confirmed from a Meta page.
- Standard vs contributor tiers: NOT mentioned on the Meta page (secondary sources only; see Muse Code pricing).

**Muse personal AI agent — Singapore (27 Oct 2026) — Primary**
- Muse "doesn't just answer questions, it actually does the work." Manages email and schedules, takes on tasks, turns goals into plans. Asks before sensitive actions like sending an email or making a purchase.
- Available in Singapore from 27 Oct 2026 on iOS, Android, and web (muse.ai). Free for most needs, subscriptions for heavier use. Connectors: Gmail, Google Calendar, Instagram (rolling out). Glasses support "coming soon." — [Meta blog](https://about.fb.com/news/2026/10/muse-is-now-available-in-singapore-the-worlds-first-personal-ai-agent-built-for-everyone/)
- Local partners: Shopee, Grab, Singapore Airlines, Agoda, ShopBack, Klook, Trip.com, Lazada (same source).
- The Q3 call put Muse at more than 10M US/Canada sign-ups (secondary, see section 1).

**Meta Business Agent and Business Agent Platform (launch 3 Jun 2026 per most coverage) — Secondary**
- Meta Business Agent runs across WhatsApp, Instagram, and Messenger. Answers business questions, recommends products, books appointments, qualifies leads, processes sales, and hands off to humans. Market research and competitive intelligence described as planned. [TechWyse](https://www.techwyse.com/news/platform-updates/meta-business-agent-global-launch-whatsapp-instagram), [CX Today](https://www.cxtoday.com/?p=991187)
- Launch date CONFLICTS: 3 June 2026 at Meta's Conversations conference in London (most sources), 1 July 2026 (one source). A July 2026 India announcement at the Mumbai Business Summit is a regional event, not a separate global launch.
- Meta says more than one million businesses use a Business Agent on WhatsApp and Messenger (Meta figure as reported by secondary; not verified on a Meta page).
- Business Agent Platform: businesses can build, customize, and deploy their own agents. Enterprise custom agents can connect to systems such as Shopify and Zendesk. Free entry tier available now; paid options "in coming months." — [Omnichat](https://blog.omnichat.ai/meta-business-agent-platform-explained-features-pricing-and-what-the-2026-whatsapp-changes-mean-for-your-business/)
- WhatsApp billing change from 1 Oct 2026 (ends free service messages / in-window utility templates): reported by several analyses, but DETAILS CONFLICT (some say replies carry a delivery charge; others say all in-window service messages become billable with no volume discount). Token pricing of $2.00 per million tokens from 1 Aug 2026 is reported by one source. Unverified against Meta's WhatsApp pricing docs. [Zernio](https://zernio.com/blog/meta-business-agent-pricing)

**Glasses developer platform — Secondary (opened ~May 2026)**
- Wearables Device Access Toolkit: native mobile SDK for iOS (Swift) and Android (Kotlin), described as a developer preview. Web Apps for Meta Ray-Ban Display: built on HTML, CSS, and JavaScript. — [Android Central](https://www.androidcentral.com/gaming/virtual-reality/metas-ray-ban-display-build-for-the-future-opens-its-doors-to-developers), [VR.org](https://vr.org/articles/meta-ray-ban-display-developer-sdk-2026)
- Launch date: one source says 14 May 2026. Gesture input via Neural Band (EMG). An earlier pre-launch claim that the SDK cannot send imagery to the display may be stale.
- A Spanish-language source says apps require enabling developer mode in the Meta app.

**Meta Connect 2026 (23–24 Sep 2026) — Gap**
- Keynote 23 Sep; Developer State of the Union 24 Sep (Meta developers listing dated 24 Sep 2026: [developers.meta.com](https://developers.meta.com/resources/videos/developer-state-of-the-union-2026/)).
- No verified recap found. Only pre-event previews ([Road to VR](https://roadtovr.com/meta-connect-2026-keynote-livestream-watch-time/)). Unverified post-event claims: "Meta VR Glasses" at $1,299.99, Ray-Ban Meta Audio at $349, a "Muse Charm" keychain ([ExitLag](https://www.exitlag.com/news/meta-connect-2026-announcements/)). This source is internally inconsistent on prices and not corroborated. Do not use.

**Other Sept–Oct 2026 items — Primary titles only (summaries not read)**
- Muse for Small Business article (29 Sep 2026, title only, listed as related news).
- Small business survey on AI productivity (14 Oct 2026, about.fb.com).

**Background (before Sept 2026; labeled)**
- Muse Spark 1.1 and Model API public preview: 9 Jul 2026 (Primary, see above).
- Muse Image and Muse Video: 7 Jul 2026 (Primary title on [ai.meta.com](https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/)).
- SAM / DINO used by Pittsburgh assistive robotics and Genesis Mission projects (Jul 2026, Primary, tagged "Open Source" but open-weights status not stated).

### Inferences
- The developer surface Meta is pushing as of Nov 2026 is the Model API plus Muse Code, with Muse Wonder as the newest model. Pricing and tier structure are unsettled across sources.
- Meta's consumer agent (Muse) and its business agents (Business Agent / Platform on WhatsApp, Messenger, Instagram) are the two agent surfaces it is promoting. Glasses are a third, with an SDK in preview.
- Agent protocol partnerships (Stripe, Shopify) and business connectors (Shopify, Zendesk) suggest Meta wants agents that act on commerce and customer workflows, not just answer questions.
- The project's CLAUDE.md assumes contributor-tier pricing near US$0.25 per batch. Secondary reports show a $0.30/M-token contributor tier for Muse Code, but that is a different product. Confirm the Model API contributor tier against Meta's pricing before budgeting.

### Gaps
- Voice transcription model, SAM 3.1, Muse Glimmer open weights, and Muse Code general availability: no 2026 Meta-primary source found.
- Open-weights status for Muse models: one secondary source says open weights are "planned" for a later release; not verified.
- No Connect 2026 developer recap, and no Meta developer blog for Sept–Oct 2026.

---

## 3. How Meta talks about ads and generative AI (Oct 2026)

### Takeaway
Meta's public ad-automation target is fully AI-run campaigns by end of 2026, but that target comes from 2025 reporting and secondary sources. The Q3 2026 release does not mention Advantage+. No Meta-native tool that predicts ad performance before spend was found. Pre-spend prediction is sold by third-party vendors.

### Cited Findings
- Target for fully automated campaigns by end of 2026: reported as a Meta statement ("expects to offer fully AI-automated ad campaigns by the end of 2026"). Original reporting from 2025 (advertisers give product image and budget; AI generates images, video, text, and audiences). — [Exchange4media](https://www.exchange4media.com/digital-news/meta-aims-to-fully-automate-advertising-with-ai-by-2026-144037.html), [MediaPost](https://www.mediapost.com/publications/article/406315/) (2025 reporting; secondary).
- April 2026 roundup: end-to-end AI campaigns rolling out where advertisers provide a business URL and budget. — [Digital Applied](https://www.digitalapplied.com/blog/social-media-ai-advertising-april-2026-meta-google) (secondary).
- Advantage+ end-to-end revenue "more than $75 billion" annual run-rate during Q2, year not stated. Internal Meta study claims 22% ROAS improvement. Both secondary, unverified. — [Pulse/MediaPost summaries](https://www.pulse.bot/digital-marketing/news/meta-takes-advantage-plus-ai-ads-global-adding-generative-creative-tools-076cf366-067e-41c5-b816-cc9553db4c08/) (secondary).
- Agencies say clients still demand brand guidelines and often reject fully automated concepts. — same April 2026 roundup (secondary).
- Advantage+ Creative: included with ad spend; AI dubbing, backgrounds, variation testing inside Ads Manager. No evidence it predicts performance before spend. — [Rework/Segwise](https://resources.rework.com/tools/ai-tools/best-ai-tools-for-facebook-instagram-ads-2026) (secondary).
- Rework cites Meta data: about 8M advertisers used at least one AI creative tool in Q1 2026, and a conversion-rate gain above 3% in Meta's AI video tests. Unverified; no primary Meta document.
- Third-party pre-launch scoring: Extuitive, Pencil, AdCreative.ai, Madgicx, Smartly.io. Madgicx claims 90%+ accuracy vs 52% for humans (vendor marketing, not a benchmark).

### Inferences
- Meta's ads story is "give us the goal and budget, we automate creative and targeting," but the exact phrase was not found on a 2026 Meta page. Treat as a paraphrase.
- The Q3 release grounds AI ad value in engagement and ad prices (+14% price per ad), not in creative generation.
- Pre-spend ad performance prediction is a niche Meta has not claimed as its own. Vendors fill it. This is an inference from the absence of Meta announcements, not from a Meta statement.

### Gaps
- Andromeda, GEM, Lattice: no 2026 Meta source found in this research. Do not cite without a primary.
- "Give us your goal and budget and we do the rest": no verbatim 2026 quote found.
- No Meta statement on creative testing or ad-performance prediction before spend in Sept–Oct 2026.

---

## 4. Third-party products and partners Meta showcases (2026)

### Takeaway
Meta's showcases in Sept–Oct 2026 are consumer and enterprise partnerships: Muse connectors, commerce partners, universities, and glasses partnerships. No developer case-study or app-spotlight page for Sept–Oct 2026 was retrieved.

### Cited Findings
- Muse Singapore connector partners: Shopee, Grab, Singapore Airlines, Agoda, ShopBack, Klook, Trip.com, Lazada — [Meta blog, 27 Oct 2026](https://about.fb.com/news/2026/10/muse-is-now-available-in-singapore-the-worlds-first-personal-ai-agent-built-for-everyone/) (Primary).
- Five US universities partnership on medical and scientific breakthroughs using Meta models, 28 Oct 2026 — [Meta newsroom](https://about.fb.com/news/2026/10/meta-partners-with-five-us-universities-to-accelerate-medical-and-scientific-breakthroughs/) (Primary title only; summary not read).
- Pinacoteca di Brera and EssilorLuxottica use AI glasses for art access, 14–15 Oct 2026 — [Meta newsroom](https://about.fb.com/news/2026/10/meta-milans-pinacoteca-di-brera-and-essilorluxottica-expand-access-to-art-through-ai-glasses/) (Primary title).
- Pittsburgh assistive robotics and Genesis Mission projects using SAM/DINO, Jul 2026 — [ai.meta.com](https://ai.meta.com/blog/assistive-robotics-university-of-pittsburgh-sam-dino/) (Primary, background).
- Replit CEO Amjad Masad calls the Model API a "clean OpenAI-compatible package" — quoted on the Muse Spark 1.1 Meta page (Jul 2026, secondary quote on a primary page).

### Inferences
- Meta's showcases lean toward enterprises, research institutions, and consumer commerce partners. Developer showcases were not visible in what I retrieved.

### Gaps
- dev.meta.ai and developers.facebook.com case studies for 2026: not retrieved.
- No partner-spotlight list for Model API or Muse Code developers.

---

## Source-quality notes
- Primary pages used: investor.atmeta.com Q3 2026 release (21 Oct 2026); about.fb.com Muse Wonder (12–13 Oct), Muse Singapore (27 Oct), universities (28 Oct), Pinacoteca (14–15 Oct), small business (14 Oct); ai.meta.com Muse Spark 1.1 Model API (9 Jul), Muse Image/Video (7 Jul), assistive robotics (27 Jul). Quotes from these come from a fetch summary, not the raw text.
- Secondary sources used heavily: Motley Fool transcript summary (21 Oct 2026); press on Muse Spark 1.3, Muse Code, Business Agent, Ray-Ban Display SDK, Advantage+.
- Vendor blogs (Omnichat, Zernio, Rework, Segwise, Extuitive, Madgicx) used only for background and flagged. Several are commercial and not independent.
- Conflicting sources flagged inline: Business Agent launch date (3 Jun vs 1 Jul), Muse Spark 1.3 pricing, contributor-tier pricing ($0.30 vs. project's ~US$0.25 per batch assumption), WhatsApp billing details, Connect 2026 product prices (ExitLag, not used).
- Cannot verify from this research: Meta's own WhatsApp pricing doc, Model API pricing page, Connect 2026 recap, the Q3 transcript verbatim.

## Suggested next checks before a pitch
1. Read the official Q3 2026 transcript (investor.atmeta.com webcast/transcript) and pull verbatim quotes on Advantage+, business agents, and Muse.
2. Check the Meta Model API pricing and tier page for Muse Spark 1.3 and Muse Wonder (standard vs contributor).
3. Find Meta's official Connect 2026 recap (about.fb.com) and the Developer State of the Union content (developers.meta.com).
4. Confirm the Business Agent launch date and the WhatsApp Oct 1 billing change on Meta's business pricing pages.
