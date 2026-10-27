# Meta 2026 AI Stack: Frontier Capabilities for the Meta Global AI Developer Hackathon

Research date: 2026-10-26. Scope prioritized to 2026 (especially Jul–Oct 2026) per coordinator instruction. Items marked [VENDOR] are Meta-reported or self-reported. Items marked [3P] come from third-party write-ups. Items marked [UNVERIFIED] could not be confirmed against a primary source. Tool budget was roughly 15 calls; several questions remain open (see Gaps).

## Key Question 1: Muse Spark 1.3 and Muse Wonder: benchmarks, multimodality, agentic features, computer use, web search, long-horizon tasks. What did Meta demo at launch?

### Takeaway
Muse Spark 1.3 (released 2026-09-02) is positioned by Meta as a coding and long-context model; its strongest numbers are vendor-reported, and independent indices place it behind Claude Opus 5 and Claude Fable 5.1. Muse Wonder (released 2026-10-12) is Meta's long-running-agent tier, with Active Memory and Active Focus features, priced at $4/$20 per M tokens. Multimodal breadth is uneven: Meta itself warns that audio understanding is not fully supported in 1.3.

### Cited Findings
- Muse Spark 1.3 released September 2, 2026; described as bringing "frontier-level reasoning" to coding and agentic workflows, available through Oracle Cloud AI Platform, with Google Cloud in private preview — [Meta Connect 2026 developer recap, Sep 24 2026](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]
- Released September 2, 2026 per Artificial Analysis dating — [Artificial Analysis, Muse Spark 1.3](https://artificialanalysis.ai/articles/muse-spark-1-3) [3P]
- Vendor scorecard for 1.3: DeepSWE v1.1 75.4 (leads listed rivals); Terminal-Bench 2.1 88.8 (ties GPT-5.6 Sol); SWEAtlas CodeBase QnA 59.4; MRCR 98.5 (256K–512K) and 98.1 (512K–1M) vs GPT-5.6 Sol 91.5 and 73.8; JobBench 64.9 vs GPT-5.6 Sol 45.4. Claude Opus 5 leads on most agent evaluations (four of six) — [TechRepublic](https://techrepublic.com/article/news-meta-muse-spark-1-3-ai-coding-2026/) and [eesel.ai review](https://www.eesel.ai/blog/meta-muse-spark-13-review) [VENDOR, relayed by 3P]
- Artificial Analysis Intelligence Index: 61 (xhigh) and 62 (max), behind only Claude Fable 5.1 and Claude Opus 5. Output-token volume 120M vs field median 72M; per-task cost $0.40 (1.2) → $0.55 (1.3) — [Artificial Analysis](https://artificialanalysis.ai/articles/muse-spark-1-3) [3P; figures as relayed in search summary, verify on source]
- The top "max" configuration was gated pending additional safety testing per Meta; sources disagree on when it became selectable via API (one says September 4) — [TechRepublic](https://techrepublic.com/article/news-meta-muse-spark-1-3-ai-coding-2026/) [3P]
- Tool calling and web search: Muse Spark 1.3 supports tool calling; Cursor docs say the model can generate search queries and fetch web results through Cursor's agent tools — [Cursor docs, Muse Spark 1.3](https://cursor.com/docs/models/muse-spark-1-3) [3P]
- Served through Responses, Chat Completions and Messages API formats; a listing says Meta reports ~20% fewer tool calls and ~25% fewer tokens than 1.2 — [Requesty model page](https://www.requesty.ai/model/meta/muse-spark-1.3) [3P, source of the 20%/25% figure unverified]
- Computer use: Meta's developer page lists a computer-use cookbook — [Meta developer start-building page](https://developer.meta.com/ai/lp/start-building/) [VENDOR]. OSWorld figures circulate with conflicting metrics: 66.9 "mean partial score" in one table; 57.2 (1.3 xhigh) vs 47.6 (1.2 xhigh) on OSWorld 2.0 in another — [MyClaw blog](https://myclaw.ai/de/blog/muse-spark-1-3) [3P, not directly comparable]
- Web search pricing listed at $2.50 per 1,000 queries — [Product Builder](https://www.productbuilder.net/zh/models/muse-spark-1-3) [3P, UNVERIFIED]
- Pricing $1.25 input / $4.25 output / $0.15 cached input per M tokens — [Requesty](https://www.requesty.ai/model/meta/muse-spark-1.3) [3P; consistent with user's known figure]
- Meta caveat: audio understanding is not fully supported in 1.3 yet — [MyClaw blog](https://myclaw.ai/de/blog/muse-spark-1-3) [3P, attributed to Meta, UNVERIFIED against Meta's own page]
- Muse Wonder and Wonder Full released October 12, 2026; Wonder is available via the Meta Model API and Muse Code; Wonder Full only in Muse Code on the two top plans ($50 and $200) — [DataCamp](https://www.datacamp.com/blog/muse-wonder-and-muse-wonder-full) [3P]; [VKTR](https://www.vktr.com/ai-news/meta-debuts-muse-wonder-frontier-ai-agent-models/) [3P]
- Muse Wonder features: Active Memory (carries information across conversations and retrieves it for new tasks) and Active Focus (keeps an agent going when blocked, including by trying another approach) — [DataCamp](https://www.datacamp.com/blog/muse-wonder-and-muse-wonder-full) [VENDOR, relayed]
- Muse Wonder evaluated on SWE-Marathon (long-running software projects). A Spanish-language report says Meta did not publish how its index is computed, and acknowledged its SWE-Marathon comparison was not controlled and its model ran at maximum effort — [Ecosistema Startup](https://ecosistemastartup.com/?p=117114) [3P]
- Independent indices (secondhand via Notebookcheck, as reported by Ecosistema Startup): Wonder Full 56, Wonder 52 on the Artificial Analysis index, one point below GPT-6 Astra and Claude Fable 5.1 — [Ecosistema Startup](https://ecosistemastartup.com/?p=117114) [3P, UNVERIFIED on AA directly]
- DataCamp review: Claude Opus 5.5 remains ahead on terminal coding, building programs from scratch, health questions, and an independent intelligence ranking — [DataCamp](https://www.datacamp.com/blog/muse-wonder-and-muse-wonder-full) [3P]
- Wonder pricing: $4 input / $20 output per M tokens, same as Claude Opus 5.5 — [DataCamp](https://www.datacamp.com/blog/muse-wonder-and-muse-wonder-full) [VENDOR, relayed]
- Muse (personal agent) debuted as Meta's long-planned personal AI agent, described as more proactive and long-running than typical chatbots; Wonder to power Muse starting with subscribers — [Axios, Sept 8 2026](https://axios.com/2026/09/08/meta-debuts-muse-personal-ai-agent) [3P]
- Muse Code: out of beta, available on Windows; multi-agent by default, with parallel workers writing and testing code in isolated workspaces — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]
- Muse Connector Platform recently launched, letting developers connect their products to tasks people use Muse for — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]
- Meta launch demos: the Connect 2026 developer recap names no specific demos, only session titles and recaps — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]

### Inferences
- Muse Spark 1.3's clearest differentiator for a hackathon is its 1M-token context with strong long-context recall (MRCR), combined with cheap per-token pricing relative to Wonder. This favors demos that ingest long material (meeting archives, full codebases, long video transcripts) over demos that depend on native audio/video perception.
- Muse Wonder's Active Memory and Active Focus are the most "only possible now" agent features in this stack, but evidence is vendor-reported. A demo should show a multi-session memory and a self-recovering task, not rely on a headline benchmark.
- Computer use is available as a cookbook pattern, not as a first-party hosted product in the sources found. Expect to build the browser/desktop loop yourself.

### Gaps
- Meta's own Muse Spark 1.3 and Wonder launch posts (about.fb.com / ai.meta.com) were not fetched; all benchmark figures come from secondary coverage.
- Native multimodality (video understanding, audio output, realtime voice-out) for Muse Spark 1.3 and Wonder is not confirmed. The only confirmed multimodal developer surface is speech-to-text (see Q2).
- The Meta-published status of the "max" tier and its safety gating was not resolved.
- The cookbook for computer use was not fetched; its details are unknown.
- Launch demos by Meta for Spark 1.3 and Wonder were not found.

## Key Question 2: Meta open research releases (2025–2026) usable in a hackathon. Which have public weights or APIs now?

### Takeaway
The 2026 items that are usable now are SAM 3.1 (reported available via the Meta Model API) and the 2026 Muse family, with Muse Voice Transcribe as a real-time speech API. Muse Glimmer (30B, single GPU / Mac Mini) is the main open-weights candidate, but its release status is contested in sources. I did not verify the status of V-JEPA 2, SAM 3D, DINOv3, Meta Motivo, Seamless, Audiobox, Movie Gen, Code World Model, Habitat or Agents Research Environments within this budget, so no claim is made about them.

### Cited Findings
- SAM 3.1 announced around March 27, 2026 as a drop-in update to SAM 3, adding object multiplexing to process multiple object tracks concurrently for video segmentation on smaller GPUs — [Blockchain.News](https://blockchain.news/ainews/meta-releases-sam-3-1-with-object-multiplexing-latest-analysis-on-3x-10x-video-segmentation-efficiency-gains) [3P, secondary; cites Meta's post on X]
- The same source headlines "3x–10x" efficiency gains; not verified elsewhere — [Blockchain.News](https://blockchain.news/ainews/meta-releases-sam-3-1-with-object-multiplexing-latest-analysis-on-3x-10x-video-segmentation-efficiency-gains) [3P, UNVERIFIED]
- SAM 3.1 is reported as available on the Meta Model API, where one call returns detections, masks and video tracks (undated) — [Digg](https://digg.com/ai/icmesfai) [3P]
- Conflict: a ComfyUI model page lists SAM 3.1 as a 2025 image-segmentation model; this looks like a third-party repackage and is weighted lower — [ComfyUI Wiki](https://comfyui-wiki.com/en/models/sam/sam3.1) [3P, conflicting]
- SAM 3 baseline (2025 coverage): text and/or image exemplars as input for concept segmentation — [ComfyUI Wiki](https://comfyui-wiki.com/en/models/sam/sam3.1) [3P, 2025 baseline]
- Muse Voice Transcribe: released September 1, 2026; Meta describes it as its first real-time audio perception model. One model handles live transcription, speaker separation and end-of-speech detection; sessions up to about an hour with 20+ speakers; trained across 70+ languages, 25 validated at launch — [Pro Pakistani](https://propakistani.pk/2026/09/02/metas-muse-voice-transcribe-70-languages-and-20-speakers-simultaneously/) [3P] and [Datanorth](https://datanorth.ai/news/meta-launches-muse-voice-transcribe) [3P]
- Muse Voice Transcribe endpoints: model id muse-voice-transcribe-1.0; WebSocket endpoint for live audio and a file-upload endpoint for batch — [Bibigpt explainer](https://bibigpt.co/features/muse-voice-transcribe-explained) [3P, UNVERIFIED against Meta docs]
- Muse Voice Transcribe price: about $0.18 per audio hour ($3 per 1,000 minutes), same for streaming and file upload — [Pro Pakistani](https://propakistani.pk/2026/09/02/metas-muse-voice-transcribe-70-languages-and-20-speakers-simultaneously/) [3P; user's known $3/1000 min matches]
- Caveats on Voice Transcribe: no open weights; Meta's diarization benchmark is self-scored; no per-language word error rate published — [The New Stack](https://thenewstack.io/meta-muse-voice-transcribe/) [3P]
- Muse Voice (consumer feature with custom voices and speed/accent controls) unveiled at Connect, September 23, 2026 — [Etv Bharat](https://www.etvbharat.com/en/technology/muse-voice-transcribe-meta-ai-now-supports-real-time-multilingual-speech-to-text-with-20-plus-speakers-enn26090201991) [3P]. A leak claiming an 80ms custom-voice model is reported by tech-insider; UNVERIFIED — [Tech Insider](https://tech-insider.org/?p=22655)
- Muse Glimmer: open-weights 30B model designed to run on a single GPU or Mac Mini for local/on-device agents — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]
- Conflict on Muse Glimmer release timing: Ars Technica reported on August 10, 2026 that Meta announced Muse Glimmer and planned to open weights of Muse Spark 1.2 within weeks. AI Understanding describes the same August 10 essay as strategy only, with no model, parameter count, license, repository or date — [AI Understanding](https://aiunderstanding.org/news/meta-resumes-open-source-ai-model-releases) [3P, conflicting]. Ars Technica report referenced in summary only (not fetched). Secondary summary says Glimmer can be freely downloaded and modified; license not verified. The user's prior note of Apache 2.0 is not confirmed in these sources.
- An Emergent article (Sept 28, 2026) describes a broad open-model launch, but is internally inconsistent and names no models — [Emergent](https://emergent.sh/news/meta-open-models-2026-officially-launched) [3P, low reliability]
- No Meta FAIR research release dated October 2026 was found in search — [search result set, Oct 2026 query, no direct source]

### Inferences
- Muse Voice Transcribe plus Muse Spark 1.3 (or Wonder) is a complete realtime-audio pipeline available through one API vendor: speech in with speaker separation, reasoning and action out, which is strong for a live meeting or field-capture demo.
- SAM 3.1 on a glasses camera feed or a phone camera would be a visual demo using a Meta-hosted model; verify the API endpoint and pricing ($2.50/1,000 images, $0.20/1,000 video frames per user notes) before committing.
- Muse Glimmer is the only confirmed open-weights option for an offline or privacy-first demo; its license and availability must be checked on the model page before relying on it.

### Gaps
- Status (weights, API, license) of V-JEPA 2, SAM 3D, DINOv3, Meta Motivo, Seamless / translation / voice cloning, Audiobox, Movie Gen / video generation, Code World Model, Habitat, Agents Research Environments: NOT researched within budget. Several are 2025 releases; coordinator instructed to mention them only if still Meta's current tool in Oct 2026, which I could not confirm.
- Meta's own release posts for SAM 3.1 and Muse Glimmer were not fetched.
- The Muse Voice Transcribe endpoint names and WebSocket details come from third-party explainers; confirm against Meta's API docs.

## Key Question 3: Meta wearables: Ray-Ban Meta, Oakley Meta, Meta Ray-Ban Display, Wearables Device Access Toolkit. Is it usable by hackathon participants now? Neural band?

### Takeaway
The Wearables Device Access Toolkit 1.0 was officially launched at Meta Connect 2026 (Sep 24 2026 recap), after a year in developer preview. Sources conflict on whether third-party apps can be published publicly: Meta's recap implies a full launch, while late-September 2026 coverage says publishing is still closed and GA is targeted for 2026. For a hackathon, development and testing with the Mock Device Kit or real glasses is the safe path; public distribution is uncertain.

### Cited Findings
- Meta Connect 2026 developer recap (Sep 24, 2026): Wearables Device Access Toolkit 1.0 officially launched after a year in developer preview; lets developers extend existing mobile apps to AI glasses. Features: "Hey Meta" invocation, speech recognition, swipe navigation via Meta Neural Band, camera capture, voice streaming, motion tracking. One integration covers display and displayless glasses — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]
- Conflict: a late-September 2026 article reports the Wearables FAQ still says "publishing is currently not available during the Developer Preview phase", and that GA for publishing is targeted for 2026 — [vr.org, Sep 23 2026](https://vr.org/articles/meta-glasses-three-tiers-wearables-toolkit-publishing-connect-2026) [3P, UNVERIFIED against live FAQ]; see also [Meta Wearables FAQ](https://developers.meta.com/wearables/faq) [VENDOR; content as seen in search summary, 2025 era]
- Development path: Mock Device Kit simulates a device and its permissions so developers can build without glasses; full docs at wearables.developer.meta.com/docs/develop; sample app and tutorial provided — [Meta FAQ / developers.meta.com](https://developers.meta.com/wearables/faq) [VENDOR; 2025-era text]
- Supported hardware named in the toolkit documentation (2025-era): Ray-Ban Meta Gen 1 and 2, Ray-Ban Meta Display, Oakley Meta HSTN, Oakley Meta Vanguard — [UploadVR](https://www.uploadvr.com/meta-wearables-device-access-toolkit-public-preview/) [3P, December 2025 sources]
- Launch limitations recorded at the December 2025 preview: no Meta AI in the toolkit; developers must run their own continuous audio stream and send camera images to their own AI model, at their own cost, affecting battery life; sending imagery to the Ray-Ban Display HUD and reading Neural Band gestures were unsupported at launch — [UploadVR](https://uploadvr.com/meta-wearables-device-access-toolkit-announced-smart-glasses-sdk) [3P, December 2025]. Note the Connect 2026 recap now lists Neural Band swipe navigation as a feature, so this limitation may have changed at 1.0; verify.
- Camera via the toolkit; microphone and speakers via iOS or Android Bluetooth profiles — [Meta developer blog](https://developers.meta.com/blog/introducing-meta-wearables-device-access-toolkit/) [VENDOR, 2025-era]
- Full toolkit capabilities, including Wearables Developer Center, are limited to AI-glasses supported countries — [Meta FAQ](https://developers.meta.com/wearables/faq) [VENDOR, 2025-era]
- Web apps for Meta Ray-Ban Display, built with standard web APIs (no native app or SDK needed): device position, location, wrist motion via Neural Band; text input via dictation, handwriting or on-screen keyboard; new UI Toolkit for Ray-Ban Display — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]
- Discovery: experiences will be findable on Ray-Ban Display and in a curated section of the Meta AI app; submission details "coming soon" — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]
- Meta AI Connectors (developer preview): connect a service via API or MCP server so users access it inside Meta AI without an app. WebMCP (developer preview): lets Meta AI complete tasks inside a web app using only functions the developer exposes — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]
- Hardware prices reported at Connect (single secondary source, weak): Ray-Ban Meta (Gen 3) from $449 available now; Ray-Ban Meta Audio from $349 with preorders from Oct 13; Muse Charm expected in December; Meta VR Glasses $1,299.99 spring 2027 — [Tom's Guide](https://www.tomsguide.com/computing/smart-glasses/meta-connect-2026-kicks-off-in-september-date-time-and-mystery-new-smart-glasses-teased) and [ExitLag roundup](https://www.exitlag.com/news/meta-connect-2026-announcements/) [3P; ExitLag is a gaming-VPN blog, UNVERIFIED]
- Meta VR Glasses: compute in a tethered puck, runs Meta Quest OS, hardware ships spring 2027; v207 SDKs (Unity, Unreal, Android, Web) available now for building — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]

### Inferences
- A hackathon team can build and test a glasses-integrated app now with the Mock Device Kit, and with real Ray-Ban Meta glasses if the team has them. Whether judges or users can run it on glasses beyond tester groups depends on the unresolved publishing status.
- The Ray-Ban Display web-app path appears to avoid native SDK publishing friction, but its distribution is "curated" and submission details are not published yet. Treat this as an opportunity, not a guaranteed channel.
- A glasses demo with Meta-hosted models needs the team's own AI pipeline when using the toolkit at launch (no Meta AI in the toolkit per December 2025 sources). Pair with Muse Spark 1.3 or SAM 3.1 through the Model API, paying for camera frame and audio streaming.

### Gaps
- Whether Connect 2026 changed the December 2025 launch limits (no Meta AI, display imagery, Neural Band) is not confirmed.
- Publishing status conflict (open to public vs. select partners only) is unresolved.
- Hardware prices from ExitLag/Tom's Guide not verified against Meta newsroom.
- Developers.meta.com/wearables pages were not fetched directly; the FAQ text is from search summaries.

## Key Question 4: Meta platforms usable by developers: WhatsApp Business AI / Cloud API, Instagram, Messenger, Horizon / Quest. What APIs exist for AI agents?

### Takeaway
The clearest agent-facing APIs in Meta's 2026 stack are the Meta Model API (GA globally at Connect 2026), Meta AI Connectors and WebMCP (both in developer preview), and a WhatsApp Business Tools MCP server reported in September 2026. Connect 2026 announced no developer API changes for Messenger or Instagram; Instagram appears only as a distribution surface for Horizon-created games.

### Cited Findings
- Meta Model API: generally available globally, announced at Meta Connect 2026; enterprise support via Meta's first-party API and third-party partners; no pricing beyond "frontier performance at accessible prices" — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]
- WhatsApp Business Tools MCP server (reported September 2026): lets agents such as Claude, Cursor, Codex and ChatGPT handle setup tasks: creating accounts, registering numbers for the Cloud API, editing templates, testing webhooks — [Mezha, citing TechCrunch](https://mezha.net/eng/?p=3723224) [3P, secondhand; verify against Meta docs]
- WhatsApp pricing (secondary guide, July 29, 2026 update): pricing based on delivered template messages, varying by market and by marketing, utility or authentication category; free-form replies allowed within 24 hours of the customer's last message, otherwise an approved template is required — [Visito AI guide](https://www.visitoai.com/blog/whatsapp-business-ai-chatbot-ultimate-guide) [3P, low-authority; verify pricing with Meta]
- WhatsApp build paths described by sources: Meta's own business agent (eligible businesses), managed platforms, or direct Cloud API build — [Visito AI guide](https://www.visitoai.com/blog/whatsapp-business-ai-chatbot-ultimate-guide) [3P]
- Connect 2026 developer recap: no developer API changes announced for WhatsApp, Messenger or Instagram — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]
- Meta AI Connectors (developer preview) and WebMCP (developer preview) — see Q3 citation [VENDOR]
- Horizon Create (mobile, no code) and Horizon Studio (web, prompts plus visual editing), both on the Meta Horizon Engine's agentic creation; published games reach people in feeds across Facebook, Instagram and Horizon; early access sign-up at developers.meta.com/horizon-worlds/ — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]
- Meta VR Start Developer Competition 2026: runs Sep 24 to Nov 18, 2026; $1M across 20 cash prizes; top prizes $100,000 per category; winners live Dec 11, 2026; open to Meta Horizon Start Program members — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]. Relevant if the team is also eligible; check for conflicts with the Global AI Hackathon rules.
- Meta VR CLI (platform docs, device debugging, profiling) and Meta XR Operator (agent-driven build, test and verify loop in Meta XR Simulator) — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]

### Inferences
- For an "agent that does things in WhatsApp" demo, the WhatsApp Business Tools MCP is the newest developer hook, but the Cloud API's 24-hour and template rules still constrain the experience. Outbound-first flows need approved templates.
- Meta AI Connectors plus WebMCP suggest a path where a team's own web app or service becomes an action surface inside Meta AI. This is the most "only possible now" distribution angle in the stack, but it is still in developer preview.
- Instagram is currently a distribution surface (Horizon games), not an AI API. Do not build the demo around an Instagram API without new evidence.

### Gaps
- WhatsApp Business Tools MCP details (tools, scopes, rate limits, availability) were not verified from Meta docs.
- Current WhatsApp pricing per market was not verified from a primary source.
- Messenger API status in 2026 was not researched.
- WebMCP and Meta AI Connectors documentation and access requirements were not fetched.

## Key Question 5: What kinds of demos at Meta Connect 2026 (Sept 2026) and LlamaCon / Meta dev events drew the most attention?

### Takeaway
Meta's Connect 2026 developer recap names no specific demos and provides no attention metrics, so there is no reliable evidence on which demos drew the most attention. Connect's themes per secondary coverage were AI agents, smart glasses, VR and immersive entertainment. The hackathon itself is confirmed as a 10-day virtual event with a $1M prize pool, but its dates conflict across sources.

### Cited Findings
- Meta Connect 2026 keynote: September 23, 2026 (Menlo Park); developer sessions September 24, 2026 — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR, post date Sep 24]; [Road to VR date announcement](https://roadtovr.com/meta-connect-2026-date-announcement/) [3P]
- Main themes per post-event roundup: AI agents, smart glasses, virtual reality and immersive entertainment; four new devices listed (secondary, weak source) — [ExitLag roundup](https://www.exitlag.com/news/meta-connect-2026-announcements/) [3P, UNVERIFIED]
- Post-event coverage is limited and sources disagree on device details; treat as preliminary — [Tom's Guide](https://www.tomsguide.com/computing/smart-glasses/meta-connect-2026-kicks-off-in-september-date-time-and-mystery-new-smart-glasses-teased) [3P]
- Muse personal agent debut (September 8, 2026, ahead of Connect) — [Axios](https://axios.com/2026/09/08/meta-debuts-muse-personal-ai-agent) [3P]
- Global AI Developer Hackathon: 10-day virtual event run by Meta Superintelligence Labs, open worldwide; $150 Meta Model API credit per participant; $1M prize pool; Indie Developer and Startup tracks; live workshops with Meta's team — [CourseJoiner](https://coursejoiner.com/hackathon/meta-global-hackathon-2026-1/) [3P]; [Sequenzy promotional email](https://www.sequenzy.com/api/email-examples/j5iypr0umhagob6hpglchdwg/html) [3P]
- Hackathon dates conflict: Sequenzy email says the application window runs October 26 through November 4 but also says apply by October 25 (internally inconsistent). Meta's Connect 2026 developer recap says applications had not yet opened, sign-up at dev.meta.ai, and cookbook resources on GitHub (meta-models) — [Meta Connect 2026 developer recap](https://developers.meta.com/blog/meta-connect-recap/) [VENDOR]. Check dev.meta.ai/events/global-hackathon directly (referenced in search summary, not fetched).
- Hackathon credit and prize details are relayed by aggregators; confirm exact credit amount and rules on Meta's page — [CourseJoiner](https://coursejoiner.com/hackathon/meta-global-hackathon-2026-1/) [3P]

### Inferences
- Because Meta's developer recap emphasizes agentic coding (Muse Code multi-agent, Meta XR Operator, Horizon agentic creation) and agent connectors, judges are likely to reward agent-driven demos that show an action happening in the real world, not a chatbot answer.
- Demos that combine glasses hardware, live audio and a Meta-hosted model are the closest match to Meta's 2026 announcements, but there is no evidence of which ones won attention at Connect.

### Gaps
- No evidence on which Connect 2026 demos drew the most attention; no viewership or social metrics found.
- LlamaCon 2026 or other Meta dev events were not researched; no evidence found in this pass.
- Hackathon dates and application status must be confirmed on dev.meta.ai before the team plans around the Oct 26 – Nov 4 window.

## Cross-cutting: Conflicts and verification list
- Muse Glimmer open-weights timing and license: conflict between Ars Technica (per summary) and AI Understanding.
- Wearables Toolkit publishing: developers.meta.com recap ("officially launched") vs. vr.org Sept 23 article ("publishing still closed; GA targeted 2026").
- Neural Band gesture support: unsupported at December 2025 preview vs. listed as swipe navigation at 1.0.
- SAM 3.1 release date: March 2026 (secondary) vs. 2025 (ComfyUI listing).
- Muse Spark 1.3 max-tier availability: Sept 4 API availability claim vs. "pending safety testing" statement.
- Hackathon application window: Oct 26 – Nov 4 (user brief; Sequenzy) vs. "applications not yet opened" (Connect recap) vs. apply-by Oct 25 (Sequenzy).
