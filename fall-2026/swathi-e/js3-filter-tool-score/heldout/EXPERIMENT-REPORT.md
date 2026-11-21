# EXPERIMENT-REPORT.md — threshold 5 vs 6 on held-out postings

Reviewed and approved by Swathi, 2026-11-20. Drafted by Claude Code from the committed records;
decisions and labels are Swathi Baba Eswarappa's.

## Purpose and pre-registered hypothesis
`HELDOUT-PLAN.md` (commit `4cbb88c`, written 2026-11-19, before collection)
pre-registered one change: the shortlist threshold 5 -> 6, with filter v1.1
(code `2c3ef12`) otherwise unchanged. FILTER.md's revision "topic words and the
threshold" (2026-11-17, commit `aa1049c`) names it as the candidate experiment:
in v1, every scored posting already has the 2 early-career points, so
role (3) + early (2) = 5 reaches the threshold and topic words never change a
verdict. Threshold 6 would require at least one topic word.

Hypothesis (as framed in FILTER.md): requiring a topic word would remove
shortlisted postings that are not relevant, at the possible cost of missing
relevant ones. The plan fixed the reporting, but not a direction or success
criterion.

## Where every number in the score comes from
Checked against FILTER.md and `job_filter.py` on 2026-11-20.

| Number | Value | Origin | Where and when set |
|---|---|---|---|
| Role weight (R1/R2) | 3 | hand-set | FILTER.md v1 "The score (every number hand-set by me)", commit `0f689b8`, 2026-11-17; code `WEIGHTS["role"]`, `job_filter.py:45`, commit `6e6b4bf`, 2026-11-17 |
| Early-career weight (R5) | 2 | hand-set | same FILTER.md section and commit; `WEIGHTS["early"]`, `job_filter.py:45`, `6e6b4bf` |
| Topic word weight (R7) | 1 each | hand-set | same; `WEIGHTS["topic"]`, `job_filter.py:45`, `6e6b4bf` |
| Topic cap | 3 | hand-set | same; `TOPIC_MAX`, `job_filter.py:46`, `6e6b4bf` |
| Threshold | 5 | hand-set | same; `THRESHOLD`, `job_filter.py:47`, `6e6b4bf` |
| Threshold (experiment) | 6 | hand-set candidate | FILTER.md revision commit `aa1049c`, 2026-11-17; HELDOUT-PLAN.md `4cbb88c`, 2026-11-19; applied only in analysis (`measure_heldout.py`), not in the filter code |

- **Inherited:** none. My JS1 rule (`rule.py`) and JS2 loop (`loop.py`) have
  no weights or scores. The JS1 term lists (US terms and states, non-US
  countries) are reused by R4, but they are not score numbers.
- **Fitted:** none. No number was tuned to data. The v1.1 changes (commits
  `4a6dcfb`, `c0790a4`, `2c3ef12`, 2026-11-19) changed rule wording for R5 and
  R6, not the weights, cap or threshold. `git blame` dates those lines to
  `6e6b4bf`.

## Method
1. **Labels first.** I labeled all 20 rows of `heldout/HELDOUT.csv` from the
   reading files. The labels were committed in `b09f9ce` before any filter ran
   on these postings.
2. **One filter run.** `measure_heldout.py` loaded the saved 2026-11-19 raw
   responses (`runs/2026-11-19T17-31-47-142253-0500/`), with each SHA-256
   checked against `trace.json`. It applied `job_filter.evaluate` (v1.1,
   unchanged) once per held-out posting and recorded the verdict, score,
   points and rule results.
3. **Threshold 6 in analysis.** For a posting with a score, it is shortlisted
   when it has a role match and score >= the threshold. Rejected and "I cannot
   tell" verdicts have no score, so the threshold does not affect them. The
   script checks that its threshold-5 verdict equals the filter's committed
   verdict for every row.
4. **Groups after the run.** `heldout/selection.json` was opened only after
   the filter had run, to assign groups A and B.
5. **Saved once.** The output is in
   `runs/heldout-v1.1-threshold-2026-11-19T17-31-47-142253-0500/measurement.json`
   (commit `698efbb`). It records the SHA-256 of the labels, trace and code.
   The evidence policy writes it once and never overwrites it.

## Results (held-out, per group, never pooled)
These are sample counts for these 20 postings, not rates for all postings.
Group A was chosen by title words, so it is not representative of the boards.

| Group | Threshold | Shortlisted and relevant | Shortlisted and not relevant | Relevant but not shortlisted |
|---|---|---|---|---|
| A (10) | 5 | 0 | 0 | 0 |
| A (10) | 6 | 0 | 0 | 0 |
| B (10) | 5 | 0 | 0 | 0 |
| B (10) | 6 | 0 | 0 | 0 |

- **Abstentions:** I marked 0 rows "can't tell". The filter returned
  "I cannot tell" on 0 rows.
- **Threshold effect:** no verdict changed between thresholds. All 20
  postings were rejected by a gate (R3, R4, R5 or R6) and have no score.

### Group A, per posting
| Row | Posting | Title | Score | At 5 | At 6 | Gate failed | My label |
|---|---|---|---|---|---|---|---|
| 3 | databricks 8930378002 | AI Forward Deployed Engineer - Netherlands | none | rejected | rejected | R4, R5 | not relevant |
| 4 | databricks 8930374002 | AI Forward Deployed Engineer - Germany | none | rejected | rejected | R4, R5 | not relevant |
| 5 | databricks 8952028002 | Specialist Solutions Architect - Azure Infrastructure & AI Platform | none | rejected | rejected | R5 | not relevant |
| 6 | databricks 8793863002 | Senior Manager, AI Forward Deployed Engineering - London | none | rejected | rejected | R3, R4 | not relevant |
| 9 | stripe 8130876 | Software Engineer, New Grad | none | rejected | rejected | R4 | not relevant |
| 13 | databricks 8948868002 | Senior Manager, AI Forward Deployed Engineering | none | rejected | rejected | R3, R4 | not relevant |
| 14 | databricks 8948870002 | Senior Manager, AI Forward Deployed Engineering | none | rejected | rejected | R3, R4 | not relevant |
| 16 | databricks 8948900002 | Senior Manager, AI Forward Deployed Engineering | none | rejected | rejected | R3, R4 | not relevant |
| 18 | databricks 8937360002 | Senior Manager, AI Forward Deployed Engineering | none | rejected | rejected | R3, R4 | not relevant |
| 19 | databricks 8929894002 | AI Forward Deployed Engineer - France | none | rejected | rejected | R4, R5 | not relevant |

### Group B, per posting
| Row | Posting | Title | Score | At 5 | At 6 | Gate failed | My label |
|---|---|---|---|---|---|---|---|
| 1 | stripe 8172495 | Marketing Operations Manager, EMEA Events | none | rejected | rejected | R3, R4, R5 | not relevant (see limitations) |
| 2 | stripe 7370967 | Pre-Sales Solutions Architect, Money Management | none | rejected | rejected | R5 | not relevant |
| 7 | plaid 2602117d-bfcc-407a-ae28-ea3a7c7aa216 | Fraud Intelligence Analyst | none | rejected | rejected | R5 | not relevant |
| 8 | stripe 7917880 | Technical Solutions Engineer | none | rejected | rejected | R5 | not relevant |
| 10 | databricks 8949593002 | Business Development Representative | none | rejected | rejected | R4, R5 | not relevant |
| 11 | stripe 7901987 | Product Manager, Startup Products | none | rejected | rejected | R3, R4, R5 | not relevant |
| 12 | databricks 8930381002 | AI Forward Deployed Engineer - Sweden | none | rejected | rejected | R4, R5 | not relevant |
| 15 | databricks 8893767002 | Solutions Architect - Public Sector (Manufacturing / Supply Chain) | none | rejected | rejected | R5 | not relevant |
| 17 | stripe 8350917 | Activations Specialist, Bridge | none | rejected | rejected | R4, R5 | not relevant |
| 20 | databricks 8893778002 | Solutions Architect - Public Sector (Federal Civilian) | none | rejected | rejected | R5 | not relevant |

### What this result says
- **I judged all 20 postings not relevant.** The filter rejected all 20
  before scoring, so it agreed with me on every row at both thresholds.
- **No verdict changed between thresholds. That is the result.** The
  threshold could not matter here, because no posting reached the scoring
  step.
- **Missed relevant postings cannot be measured on this sample.** It has no
  relevant posting, so "relevant but not shortlisted" is 0 by construction.
  The sample therefore does not test the trade-off that threshold 6 is
  supposed to reveal.
- **Nearest case: row 9**, Stripe "Software Engineer, New Grad". It passed
  R1, R3, R5 and R6, had 0 topic words and failed only on location
  (Bangalore). Had it been in the US, it would have scored 5: shortlisted at
  5, not shortlisted at 6. That is a hypothetical, not a measurement.

## Limitations
- **Row 1's label was not independent.** I formed the verdict myself but
  consulted ChatGPT about the labeling format and the verdict before
  recording it. Its `how_judged` says so. Rows 2–20 were judged
  independently, with no AI draft. Row 1's outcome does not depend on the
  threshold (the filter rejected it on R3, R4 and R5).
- **No relevant and no scored postings.** With n = 20, every count is 0 and
  no rate can be estimated. Group A's title-word selection did not produce
  any eligible early-career US role.
- **One collection, three boards, one date.** 60 new postings: Databricks 33,
  Stripe 25, Plaid 2.
- **Group A excludes interns** and was chosen by title words. It is not
  representative.
- **Threshold 6 was applied in analysis.** This is equivalent to the code
  change only because the verdict depends on the score solely through
  `is_shortlisted`. The script checks that equivalence at threshold 5.

## Development data: Nov 17 batch, used to build v1.1, NOT held-out
This batch was used to build v1.1, and its audit labels were seen while
changing the rules, so it is not evidence for the experiment. All audit
labels below were recorded after seeing a ChatGPT-assisted draft (rows 5–48
of the audit). The v1 and v1.1 scores are identical for these postings.

| Audit row | Posting | Title | v1.1 score (points) | At 5 | At 6 | My audit label |
|---|---|---|---|---|---|---|
| 42 | databricks 6865698002 | Software Engineer - New Grad (2027 Start) | 6 (3+2+1) | shortlisted | shortlisted | relevant |
| 16 | databricks 6865704002 | Software Engineer - New Grad, Distributed Data Systems (2027 Start) | 5 (3+2+0) | shortlisted | **not shortlisted** | relevant |
| 24 | stripe 8128744 | Software Engineer, New Grad | 5 (3+2+0) | shortlisted | **not shortlisted** | relevant |
| 12 | stripe 8212508 | Software Engineer, Early Career — Immediate Start | 5 (3+2+0) | shortlisted | **not shortlisted** | relevant |

- **Postings not shortlisted in this batch.** The batch's other two scored
  postings were not shortlisted at either threshold, since neither has a role
  match. They are Product Design New Grad (score 4; audit row 35, adjudicated
  not relevant in `audit/ADJUDICATION.md`) and Sales Development
  Representative (score 2; not relevant).
- **The trade-off this suggests.** At threshold 6, three of the four
  shortlisted postings would drop, and I had labeled all four relevant. Here,
  threshold 6 removes no non-relevant posting, because there was none on the
  shortlist, and it loses three relevant ones.
- **Why they would drop.** Early-career software-engineering postings
  describe the work in words that are not on the R7 topic list. A topic-word
  requirement filters on vocabulary rather than on fit.
- **What this does not show.** These are development observations on a batch
  that shaped v1.1. They are not held-out evidence, and they are not a
  measured effect of threshold 6.

## Why the behavior persists: saved files and rules, not model training
- **The filter is deterministic Python** (`job_filter.py`, standard library
  only). It makes no model call, so its verdicts are fixed by FILTER.md's
  rules as coded, and by the hand-set numbers above.
- **What carries across sessions is in files.** These are FILTER.md and its
  change log, the tests (`tests/`), `TEST-PREDICTIONS.md`, the saved raw
  responses and traces under `runs/`, the JS2 state file
  (`state/seen_ids.json`), the audit and held-out label files, and the git
  history.
- **Anyone can rerun it.** The same inputs and code produce the same output,
  and each result file records the SHA-256 values needed to check that.
- **No model was trained or fine-tuned** on my labels or these postings. The
  v1.1 change came from me rewriting rules after reading the audit
  disagreements, recorded in FILTER.md's change log and then implemented
  test-first.
- **Claude Code and ChatGPT keep nothing between sessions.** They don't learn
  from these labels. When Claude Code continues the work, it reads these
  files again.
- **To change the behavior, change a file**, such as a rule in FILTER.md, a
  number in `job_filter.py` or a test, and record why in the change log.

## Decision
Decision (2026-11-20, Swathi): Keep threshold 5; threshold 6 is not adopted.

- **Held-out:** No measurable difference because all 20 postings were
  rejected by gate rules before scoring.
- **Development data (not held-out):** Threshold 6 would drop 3 of the 4
  postings I judged relevant and remove none I judged not relevant.
- **Not checked:** A held-out sample containing relevant postings.
