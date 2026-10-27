# How hackathon judges decide winners (judge's-eye view, sponsor hackathons 2024-2026)

Research date: 2026-10-26. Scope: published rubrics and rules, judge and practitioner writing, sponsor-judge preferences, and loss patterns, with emphasis on Meta, Google, OpenAI, Anthropic and Microsoft events.

Evidence labels used below:
- **[HARD]** = rules or judging criteria text from an official event page, fetched directly or via a summary of it.
- **[SECONDARY]** = a copy, mirror, or search snippet of a rubric or rule that I could not verify against the official page.
- **[OPINION]** = judge, practitioner, vendor or training-company writing. Not evidence of how judges actually scored.

Bottom line: published sponsor rubrics converge on five things: a working demo, real impact on a named user, originality, a visible use of the sponsor's technology, and sound execution. No big-tech sponsor I could verify published a 2024-2026 rubric with Meta-specific weights. Judges' behavior (short time per project, video first, the opening sentence decides) comes almost entirely from [OPINION] sources, so treat it as strong practitioner consensus rather than measured fact. Searches for Reddit and Hacker News judge threads returned nothing usable.

---

## Key Question 1: Standard judging criteria and weights in big sponsor hackathons

### Takeaway
Where weights are published, the demo or working product carries the most weight (30% in the Anthropic-sponsored Opus 4.6 hackathon), and use of the sponsor's technology is a separately scored criterion at roughly 20-25%. Meta has published criteria for its Llama events, but with no weights, and I could not find a 2026 Meta rubric.

### Cited Findings
- [HARD] Built with Opus 4.6 (Cerebral Valley + Anthropic, Feb 10-18, 2026). Stage 1 is async: six Anthropic judges score independently on Demo (30%), Impact (25%), Opus 4.6 Use (25%, "Did they go beyond a basic integration?"), and Depth & Execution (20%). Top 6 are judged live from pre-recorded 3-minute demos. Video cap: 3 minutes. Source: [Hackathon Rules & Judging, mirrored copy](https://huggingface.co/datasets/introvoyz041/postvisit/blob/main/data/docs/hackathon-rules.md). **Caveat:** this is a secondhand mirror. The official cerebralvalley.ai page returned 404, so the weights are not verified against the original.
- [HARD] Anthropic's own winners post (Apr 20, 2026) states no judging criteria and gives no judge reasoning. It notes that "four out of five winners were not professional developers." Source: [Meet the winners of our Built with Opus 4.6 Claude Code hackathon](https://claude.com/blog/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon).
- [HARD] Microsoft AI Agents Hackathon (2025 official rules): five criteria, each 20%: Innovation ("Is the project premise interesting and original?" and "Is the demo video engaging and representative?"), Impact (valuable to others; usable by an organization), Usability (solves a real problem; aligns with Responsible AI), Solution Quality (repo complete with documentation, instructions and security practices), and Alignment with Hackathon Category ("Are AI technologies central to the functionality or just a minor addition?"). Video must be 5 minutes or less and must explain how an agentic framework helped build it. Decisions are "final and binding." Source: [Microsoft AI Agents Hackathon official rules](https://microsoft.github.io/AI_Agents_Hackathon/rules/).
- [HARD] Meta-sponsored: Llama Impact Pan-LATAM Hackathon (lablab.ai, Nov 22-25, 2024; Meta AI mentors). Four criteria, no weights: Application of Technology ("how effectively the model(s) are integrated, focusing on the agent's ability to perform tasks autonomously"), Presentation, Impact ("how well it fits into business areas"), and Originality. Submissions: cover image, video presentation, slide deck, public GitHub repo, and demo URL. The page gives no video length. Source: [Llama Impact Pan-LATAM Hackathon](https://lablab.ai/event/llama-impact-hackathon-pan-latam).
- [HARD] Meta LlamaCon Hackathon (San Francisco, May 2025; Meta blog dated May 13, 2025): 44 submitted projects, two judging rounds down to a top six, judges drawn from Meta and sponsors (Groq, CrewAI, Tavus, Lambda, Nebius, SambaNova), $35K total prizes, and a special prize for "best usage of Llama API." The post does not state judging criteria. Source: [Meta LlamaCon hackathon](https://ai.meta.com/blog/llamacon-hackathon/).
- [SECONDARY] Okta-hosted Devpost-style rules (search snippet): Stage 1 is pass/fail on theme fit and required APIs/SDKs. Stage 2 has three equally weighted criteria: creativity and originality, implementation, and potential impact. No separate design criterion. Source: [Okta developer forum, judging criteria thread](https://devforum.okta.com/t/what-are-the-judging-criteria-for-the-hackathon/15842).
- [HARD, partial] Google Gemini API Developer Competition: the official page (ai.google.dev/competition) redirected to AI Studio and I could not retrieve scoring. A Google staffer's forum reply (as reported in search results) says judges "score the app against the judging criteria and how prominently the Gemini API is used." Forum replies also say code is required and omitting it "may result in disqualification." Sources: [Google AI forum, full code thread](https://discuss.ai.google.dev/t/do-we-need-to-submit-the-full-code-how-will-judges-verify-partial-code/33566); [Competition rules](https://ai.google.dev/competition?authuser=0).
- [SECONDARY] Gemini 3 Hackathon (Google DeepMind on Devpost, deadline Feb 10, 2026): a third-party blog gives Technical Execution 40%, Innovation & Wow Factor 30%, Potential Impact 20%. These add to 90%, and I found no corroboration. The gemini3.devpost.com rules page returned 403. Source: [thenewviews.com, Gemini 3 hackathon](https://thenewviews.com/gemini-3-hackathon/). **Treat as unverified.**
- [SECONDARY] Kaggle "Vibe Code with Gemini 3 Pro in AI Studio": hard filters were use of the Gemini 3 API, a video demonstration, and a live public demo URL. It drew 4,097 submissions in one week. Source: [Gemini 3 Kaggle hackathon winners (Medium/PlainEnglish)](https://ai.plainenglish.io/gemini-3-kaggle-hackathon-winners-officially-announced-4e762f6f9eea).
- [SECONDARY] AI Tinkerers events sponsored by Anthropic (Paris, Abu Dhabi), per a search summary I did not fetch: running code 25%, innovation 25%, real-world impact 25%, theme alignment 25%. Source: [AI Tinkerers Paris x Anthropic](https://paris.aitinkerers.org/p/ai-tinkerers-and-anthropic-ai-agents-hackathon-in-paris). Do not mix with the Cerebral Valley event.
- [SECONDARY] GovTech x OpenAI Hackathon 2024 (Singapore, Nov 22, 2024), listed as scoring five areas: effective use of the AI model, innovative use case, implementation quality, presentation clarity, and practical real-world impact. No weights. Source: [GovTech x OpenAI Hackathon 2024](https://www.tech.gov.sg/events/govtech-openai-hackathon-2024/). No OpenAI gpt-oss rubric was found. The gpt-oss prize tracks were Best Overall, Weirdest Hardware, Most Useful Fine-Tune, Wildcard and For Humanity, with no scoring described ([Luma event page](https://luma.com/aic-oss)).
- [SECONDARY] Microsoft VSLive! AI Hackathon 2026 lists relevance, architecture and design, safety and security, creativity and originality, and user experience, with no weights. Source: [VSLive! Microsoft AI Hackathon](https://vslive.com/aihackathon).
- [OPINION] A generic five-criterion rubric circulates in 2026 vendor content: innovation 20-25%, technical 20-25%, impact 20-25%, demo 15-20%, completeness 10-15%. The author cites no source, and the midpoints sum to about 97.5%. Source: [Reskilll, Aug 21, 2026](https://blogs.reskilll.com/what-hackathon-judges-look-for-complete-judging-criteria-breakdown-2026/).
- [OPINION] Devpost-style judging "usually has 4-5 criteria." The most common set is innovation, technical execution, impact, presentation and design. Source: [Reskilll criteria breakdown](https://blogs.reskilll.com/what-hackathon-judges-look-for-complete-judging-criteria-breakdown-2026/).

### Inferences
- Across published rubrics the stable core is: working demo or execution, impact on a named user, originality, and sponsor-tech use. The sponsor-tech criterion is scored separately (Opus 4.6: 25%; Microsoft: "central, not a minor addition"). It is not a bonus.
- Where weights are published, the demo is the largest single item (30% for Opus 4.6). Microsoft spreads weight evenly. A 40% "technical" weighting for Gemini 3 is plausible but unconfirmed.
- Code and repo quality act as a gate in several rubrics (Google: code required; Microsoft: repo documentation and security are scored). A clean repo with a README is cheap insurance.
- For the Meta hackathon the team is entering: the only Meta-sponsored rubric I verified is the Pan-LATAM template (Application of Technology / Presentation / Impact / Originality). Treat it as the likely shape, not as the rule. **Pull the rules page of the specific event first**, then build the pitch so that every slide answers one of those criteria.

### Gaps
- No 2026 Meta hackathon rubric found. The Meta LlamaCon 2025 post and the Pan-LATAM page both leave weights out.
- Gemini 3 Devpost rules page returned 403 and the official Google competition page redirected. The 40/30/20 split is unconfirmed.
- OpenAI gpt-oss criteria: not found. The GovTech 2024 rubric is a different event.
- The official Cerebral Valley Opus 4.6 page returned 404, so the 30/25/25/20 weights rest on a mirror.

---

## Key Question 2: How judges actually behave (time per project, video first, first 30 seconds, what they skip)

### Takeaway
Judges spend roughly 3-5 minutes per project, and the first sentence or first 30 seconds largely sets the score. Judges watch the submitted video before any live demo, and they skip code unless a gate requires it. All of this is practitioner consensus, not measured data.

### Cited Findings
- [HARD] Time allotted: MLH's judging plan example assumes 4 minutes per project: 2 minutes for presentation and demo, 1 minute for questions and score compilation, and 1 minute for judge travel. Its science-fair example uses 3 minutes per team. Source: [MLH judging plan](https://guide.mlh.io/general-information/judging-and-submissions/judging-plan) (summary via search; the page redirects to guide.mlh.com).
- [HARD] Video-first structure: Built with Opus 4.6 capped submission videos at 3 minutes, judged submissions asynchronously in Stage 1, and judged only the top 6 live ([rules mirror](https://huggingface.co/datasets/introvoyz041/postvisit/blob/main/data/docs/hackathon-rules.md)). Devfolio's guide sets demo videos at 2 to 4 minutes. ETHGlobal Superhack requires a 2-4 minute video and advances only the top 20% of projects to live judging (search snippets: [Devfolio](https://guide.devfolio.co/docs/guide/participating-in-hackathons/judging-1), [Superhack](https://ethglobal.com/events/superhack/info/details)).
- [OPINION] Judge's notes, Jul 27 (2026 by context): "demos start to blur together by the middle of the block." Winners separated on "whether the demo ran, how clearly the project was framed, and whether scope fit the time available." The opening sentence is where judges form their view. Teams that opened with market context or a personal story "lost time before the product appeared." Source: [Kurbaitaev, DEV Community](https://dev.to/kurbaitaev/what-judges-actually-score-notes-from-a-year-of-hackathon-judging-3p4l).
- [OPINION] A DEV post by a judge (search snippet) says "the opening of a demo is where the score is largely set." Rehearse the opening out loud. Source: [DEV Community, Kurbaitaev feed](https://dev.to/feed/kurbaitaev).
- [OPINION] Ray Deck (Nov 21, 2022, old but on point): "The video is the judges' main entry point, and often the only part many judges see." Sponsors also reuse the video when announcing winners. Source: [Sustained, Lessons from Winning Five Hackathons](https://sustained.substack.com/p/lessons-from-winning-five-hackathons).
- [OPINION] Scale: "judges can see 30 to 100 demos in a day" (training-company guide). Source: [Masai School, How to win an AI hackathon in 2026](https://www.masaischool.com/blog/how-to-win-an-ai-hackathon-in-2026-full-guide/). Vendor source; treat as an anecdote.
- [OPINION] HackerEarth (search snippet): a judge should grasp what the project does "in under 30 seconds," with the "wow" moment landing in the first minute. Source: [HackerEarth, 10 tips to win a hackathon](https://www.hackerearth.com/blog/10-tips-win-hackathon).
- [OPINION] Code: Kurbaitaev says framework choice "did not raise scores." Reskilll claims judges "usually don't read code" (single blog, unverified). Google's forum says code is required as a gate.
- [SECONDARY] Judges check sponsor-tech depth: the Opus rubric asks "Did they go beyond a basic integration?"; Microsoft asks "central or minor addition?"; the Google forum says "prominent use" of the API is judged.

### Inferences
- Plan for about 3 minutes of judge attention per project, and assume the video is watched before the live demo. The video must stand alone.
- The first sentence must state what the product does and for whom. Anything before that costs score.
- Judges check sponsor-tech depth quickly. Make the sponsor's model or API visibly central in the first two minutes, not in a footnote.

### Gaps
- No measured data on judge time or watch-completion rates. The 3-5 minute figures are event-planning assumptions, not observations.
- No Reddit or Hacker News judge threads surfaced in searches.
- The JetBrains piece "how to win a hackathon: notes from the judging table" (June 2026) returned 403 on fetch. Only search snippets were available, so I did not quote it directly.

---

## Key Question 3: Demo that becomes memorable (wow moment, structure, numbers)

### Takeaway
Memorable demos in 2026 winner write-ups share a one-sentence problem framing, a concrete number or real user, and a live core action that runs without a stall. The structures below are practitioner templates, not tested against judge outcomes.

### Cited Findings
- [OPINION] Kurbaitaev: a live demo "removes doubt, and doubt is what a judge is actually managing under time pressure." Use a "60-second screen capture of the working flow as insurance." Keep slides to "one screenshot of the thing running, as a fallback if the wifi died." Source: [Kurbaitaev, DEV](https://dev.to/kurbaitaev/what-judges-actually-score-notes-from-a-year-of-hackathon-judging-3p4l).
- [OPINION] JetBrains (June 2026, search snippet): "Mock everything you can... Pre-fill the data. Mock the slow API call. Remove every place the demo could stall." Judges can tell when a team is "talking around a feature that doesn't exist yet." Source: [JetBrains, how to win a hackathon](https://blog.jetbrains.com/ai/2026/06/how-to-win-a-hackathon-notes-from-the-judging-table/) (not fetched; snippet only).
- [OPINION] HackerEarth (snippet): build a 90-second demo script and hardcode the demo path, since "judges penalize demos that never reach their punchline." Source: [HackerEarth](https://www.hackerearth.com/blog/10-tips-win-hackathon).
- [OPINION] Pitch structure (AngelHack, Aug 2026, snippet): in a three-minute slot, the first 30 seconds cover team, problem and one-line solution. Source: [AngelHack, 10 tips to rock your hackathon demo](https://angelhack.com/blog/10-tips-to-help-you-rock-your-next-hackathon-demo/). Reskilll (snippet) proposes a 20-second problem hook, then about 20 seconds on what was built, and says not to show code or a terminal on screen. Source: [Reskilll demo tips](https://blogs.reskilll.com/hackathon-demo-presentation-tips-pitch-3-minutes-win-2026/).
- [HARD, as examples of framing] Winner framing from the Opus 4.6 post. CrossBeam targets California housing permits, with a "90%+ rejection rate on first submission" and an "average six-month delay." TARA cuts a process that "once took weeks to about five hours" (self-reported by the builder). Elisa was "built in about 30 hours." Source: [Anthropic winners post](https://claude.com/blog/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon). These are the builders' own claims, not verified figures.
- [HARD, as examples] Meta LlamaCon 2025 winners used one clear, plain-language capability claim. Example: "detects user-defined video events described in plain language... without fine-tuning" (Llama CCTV Operator, third place). Geo-ML converted "400-page geology reports into 3D subsurface models" and won the best Llama API usage prize. Source: [Meta LlamaCon hackathon](https://ai.meta.com/blog/llamacon-hackathon/).

### Inferences
Working template for a 2-3 minute video or live slot, derived from the sources above (my synthesis):
1. 0:00-0:20: one sentence naming the user and the problem, with one number if you have one.
2. 0:20-1:30: the core action live or from a recording, with pre-filled data and mocked slow calls.
3. 1:30-2:15: why the sponsor's model or API is central, shown on screen, not described.
4. 2:15-2:50: impact (named user or measured result) and one honest limitation.
5. Close: one sentence restating the problem solved.

Keep a 60-second screen-capture fallback and one screenshot ready, in case the network fails.

### Gaps
- No outcome data linking demo features to scores. The template is inference.
- No quantitative study of which demo elements win.

---

## Key Question 4: Why strong projects lose (and what disqualifies)

### Takeaway
Strong projects mostly lose on framing and execution risk: opening with background, an over-scoped platform, a demo that stalls, or a thin AI wrapper. Disqualification rules are separate and written down. Read them.

### Cited Findings
- [OPINION] Kurbaitaev lists what sinks projects: opening with background instead of product; "ambitious platforms built in a weekend instead of one narrow, well-executed feature"; "demos that don't run, or slides in place of live software"; time spent on stack choices or polish; no single-sentence identity; vague answers about what was built, or refusing to name known weaknesses. Source: [Kurbaitaev, DEV](https://dev.to/kurbaitaev/what-judges-actually-score-notes-from-a-year-of-hackathon-judging-3p4l).
- [OPINION] Ray Deck: "Cut bone to ship." A working simpler demo beat "ambitious claims that were never delivered." Table stakes are a public repo, a working demo and a short video; missing any of these means "you might as well not have entered." Source: [Sustained, Ray Deck](https://sustained.substack.com/p/lessons-from-winning-five-hackathons). Dated 2022.
- [OPINION] Generic and thin projects: Reskilll lists "another chatbot" and "thin API wrappers" as lower-scoring on innovation, and "mockups and hardcoded data" as lower-scoring on technical implementation ([Reskilll breakdown](https://blogs.reskilll.com/what-hackathon-judges-look-for-complete-judging-criteria-breakdown-2026/)). A separate, unattributed search summary lists "wrapping an API without adding value" as a weak integration (no page confirmed for this claim).
- [OPINION] Teams that lose rely on AI to build the differentiated part and cannot explain it in Q&A (HackerEarth, snippet).
- [HARD] Disqualification rules, from the official texts:
  - Microsoft: multiple accounts "will void your entries"; "use of any automated system to participate is prohibited"; content must not be obscene, offensive, or promote alcohol, tobacco, illegal drugs or a particular political agenda; entrants must be 18+. Source: [Microsoft rules](https://microsoft.github.io/AI_Agents_Hackathon/rules/).
  - Anthropic / Cerebral Valley: disqualification if the project "violates legal/ethical/platform policies" or "uses code/data/assets without rights." Source: [rules mirror](https://huggingface.co/datasets/introvoyz041/postvisit/blob/main/data/docs/hackathon-rules.md).
  - Google: omitting code "may result in disqualification" (forum reply, see Q1).

### Inferences
- The most avoidable losses are: a stall in the live demo, missing or undocumented code, and not being able to answer "what did you build yourself?" Fix these before scope or polish.
- Name your weakest point before a judge does. The Kurbaitaev notes say judges reward candor.
- Check the rules for AI-generated content, third-party data and assets, and account limits before building.

### Gaps
- No public tally of disqualifications by reason at any sponsor hackathon.
- Reddit and Hacker News threads on judging were not found.

---

## Key Question 5: What sponsor-company judges want (vs. investor or engineer judges)

### Takeaway
Sponsor judges score against their own rubric and reward visible use of their technology in a domain that suits their story. Published evidence supports this for Anthropic, Meta and Google. I found no DevRel or product-team statement from Meta, Google, OpenAI, Anthropic or Microsoft describing what they want, so the "marketing feature" angle is unverified.

### Cited Findings
- [HARD] Anthropic's Opus 4.6 rubric weights "Opus 4.6 Use" at 25%, and the judges were six Anthropic team members. Source: [rules mirror](https://huggingface.co/datasets/introvoyz041/postvisit/blob/main/data/docs/hackathon-rules.md). Judge names appear in a secondary article (AdwaitX), which I did not verify.
- [HARD] Anthropic's winners were domain practitioners: a personal-injury lawyer (CrossBeam), a Brussels cardiologist (PostVisit.ai), and a former Ugandan ministry official (TARA). Anthropic notes that "four out of five winners were not professional developers." Source: [Anthropic winners post, Apr 20, 2026](https://claude.com/blog/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon).
- [HARD] Meta LlamaCon 2025 had a sponsor-specific track ("best usage of Llama API") and judges from six sponsor companies. Source: [Meta LlamaCon hackathon](https://ai.meta.com/blog/llamacon-hackathon/).
- [SECONDARY] Google's forum reply says judges weigh "how prominently the Gemini API is used" (see Q1).
- [OPINION] Sponsors come for recruiting, testing how developers use their APIs, and brand visibility (one unnamed guide in search results; the likely page is [Reskilll, The Hackathon Ecosystem](https://blogs.reskilll.com/?p=146), not confirmed).
- [OPINION] Ray Deck: winners "consistently answered yes" to "If I reward this project, will my company look good?" and judges "did not necessarily reward superior technical output." Source: [Sustained, Ray Deck](https://sustained.substack.com/p/lessons-from-winning-five-hackathons). Dated 2022.
- [HARD] Meta LlamaCon winners: knowledge-graph expert matching (OrgLens), fraud detection with voice reporting (Compliance Wizards), plain-language video surveillance (Llama CCTV Operator), and geology report to 3D model (Geo-ML). Source: [Meta LlamaCon hackathon](https://ai.meta.com/blog/llamacon-hackathon/).

### Inferences
- Compared with investor judges, who ask about market size and traction, sponsor judges ask whether their model was used well and whether the project makes their platform look good. Engineer judges look at code. This difference is my inference from the rubrics. No source compares the three judge types directly.
- A sponsor track (e.g., "best use of [model]") is a second route to a prize with less competition. Ray Deck reports that some bounties drew fewer entries, but this is anecdotal.

### Gaps
- No DevRel or product blog from Meta, Google, OpenAI, Anthropic, Vercel or Microsoft on judging preferences surfaced in searches.
- "Projects the sponsor can feature in marketing" is supported only by Ray Deck's 2022 post, which says sponsors share winning videos.

---

## Key Question 6: 2026 trends in judging (fatigue, hardware, multimodal, open models, on-device)

### Takeaway
The best-evidenced 2026 trend is toward domain-specific, practitioner-built projects with multimodal input. Fatigue with generic chatbots and todo apps is repeated in vendor content but not measured. Hardware, open-model, and on-device preferences have only thin evidence.

### Cited Findings
- [HARD] Anthropic's Opus 4.6 winners (Feb-Apr 2026) were domain projects: permits, cardiology notes, road-infrastructure investment appraisal from dashcam video using vision, and a browser music bandmate. Source: [Anthropic winners post](https://claude.com/blog/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon).
- [HARD] Meta LlamaCon 2025 winners leaned multimodal and vertical: CCTV event detection using Llama 4 image understanding, and geology PDFs to 3D models. Source: [Meta LlamaCon hackathon](https://ai.meta.com/blog/llamacon-hackathon/).
- [SECONDARY] Volume: about 13,000 people applied to an Anthropic Claude Code hackathon and 500 were selected (Gigazine, unverified; the search summary did not make clear whether this was the Opus 4.6 or 4.7 event). Source: [Gigazine, Apr 25, 2026](https://gigazine.net/gsc_news/en/20260425-anthropic-hackathon). The Kaggle Gemini 3 event drew 4,097 submissions in a week (see Q1).
- [OPINION] Generic ideas judges "are tired of": "AI chatbot for X," blockchain projects, todo apps. Winners "use AI as a component rather than the whole product" and have demos that "work on the first try." Source: [Reskilll, Hackathon Ideas That Won in 2026](https://blogs.reskilll.com/hackathon-ideas-that-won-2026-judges-actually-pick-examples/) (search snippet; vendor content, no survey).
- [HARD, thin] OpenAI gpt-oss hackathon prize tracks included "Weirdest Hardware" (Luma event page). This shows a hardware track, not a judging preference. Source: [Luma, OpenAI Open Model Hackathon](https://luma.com/aic-oss).
- [SECONDARY] Open-model and on-device preferences: no judging evidence found. The Llama events were built around open-weight models, but their rules do not favor open models in scoring.

### Inferences
- The strongest 2026 signal is domain specificity with a named user. This matches the Impact and Usability criteria in the rubrics above.
- With thousands of entries, judges will read first sentences quickly, so the framing advantage increases.
- Multimodal input (video, images, PDFs) appeared in several winning projects, and the Llama CCTV and Geo-ML examples suggest it helps when a sponsor is a model provider.

### Gaps
- No survey or hard data on judge fatigue with chatbots or agents. The Reskilll claim is opinion.
- No evidence on hardware, on-device or open-model preference at Meta, Google, OpenAI or Anthropic events.
- The Kaggle Gemini 3 winners page and the gemini3.devpost.com winners list were not reached.

---

## Overall gaps and next steps
- Highest-value next step: get the rules page of the specific Meta hackathon you will enter. Check for the judging-criteria tab, video length, required sponsor APIs, and any disqualification rules. Every other finding here is a proxy for it.
- Not retrieved: Meta's 2026 rubric, the official Google Gemini 3 rules, the official Cerebral Valley Opus 4.6 page, the JetBrains judging-table article, and any Reddit or Hacker News judge thread.
- Search quality: most 2026 judging content is vendor or training-company writing (Reskilll, Masai, HackerEarth, AngelHack). Weight it accordingly.
