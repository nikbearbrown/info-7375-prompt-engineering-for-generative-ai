# AUDIT-REPORT.md — JS3 reject audit, filter v1 and v1.1

Reviewed and approved by Swathi, 2026-11-20. Drafted by Claude Code on
2026-11-18 and revised 2026-11-19. Every number here was recomputed from
committed files.

## What was compared

| Item | Source |
|---|---|
| Filter v1 verdicts | `runs/filter-2026-11-17T21-47-06-167440-0500/results.json` (commit `beb8a26`, sha256 `a836225b…3ff0`, matches `audit/selection.json`): v1 applied offline to the saved LIVE run of 2026-11-17, 1,832 postings |
| Filter v1.1 verdicts | `runs/filter-v1.1-2026-11-17T21-47-06-167440-0500/results.json` (commit `7672a21`, sha256 `a7f90a74…edeff`): v1.1 (code at `2c3ef12`) applied offline to the **same** saved run; raw-response sha256s and the trace are identical to v1's |
| Sample and strata | `audit/selection.json`, drawn by `make_audit_sample.py` (seed 20261117) |
| Human judgments | `audit/HUMAN_AUDIT.csv` (commit `fed055f`, sha256 `b243b41f…89e2`), judged against `AUDIT-RULE.md` (my JS1 labeling rule, reused unchanged) |
| Adjudication | `audit/ADJUDICATION.md` (commit `40f130e`): Row 35 only |
| Rule decisions | `FILTER.md`, "Change log: Rules changed after measuring — 2026-11-19" (commit `4a6dcfb`) and its addendum (commit `c0790a4`) |

- **Matching:** by board and `posting_id`, not row position.
- **Verdict mapping** (accepted by Swathi on 2026-11-18):
  - `shortlisted` = relevant
  - `rejected` and `not shortlisted` = not relevant
  - the filter's `I cannot tell` = an abstention

  My `can't tell` is reported separately.

## A. Original human audit results (v1, original labels)

These are counts within each group. The sample was selected by group, so the
groups cannot be pooled into a precision, recall, F1, accuracy or error rate
for the 1,832 postings.

| Group | Drawn | Filter v1 | My original judgment | Agree |
|---|---:|---|---|---:|
| Random rejects | 30 of 1,792 remaining rejects | `rejected` | 30 not relevant | 30 / 30 |
| Close call: rejected only by R4 | 4 of 132 | `rejected` | 4 not relevant | 4 / 4 |
| Close call: rejected only by R5 | 4 of 256 | `rejected` | 4 not relevant | 4 / 4 |
| Close call: not shortlisted (all) | 2 of 2 | `not shortlisted` | 1 not relevant, 1 relevant (row 35) | 1 / 2 |
| Filter abstentions ("I cannot tell") | 4 of 26 | `I cannot tell` | 3 can't tell, 1 not relevant (row 47) | see below |
| Shortlisted (all) | 4 of 4 | `shortlisted` | 4 relevant | 4 / 4 |

### The 30 random rejects

- **Observed: 0 false rejects in 30.** Not one of the 30 was relevant by my
  judgment.
- **Uncertainty:** zero in 30 does not show the filter never rejects a relevant
  posting. By the rule of three, the approximate 95% upper bound is 3/30 =
  **10%** (the exact one-sided Clopper–Pearson bound is 9.5%). That is
  consistent with up to roughly 180 of the ~1,792 remaining rejects being
  relevant.
- This is a sample estimate for the "rejected" pool only, not a measured rate.

### Close calls

- **R4 only:** all four locations are outside the US (Amsterdam, Remote –
  United Kingdom, Singapore, Baden-Württemberg).
- **R5 only:** each asks for 2 or more years, quoted by the filter.
- **Not shortlisted:** row 43 (Sales Development Representative) agrees; row
  35 is the disagreement (sections B and C).

### Filter abstentions

All three of my `can't tell` rows were v1 abstentions on R5. In each one I
recorded that no experience requirement was stated:

- row 22, 6545547002, Solutions Architect - Manufacturing
- row 28, 8085877002, Solutions Architect - Healthcare/Life Sciences Team (HLS)
- row 37, 4c51247f-8da5-4fa3-b331-7da94b76bdac, TechOps Site Support

Row 47 was an abstention I could decide (section C).

### Shortlisted

4 of 4 were relevant. With n = 4 that supports little: the exact 95% interval
for 4/4 runs from about 0.40 to 1.

## B. Row 35 adjudication

| | Verdict |
|---|---|
| Original (`HUMAN_AUDIT.csv`, unchanged) | `relevant` |
| Adjudicated (`ADJUDICATION.md`, 2026-11-19) | `not relevant` |

- **Reason:** product design and UX are not AI/ML, data, or early-career
  software engineering work under `AUDIT-RULE.md`, Check 1.
- **Timing:** this correction was made **after** seeing the filter's
  prediction, so it is not a blind judgment. The original judgment remains
  part of the historical audit.

Only the "not shortlisted" group changes between the two label sets:

| Group | v1 with original labels | v1 with adjudicated labels |
|---|---:|---:|
| Close call: not shortlisted (all) | 1 / 2 agree | 2 / 2 agree |
| Every other group | unchanged | unchanged |

## C. Disagreements and audit discoveries

My explanations are quoted exactly from `HUMAN_AUDIT.csv`.

### Row 35 — databricks 8843577002, Product Design New Grad (2027 Start)

- **My original judgment:** relevant.
  > New-graduate position, starting in 2027
  > Skills⇥Product design and human-computer interaction; familiarity with SQL, Python, and AI tools is useful.
- **Adjudicated:** not relevant (section B).
- **Filter (v1 and v1.1, the same):** `not shortlisted`, score 4, "no role
  match (R1/R2 required)".
  - R1 fail: "title names no R1 role term"
  - R2 not applied
  - R3 pass
  - R4 pass ("San Francisco, California; Seattle, Washington")
  - R5 pass ("Product Design New Grad (2027 Start)")
  - R6 pass
  - R7 pass: "You have some first hand experience with SQL and/or Python"
- **Why they differed:** R1 has no design role. My original judgment counted
  the new-grad start and the SQL/Python skills. Under the adjudicated label
  this is an agreement.

### Row 47 — stripe 8248088, Product Tax Specialist

- **My judgment:** not relevant.
  > Requires 7+ years of relevant cross-border tax experience.
- **Filter v1:** `I cannot tell`, "cannot tell: R5".
  - R1 fail
  - R2 not applied
  - R3 pass
  - R4 pass ("San Francisco, Seattle, New York City")
  - R5 cannot tell: "no experience stated and no early-career words describing the job"
  - R6 pass
  - R7 fail
- **Why they differed:** the posting says "7 or more years of cross-border tax
  experience at an accounting or law firm, in-house, or in the financial
  services or payments industry". v1's R5 did not recognize "N or more years".
- **Filter v1.1:** `rejected`, "fails R5", quoting "7 or more years of
  cross-border tax experience…" (regression test R5f).

### What the audit led to

The scan of all 1,832 descriptions (Claude Code, pattern matching, not hand
judgment) found more experience phrasings v1 missed:

- "N years or more"
- "five (5) years"
- "N years+"
- "Minimum 3 years’"
- "at least five years"
- "N years’ experience"
- degree ladders
- "N-N full year"

The "at least N years" and "minimum of N years" forms with digits were already
recognized (74 and 47 times).

## D. Rule-change decisions (FILTER.md change log, 2026-11-19)

| Decision | Proposal | Reason recorded in FILTER.md |
|---|---|---|
| **ADOPTED** | R5: recognize "N or more years", "N years or more", "at least N years" (incl. written-out numbers), "minimum (of) N years", "five (5) years", "N years+", "N years'/’ experience". Education years are not work experience. Optional statements do not reject. Explicit "or" alternatives reject only if every alternative is above 1 year. The largest mandatory minimum decides. | Row 47 and the corpus scan |
| **ADOPTED (addendum)** | An optional word counts only in the statement's own clause (commas, semicolons, full stops are boundaries). "ideal"/"ideally" are not optional words. | Found by existing test W3 (Plaid 4d2f0d16, "3+ years of relevant FP&A experience, ideally in Corporate Finance…"), which stays unchanged |
| **ADOPTED** | "university" counts as early-career evidence only in the job title | "in a university or professional setting" and "Two years of university education" passed R5 with no level information |
| **ADOPTED** | R6: explicit U.S. citizenship requirements in one sentence, and secret / top secret / TS/SCI / active / government / security clearance with requirement wording. Not counted: government customers, regulatory clearance, "citizenship status", export-control text, clearance as preferred / an advantage / a plus. | Databricks 8760167002 ("U.S. citizenship and eligibility for a U.S. government secret clearance are required") was "I cannot tell" in v1 |
| **REJECTED** | Spark false-friend adjustment | Topic words did not determine any v1 verdict |
| **REJECTED** | Word-ending adjustments ("LLMs", "data pipelines") | Did not affect any v1 verdict in the audit |
| **REJECTED FOR NOW** | US city-list expansion for R4 | City-only locations are a limitation, but none of the 48 verdicts changed solely because of it |

Tests for the adopted changes were written and their outcomes predicted
before the code (commits `bb08b32`, `bf291f2`). All 113 tests passed on the
v1.1 code (`2c3ef12`), including W3 unchanged.

## E. Version 1.1 results — on the original saved batch

**This is version 1.1 on the same saved Nov 17 batch that v1 processed, and
the rules were changed using findings from this batch and its audit. It is
not a held-out evaluation.**

### Verdict counts

| Board | v1 | v1.1 |
|---|---|---|
| databricks (901) | I cannot tell 14, rejected 884, not shortlisted 1, shortlisted 2 | I cannot tell 12, rejected 886, not shortlisted 1, shortlisted 2 |
| stripe (789) | I cannot tell 6, rejected 780, not shortlisted 1, shortlisted 2 | I cannot tell 3, rejected 783, not shortlisted 1, shortlisted 2 |
| plaid (142) | I cannot tell 6, rejected 136 | unchanged |
| deliberate-bad-name | failed, 0 postings | failed, 0 postings |
| **all (1,832)** | I cannot tell 26, rejected 1,800, not shortlisted 2, shortlisted 4 | I cannot tell 21, rejected 1,805, not shortlisted 2, shortlisted 4 |

### Verdict transitions (7 postings)

| Transition | databricks | stripe | plaid | All |
|---|---:|---:|---:|---:|
| I cannot tell → rejected | 2 | 4 | 0 | 6 |
| rejected → I cannot tell | 0 | 1 | 0 | 1 |
| Any change involving shortlisted / not shortlisted | 0 | 0 | 0 | 0 |

### Every posting whose verdict changed

| Board, ID | Title | v1 → v1.1 | Rule | Quote (v1.1 evidence) |
|---|---|---|---|---|
| databricks 8760167002 | AI Engineer – Forward Deployed Engineering (AI FDE), U.S. Public Sector (Federal Focus) | I cannot tell → rejected | R6 pass → fail | "U.S. citizenship and eligibility for a U.S. government secret clearance are required to access classified information." |
| databricks 8859666002 | Data+AI Workforce Transformation Practitioner — Customer Delivery | I cannot tell → rejected | R5 cannot tell → fail ("N or more years") | "8 or more years leading workforce or organizational transformation in a technology adoption context." |
| stripe 7819426 | Integration Engineer (Chicago) | I cannot tell → rejected | R5 cannot tell → fail ("N years+") | "4 years + experience in a Software Engineering / Integration Engineering role" |
| stripe 8230758 | User Risk Strategist | I cannot tell → rejected | R5 cannot tell → fail ("five (5) years") | "Must also have five (5) years of experience in each of the following:" |
| stripe 8248088 (audit row 47) | Product Tax Specialist | I cannot tell → rejected | R5 cannot tell → fail ("N or more years") | "7 or more years of cross-border tax experience at an accounting or law firm, in-house, or in the financia…" |
| stripe 8384287 | Software Engineer, Full Stack | I cannot tell → rejected | R5 cannot tell → fail ("five (5) years", largest minimum) | "Must also have five (5) years of experience in each of the following:" (the posting also says "Must have one (1) year of experience in the following:") |
| stripe 8337362 | Recruiting Scheduler | rejected → I cannot tell | R5 fail → cannot tell (optional heading) | v1 quoted "1+ years of experience in an admin/coordination-based role in a fast-paced environment", which sits under "Preferred qualifications"; v1.1 finds no mandatory statement and no early-career words |

**Checks:**
- **Row 47** (stripe 8248088) is now `rejected`.
- **Databricks 8760167002** is now `rejected`.
- **The four originally shortlisted postings** kept their verdicts and scores:
  databricks 6865698002 (6), databricks 6865704002 (5), stripe 8212508 (5),
  stripe 8128744 (5).

### Changed rule results vs. changed verdicts

59 postings changed at least one rule result; only 7 changed verdict. The
other 52 were already decided by another rule.

| Rule change | Postings | Of which verdict changed |
|---|---:|---:|
| R5 cannot tell → fail | 22 | 5 |
| R5 fail → cannot tell | 24 | 1 |
| R5 pass → cannot tell ("university" no longer counts in the description) | 5 | 0 |
| R5 fail → pass | 1 | 0 |
| R6 pass → fail | 7 | 1 |

Notes on the rule-only changes:
- **R5 pass → cannot tell (5 postings):** stripe 8186445 and four Master's/PhD
  Machine Learning Engineer intern postings ("Two years of university education
  or equivalent experience…"). All stay rejected by R3 or another rule.
- **R5 fail → cannot tell (24 postings):**
  - 7 have their years statement under a "Preferred qualifications" heading;
  - 9 are education years (intern postings, "At least 1 year of university
    education, or equivalent work experience.");
  - 8 have "preferred" in the same clause (5 "(preferred)" on the requirement
    itself, 3 the parenthetical case in limitation G1).

  Only stripe 8337362 changes verdict.
- **R5 fail → pass (1 posting):** stripe 8159355, University Recruiter; see
  limitation G4.
- **R6 pass → fail (7 postings):** six other public-sector and security postings
  besides 8760167002 now also fail R6, for example "This role requires an
  active Top Secret Clearance…" (databricks 8430837002). All six were already
  rejected. Two (databricks 8657488002, 8823788002) require "the elligibility to
  obtain an active Public Trust, Secret or Top Secret clearance". Counting
  required *eligibility* as exclusionary is a judgment under the adopted
  wording.

### The audit sample under v1.1 (not held-out)

In the 48 audit postings, only two rule results changed:
- **Row 47:** R5 cannot tell → fail, verdict `I cannot tell` → `rejected`. It
  now agrees with my judgment.
- **Row 13:** R5 fail → cannot tell, "8+ years of related experience
  preferred". It is still `rejected` by R3.

Every other group count in section A is unchanged under v1.1, with either
label set. Because v1.1 was built from these findings, this agreement is
**not** evidence that v1.1 is better on new postings.

## F. Methodological limitations

- **The sample was selected by group** (all shortlisted, all not-shortlisted,
  a few close calls and abstentions, 30 random rejects), not drawn as one
  random sample. Group results cannot be pooled into population-wide
  measurements.
- **AI-assisted labels:**
  - **Rows 1–4** were judged after reading the posting evidence, **before**
    seeing a ChatGPT-assisted draft.
  - **Rows 5–48** were reviewed **after** seeing a ChatGPT-assisted draft (row
    19 was revised after checking the posting). The `how_judged` column records
    this per row.

  These labels are not a blind gold standard. Where the draft and the filter
  share a mistake, this audit may not detect it.
- **Row 35's adjudication** was made after seeing the filter's prediction.
- **Version 1.1 was developed using findings from this audit and this batch.**
  Consequently, these same 48 labels cannot serve as independent held-out
  evidence for the revised filter, and the v1.1 results above describe the
  original saved batch only.
- **Fresh, independently labeled postings will be required** for the Chapter 9
  experiment and for any claim that v1.1 performs better than v1.
- **The corpus scans** (experience phrasings, false friends, limitations) are
  pattern matching by Claude Code, not hand judgments.

## G. False friends and unresolved limitations

### False friends

| Word (rule) | Example | Exact quote | Status in v1.1 |
|---|---|---|---|
| "university" (R5, description) | stripe 8186445, Integration Reliability Engineer, Technical Operations | "…working collaboratively on multi-person coding projects (in a university or professional setting)." | **Fixed by an adopted rule:** "university" now counts only in the title |
| "Spark" (R7) | Audit row 34, databricks 8588516002, Enterprise Account Executive - Gaming | "Promote Databricks' Data Intelligence Platform powered by Apache Spark™ and Delta Lake" | **Unchanged (rejected proposal).** The same wording supplies 99 R7 quotes; it affects only score and order |
| "AI" (R1) | databricks 8859666002, Data+AI Workforce Transformation Practitioner — Customer Delivery | Title "Data+AI Workforce Transformation Practitioner — Customer Delivery" | **Unchanged.** The posting is now rejected by R5 ("8 or more years leading workforce or organizational transformation…") |
| "machine learning" (R7) | Audit row 1, stripe 8112448, Fraud Strategist | "Experience working with machine learning teams" | **Unchanged.** Score and order only |

### Unresolved limitations

1. **Parenthetical preference (R5).** The word "preferred" inside a parenthesis
   describing another qualification can still make the years requirement
   optional, because the clause rule treats a parenthesis as part of the
   clause. Examples:
   - Stripe 8237526 (SDC Recruiter): "8+ years of full-cycle recruiting
     experience (in-house experience strongly preferred)"
   - Stripe 8154525 (Technical Recruiter, Fixed Term Contract): "6+ years of
     full-cycle recruiting experience (in-house experience strongly preferred)"
   - Stripe 8142856 (Technical Recruiter, Fixed Term Contract): "You have 6 - 10
     years of full-cycle recruiting experience (in-house experience strongly
     preferred)"

   These postings remain rejected by other rules, so no final verdict in the
   saved batch changes. Not addressed in FILTER.md or the code.
2. **City-only locations (R4).** US cities without a state fail or abstain on
   R4. Examples: audit rows 3 ("SEA, SF, NYC, CHI"), 17 ("SEA"), 26
   ("Chicago"), and row 2 ("Chicago, Atlanta, Remote", which gives "cannot
   tell"). In the audit these rows were also rejected by R5 or R3. In the batch,
   10 postings are rejected by R4 alone because of a US-city location, e.g.
   stripe 8189909 Data Analyst, SF ("San Francisco"). Rejected for now as a rule
   change; documented in FILTER.md.
3. **Word endings (R7, R3).** "data pipelines" (99 times) and "LLMs" (52
   times) do not match the topic words. Audit row 3 contains "optimizing data
   pipelines that feed them". This is score and order only. Rejected as a rule
   change.
4. **University Recruiter false friend (R5, title).** The title "University
   Recruiter" counts as early-career evidence even though the role isn't
   necessarily entry-level. Example: Stripe 8159355, whose 3-4 years
   requirement ("A minimum of 3-4 years full-cycle university recruiting
   experience…") sits under "Preferred qualifications". In v1.1 its R5 changed
   from fail to pass, and it stays rejected by another rule, so no final verdict
   in the saved batch changes. Not addressed in FILTER.md or the code.
5. **Phrasings still not recognized.** Degree ladders ("MS or MA plus 6 years,
   or BS or BA plus 8 years…", stripe 5601881, still `I cannot tell`) and
   "2-3 full year experience" (stripe 8322582, 8286685) were not in the adopted
   list.

## Not checked

- Whether the 30 random rejects are representative beyond the stated bound.
- The corpus-scan counts were not hand-verified posting by posting.
- How the ChatGPT-assisted draft affected rows 5–48.
- Any v1.1 verdict against a fresh human label: none have been collected.
