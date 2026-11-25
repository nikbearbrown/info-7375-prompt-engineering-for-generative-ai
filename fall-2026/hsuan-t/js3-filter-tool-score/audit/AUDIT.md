# Filter audit (hand labels vs the rule filter)

k counts the samples where Isaac's label differs from the filter's verdict.

| stratum | n | k | k/n | 95% Clopper-Pearson interval |
|---|---|---|---|---|
| random_reject | 30 | 1 | 0.033 | 0.001 – 0.172 |
| close_call | 10 | 3 | 0.300 | 0.067 – 0.652 |
| kept | 10 | 4 | 0.400 | 0.122 – 0.738 |

This is an estimate from 30 random rejects, not a measured rate for all postings.

## Disagreements

| sample | title | filter verdict | Isaac's label and reason |
|---|---|---|---|
| S01 | Software Engineer, Early Career — Immediate Start | relevant | not_relevant: Professional experience exceeds the 18-month new grad limit. |
| S11 | Product Evals Engineer, ChatGPT Learning | not_relevant (cut at 1b) | relevant: Internal AI tooling; limited direct eval experience |
| S16 | Software Engineer, Backend | relevant | not_relevant: Six years of software development required |
| S17 | Software Engineer, AI accelerator Runtime | relevant | not_relevant: No accelerator runtime or hardware simulation experience |
| S20 | Software Engineer, Applied Emerging Talent (2027) | relevant | not_relevant: 0–1 year target; over the range |
| S24 | Connectivity Software Engineer, Consumer Devices | relevant | not_relevant: No Linux wireless shipping or C/C++ driver experience |
| S42 | Host Systems Software Engineer | relevant | not_relevant: No C/C++ or low-level systems experience |
| S46 | Software Engineer, Core Network Engineering | relevant | not_relevant: No low-level Linux or datacenter networking experience |

## False friend

**S20** — openai `55150071-fce8-48f5-aea4-14ed78b83511`, "Software Engineer, Applied Emerging Talent (2027)" (chosen by Isaac, 2026-11-25).

JD: "0-1 years of experience in software engineering or a relevant field"

Rule 4 read it as `min 0 years ≤ 4` and passed it: the number matched the rule. But in this JD the number is a **ceiling**, not a requirement. The role is for people with at most 1 year, and Aarav has 2, so he is too experienced. The words fit the rule, and the meaning is the opposite. Isaac: `not_relevant` ("0–1 year target; over the range"). The same thing happens in S01 ("no more than 18 months of professional experience").

## Rule changes (v2)

Measured 2026-11-25 by `reports/filter_v2_measure.py` → `reports/filter_v2_measure/result.md` (A, B1, B2, C on all 2,123 postings and these 50 labels). Isaac's decisions (2026-11-25, FILTER.md §5): **A added** (experience ceiling), **B2 added** (largest years number, "(6) years" read), **B1 rejected** (no effect), **C rejected** (≥ 2 skills broke 5 of his relevant labels), **L1 rejected** (0 verdict changes under v2). Later, v2.1 changed one rule-5 phrase, found on the F5 held-out set (FILTER.md §5).

Under v2 (`audit/all_verdicts.json`; the v1 run this audit judged is kept in `audit/v1/`): relevant 70 → 59, disagreements with these 50 labels 8 → 5 (S11, S17, S24, S42, S46). The table above stays the audit of **v1**; the v2 rules were found on these same samples, so the 5 is not an independent measurement.
