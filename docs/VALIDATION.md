# How we tested Second Look

This is the full protocol behind the numbers in the [README](../README.md), including what it doesn't prove.

Check the main results yourself. This needs no API key, no network and no dependencies beyond Python 3.12, and the commit order needs a full git clone:

```bash
python3 scripts/verify_results.py
```

## The question

People post messages, screenshots and calls on Reddit and ask "is this a scam?", and the community answers in the replies. That gives us real cases, in the words people actually use, with an answer key written by other people. Can Second Look, seeing only the post, reach the community's answer?

## Protocol

| Step | What we did | Where |
|---|---|---|
| **Cases** | Posts published **from 3 September 2026 on**, the day after Muse Spark 1.3 was released, so the model can't have memorized them. Attempt 1: r/Scams to 23 September, r/isthisascam, r/IsThisAScamIndia, plus 40 posts from an Apify pilot, most of them from r/Scams and up to 2 November. Attempt 2: r/Scams from 24 September, r/ScamCenter, r/scamsUK, leaving out every post from attempt 1. | `scripts/scam_arctic.py`, `scripts/scam_reddit.py` |
| **Answer key** | Muse Spark 1.3 reads **only the replies** and extracts the community's verdict: scam, legit or unclear. Unclear threads are dropped. | `data/scams/labels*.json` |
| **Audit** | We read 30 random labels by hand before scoring. | Results below |
| **Prediction** | Muse Spark 1.3 reads **only the post**: title, text and up to 3 images. It never sees the replies. | `scripts/validate_scams.py` |
| **Preregistration** | The SHA-256 of all predictions is committed before scoring. | `results/scam_predictions*.sha256` |
| **Baselines** | A keyword filter (2 or more typical scam terms, matched as substrings) and "always say scam". | `scripts/validate_scams.py` |

**The rule, written before each attempt (commits `8a0395b` and `b570050`; the rule is in `ESTADO.md` at those commits, in Spanish). All four must hold:**

1. At least 30 genuine cases.
2. Balanced accuracy of at least 0.80.
3. It beats the keyword filter by at least 0.10, with the 95% bootstrap interval of the gap above zero.
4. False alarms on genuine cases of 30% or less.

We use balanced accuracy because 85% to 87% of the cases are scams. A model that always says "scam" would be right that often and still score 0.50 here.

## Results

| | Attempt 1 | Attempt 2 |
|---|---|---|
| Date | 2 November | 3 November |
| Posts labeled | 1,547 | 1,189 |
| Dropped | 407 unclear, 2 labels and 1 prediction failed | 244 unclear |
| Cases scored (scams / genuine) | 1,137 (968 / 169) | 945 (823 / 122) |
| Balanced accuracy | **0.787: did not pass** | **0.801: passed** |
| 95% interval | 0.750 to 0.819 | 0.759 to 0.839 |
| Scams caught | 78.6% | 84.0% |
| False alarms on genuine cases | 21.3% | 23.8% |
| AUC | 0.85 | 0.88 |
| Keyword filter, balanced accuracy | 0.505 | 0.517 |
| Gap over keywords (95% interval) | +0.28 (0.23 to 0.33) | +0.28 (0.22 to 0.34) |
| Label audit, by hand | Scam 15/15 correct; genuine 13/15 clear | Scam 15/15 correct; genuine 12/15 clear |
| Predictions hash | `1665740b…d898` | `38b435bb…bb2c` |
| Commit with the hash → commit with the score | `4de2c5f` → `d3da904` | `be7ec95` → `66d935b` |

### What changed between attempts

Attempt 1 failed. Reading the missed cases afterwards, many were posts where someone describes what happened to them ("they took US$200 from my account"). The model was judging whether the *post* was deceptive, while the community answers whether *what the person ran into* was a scam.

So we changed the question: judge the situation the person describes, even if it has already happened, and treat bad service, disputes and commercial spam as genuine. The model, the threshold, the rule and the labeling method stayed the same. We ran it on **new posts only**, excluding every ID from attempt 1. Had it failed, we had committed to dropping the idea.

### The sample changed too

The new posts didn't come from the same places. Attempt 2 added r/ScamCenter and r/scamsUK and left out r/isthisascam and r/IsThisAScamIndia, the two lowest scores in attempt 1. We set that before seeing attempt 2's results, but after seeing attempt 1's.

| Community | Attempt | Scams / genuine | Balanced accuracy |
|---|---|---|---|
| r/Scams | 1 | 393 / 92 | 0.816 |
| r/isthisascam | 1 | 370 / 32 | 0.790 |
| r/IsThisAScamIndia | 1 | 205 / 45 | 0.738 |
| r/Scams | 2 | 549 / 106 | 0.803 |
| r/ScamCenter | 2 | 200 / 6 | 0.824 |
| r/scamsUK | 2 | 74 / 10 | 0.828 |

On r/Scams, the only community in both, the score went from 0.816 to 0.803: scams caught rose from 85% to 86%, and false alarms from 22% to 26%. **So we can't credit the pass to the new question.** Part of it comes from the sample, and r/ScamCenter and r/scamsUK have too few genuine cases to say much alone. Across communities, the score ranges from 0.74 to 0.83. These figures need the raw posts, so `verify_results.py` doesn't recompute them.

### What each answer means (attempt 2)

| The product says | Cases | How many were scams |
|---|---|---|
| "Likely a scam" (50% or more) | 720 | 96% |
| "Be careful" (20% to 49%) | 120 | 70% |
| "No clear signs of a scam" (under 20%) | 105 | 46% |

This table is why the product never says "safe". Even the lowest band was a scam about half the time, because people post when something already worries them.

## What this doesn't prove

We'd rather you hear these from us.

- **It passed at the edge.** 0.80 is inside the confidence interval, so "about 8 in 10" is the honest claim.
- **We got two attempts.** The second used new data, but we wrote its question and chose its communities after seeing the first one fail. It's less clean than a single shot.
- **The answer key is a Reddit community,** read by a model, not fraud investigators. Across both audits, 5 of 30 "genuine" labels were debatable, while all 30 "scam" labels were correct.
- **We dropped unclear threads,** 26% in attempt 1 and 21% in attempt 2. Real messages can be just as unclear.
- **People post when already suspicious,** so a mix that is mostly scams isn't what a person's inbox looks like. On ordinary messages, the share of correct "Likely a scam" answers would be lower than 96%.
- **About 1 in 4 genuine cases gets a false alarm.** We read the model's reasons for all 29 in attempt 2. By our rough reading, about half look like consumer disputes, and several look like real fraud that the community's label missed.
- **The keyword filter is a low bar.** It's close to a coin flip, and it matches substrings, so "fee" also matches "feel". A strict 3-term rule scores about the same (0.513).
- **We didn't test it against adversaries.** Scammers could write messages designed to fool the model, including prompt injection.
- **The posts lean English.** Attempt 2 has no India-specific community, and attempt 1's India community scored lowest. The product answers in other languages, but we didn't test its accuracy in them.
- **Voice notes weren't tested.** Neither were the agents: the investigation, the families and the prepared actions run after the verdict and don't change it.
- **The test and the product use different endpoints.** Public Reddit data went through `muse-spark-1.3-contributor`; user messages go through standard `muse-spark-1.3`. The product also adds one line asking it to answer in the person's language. A test (`tests/test_shield.py`) confirms the rest of the message is identical.

## How far the preregistration goes

- **What you can check:** the predictions still match their hash, and in git history the commit with the predictions comes before the commit with the score. Run `git show 4de2c5f --stat` and `git show be7ec95 --stat`.
- **How close those commits are:** 38 and 36 seconds apart. They show the predictions weren't changed after that point, and they can't show that we hadn't scored them on the side first.
- **No hidden third run in the ledger:** [`results/costs.jsonl`](../results/costs.jsonl) logs 2,083 prediction calls, one per case that reached the model in the two attempts.
- **What you can't check from git alone:** commit dates are set by the author, and the repository was private during the event, so no third party saw the hash at that moment.
- **The labels were committed later.** They were produced before the predictions, as the script requires, but `labels.json` and `labels2.json` only reached git in `f45c833`, about 13 and 11 hours after their scores. So you can't rule out from git alone that they were edited in between. The ledger committed with each hash does log the labeling calls finishing before the first prediction (23:17, then 23:18 in attempt 1; 00:54, then 00:55 in attempt 2), but it doesn't record the labels themselves.
- **The raw posts aren't in the repository.** We don't redistribute Reddit text. The post IDs are the keys in `results/scam_predictions*.json`, so anyone can pull the public threads and compare them to our labels.

The strongest check remains an independent test on new posts. `scripts/validate_scams.py` reproduces attempts 1 and 2 for a few dollars of model credits (see the README, and note that it overwrites the published files). It has no mode for a third sample yet, so a new test would need its own paths and a new rule.

## Early warning is not part of this test

[`scripts/scam_network.py`](../scripts/scam_network.py) replays public reports by date. A campaign is one imitated brand within one family, flagged at 3 reports in 14 days. It flagged 15 campaigns from 478 reports naming a brand, with 34 later reports after the flag, a median of 22.5 days later. We chose the threshold on the same data, so this illustrates the idea and proves nothing about how well it would work. Later reports concentrate in a few big brands: Apple alone accounts for 11 of the 34.

## Cost of the whole project

The ledger in [`results/costs.jsonl`](../results/costs.jsonl) records every model call we made from this machine: under US$ 10 in total, including both attempts and the families. The server keeps its own ledger for live traffic.
