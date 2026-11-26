# The filter and the reject audit (JS3, step 2.1)

## 1. The run

The filter ran offline on everything the agent collected: **1,235 postings** from 16 saved raw
responses of four boards (Stripe 871, Ramp 181, Figma 150, Linear 33; a posting seen in several
raws counts once, from its newest). No source was missing; no posting lacked a title.
`ashby/linearapp` and `greenhouse/ramp` are excluded by FILTER.md §3.

| Version | Kept | Run summary |
|---|---:|---|
| v0.1 (written before the code) | 65 | [`filter/FILTER_RUN_v0.1.md`](filter/FILTER_RUN_v0.1.md) |
| v0.3 (current) | 53 | [`filter/FILTER_RUN_v0.3.md`](filter/FILTER_RUN_v0.3.md) |

Every posting's decision and every rule's points: `data/js3/filter/decisions-v0.1.json`,
`decisions-v0.3.json`.

## 2. False friends (found by Claude, by counting and reading matched sentences)

| Word | Rule | Matched for the wrong reason | Example | What was done |
|---|---|---|---|---|
| **"API" / "APIs"** | R5 topic | Stripe sells APIs, so sales and product postings say it: "preferably at an API-first company", "Ability to understand the Stripe API" (Account Executive postings). 193 of 984 postings without a role word got R5 from these two words alone | It lifted 8 generic-title specialty jobs (Security, Solutions, Compliance, Integration Engineer) over the line | Cut in v0.2 |
| **"engineer"** | R2 generic word | Right word, different job: "Security Engineer", "Technical Solutions Engineer", "Integration Engineer, Professional Services" | 4 such postings were still kept in v0.2 | R2 blockers in v0.3 |
| "SQL", "Python" | R4 skills | Analyst and data-science postings list them: SQL is the most common skill in postings with no role word (172) | None kept: without a role word the score cannot reach 7 | Recorded; no change |

Every rule added, cut, or rejected after measuring, with its measured effect, is in FILTER.md §8.

## 3. The audit

Drawn once, as registered in FILTER.md §5, by `uv run python -m job_search_agent.js3 audit-draw`
(commit `e470923`, before any hand verdict existed), from the **v0.1** decisions:

| Stratum | n | How drawn |
|---|---:|---|
| Random rejects | 40 | `random.Random(20261125).sample` of the 1,170 v0.1 rejects |
| Closest rejects | 8 | Highest-scoring rejects (score 6) |
| Closest kept | 8 | Lowest-scoring kept (score 7) |
| Random kept | 12 | Same generator, from the kept postings not already drawn |
| Changed or contested | 14 | Every posting whose decision differs between v0.1 and v0.3 (12), plus the two Forward Deployed Engineer postings (FILTER.md §8) |

78 distinct postings in the [blind worksheet](audit/WORKSHEET.md): shuffled, with no score, no
decision and no stratum. The strata and scores are in `data/js3/audit/draw.json`.

**The hand verdicts are Shubham's, not Claude's.** Claude made no verdict on any of these
postings. The report, [`audit/AUDIT_REPORT.md`](audit/AUDIT_REPORT.md), is generated from
`experiments/js3/audit/hand_verdicts.json` by `uv run python -m job_search_agent.js3 audit-report`.
It counts, for v0.1 and v0.3 on the same postings, how many the filter got wrong in each stratum,
gives an exact 95% interval for the miss rate among all rejects from the 40 random ones, and lists
every posting the filter got wrong and whether each v0.2/v0.3 change was right.

**What a sample of 40 can show** (FILTER.md §5): with 0 misses the exact 95% upper bound is 8.8%;
with 1 miss, 0.1% to 13.2%; with 2, 0.6% to 16.9%. Applied to 1,170 rejects, even zero misses in
40 cannot rule out about 100 relevant postings lost, more than the 65 the filter kept. The audit
can catch a filter that is badly wrong; it cannot certify one as good. The close calls and the
kept sample are not random, so they get counts, not rates.

### My reading of the audit 

The audit shows that the filter has improved from v0.1 to v0.3, particularly by addressing misleading keyword matches and adding blockers for generic engineering titles. However, the results also make it clear that a higher filtering accuracy does not necessarily mean we are capturing every relevant opportunity. The 40 randomly sampled rejects provide a useful indication of potential false negatives, but the sample is too small to confidently rule out a significant number of missed postings across the full dataset. I also think the closest rejects, closest kept, and changed postings are important because they help identify where the rules are working and where they may still need refinement. Going forward, I would rather keep the filter conservative and continuously improve it using actual audit findings than aggressively reject postings based on keywords alone. My takeaway is that v0.3 is a better starting point, but the filter still needs ongoing validation before we can rely on it to capture relevant opportunities consistently.

Before making my judgments, I reviewed the job titles and descriptions without seeing the filter's scores, decisions, or audit categories, so my verdicts were based on the actual posting content. Out of 40 randomly sampled rejects, I found 0 relevant postings (95% confidence interval: 0–8.8%), but this still means we cannot rule out approximately 100 relevant postings being missed across all 1,170 rejects. However, the bigger finding was that the filter tends to keep too many irrelevant postings rather than reject too many relevant ones: 4 of 8 closest rejects were relevant, while 9 of 12 randomly sampled kept postings were not relevant, with most of the latter requiring 5+ years of experience. I also judged all 12 postings whose decisions changed between v0.1 and v0.3 as correctly handled by the newer rules. This suggests that the changes made in v0.2 and v0.3 were directionally right, although it does not establish overall filter accuracy. My next step would be to tighten the experience criteria to remove unsuitable 5+ years postings while revisiting score-6 rejects to avoid missing potentially relevant opportunities.
