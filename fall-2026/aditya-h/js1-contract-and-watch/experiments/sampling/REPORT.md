# Sampling report (Chapter 1)

**Question:** if I ask Claude my contract about the same posting several times, each in a fresh conversation, how much do the answers vary? And does repeating the same answer mean it's right?

**Setup:** 5 development postings, chosen before any call ([`POSTINGS.md`](POSTINGS.md)), with 4 fresh `claude -p` calls each: no tools, no saved session, an empty working directory. I did this for **both** prompt contracts.
- **v1:** 20 calls, 2026-10-31 22:59–23:01 EDT
- **v2:** 20 calls, 23:06–23:08 EDT

All 40 replies reported the model as `claude-sonnet-5-5`, and every one is recorded in `results-judge_v1.jsonl` / `results-judge_v2.jsonl`. The hand labels are Aditya's (`../prompt/labels.csv`; none of these five was corrected).

```bash
python3 experiments/run_sampling.py --summarize --prompt prompts/judge_v1.txt
```

## Results

**Prompt v1** (no definition of "relevant"):

| id | title | relevant | not_relevant | invalid | hand label | majority = hand? |
|---|---|---|---|---|---|---|
| 7983725 | Staff Product Manager, Billing | 0 | **4** | 0 | relevant | **no**: 4/4 agree, all wrong |
| 8331124 | Product Marketing Manager, Subscriptions | 0 | 4 | 0 | not_relevant | yes |
| 8195440 | Product Manager, Connect Growth & Monetization | **1** | **3** | 0 | relevant | **no**: split 3–1 |
| 8163193 | Design Recruiter | 0 | 4 | 0 | not_relevant | yes |
| 8127182 | Software Engineer, Revenue and Financial Automation | 0 | 4 | 0 | not_relevant | yes |

**Prompt v2** (adds the contract rule):

| id | title | relevant | not_relevant | invalid | hand label | majority = hand? |
|---|---|---|---|---|---|---|
| 7983725 | Staff Product Manager, Billing | 4 | 0 | 0 | relevant | yes |
| 8331124 | Product Marketing Manager, Subscriptions | 0 | 4 | 0 | not_relevant | yes |
| 8195440 | Product Manager, Connect Growth & Monetization | 4 | 0 | 0 | relevant | yes |
| 8163193 | Design Recruiter | 0 | 4 | 0 | not_relevant | yes |
| 8127182 | Software Engineer, Revenue and Financial Automation | 0 | 4 | 0 | not_relevant | yes |

## How much they varied

- **Verdicts:**
  - **v1:** 19 of 20 verdicts matched the majority for their posting. One posting (8195440) flipped once: three replies said "more than three years required … about two years", and one weighed the payments fit higher and said `relevant`.
  - **v2:** 20 of 20 were unanimous.
- **Format:** 0 of 40 replies were invalid.
- **Reasons, even when the verdict didn't change:**
  - v1's arithmetic on Maya's experience moved from call to call. For the same posting, it said "roughly 2 years total", "roughly 1.5 years" and "about 1 year at NTT DATA plus about 1 year at Revvity" (7983725), and "about two" vs "about 2.2 years" vs "roughly 2.3 years" (8195440).
  - The cited résumé fields also changed: for 8331124, one call cited `education[0].degree` and the other three cited `experience[1].bullets[0]`.
  - v2's reasons were near-paraphrases of the rule ("contains the phrase 'product manager', and offices[0].name is exactly 'US'").

## What I can conclude

- **Repeatability is not correctness.** v1 said `not_relevant` to "Staff Product Manager, Billing" four times out of four, perfectly repeatable and wrong against my label. Its reason was its own criterion ("requires 10+ years … far short of the minimum"), which my rule deliberately excludes. Had I sampled only v1 and seen 4/4 agreement, I would have trusted a wrong verdict.
- **The spread showed up where the prompt left room for judgment.** v1's one flip was on the borderline seniority call (8195440), which v1 had to decide for itself. v2 removed that room, and the spread disappeared for these five postings.
- **One sample per posting is risky for a v1-style prompt.** The watch would have been unlucky on 8195440 one time in four. That's why the watch uses v2, and why the report always shows the rule's verdict alongside Claude's.

## What I cannot conclude

- **True error rates.** Four samples per posting can't tell a 0% from a 10% flip rate. "4/4 agree" is compatible with a real chance of disagreeing.
- **Anything beyond these five postings.** They were chosen to include tricky cases, so they aren't a random sample of the board.
- **That v2's unanimity will hold** on postings the rule describes ambiguously, e.g. a location like "Remote (Americas)". None of the five tested that.
- **Variation across models or days.** All calls used one model within ten minutes.
