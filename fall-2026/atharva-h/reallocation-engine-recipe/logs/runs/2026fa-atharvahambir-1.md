# Run 1 — data-roles daily check — 2026-10-03

## Executive summary

This records the first logged run of the daily data-role checker: an offline sample run as a fictional persona against invented job postings and the real sponsorship data shipped with the repo. It read 11 of 13 company boards, kept 13 of 22 postings, and ended with 6 Apply, 1 Consider, 2 Skip and 4 held for the person. Every stopping point behaved as designed. No real person's data was used, and no human decision has been recorded yet.

## Record

*Paths below are as they were at run time; the folder and recipe were renamed from `atharvahambir-data-roles-opt90-h1b-daily` to `atharvahambir-reallocation-engine` on 2026-10-03 (current recipe: `recipes/cases/2026fa/atharvahambir-reallocation-engine.md`).*

- **Recipe:** atharvahambir-data-roles-opt90-h1b-daily v0.1.0 (`recipes/cases/2026fa/atharvahambir-data-roles-opt90-h1b-daily.md`)
- **Mode:** offline sample — saved board responses, no network (simulated date 2026-10-01; run on 2026-10-03)
- **Command:** `python3 scripts/contrib/2026fa/atharvahambir-data-roles-opt90-h1b-daily/daily_check.py --sample --out-dir course/2026fa/submissions/atharvahambir/runs/evidence-2026-10-03/sample`
- **Inputs:** candidate `search/examples/atharva/daily-check.candidate.json` (fictional persona) · targets `scripts/contrib/2026fa/atharvahambir-data-roles-opt90-h1b-daily/fixtures/targets.sample.json` (13 companies; postings and E-Verify values synthetic) · sponsorship CSV sha256 `eccdee2addf472b1…` (30,369 rows, 1,557 with H-1B fields)
- **Outputs:** `course/2026fa/submissions/atharvahambir/runs/evidence-2026-10-03/sample/2026-10-01/` → `daily-check.json`, `daily-check.md`, `roles.json`, `role-scores.json`, `role-scores.md`; plus `course/2026fa/submissions/atharvahambir/runs/evidence-2026-10-03/sample/state.json`
- **Result:** boards read 11/13 · listed 22 · matching 13 (new 13, first run) · Apply 6 · Consider 1 · Skip 2 · Needs you 4 · closed 0 · network 1 (Databricks) · not checked 2
- **Gates:**
  - G0: passed. Deadline 2026-12-17, set by the unemployment allowance; the OPT end date is 2027-03-15.
  - G1: Adobe not checkable (Workday link); Dropbox not checked (no saved response).
  - G3: Roblox gated to 0, because a 12-week hire starts 2026-12-24, after the deadline.
  - G4: Moloco skipped (not E-Verify enrolled, a synthetic value); Pinterest held (enrollment not recorded; the scorer would say Apply, 0.367).
  - G5: Coinbase held (row has no H-1B fields), Northwind Analytics held (no row), Apricus Biosciences held (record identical to ASCUS BIOSCIENCES INC).
  - G6: scorer exit 0, `_scorer = bayesian-role-scorer`.
- **Checks run alongside:** 18 offline tests pass (`course/2026fa/submissions/atharvahambir/runs/evidence-2026-10-03/02-prototype-tests.txt`); all 4 break mutants caught (`course/2026fa/submissions/atharvahambir/runs/evidence-2026-10-03/09-break-attempts.txt`); conformance passes (`course/2026fa/submissions/atharvahambir/runs/evidence-2026-10-03/04-conformance-prototype.txt`).
- **Human decision (G7):** Atharva Hambir, 2026-10-03 — "Reviewed; the decisions make sense for the sample, including the Apply, Consider, Needs you, and Skip outcomes. No action from me because the data is fictional."
- **Open issues:**
  - No live run yet, so the filters have only seen synthetic postings.
  - F5 (sponsor on record but no matching title) is visible in the report but has no dedicated test assertion.
  - E-Verify and hiring-time inputs have no data source.
  - The repo's PII scan reports one finding that predates this work (an email in `package-lock.json`); this work adds none.
