# Failure log — SponsorSQL evaluation, 2026-11-21

Every failed case, with what the model's SQL did, what the key expected, and the cause. Raw outputs: `results/*.json`. Model replies, word for word: `proposals/*-raw.json`. The October draft-SQL evaluation is a separate, earlier file: `FAILURE-LOG-october-draft.md`.

## Development round 1: contract v1, 4/10 (`results/dev-round1-contract-v1.json`)

| Q | Result | What the SQL did | Expected (key) | Cause |
|---|---|---|---|---|
| D1 | Pass | — | — | Substring title match, but no near-match title occurred among the top ten Massachusetts employers |
| D2 | Pass | 40 | 40 | Same as D1: the Boston rows had no near-match titles |
| D3 | **Fail** (budget stop) | Its evidence query joined `lca` to a 10-row CTE on text columns with `IS`; ran past 10 s | Top ten cities | No index on 437,496 rows; the time budget interrupted the statement and the loop stopped (`budget_exhausted`), as designed |
| D4 | **Fail** | 10 of 49 states differ, for example MA median 100,043 on 103 cases | MA 100,021.5 on 104 cases | `LOWER(JOB_TITLE) LIKE '%data analyst%'`: near matches in, punctuation variants out (predicted in `../pre-mortem.md`) |
| D5 | **Fail** | I 1,026 · II 1,605 · III 514; blank labelled `(blank)` | I 1,027 · II 1,609 · III 516; `[blank]` 402 | Substring title match; blank label differed |
| D6 | **Fail** | 218 of 1,297 employer entries differ | 1,114 employers | Substring match, plus `business intelligence analyst` added beyond the three phrases the question names |
| D7 | Pass | — | — | Capgemini titles had no near-match variants |
| D8 | **Fail** | Data Scientist 2,631 | 2,636 | Grouped `JOB_TITLE` untrimmed, so `"Data Scientist "` was split off |
| D9 | **Fail** | 7 of 9 months differ, for example 2026-04: 696 | 701 | Substring title match |
| D10 | Pass | — | — | — |

**Reading:** the predicted failure appeared in four questions (D4, D5, D6, D9). Each query ran without error and looked reasonable. Only the independent key showed the counts were wrong.

## Development round 2: contract v2, 9/10 (`results/dev-round2-contract-v2.json`)

| Q | Result | What the SQL did | Expected (key) | Cause |
|---|---|---|---|---|
| D1–D7, D9, D10 | Pass | — | — | `title_has()`, trimming, the `[blank]` label and the `IN (SELECT …)` rows query fixed the round-1 causes |
| D8 | **Fail** | Data Scientist 2,635 · Senior Data Scientist 602 · Business Analyst 491 · Machine Learning Engineer 319 | 2,636 · 603 · 493 · 320 | Four source titles end in a non-breaking space or tabs (`'Business Analyst\xa0'` ×2, `'Senior Data Scientist\t\t\t'`, `'Data Scientist\xa0'`, `'Machine Learning Engineer\xa0'`). The key uses Python `strip()`, which removes them; the contract tells the model to use SQLite `TRIM()`, which removes spaces only. **A definition gap between the key and the contract, not a model mistake.** |

**Not fixed on purpose:** a v3 contract could define trimming to include tabs and non-breaking spaces. It wasn't written, because the development bar (8/10) was met, and every further revision tuned on development makes the held-out score less meaningful. Recorded as an open item in `../transfer-reflection.md`.

## Held-out: contract v2, scored once (`results/heldout-contract-v2.json`)

**5/5 pass.** Third, separate SQL-writer subagent; 1 tool use; contract v2 unchanged after development round 2.

| Q | Result | Answer | Note |
|---|---|---|---|
| H1 | Pass | 564 Business Analyst cases in Texas | Count check: answer 564 = 564 matching rows |
| H2 | Pass | Top ten Boston employers, any title (Wayfair LLC 158, Amazon.com Services LLC 156, …) | — |
| H3 | Pass | Median annual base wage, Data Scientist, California: $174,304.00 (1,595 Year-unit cases) | **Defect found in SponsorSQL, not in the model:** the model labelled this median `answer_type: "count"`, so the count-versus-rows check compared 174,304 with 1,595 rows and showed **"MISMATCH"** in the gate view. That warning is a false alarm. Cause: the contract offers only `count`, `ranking` and `table`, with no type for a single non-count value, and the check trusts the label. Not patched after the held-out run; listed as an open fix in `../transfer-reflection.md`. |
| H4 | Pass | Wage levels for SOC 15-2051 certified H-1B: I 4,455 · II 9,747 · III 5,102 · IV 4,332 · [blank] 3,076 | — |
| H5 | Pass | 20 denied H-1B Data Engineer cases | Count check: 20 = 20 matching rows |

**What 5/5 can and cannot show:** five questions, one file, one model run each. It shows that contract v2 carried over to questions it was not tuned on (new title phrases, a new state, a median, a denied status, an untitled ranking). It does not estimate accuracy on arbitrary questions; with five items, one more failure would drop the score to 4/5.

## Unsafe SQL

No model reply in any round was denied by the policy: the model never attempted unsafe SQL. So "0 unsafe SQL executed" is true, but it isn't evidence about the policy. (An earlier "executed SQL failing policy" field re-checked SQL that could only run after passing the same check; it was removed after the independent review, finding 2.) The policy itself is evidenced by tests 1–4 and the scripted failure cases F1–F4 (`results/failures-2026-11-21.json`, `results/failures-after-review.json`), where unsafe SQL was denied before execution and the table still had 437,496 rows afterwards.

## Re-scored after the independent review

The comparators were made stricter: single values must be one row and one column; counts must be whole numbers; labels must be unique. The same saved replies were then re-scored (`results/*-rescored-after-review.json`, `../evidence/rescore-after-review.log`): **development v1 4/10, development v2 9/10, held-out 5/5. No case changed.** The replies, contracts and keys were not changed.
