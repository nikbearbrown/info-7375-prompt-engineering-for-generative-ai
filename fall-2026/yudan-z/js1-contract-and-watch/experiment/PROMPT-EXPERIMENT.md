# Prompt experiment (Chapter 2)

## Executive summary

I hand-labeled 20 real postings (10 development, 10 held-out) using a labeling rule I wrote first. I then measured how often Claude's verdict matched my label under a baseline prompt contract and under one revision that changed exactly one line, R1.

- **Development set:** the baseline won, 9/10 to 7/10.
- **Held-out set:** the revision won, 9/10 to 8/10.
- **Overall:** 17/20 vs 16/20.

The two sets point in opposite directions. Ten cases per set are far too few to say the revision helped or hurt; the honest result is "no detectable difference".

## Materials (all in this folder)

| File | What |
|---|---|
| `LABELING-RULE.md` | My labeling rule, committed (`acc396f`) before I labeled anything |
| `split.json` | The 20 real postings (fetched 2026-10-30 from `boards-api.greenhouse.io`), shuffled with `random.Random(7375)` into dev (n=1–10) and held-out (n=11–20) before labeling |
| `postings/*.json` | The raw posting responses |
| `labels.json` | My 20 labels with my reasons verbatim (`50a1f2d`), plus two dated reason revisions (n=3, n=12) made before any model run. **6 relevant: 4 dev, 2 held-out.** |
| `../prompts/contract_v1.txt` | Baseline prompt contract (R1–R9, fixed JSON output) |
| `../prompts/contract_v2.txt` | Revision. **One change: R1** |
| `results/*.json` | Every answer, raw, per prompt × split |

**The one change (v1 → v2):**
```diff
- R1 the title contains one of target_roles.
+ R1 judging from the title AND the content together, the day-to-day work is entry-level data or analytics work of the kind named in target_roles (the title wording alone does not decide it).
```
I chose this change myself after seeing v1's only development miss (#4, "Fraud Investigations Analyst"). There, v1 followed the title rule literally, but my labeling rule judges the work, not the title.

## Commands

```bash
python -m experiment.run_experiment --prompt contract_v1.txt --split dev
python -m experiment.run_experiment --prompt contract_v2.txt --split dev
python -m experiment.run_experiment --prompt contract_v1.txt --split held-out
python -m experiment.run_experiment --prompt contract_v2.txt --split held-out
```

These ran on 2026-10-30, 23:34–23:38 UTC, with one fresh `claude -p` conversation per posting. Terminal output is in `results/terminal-dev.txt` and `results/terminal-held-out.txt`. An invalid answer (one that fails the validator) counts as a miss.

## Results

| Prompt | Development (n=10) | Held-out (n=10) | All 20 | Invalid answers |
|---|---|---|---|---|
| v1 baseline | **9/10** | 8/10 | 17/20 | 1 (held-out #15) |
| v2 one change (R1) | 7/10 | **9/10** | 16/20 | 1 (dev #10) |

Misses, with Claude's own reason:

| # | Split | My label | v1 | v2 | What happened |
|---|---|---|---|---|---|
| 4 | dev | relevant | not_relevant | not_relevant | v1: title has no target role. v2: "fraud alert queue … operations/risk work, not data". Both disagree with me, for different reasons. |
| 9 | dev | relevant | relevant ✓ | not_relevant | v2 judged the work as engineering ("ETL/ELT pipelines … DAGs"). That is arguably right about the work, but it disagrees with my label. |
| 10 | dev | relevant | relevant ✓ | *invalid* | v2's justification ran over 400 characters, so the validator rejected it. |
| 14 | held-out | relevant | not_relevant | not_relevant | Both: finance (FP&A) work, not data analytics. |
| 15 | held-out | relevant | *invalid* | relevant ✓ | v1's justification ran over 400 characters. v2 judged the master's new-grad data-scientist role relevant. |

## What this can and cannot show

- **Cannot show that v2 is better or worse.** The difference flips sign between splits. Overall it is one posting out of 20. One more invalid answer or one changed label would reverse it. With 10 held-out cases, each case is 10 percentage points.
- **Can show where the disagreements live.** Every miss is on a posting I labeled `relevant` whose title is not a plain analyst title (#4, #9, #14, #15) or that produced an over-long answer (#10, #15). Claude never called one of my `not_relevant` postings relevant on held-out.
- **Two of my "misses" may be my label, not the model.** #14 is FP&A finance work, and I labeled #12 (also finance) not relevant. #9's day-to-day work is engineering. A second labeler would help, and I did not have one.
- **The class balance is thin:** only 2 relevant postings in held-out. A prompt that said `not_relevant` to everything would score 8/10 there, the same as v1.
- **Invalid answers matter as much as wrong ones.** 2 of 40 answers broke the 400-character limit. The limit is mine, from the contract, and the validator enforced it.

## Process notes (honesty)

- My first dev runs (v1 9/10, v2 6/10) used descriptions truncated at 6,000 characters, which hid Affirm's no-sponsorship sentence. I fixed the truncation and re-ran both prompts on dev **before** touching held-out. The discarded runs are kept in `results/superseded-truncated-input/` and are not used above.
- I did not look at any held-out result until both prompts were fixed. Held-out ran once per prompt.
