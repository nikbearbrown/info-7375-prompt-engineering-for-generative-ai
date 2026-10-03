# CHANGE-BRIEF — Data Analyst, OPT ending in 90 days, H-1B sponsors

## Executive summary

This is the plan, written *before* building anything, for a job-search recipe aimed at one person: a master's student looking for Data Analyst jobs whose work authorization ends in 90 days and who will need an employer willing to sponsor a work visa. The recipe checks each candidate job against three things the student cannot easily see from outside — whether the employer has a real record of sponsoring visas for analyst-type work, whether the posting is actually still open, and whether the employer's hiring process can realistically finish before the authorization runs out — and returns Apply, Consider, or Skip with every input labeled by where it came from.

Read this if you want to know what the recipe will and will not be able to check, and what I predicted would go wrong. The main finding from the pre-build look at the data: the sponsorship dataset carries visa history for only about one company in twenty, it records job titles as free text rather than occupation codes, and the funding samples that ship with the repository do not match any company in it. So the recipe's honest core is **sponsorship + liveness + timeline**; funding is reported as "not available on sample data," not faked.

---

## Record

- **Author:** Atharva Hambir (GitHub `AtharvaHambir`; namespace written lowercase `atharvahambir`)
- **Written:** 2026-09-30, before any prototype code exists
- **Proposed slug:** `atharvahambir-data-analyst-opt90-h1b-15-2051`
- **Revision policy:** original predictions below are frozen. Later corrections go in *Revisions* at the bottom, dated; nothing above that line is rewritten.

## 1. The career situation

| Field | Value | Label |
|---|---|---|
| Degree | MS student (analytics/data program) | your-input |
| Target role | Data Analyst (entry-level / new grad; includes BI Analyst titles) | your-input |
| Work authorization | F-1 OPT, end date **about 90 days out** (exact date kept in the private profile, not here) | your-input |
| Unemployment days already used | not yet recorded — required input, no default | your-input |
| STEM OPT extension eligibility | see *Revisions* (2026-09-30 r1) | your-input (DSO) |
| Sponsorship need | needs an H-1B sponsor | your-input |
| Target occupation code | SOC 15-2051 (Data Scientists), with 15-2051.01 Business Intelligence Analysts as the O*NET detail row. There is **no dedicated "Data Analyst" SOC**; this mapping is my judgment, not a record. | your-input |

**Why this is specific enough:** the binding constraint is not "find a sponsor" — it is "find a sponsor whose process finishes inside a 90-day window, for a job title the public data doesn't code cleanly." A student on a 24-month STEM runway, or targeting software engineering, would get a different recipe.

**Engine layers used:** 80 Days to Stay (sponsorship), Job-Ops (liveness), visa timeline (a new computation — see §2). The Cognitive Pivot layer (BLS/O*NET) is used for *reporting only*, not scoring (Fact 1).

## 2. What I reuse, and what I propose

### Reused (paths verified present on a fresh clone, 2026-09-30)

| What | Path / command | Checked |
|---|---|---|
| Sponsorship + funding CSV | `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` | 30,369 rows; only **1,557** have H-1B fields; **34** list a "data analyst" title; **166** list any "analyst" title |
| Form D samples | `data/sec/form-d/processed/sample/companies-sec-2025q{2,3,4}-d.sample.json`, `…-2026q1-d.sample.json` | 196 companies; **0** match any CSV company by normalized name |
| Occupation / wage rows | `data/bls/compact/soc_occupation_compact.csv` | rows exist for `15-2051.00` and `15-2051.01` |
| Liveness checker | `npm run ats:liveness -- <url>` (`scripts/ats/check-liveness.mjs`) | returns active / expired / uncertain; exits 1 if any URL isn't active |
| Scorer | `npm run score -- <roles.json> --out-dir <dir>` (`scripts/score/role-scorer.mjs`) | ran on `data/examples/ch11-roles.json`: Apply 2 · Consider 1 · Skip 2 |
| Gate harness (reference for test style) | `npm run score:gates` (`scripts/score/gate-harness.mjs`) | present |

The prototype will **not** copy the scorer. It will write a `roles.json` shaped like `data/examples/ch11-roles.json` and shell out to `npm run score`.

### Proposed (repo does not have these)

| Addition | Why it belongs | Marker |
|---|---|---|
| `timeline_factor(auth_end_date, today, unemployment_days_used, expected_time_to_start_days, buffer_days)` in my contrib folder | Ch.10 describes the factor and three worked cases (≈5 months → 0, ≈6 weeks → ≈1, ≈12 weeks → ≈0.6) but **no script implements it**. The mapping from buffer to a number between 0 and 1 is not pinned anywhere. | `[TODO: DEV]` + `[TODO: DEFINE]` the curve |
| Analyst-title matcher over `top_job_titles_sponsored` | The CSV has no SOC column; "has this company sponsored analysts?" can only be answered by text-matching a list of at most five titles. | `[TODO: DEFINE]` include/exclude lists |
| Sponsorship tier cut-offs (approvals, approval rate → Proven/Likely/Unknown/Avoid) | Ch.7 says the thresholds are **not pinned** and need reconciling with the SDD. I will propose numbers and label them mine. | `[TODO: DEFINE]` |
| Per-company hiring-lag table | No repo data on time-to-hire. Every value will be your-input with a stated source (recruiter said / Glassdoor-type estimate / guess). | `[TODO: DATA SOURCE]` |
| Cap-exempt employer flag | For an OPT end date in late December, a cap-subject H-1B may not bridge the gap without a STEM extension — **this is a legal question for the DSO, not a rule the recipe applies.** The repo has no cap-exempt field. | `[TODO: DATA SOURCE]` |

## 3. Gates (hard stops)

| Gate | Testable condition | What the human must see to clear it |
|---|---|---|
| **G0 — Intake** | persona JSON parses; `auth_end_date` > today; `unemployment_days_used` present; `stem_status` ∈ {`dso-confirmed-eligible`, `not-eligible`, `unknown`} | the dates, and that `stem_status` came from the DSO. `unknown` is allowed but forces the conservative (no-extension) runway. |
| **G1 — Liveness** (gate) | each role's `ats:liveness` line is `active` → factor 1.0, `expired` → 0.0. `uncertain` **stops that role** — not scored as live or dead. | the URL and the checker's reason (e.g. `ERR_TOO_MANY_REDIRECTS`), then a manual look at the posting |
| **G2 — Timeline** (gate) | factor computed with the three dates shown (today, expected start, auth end); expected start > auth end → 0.0 | whether each hiring-lag estimate is believable, and its source |
| **G3 — Decision** | Markdown report exists and every row has sources on every term | the person reads it and decides; the recipe applies to nothing itself |

Gate artifacts are written to `course/2026fa/submissions/atharvahambir/runs/` (exists once I create it) — **not** `logs/gate-decisions/`, which does not exist (Fact 4).

## 4. Predicted failure cases, and how I'll check each

| # | Failure | Expected handling | How I'll exercise it |
|---|---|---|---|
| F1 | **Company not in the CSV** | sponsorship = *no record*, tier Unknown, labeled; **never p = 0**. Unknown ≠ Avoid (Ch.7). | fixture role with a made-up company name |
| F2 | **Company in CSV but H-1B fields empty** (28,812 of 30,369 rows) | same as F1 — absence of a record is not evidence of non-sponsorship | fixture using a real CSV row with empty `Total Approvals` |
| F3 | **Posting dead or unreadable** | `expired` → liveness 0 → Skip (gated). `uncertain` → role held for human, not scored | reuse the observed cases: fake Greenhouse ID → expired; Databricks URL → uncertain (redirect loop) |
| F4 | **Expected start after the OPT end date, or OPT date already past** | timeline 0 → Skip; past auth date fails G0 and the run stops | fixture persona with `auth_end_date` in the past; role with 150-day lag |
| F5 | **Sponsor record exists but no analyst title** | sponsorship tier from volume/approval rate, but flagged "no analyst-type title in the ≤5 listed" | real row, e.g. a large engineering-only sponsor |
| F6 | **Suspected join artifact** — two companies with identical H-1B fields (observed: APRICUS BIOSCIENCES INC and ASCUS BIOSCIENCES INC, both 90 / 0 / 100%, same titles) | flagged for human review, value not trusted as a record | check on those two rows |

## 5. What I predict the prototype will get wrong on the first pass

1. **The title matcher will misfire.** A regex for "analyst" will pull in Financial / Clinical / Security analysts and miss titles like "Analytics Associate" or "BI Engineer." I expect the first run's "analyst-type sponsor" list to need hand-pruning.
2. **The timeline gate will look more precise than it is.** The formula will be exact; the hiring-lag input feeding it is a guess with no record behind it. The factor will print to three decimals on a number I made up.
3. **The funding signal will contribute nothing** on sample data (0 of 196 Form D companies match), and the CSV's own `latest_funding_*` columns have no documented provenance. I expect to report funding as unavailable rather than use it.

## Open questions (for me, not answered by the data)

- Is my program STEM-eligible, and has anything been filed? (DSO)
- Should `role_quality` get a non-zero weight? Current plan: **no** — report the 15-2051 wage row beside the decision, leave the scorer's weight at 0.0 as shipped (Fact 1), and say so.
- The CSV README names `mapped_student_employment_targets.csv`; the shipped file is `_v3.csv`, and neither says which fiscal years the H-1B counts cover. I'll treat recency as unknown.

---

## Revisions

*Dated entries only; the predictions above stay as written.*

### 2026-09-30 r1 — STEM status known; real data moved out of tracked files

**Changed input.** The program is STEM-designated → `stem_eligible: true` (your-input; the CIP code and filing still to be confirmed with the DSO — the recipe never asserts eligibility).

**What this changes in the design:**

- Unemployment ceiling becomes 150 days once on the extension (Ch.10), instead of 90.
- **It does not remove the current OPT end date as the job-search cliff** (my understanding — to confirm with the DSO): the extension is filed on the basis of a job with an employer enrolled in E-Verify that signs a training plan (Form I-983), and must be filed before current OPT ends. So the runway is *land an E-Verify employer's offer before the end date*, then the longer extension applies. The G2 timeline gate is therefore still computed against the current OPT end date.
- **New gate G1b — E-Verify.** Testable condition: each role carries `e_verify: {enrolled: true|false|unknown, source}`. `false` → Skip (gated); `unknown` → held for the human, like `uncertain` liveness. The repo has no E-Verify data → `[TODO: DATA SOURCE]`; for now the value is your-input from E-Verify's public employer search, with the date checked.
- The *Open questions* item "Is my program STEM-eligible?" is answered; "has anything been filed?" is still open (nothing filed — no employer yet).
- Earlier worry about cap-subject H-1B timing is reduced but not closed: it becomes a DSO question about the extension period, not a gate this recipe computes.

**New failure case F7:** employer sponsors H-1B but is not E-Verify enrolled (or unknown) → cannot support the STEM extension → gated/held, never scored as clear.

**Data-contract correction (not a prediction change).** DATA_CONTRACT §Zero-Conditions counts real immigration details tied to a real person as PII that may never be committed. §1 originally stated my exact OPT end date; I replaced it with "about 90 days out." Real dates and status now live only in the gitignored private profile (`private/`). Committed fixtures and the worked run will use a fictional persona with the same *shape* of situation (Data Analyst, STEM, ~90 days) and an invented date. This is the only edit made above this section.

### 2026-09-30 r2 — design change: a daily checker over my own target companies

**What changed.** The recipe is no longer "score a list of roles I already found." It becomes a **daily checker**: I keep a list of target companies with their job-board links; one command each morning pulls every board, keeps only new postings that match my role and experience filters, and scores each one (sponsorship record, E-Verify, liveness, timeline) into Apply / Consider / Skip. Chosen because the research half of the 2-hour block is mostly *finding* postings worth tailoring for, not scoring ones already found.

**Decisions (mine):**

| Decision | Value |
|---|---|
| How it runs | one command, run by me each morning (no scheduler yet) |
| Titles that match | Data Analyst, Data Analyst I, Associate Data Analyst, Business Analyst, Business Intelligence Analyst, Analytics Engineer, Data Engineer, Data Engineer I, Associate Data Engineer |
| Seniority | exclude Senior / Staff / Lead / Principal / Manager / Director; target 0–3 years of experience |
| Experience not stated in posting | keep, flagged `experience: unknown` — never guessed |
| Location | any US city, or US-remote |
| Hiring time (timeline gate input) | one default I set + per-company override in the target list; all `your-input` |
| Job boards supported | **Greenhouse and Ashby only for now**; other sources (Lever, SmartRecruiters, Workday, iCIMS…) added one at a time later — each a `[TODO: DEV]` |
| Slug | renamed to `data-roles-opt90-h1b-daily` (Data Engineer maps to a different SOC than Data Analyst — 15-1243 / 15-1252 vs 15-2051; per-title mapping is my judgment) |

**Reuse, verified present:** `scripts/ats/providers/greenhouse.mjs` and `ashby.mjs` (public board APIs; Greenhouse host allowlist + `redirect:'error'`); `scripts/ats/scan.mjs` already dedups against a scan history — the "new since yesterday" idea exists, but it writes to `data/ats/`, so my prototype keeps its own seen-state in its output folder.

**New consequences to plan for:**

- **Liveness gets a better record.** A posting returned by the company's own board API *is* open on that board — a record, stronger than the browser check that looped on Databricks. A posting that disappears from the board between runs = closed. The browser check (`ats:liveness`) becomes a fallback, not the main gate.
- **Years of experience needs the posting text**, which the existing providers do not return (they return title, URL, company, location). Needs the description field from each board API. `[TODO: DEV]`.
- **Title filters will over- and under-match** (prediction 1 still stands, now across nine titles instead of one).

**New failure cases:**

- **F8 — board link wrong or not Greenhouse/Ashby** → company reported "not checkable", nothing invented.
- **F9 — board API down / network error** → that company reported as "not checked today", previous postings are *not* marked closed.
- **F10 — posting states 5+ years** → excluded with the stated number shown; "3–5 years" → kept, flagged for me.

### 2026-10-03 r3 — how the predictions turned out (after the build, the sample run and one live run)

The predictions above are left as written; this records the outcome of each.

| Prediction (§5) | Outcome | Evidence |
|---|---|---|
| 1. The title matcher will misfire | **Partly confirmed.** On the live Robinhood board the phrase list missed a data-analyst-type title worded differently ("Data Solutions & Analytics Senior Analyst" — senior, so dropped anyway). No over-match seen yet. Proposed fix: a "near-miss" list in the report. | `WORKED-RUN.md` → Reflection |
| 2. The timeline gate will look more precise than it is | **Confirmed.** The live run prints a factor of 0.633 to three decimals, from an 8-week hiring time that is my guess. | `runs/worked-run-2026-10-03/step2/` |
| 3. Funding will contribute nothing | **Confirmed.** 0 of 196 Form D sample companies match the CSV, so funding is not used. | recipe → Fact 3 |

| Failure case (§4) | Outcome |
|---|---|
| F1 company not in the CSV | handled as predicted (Held, never p = 0). **New finding:** legal-name mismatches are far more common than predicted. Notion, Coinbase and Robinhood all needed a `csv_name`, and "Chime" exact-matches the wrong company. So the report now prints similar-name hints. |
| F2 row without H-1B fields | handled as predicted. The first sample run silently turned this case into F1 (Coinbase's legal name differs); caught by reading the report, fixed in the fixture. |
| F3 posting dead or unreadable | split in two by the design change: a posting that leaves the board → "closed"; an unreadable board → "not checked" (F9). The browser liveness check is no longer the main gate. |
| F4 deadline / past OPT date | handled as predicted. Both clocks are now named separately. |
| F5 sponsor with no analyst title | flagged as predicted; **no dedicated test assertion** (open). |
| F6 identical records (APRICUS / ASCUS) | handled as predicted (Held). |

### 2026-10-03 r4 — slug renamed

The slug proposed in r2 (`data-roles-opt90-h1b-daily`) is now **`reallocation-engine`**. The prototype lives at `scripts/contrib/2026fa/atharvahambir-reallocation-engine/`, the recipe at `recipes/cases/2026fa/atharvahambir-reallocation-engine.md`, and the branch is `contrib/2026fa-atharvahambir-reallocation-engine`. Nothing else about the design changed.
