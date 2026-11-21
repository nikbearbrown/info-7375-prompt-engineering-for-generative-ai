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

*Filled in after the single held-out run.*

## Unsafe SQL

Policy denials in development rounds 1 and 2: **0**. Executed SQL failing the policy re-check: **0**. Unsafe SQL was exercised only through the scripted failure cases F1–F3 (`results/failures-2026-11-21.json`), where it was denied before execution and the table still had 437,496 rows afterwards.
