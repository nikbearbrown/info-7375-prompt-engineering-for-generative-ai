# Prompt experiment — plan, frozen before any experiment call

**Frozen:** 2026-10-31, about 23:05 EDT. At that point no sampling or experiment call had been made. The only Claude call so far was the one smoke test on posting 8275556 (see `evidence/`).
**Drafted by:** Claude Code. Aditya asked Claude Code to "run it and finish the assignment".

## The one change

| | `prompts/judge_v1.txt` (baseline) | `prompts/judge_v2.txt` (revision) |
|---|---|---|
| Résumé, posting, output format, citation rules | same | same |
| Definition of "relevant" | **none**: "decide whether the posting is relevant to this person's job search" | **adds the CONTRACT rule `title-us-v1` verbatim**, with "do not add other criteria such as years of experience, seniority, or salary" |

`diff prompts/judge_v1.txt prompts/judge_v2.txt` shows that the only difference is the inserted DEFINITION block.

**Why this change:** the hand labels follow the contract rule (`LABELING-RULE.md`). The baseline lets Claude use its own idea of "relevant". The smoke test showed it doing exactly that: it rejected a US PM role over years of experience and over not being in Boston.

**Prediction, written before running:** v2 will pass more development cases than v1. The likely v1 failures are US PM-family postings, which v1 rejects for seniority or for not being in Boston.

## Procedure

1. Both prompts are frozen now. v2 was **not** tuned on development results; there is a single revision.
2. Collect replies: v1 on dev, v2 on dev, then v1 and v2 on held-out (`run_experiment.py --final`). Collecting replies does not read the hand labels.
3. Aditya hand-labels the 20 postings without seeing any Claude verdict from these runs.
4. Score with `python3 experiments/run_experiment.py --score`: dev first, then held-out.

**Pass** = the reply is valid under the contract validator **and** its verdict equals Aditya's hand label. An `invalid` reply counts as a fail.

## Honest limits, stated in advance

- 10 cases per set: one case is 10 percentage points. A difference of one or two cases is noise.
- The postings come from one board on one day, and the rule is narrow.
- Each prompt gets one sample per posting here; the sampling report covers run-to-run variation.
- Collecting held-out replies at the same time as dev replies is acceptable here only because neither prompt is changed after any result is seen.
