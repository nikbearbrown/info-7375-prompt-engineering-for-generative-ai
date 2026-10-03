# Daily job check — 2026-10-03

## Executive summary

This report is today's check of your target companies' job boards for entry-level data roles you could start before your work authorization runs out. Read it to decide where your application hours go today. This is the first run, so every matching posting counts as new. It read 1 of 1 company boards, found 162 open postings and kept 0 that match your titles, level, location and experience (0 new). **Apply: 0 · Consider: 0 · Skip: 0 · Needs you first: 0.** 1 sponsor company has nothing open for you — network into those instead. 0 postings closed since the last check. The recommendation is a starting point; you decide.

**Your clock:** the latest workable start date is **2026-12-17**, set by your unemployment allowance (OPT ends 2027-03-15; unemployment allowance runs out 2026-12-17). You want 30 days of slack before it. *(your-input — confirm the rules with your DSO)*

Labels used below: *(record)* came from data or a job board · *(your-input)* came from your files · *(model-judgment)* would be an AI's judgment — this run makes none.

## Apply today — tailor these (0)

Scored Apply by the existing scorer: a sponsor on record, a live posting, and a start date that fits.

_None today._

## Consider (0)

Above the floor but with a soft spot (a weaker sponsorship tier or a tight timeline).

_None today._

## Needs you before a decision (0)

The recipe stops here instead of guessing. Each row says what is missing.

_None today._

## Skipped (0)

A closed gate (timeline, E-Verify, dead posting) or too weak a score. Skipping is a good outcome.

_None today._

## Network, don't apply (1)

Sponsors on record with no matching posting today — worth an informational chat before a role opens.

| Company | Sponsorship | Next action |
|---|---|---|
| Robinhood | Proven *(record)* | Network into this company (3 networking hours): ask for an informational chat before a role opens. |

## Closed since the last check (0)

_None._

## Companies not checked today (0)

_All boards were read._

## Your target list today

| Company | Board | Sponsorship record | E-Verify | Hiring time | Listed | Matching | Filtered out (title / word / location / experience) |
|---|---|---|---|---|---|---|---|
| Robinhood | greenhouse | Proven — 824 approvals, 97.2% (ROBINHOOD MARKETS INC) *(record)* · ⚠ none of the ≤5 listed sponsored titles is one of your title phrases | enrolled *(your-input)* | 8 wk (default) *(your-input)* | 162 | 0 | 161 / 1 / 0 / 0 |

### Postings with a target title that were filtered out — check the filters are right

| Company | Role | Why it was dropped |
|---|---|---|
| Robinhood | Business Analyst Intern (Summer 2027) | title word: intern |

## What this report cannot tell you

- Whether a listed posting is actually being filled: being on the board proves it is open on the board, not that anyone is hiring.
- Whether a sponsor on record will sponsor this role now: the H-1B counts are past filings, their years are not documented, and only up to 5 titles per company are listed.
- Anything about a company with no H-1B record in the data: 'unknown' is not 'does not sponsor'.
- E-Verify enrollment: the repo has no E-Verify data; the value is whatever you recorded in the targets file.
- How long a company really takes to hire: every hiring time is your estimate.
- Immigration rules: unemployment limit, STEM extension and E-Verify requirements are your inputs to confirm with your DSO.
- Experience, title and location filters read text with fixed rules; a posting worded unusually can be kept or dropped wrongly — excluded examples are listed so you can check.
- Funding: the SEC Form D samples that ship with the repo match none of these companies, so funding is not used.

## Run record

- Recipe `atharvahambir-data-roles-opt90-h1b-daily` v0.1.0 · prototype `scripts/contrib/2026fa/atharvahambir-data-roles-opt90-h1b-daily/daily_check.py` · mode: live (board APIs)
- Sponsorship data `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` — 30369 rows, 1557 with H-1B fields, sha256 `eccdee2addf472b1…`
- Board fetcher reused from `.claude/skills/greenhouse-watch/scripts/greenhouse_watch.py`; decisions by the existing scorer `scripts/score/role-scorer.mjs`
- Scorer not called: no posting had a sponsorship value to score
- Sponsorship tier rule (proposal): Proven = ≥10 approvals and ≥90% approval rate; Likely = ≥1 approval; p Proven 0.9, Likely 0.6
- Timeline curve (proposal): expected start = today + hiring weeks; slack = cliff − expected start; factor 0 if slack < 0, 1 if slack ≥ buffer days, else slack ÷ buffer days
- Filters *(your-input)*: titles business intelligence analyst, analytics engineer, business analyst, data engineer, data analyst; excluded words senior, sr, staff, lead, principal, manager, director, head, vp, intern, internship, co op, iii, iv; max 3 years
- Skip rate: the scorer's own skip-rate line covers only the scored roles; 162 of 162 listed postings were dropped earlier by the filters.
