# Building and testing Ensayo with almost no Meta Model API credits

Research as of 1 Nov 2026. Sources are mostly secondary (aggregators, vendor blogs) unless marked primary. Anything not confirmed in a primary source is marked **unverified**. Meta's own pricing page could not be retrieved (the URL guessed at dev.meta.ai/docs/pricing returned 404; the dev.meta.ai/docs overview points to a separate "Pricing and rate limits" page), so all Meta price figures below come from third-party trackers that agree with each other.

## Open-weight models and where they can run

### Takeaway
Only Muse Glimmer 30B is a realistic local dev model on a MacBook. It is Apache 2.0, accepts images, and its quantized builds fit in roughly 17–32 GB. Muse Spark Open (816B) is not runnable locally and costs the same as Muse Spark 1.3 standard when hosted. No free hosted tier for either model was confirmed.

### Cited Findings
- Muse Glimmer 30B: Hugging Face repo `meta-models/Muse-Glimmer-30B`, Apache 2.0, released August 2026, about 29.6B total parameters including a ~1.8B ViT-G/14 vision encoder, context 131,072+ tokens, text and image input, text output, no audio, video processed as frames, up to 4,096 visual tokens per image, knowledge cutoff 4 Jan 2026 — [HF model card (via fetch)](https://huggingface.co/meta-models/Muse-Glimmer-30B)
- Glimmer quantized variants per its card: BF16 targets 64 GB VRAM; "K-Quant-Dynamic" 4-bit targets 32 GB (0.2% average degradation over 15 benchmarks); "K-Quant-17GB" 4-bit (language model under 20 GB) targets 24 GB (1.0% degradation) — [HF model card](https://huggingface.co/meta-models/Muse-Glimmer-30B)
- Glimmer card speed numbers, batch size 1, with DFlash drafter, K-Quant-17GB: RTX 5090 (llama.cpp) 74.9 to 233.4 tok/s; Apple M4 Max (ExecuTorch) 23.7 to 37.8 tok/s; Apple M5 Max (ExecuTorch) 26.6 to 50.2 tok/s. These are Meta's self-reported numbers — [HF model card](https://huggingface.co/meta-models/Muse-Glimmer-30B)
- Glimmer inference support per its card: Transformers, vLLM (OpenAI-compatible server), SGLang, llama.cpp (referenced and quantizations listed), Ollama and LM Studio (listed among compatible apps for the quantizations), Docker Model Runner, ExecuTorch. MLX is not mentioned — [HF model card](https://huggingface.co/meta-models/Muse-Glimmer-30B)
- Glimmer hosted prices are listed on OpenRouter (paid, no free tier found), roughly $0.30–0.35 per M input and $1.10–1.50 per M output depending on provider; providers listed are Phala, DeepInfra, Fireworks, Together — [OpenRouter model page](https://openrouter.ai/models/meta/muse-glimmer-30b) (price range from search-result listings, not fetched directly; the two numbers differ across listings)
- Muse Spark Open: Hugging Face repo `meta-models/Muse-Spark-Open-816B-A42B`, released 15 Oct 2026, 816B total / 42B active MoE (HF metadata says 822B), 1M context, input text/image/video/audio, output text. Gated: login plus a form with full legal name, date of birth and organization name. License "Muse Model License": commercial use allowed, requires attribution "Built with Muse Spark Open" in the product UI, and a separate written agreement if aggregate gross revenue exceeds US$20M in any 12 months to offer it as a service — [HF model card (via fetch)](https://huggingface.co/meta-models/Muse-Spark-Open-816B-A42B)
- Muse Spark Open hardware: NVFP4 needs at least 700 GB VRAM, BF16 about 2 TB; the card says it is optimized for two Mac Studio M5 Ultra with MLX. Community quantized builds (24 listed, names not given on the page) work with llama.cpp, Ollama, LM Studio — [HF model card](https://huggingface.co/meta-models/Muse-Spark-Open-816B-A42B)
- Muse Spark Open hosted: Together and Fireworks listed at $1.25 per M input and $4.25 per M output, with cached input around $0.15 per M on Together. A Groq limited preview is mentioned in Meta's developer post; no Groq price was found — [LLM Reference providers page](https://www.llmreference.com/model/muse-spark-open/providers) (aggregator; one table shows an unexplained $2.10 figure). Not verified against provider pricing pages.
- Muse Spark Open is also covered on news sites that say it is "open weights under a proprietary license" — [Latenode news](https://latenode.com/news/meta-releases-muse-spark-open-weights-with-hosted-api-options) (secondary, non-authoritative)
- Free hosted options: OpenRouter `:free` models are capped at 20 requests per minute and 50 or 1,000 requests per day depending on lifetime spend, rotate without notice, and are not the Muse models. Free-tier figures from secondary guides; OpenRouter's own page says limits change often — [TrueFoundry summary of OpenRouter limits](https://www.truefoundry.com/es/blog/openrouter-rate-limits-your-free-tier-depends-on-what-youve-already-paid), [OpenRouter free-LLM comparison](https://openrouter.ai/blog/tutorials/free-llm-apis-compared/) (search summary, not fetched)

### Inferences
- For a MacBook, the realistic path is Muse Glimmer 30B in the 4-bit 17 GB build, which should need a Mac with roughly 24 GB or more of unified memory once KV cache and the vision encoder are counted. The card's 24 GB target is for the 17 GB build; 32 GB is the safe target for the 4-bit "Dynamic" build. Mark's Mac's memory was not checked.
- Expected local speed on Apple Silicon is in the tens of tokens per second per the card. That is enough for prompt iteration on a few ads, not for 1,000 personas per ad at scale. Batch-size-1 numbers only.
- The VPS has no GPU. CPU inference of a 30B model would be far too slow for development; do not plan on the VPS as the dev model host.
- Muse Spark Open is not a cheap development model. Its hosted price equals Muse Spark 1.3 standard, and self-hosting is out of reach. Only consider it if a provider offers a free trial credit (none found).
- Glimmer is a distilled model from the Muse Spark flagship (per secondary sources). Its behavior is correlated with 1.3 but not identical. Its knowledge cutoff (Jan 2026) predates 1.3's release (Sept 2026).

### Gaps
- Official Ollama or MLX support for Glimmer was not confirmed beyond the card's listing of Ollama and LM Studio for the quantized files. Needs a test on Mark's Mac.
- Groq's current free tier and limits: no results found.
- Whether any of the Muse models has a free hosted tier: none found.

## Developing against a cheap model, then switching to muse-spark-1.3

### Takeaway
The Meta API speaks OpenAI-style chat completions, responses and Anthropic-style messages, so one client can switch by base URL and model name. Switching is easy at the transport level. The risks are that reasoning effort, token counts and image handling differ across models, so any number measured on a dev model (ranking quality, cost per call) does not transfer to 1.3.

### Cited Findings
- Model IDs and endpoints for Muse Spark 1.3 (standard `meta/muse-spark-1.3`, contributor `meta/muse-spark-1.3-contributor`): works through `/v1/chat/completions`, `/v1/responses` and `/v1/messages` (Anthropic-style). Context window 1,048,576 tokens; text, image, video and PDF input work as in 1.2. `reasoning_effort` is passed through and accepts minimal, low, medium, high, xhigh (xhigh is the current maximum). Reasoning tokens bill as output tokens. Published 2 Sept 2026 — [LiteLLM day-0 post](https://docs.litellm.ai/blog/muse_spark_1_3)
- The same LiteLLM post does not cover tool calling, streaming differences, unsupported parameters, or the thinking-output format, despite a section heading on audio. Those are **unverified** for this API.
- Rate limits per the LiteLLM post: standard 3,000 RPM, contributor 100 RPM, both enforced per team rather than per key. Web search grounding is listed at $2.50 per 1,000 queries on both tiers — [LiteLLM day-0 post](https://docs.litellm.ai/blog/muse_spark_1_3)
- Community testing reported by a secondary article found that Spark 1.3 uses roughly 3x the output tokens of Spark 1.2 on the Artificial Analysis Intelligence Index run (about 140M vs a field median of about 90M). This is secondhand — [eesel pricing article](https://www.eesel.ai/blog/muse-spark-1-3-pricing)
- Dev-model differences that matter for this project: Glimmer caps each image at 4,096 visual tokens and processes video as frames; the 1.3 image token budget was not found in any source. Glimmer has no audio input.

### Inferences
- Use a single OpenAI-compatible client with `base_url` and `model` read from env (`ENSAYO_MODEL_BASE_URL`, `ENSAYO_MODEL`). Route all calls through `ensayo.costs.Ledger` so dev and prod runs log separately.
- Run plumbing and tests at zero cost: a stub OpenAI-compatible server that replays recorded fixtures (pytest), and Glimmer locally for prompt iteration. Only the final sealed run and the live test need 1.3.
- Do not report calibration, sealed-set or live-test numbers from a dev model. The CLAUDE.md rule that the sealed set is not touched after opening still holds, so the dev model should only be used before the seal.
- Reasoning effort: set it explicitly on both the dev and final calls. A default that differs across endpoints will change output length and cost.
- Keep the same JSON schema and parser for both models, and test parse failure rates on each model before comparing rankings. Structured-output support on 1.3 was not verified.

### Gaps
- Tool calling, streaming, JSON or structured-output behavior on 1.3: no verified source.
- Whether Glimmer served through vLLM or llama.cpp returns the same token accounting as Meta's API: not tested.

## Meta Model API: free tier, batch, caching, rate limits, hackathon credits

### Takeaway
Muse Spark 1.3 standard is $1.25 per M input and $4.25 per M output; contributor is about $0.10 and $0.20. Cached input is $0.15 per M on standard and $0.002 per M on contributor (per LiteLLM). No free tier was announced for 1.3, and no batch discount was found. How the 150 hackathon credits convert to dollars and whether contributor pricing is eligible for credits are not confirmed in any source found.

### Cited Findings
- Standard price per M tokens: input $1.25, output $4.25, cached input $0.15, contributor input $0.10, output $0.20, cached input $0.002 — [LiteLLM day-0 post](https://docs.litellm.ai/blog/muse_spark_1_3); the same standard and contributor input/output figures appear on [eesel](https://www.eesel.ai/blog/muse-spark-1-3-pricing), which attributes contributor rates to a Hacker News thread quoting Meta's pricing page and says the exact cents are not fully confirmed
- Contributor data use: per the LiteLLM config comment, "Cheaper tier, but Meta may train on your prompts and completions." Per eesel, standard is "kept private, not used for training" and contributor is "used to improve Meta's products." Both quoted secondhand; the Meta contributor terms were not fetched — [LiteLLM](https://docs.litellm.ai/blog/muse_spark_1_3), [eesel](https://www.eesel.ai/blog/muse-spark-1-3-pricing)
- Contributor mode is described on the Meta developer docs overview as "a discounted Contributor mode" that Muse Code subscription plans can also include. Discount, terms and eligibility are not given there — [dev.meta.ai docs](https://dev.meta.ai/docs)
- Free tier: eesel's FAQ says no free tier was announced for Muse Spark 1.3. Its related-post teaser mentions a free allowance for "Meta Muse," which was not confirmed to apply to this API — [eesel](https://www.eesel.ai/blog/muse-spark-1-3-pricing)
- Batch API discount: not mentioned in any source found, including the dev.meta.ai overview.
- Prompt caching: the dev.meta.ai overview says only "Cache repeated prefixes to cut latency and cost," with no figures. Discount figures come from LiteLLM ($0.15 per M cached standard, $0.002 contributor) and eesel (an 88% discount on repeated input, with no source) — [dev.meta.ai docs](https://dev.meta.ai/docs), [LiteLLM](https://docs.litellm.ai/blog/muse_spark_1_3). Minimum cacheable prefix length and cache-write pricing: not found.
- Hackathon credits: the Meta Global AI Developer Hackathon details were not searched in this round. Nothing found on the 150-credit conversion or on contributor eligibility.

### Inferences (cost arithmetic, my calculations, not measured)
Assumptions are stated per call. The team's own Ledger numbers should replace these as soon as they exist.

- Scenario A, text-only persona call: 1,000 persona calls, 1,500 input and 300 output tokens each (1.5M in, 0.3M out).
  - 1.3 standard, no cache: $3.15 per full pass.
  - 1.3 standard, if 1,200 of the 1,500 input tokens are a shared prefix (instructions plus ad) and hit cache: about $1.83 per pass.
  - 1.3 contributor, no cache: about $0.21 per pass.
  - Glimmer at $0.30–0.35 in and $1.10–1.50 out (hosted, not local): about $0.78–0.98 per pass.
- Scenario B, image-heavy call (matches the team's implied figure of about US$34 per 1,000 standard persona calls in CLAUDE.md, which corresponds to about 20,000 input and 2,000 output tokens per call): standard about $33.50 per pass; contributor about $2.40 per pass.
- So 150 credits, if they are US$ (unverified), buy roughly 4 full standard passes of image-heavy persona calls, or roughly 60 contributor passes. Batching (20 personas per call) cuts the call count 20x but leaves the input tokens per persona roughly similar if each persona profile is sent in full, so the saving comes from sharing the ad and instructions, not from fewer tokens per persona.
- Caching is the largest lever left on standard. Put the ad (image and copy) and the fixed instructions first, and the persona last, so that all 1,000 personas for one ad share a prefix. This only pays off if the prefix is above the (unverified) minimum cacheable length.
- Rate limits to plan for: contributor at 100 RPM means 1,000 single-persona calls take about 10 minutes per ad. Batching 20 personas per call brings that to about 50 calls, under 1 minute.
- The CLAUDE.md estimate of "unos US$ 0,25 por lote" for contributor batches of 20 personas does not reconcile with list prices unless a lot carries about 2.5M input tokens. If "lote" there means a batch of ads rather than a batch of personas, the figure is fine. Check its derivation before relying on it.
- Plan for the 3-day window: day 1 plumbing and prompt work on a stub server and local Glimmer (zero spend); day 2 contributor calibration on the dev set with a hard cap; day 3 sealed run and live test on 1.3 with the hash committed before the deadline. Hold standard-tier spend for the demo and any client data, as CLAUDE.md already says.

### Gaps
- Meta's official pricing page and rate-limit page: not retrieved.
- Batch API discount: unknown.
- Free tier and how the 150 credits convert: unknown.
- Whether contributor is eligible for the hackathon credits: unknown.

## Ad Library access and alternatives if access does not arrive

### Takeaway
No source gives a reliable timeline for facebook.com/ID verification in 2026, and nothing found covers non-US or Chile-based users specifically. Estimates range from 1–3 business days to 1–2 weeks. More important than timing: the Ad Library does not expose conversion or click performance. A backtest label has to be a proxy such as run length or reach and spend ranges (EU/UK only).

### Cited Findings
- The Ad Library API gate is personal identity verification at facebook.com/ID, not Business Manager verification, per third-party guides. Verification involves a government-issued ID and confirming the country of residence. The token should come from the verified account — [gethookd guide](https://www.gethookd.ai/learn/how-to-use-meta-ad-library-api-access-token-generation-documentation/), [metapi.io comparison](https://metapi.io/compare/facebook-ad-library-api) (both secondary; search summaries, not fetched)
- Timing: one developer guide says identity checks usually take 1–3 business days; another puts approval at 1–2 weeks; others say days. No Meta source found — same search results as above
- facebook.com/ID itself returned a login page; the help pages and the Ad Library API page on facebook.com returned 403 or 404 to the fetch tool, so Meta's own verification steps were not read — [facebook.com/ID](https://www.facebook.com/ID) (login page), [facebook.com/ads/library/api](https://www.facebook.com/ads/library/api/) (404)
- Meta's Graph API reference for `ads_archive` (fetched, Graph v26.0): `ad_type` defaults to ALL ("ALL returns ads on all topics"); `ad_reached_countries` is required, accepts ISO codes or ALL, and "Ads that did not reach any location in the EU will only return if they are about social issues, elections or politics." Error 613 is rate limiting; no numeric limits given. The page does not mention identity verification or UK by name — [Meta Graph API reference](https://developers.facebook.com/docs/graph-api/reference/ads_archive/)
- Coverage per secondary guides: non-political commercial ads are in the archive only if delivered to the EU or UK; they remain searchable about a year after they ran. Political and issue ads are searchable worldwide for seven years. A US-only commercial advertiser is not visible. DSA transparency fields (estimated reach, age, gender, location targeting, payer and beneficiary) are available only for ads delivered to the UK and EU (plus Brazilian political ads), and spend and impressions for political and EU/UK ads come back as ranges — [EU DSA ad repositories guide](https://adlibrary.com/posts/eu-dsa-ad-repositories-developers) (secondary). Both the coverage and field claims are consistent with the Graph reference's wording on EU reach, though the Graph page used here is the current version and does not spell out the UK rule
- One guide says UK coverage only includes ads that ran after 1 July 2025, so the UK archive is still building toward a full year. Single third-party source, unverified
- The Graph reference shows the fields available, but not CTR, conversions, ROAS or add-to-cart data. Ad Library data are impression and spend ranges, reach, delivery dates and creative text or media

### Inferences
- The project's CLAUDE.md scope (EU and UK ads, United States excluded from the backtest set) matches what the secondary sources say about coverage. It is consistent with the decision recorded on 27 Oct.
- Because the Ad Library has no performance outcome, the backtest "truth" must be a proxy. The most defensible candidates from the available fields are run length (ad_delivery_start_time to stop time) and reach or spend ranges. Document the choice before the sealed set is built, since changing the proxy after seeing results would break the sealed rule.
- If verification is slow, the fallback options are limited. Manual viewing in the Ad Library web UI would produce a small labeled set but would need to respect Meta's terms, which prohibit automated collection (not verified in this round; check Meta's terms before doing any manual collection). Commercial creatives with performance labels are not in any public source found.
- Start the verification now, using the token from the account that will run the scripts, since timing is the one unknown most likely to block the backtest.

### Gaps
- Actual verification duration in 2026, and whether Chile-based accounts face any different path: unknown.
- Whether Meta's terms permit the manual web UI collection the project would do: not checked.
- Kaggle, academic, or public ad-creative datasets with performance labels: not searched in this round.
- Political-ad report CSVs: not searched; they cover political and issue ads, which the project has excluded.

## LLM synthetic panels for ad or creative preference

### Takeaway
Evidence is thin and early. The strongest finding is a 2026 Adobe-led study (SimAB) predicting web design A/B winners with persona agents: 67% overall accuracy, 83% on high-confidence cases, across 47 tests. It is about webpages, not ads, and it does not report persona counts. No peer-reviewed minimum sample size for persona panels was found; the sizes that appear come from vendors.

### Cited Findings
- SimAB (arXiv 2603.01024, March 2026): persona-conditioned agents generate personas from design screenshots and a conversion goal, each states a preference, and results are aggregated. Evaluated against real traffic outcomes of 47 historical A/B tests. Overall accuracy 67%; accuracy 83% on high-confidence cases. Persona count per test not stated. No confidence intervals reported — [arXiv 2603.01024](https://arxiv.org/abs/2603.01024). Authors include Tim Rieder, Marian Schneider and others; affiliation not checked. The LinkedIn review cited in search says it predicts the winner, not the effect size, and is a prior or filter rather than a substitute for an A/B test
- Kang (arXiv 2512.21080, Dec 2025, revised Jan 2026): theoretical. Shows that swapping humans for personas amounts to changing the evaluation population under two stated conditions, and treats persona benchmarking as a sample-size question with bounds. No numeric bounds in the abstract. No ad or preference task — [arXiv 2512.21080](https://arxiv.org/abs/2512.21080)
- Benomar et al. (arXiv 2609.24629, submitted 21 Sept 2026): uses persona-based LLM predictions as a prior inside a prediction-powered inference framework to cut A/B sample sizes. The abstract claims "substantially reduce experimental costs" on four real datasets. The paper does not name an ad task in the abstract; the claim is unverified — [arXiv 2609.24629](https://arxiv.org/abs/2609.24629)
- Vendor claims (unverified, self-reported): Toluna's ACT Instant AI reports N=200 synthetic personas per ad and says it separates strong from weak ads against human test scores — [Toluna write-up](https://tolunacorporate.com/wp-content/uploads/2026/04/ACT-Instant-AI-SuperBowl-Write-Up-v6-2-2.pdf). Neuroflash cites a retail case with +45% ROAS, +22% conversion and +36% CTR for AI-pretested creative — [Neuroflash case studies](https://neuroflash.com/blog/testing/case-studies-synthetic-audiences-ad-performance/). Neuroflash also argues that generic chatbot prompts fall short of a calibrated panel, with the gap coming from calibration data rather than the model. DataDiggers reports a 65% lower cost than panel testing — [DataDiggers case study](https://www.datadiggers-mr.com/case-studies/running-a-b-tests-for-campaign-variants-without-real-audiences)

### Inferences
- The best-supported use is as a pre-test filter that narrows variants before live testing, not as a replacement for the test. This matches the SimAB authors' framing and the critiques.
- Calibration is probably the real cost driver. Vendors that claim accuracy rely on calibration data they do not disclose. Ensayo's calibration set (the dev set in CLAUDE.md) is therefore important and should be frozen before the sealed set is opened.
- The 200-persona figure from Toluna is the only minimum found in the sources. Treat it as a vendor heuristic, not a finding. CLAUDE.md's 1,000 personas and the fallback to 200 are consistent with it.

### Gaps
- Peer-reviewed minimum persona counts for ad or creative preference: none found.
- Full text of SimAB, Benomar et al. and Kang was not read; persona counts and any ad-specific results may be in the full PDF.
- Any study that tests persona panels against Meta ad performance specifically: none found.

## Summary of what to do with this
This section is a plain cross-reference, not a finding, and does not add a new top-level section to the notes.

- Dev model on the Mac: Muse Glimmer 30B, Apache 2.0, 4-bit 17 GB build, through Ollama or LM Studio. Test this first, since the Mac's memory and the Ollama path are not yet checked.
- Plumbing tests on a stub server with recorded fixtures: zero spend.
- Final runs on 1.3: contributor for calibration, sealed set and live test (CLAUDE.md), standard only for the demo and client data. Cache the shared prefix (ad first, persona last).
- Start the facebook.com/ID verification now and decide the backtest proxy label before the sealed set is opened.
