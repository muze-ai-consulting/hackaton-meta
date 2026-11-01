# Meta Global AI Developer Hackathon: rules, organizer signals, and 2026 sponsor-hackathon evidence

Research date: 2026-11-01. The official Rules PDF was not reachable. Everything below marked UNVERIFIED comes from a secondary source that could not be checked against the primary text. The Cerebral Valley waiver page returned only a "Loading..." placeholder. Meta's event page and the Cerebral Valley page both say the Official Rules "will be published before the Hackathon begins on October 26, 2026 and must be accepted by the selected participants." Mark should read the accepted Official Rules in his participant account before relying on any rule below. That is the single highest-value check.

## Key question (a): What the official rules allow and require

### Takeaway
No reachable primary source says anything about third-party AI coding tools (Claude Code, Cursor, Copilot, Codex), pre-existing code, open-source libraries, or non-Meta model providers. The only rule-like statement about build platforms is a secondary-source claim (UNVERIFIED) that permitted platforms are Meta Model API, Muse Code, or Meta open-weights models. If that holds, using Claude or OpenAI inside the product is a real risk. Treat this as the top open question.

### Cited Findings
- Meta's event page lists the eligibility exclusions (Meta and Cerebral Valley staff, contractors, interns; government-affiliated people; Belarus, China, Russia, Ukraine, Syria; sanctioned regions) and "Every project enters one track." Team size is not stated. Submissions are due "Nov 4, 9:00 PM ET." Video length, repository requirements, live-demo requirement, and deliverable format are not stated. Rules on AI coding tools, pre-existing code, open source, and third-party models are absent. [Meta event page](https://dev.meta.ai/events/global-hackathon); [Cerebral Valley](https://cerebralvalley.ai/e/meta-ai-developer-hackathon)
- The same pages say of Muse Code only that participants can "code faster with Muse Code coding agent." No usage rule is given. [Meta event page](https://dev.meta.ai/events/global-hackathon)
- Models named on the official pages: "Muse Spark series, Muse Wonder, Muse Image and SAM 3.1 through Meta Model API," plus "Meta open weights models." No rule requires a minimum share of Meta models or forbids other providers. [Cerebral Valley](https://cerebralvalley.ai/e/meta-ai-developer-hackathon)
- UNVERIFIED (secondary, cites "Official Rules" as described by the article, which says the author could not open the document): "Permitted build platforms: the Meta Model API, Muse Code (Meta's multi-agent coding tool), or Meta's open-weights models. The article gives no rules on AI-generated code or on other AI tool use." Pre-existing code is "Not addressed." [MadRobot blog](https://madrobot.blog/2026/10/03/meta-global-ai-developer-hackathon-1-million-prizes-muse-model-api/)
- UNVERIFIED (secondary, same article, citing the Official Rules as described): entrants must be 18 or over; entrants "must own everything in their project"; "Nothing shared during the event is confidential"; entrants grant the organisers "a royalty-free, worldwide, perpetual and irrevocable licence to use, publish and modify the submission"; winners' names and likenesses may be used in publicity; winners pay their own taxes. [MadRobot blog](https://madrobot.blog/2026/10/03/meta-global-ai-developer-hackathon-1-million-prizes-muse-model-api/)
- UNVERIFIED (secondary, one search summary, source not opened): Indie track "in teams of up to four." The primary Meta page gives no team size, and the MadRobot article says no maximum is stated. The two conflict. Candidate source not opened: [CryptoAIMeta](https://cryptoaimeta.com/meta/meta-1-million-ai-hackathon-rules-who-can-enter/)
- UNVERIFIED (secondary): "Teams must name one representative, who receives any prize." [MadRobot blog](https://madrobot.blog/2026/10/03/meta-global-ai-developer-hackathon-1-million-prizes-muse-model-api/)
- Prize pool: "$1,000,000 in total prizes," with no per-track or per-place split on the primary pages. UNVERIFIED secondary split (Startup: 250k/150k/75k/50k/25k; Indie: 150k/100k/75k/50k/25k; bonus up to $50k) is attributed to the Official Rules by MadRobot. [Meta event page](https://dev.meta.ai/events/global-hackathon); [MadRobot blog](https://madrobot.blog/2026/10/03/meta-global-ai-developer-hackathon-1-million-prizes-muse-model-api/)
- Conflicting claim: one search summary said a post reported the Official Rules were published on Oct 25. That post was not opened, so it is UNVERIFIED. [Meta event page](https://dev.meta.ai/events/global-hackathon) still says "will be published."

### Inferences
- Because the primary pages say nothing about AI coding tools, the practical answer depends entirely on the accepted Official Rules text. If it matches the MadRobot summary's "permitted build platforms" wording, the product must be built on Meta's stack, and Claude or OpenAI calls in the product would be out of bounds. Claude Code as a development tool is a separate question. The summary does not address it, and the more natural reading is that a dev tool is not a "build platform," but that is an inference.
- The IP grant (if the summary is accurate) is broad: a perpetual, irrevocable license to the organisers. For a product with client data or a planned startup spin-off, that is a material term.

### Gaps
- Official Rules text (eligibility, tools, pre-existing code, third-party models, IP, team size, submission format, video length) could not be fetched. Source to check: the participant acceptance step at [Meta event page](https://dev.meta.ai/events/global-hackathon).
- Whether Claude Code, Cursor, or Codex count as permitted development tools: no source found.
- Whether a non-Meta model may run inside the submitted product: no source found.
- Whether pre-existing code is allowed (repo started before Oct 26): no source found.

## Key question (b): Hackathon credits and sponsor credits

### Takeaway
The $150 Model API credit figure comes from aggregators and a reported invite email, not from Meta's public page. Whether those credits apply to the contributor tier is not confirmed anywhere reachable. Partner credits (Baseten, Modal, Fireworks, $100 each) are for Meta's open-weights models, not the Muse API.

### Cited Findings
- Meta's public page gives no credit amount. It says only "free Model API credits" in Meta's Sept 24, 2026 post. [Meta for Developers recap](https://developers.meta.com/blog/meta-connect-recap/)
- Aggregators state $150 per participant. [AImagazine](https://aimagazine.blog/meta-opens-its-1m-global-ai-developer-hackathon-20000-seats-150-api-credits-each-and-applications-close-october-25/); [VibeCodersLife](https://vibecoderslife.com/post/meta-ai-developer-hackathon-2026) (the latter says the invite email states the figure). Not checked against an invite email.
- Partner credits, to "select participants": Baseten "$100 in credits and 2M TPM rate limits" (for Meta open-weights models); Modal "$100 in credits" plus serverless GPUs and sandboxes; Fireworks "$100 in credits" plus a workshop by Sinan Ozdemir. [Cerebral Valley](https://cerebralvalley.ai/e/meta-ai-developer-hackathon)
- Contributor tier: Meta's Sept 24 post does not mention a contributor tier. [Meta for Developers recap](https://developers.meta.com/blog/meta-connect-recap/). A search summary said the contributor tier is a lower price in exchange for permission to train on your data. One aggregator reads contributor pricing as $0.10 input / $0.20 output per million tokens against $1.25 / $4.25 standard. UNVERIFIED. [GetAIPerks](https://www.getaiperks.com/ja/ai/meta-muse-for-startups); [FourWeekMBA](https://fourweekmba.com/ai-meta-model-api-sdk-compatibility-pricing/)
- Open-weight endorsement: Meta's Sept 24 post describes Muse Glimmer as "an open-weights, 30B-parameter model for developers who need local control or on-device agents," and the partner credits are tied to open-weights serving. [Meta for Developers recap](https://developers.meta.com/blog/meta-connect-recap/); [Cerebral Valley](https://cerebralvalley.ai/e/meta-ai-developer-hackathon)

### Inferences
- The project's planning budget of 150 credits (per the repo's CLAUDE.md) matches the aggregator figure, but nothing public confirms that the credits cover contributor-tier calls. The Model API dashboard for the account should show the balance and tier before any spend.
- The partner credits point to open-weights inference as a sponsor-endorsed path. That is a signal about what the organisers expect developers to run, but it is not a rule.

### Gaps
- Whether the $150 is granted per participant and applies to contributor-tier usage: no primary confirmation found.
- Contributor-tier price figures: only one aggregator reading, not checked against Meta's pricing page (docs URL seen in search: https://ai.developer.meta.com/docs/models/, not fetched).

## Key question (c): What Meta organizers and judges have signaled

### Takeaway
The only organizer-written statements reachable are the two themes and the judging-criteria sentences. Kickoff (Oct 26) and workshop content could not be found. The judges are not named anywhere. Judging weights exist only in a secondary source.

### Cited Findings
- Theme 1, "Build for Your World": "Bring Meta's models into your domain." Theme 2, "Push the Frontier": "Use Meta's models to tackle challenges in software, robotics, manufacturing, energy, materials and beyond." Application screening is "scored equally" on project idea and technical skill. [Cerebral Valley](https://cerebralvalley.ai/e/meta-ai-developer-hackathon); [Meta event page](https://dev.meta.ai/events/global-hackathon)
- Indie track: "Judged on creativity, technical ambition, and whether it works." Startup track: "Judged on technical execution and whether it holds up in production." No weights on either primary page. [Meta event page](https://dev.meta.ai/events/global-hackathon)
- UNVERIFIED judging weights (secondary, attributed to the Official Rules as described by MadRobot): Impact 30%; creative use of Meta's AI tools 25%; demo including video 25%; technical depth and execution 20%. If accurate, 25% goes to how a project uses Meta's tools, which is the one sponsor-specific criterion. [MadRobot blog](https://madrobot.blog/2026/10/03/meta-global-ai-developer-hackathon-1-million-prizes-muse-model-api/). The same article says the judges are not named.
- Schedule per Meta: judging Nov 4 to 8; closing ceremony with live finals and winners Nov 9. "Dates may be subject to change at Meta's sole discretion." [Meta event page](https://dev.meta.ai/events/global-hackathon)
- Adjacent Meta signal (separate challenge, not the hackathon): Paradigm's Muse Spark Open kernel challenge, dated 10.22.2026, with Meta and Andromeda as partners, runs to Nov 19. Its stated goal is making the open-weight model "faster and cheaper to serve." It is a signal about where Meta's ecosystem wants builder effort, not a judging rule for the hackathon. [Paradigm](https://www.paradigm.xyz/writing/muse-spark-open-kernel-challenge)
- A Meta for Developers X post about the hackathon with Fireworks, Baseten, and Modal reads (search snippet, page returned HTTP 402 when fetched, so the text is only partly verified): "so you can run Muse Glimmer and Muse Spark Open on the tools you already build with. Compete for a share of $1M in prizes." Date not confirmed. [Meta for Developers X post](https://x.com/MetaforDevs/status/2112971571321332179)
- The Meta page's Discord office hours and live workshops run Oct 27 to Nov 4. No public FAQ was found. [Meta event page](https://dev.meta.ai/events/global-hackathon)

### Inferences
- Meta's own language makes "use Meta's models" the central requirement and "whether it works in production" the startup bar. The Paradigm challenge suggests Meta's organisers value efficiency and serving of open-weight models, but this does not show what the hackathon judges reward.
- If the UNVERIFIED 25% "creative use of Meta's AI tools" weight is correct, a product that is strong on domain but uses Meta's models only as a generic LLM would lose points there. This is an inference from a secondary source.

### Gaps
- Kickoff livestream (Oct 26) content and any speaker remarks: no post-kickoff coverage found in any search. Not confirmed.
- Discord announcements and FAQ updates after Oct 26: none found.
- Organizer or DevRel posts on X or LinkedIn in late Oct 2026, beyond the X post above (not retrieved in full): none verified.
- Judge names and judge statements: none published in reachable sources.
- Any "what we want to see" statement from Meta: none found. The Cerebral Valley/Meta themes are the closest equivalent.

## Key question (d): 2026 sponsor-run AI hackathons, what won and whether it mirrored the sponsor

### Takeaway
The "synthetic investors" winner could not be verified. No 2026 Anthropic/Claude hackathon winner matching that description was found. The closest matches are a synthetic-population simulation (Sim Francisco, 2nd at Opus 4.8 Build Day) and a synthetic-user-persona product (Zenith, Sept 2025). Anthropic's official winner pages show a mix of domain verticals, with one sponsor-specific award category (Best Use of Claude Managed Agents). That supports a narrower version of the thesis than "sponsors reward the product they dream of."

### Cited Findings
- Claude Opus 4.8 Build Day (San Francisco, 12-hour event, about 310 participants per secondary coverage). Official winners: 1st Tekton (3D reconstruction of Tang Dynasty architecture); 2nd Sim Francisco (census-based digital twin of SF population, 10,000 synthetic residents, election polling); 3rd Custom Universe (phone photo to editable 3D scene). The official page gives no judge rationale and names no judges, and says of Sim Francisco: "This does not represent an Anthropic endorsement of using AI-simulated election predictions as a use case." [Anthropic Opus 4.8 winners](https://claude.com/resources/articles/meet-the-winners-of-our-claude-opus-4-8-build-day-hackathon)
- Built with Opus 4.7 (Claude Code hackathon, official article dated June 15, 2026 per the page; announcement date not stated on the page). Official listing: 1st Medkit (simulates patient encounters for medical training); 2nd Wrench Board; 3rd Maieutic. Special awards: Most Creative Use of Opus 4.7 (Virtual Puppet Theater); "Keep Thinking" Prize (MaestrIA); Best Use of Claude Managed Agents (ARIA). No judge rationale, no judge names, no prize amounts on the page. No investor, VC, or synthetic-investor project on the list. [Anthropic Opus 4.7 winners](https://www.claude.com/blog/meet-the-winners-of-built-with-opus-4-7-claude-code-hackathon)
- Built with Opus 4.6 (Feb 2026, about 13,000 applicants). Secondary source only: judges Boris Cherny, Cat Wu, Thariq Shihpar, Lydia Hallie, Ado Kukic, Jason Bigman; first place reported as CrossBeam (permit corrections for California builders); Postvisit.ai also reported as a winner. UNVERIFIED. Official page not opened. [Claude Code hackathon winners roundup](https://kaels-lab.pages.dev/ai/claude-code-hackathon-winners/)
- "Synthetic investors" search: no page with that winner, project, or phrase found across three searches. Closest match, an earlier event: Anthropic x Forum Ventures hackathon (NYC, Sept 2025), winner Zenith, which validates product-market fit by chatting with synthetic user personas, with $15,000 in API credits. Secondary Chinese-language aggregator only; not the official Devpost. [Anthropic x Forum Ventures NYC 2025 record](https://jixiaxue-kb.pages.dev/w/research/黑客松获奖项目灵感库/evidence/Anthropic-Forum-Ventures-NYC-2025-09/)
- OpenAI "Agents Everywhere" hackathon with OpenAI (secondary LinkedIn-based summary; date not confirmed): 687 projects, 15 finalists, 5 winners; 1st place Sidekick (Alexander Payne); judges not listed. OpenAI Build Week Challenge 2026 (July–Aug): winners and judges not found. The Hugging Face Build Small hackathon had OpenAI as an anchor sponsor; 23 winning projects announced across both tracks, OpenAI podium results not found. [Hugging Face Build Small](https://huggingface.co/organizations/build-small-hackathon) (search snippet)
- Google: Gemini 3 Hackathon (Devpost, run by Google DeepMind), deadline Feb 10, 2026, $100,000 prize pool; winners page exists but names were not retrieved. [Gemini 3 Hackathon listing](https://frontlinesmedia.in/gemini-3-hackathon-2026-build-whats-next-with-google-deepmind/). Google AI Agents Hackathon (lablab.ai, Apr 7 to May 5, 2026, voice agents with Gemini and the Live API); winners not retrieved. [lablab.ai](https://lablab.ai/ai-hackathons/google-ai-agents-hackathon)

### Inferences (thesis test)
- Strong form ("sponsor hackathons reward the product the sponsor dreams of"): not supported by the evidence found. The Anthropic winner list is domain-diverse. The one project that fits a sponsor-favored pattern (a simulation of a population) is the one the sponsor explicitly disclaimed.
- Narrower form ("sponsor hackathons reward visible use of the sponsor's own product"): partly supported. Anthropic's 2026 winner lists include a sponsor-specific award for "Best Use of Claude Managed Agents" and "Most Creative Use of Opus 4.7." That is a direct product-use criterion, the same shape as Meta's 25% "creative use of Meta's AI tools" if that weight is accurate.
- Caveat: most of the 2026 evidence is official winner pages without judge rationale. Causation (why these won) cannot be read from them.

### Gaps
- "Synthetic investors" winner: not verified; no source found.
- Judges' stated reasons for any 2026 Anthropic winner: none on the official pages.
- OpenAI Build Week 2026 winners and judges: not found.
- Google Gemini 2026 winner names: not retrieved.

## Key question (e): Other signals relevant to the Muze project

### Cited Findings
- Meta's dates: applications closed Oct 25, 11:59 PM ET (or earlier at 20,000 places); submissions due Nov 4, 9:00 PM ET; judging Nov 4 to 8; winners Nov 9. [Meta event page](https://dev.meta.ai/events/global-hackathon)
- One aggregator says Oct 26 to Nov 5 and another says the winners announcement is Nov 10 (IST conversions). The primary page gives Nov 4 and Nov 9. [Meta event page](https://dev.meta.ai/events/global-hackathon); [MadRobot blog](https://madrobot.blog/2026/10/03/meta-global-ai-developer-hackathon-1-million-prizes-muse-model-api/)

### Inferences
- The CLAUDE.md deadline (Nov 4, 18:00 Chile) is earlier than the official Nov 4, 21:00 ET (23:00 Chile). The margin is correct on the primary date, and the project should not treat the later figure as the cutoff.

## Verdict summary for the thesis and open risks

1. Read the accepted Official Rules in the participant account. Priority questions: (i) whether Claude/OpenAI/Anthropic models may run inside the submitted product; (ii) whether AI coding tools and pre-existing code are allowed; (iii) the IP license grant; (iv) team size.
2. Judging weights (30/25/25/20, with 25% for creative use of Meta tools) are UNVERIFIED. Plan as if the Meta-tool criterion matters, because the primary pages say the Startup track is judged on "technical execution and whether it holds up in production," and the Indie track on "creativity, technical ambition, and whether it works."
3. Credits: $150 and contributor-tier coverage are unconfirmed. Check the account balance before running the full budget.
4. Sponsor thesis: the evidence supports "sponsor-specific product use gets rewarded" more than "sponsor's dream product wins." The "synthetic investors" winner was not found.

## Unverified or unreachable sources (for the report writer)
- Official Rules PDF: not reachable.
- Cerebral Valley waiver page: placeholder only (https://cerebralvalley.ai/e/meta-ai-developer-hackathon/waiver).
- Meta for Developers X post: HTTP 402 when fetched.
- Organizer LinkedIn posts from Oct 2026: not retrieved.
- Kickoff (Oct 26) coverage: none found.
