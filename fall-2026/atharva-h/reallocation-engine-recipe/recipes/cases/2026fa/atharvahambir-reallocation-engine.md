---
status: RUNNABLE-SAMPLE
todos_open: 7
last_gate: "sample-run 2026-10-03 — course/2026fa/submissions/atharvahambir/runs/evidence-2026-10-03/ (sample run, 18 tests, 4 break mutants caught); one live worked run 2026-10-03 (logs/runs/2026fa-atharvahambir-2.md), not attested"
attestation: null
recipe_version: 0.1.0
---

# reallocation-engine — a daily board check for entry-level data roles, OPT ending in ~90 days, H-1B needed

## Executive summary

**What it does.** Each morning, one command reads the job boards of the companies the student chose and keeps only the postings that fit: data analyst, business intelligence, business analyst, analytics engineer and data engineer titles, nothing senior, in the US or US-remote, asking for no more than three years of experience. Then it checks four things for each posting:
- whether the posting is still open on the company's own board;
- whether a hire could start before the student's work authorization runs out;
- whether the company has a public record of sponsoring work visas;
- whether the employer meets the student's E-Verify requirement.

It reports what is new since yesterday and what has closed.

**Who it is for.** An international master's student looking for entry-level data jobs, on post-completion OPT with about 90 days left, holding a STEM-designated degree and needing an employer that sponsors H-1B. That employer must also be enrolled in E-Verify for the STEM extension.

**What it decides.** For each posting it returns **Apply**, **Consider**, **Skip**, or **Needs you first**, with every number labeled by where it came from: a record, the student's own input, or an AI judgment (this recipe uses none). It never guesses. A company with no visa record, a company whose name is ambiguous in the data, or an employer whose E-Verify status nobody has checked is held for the person, never scored as a non-sponsor. The person makes the final call; the recipe never applies anywhere.

Two customers: this file is for the agent; `recipes/cases/2026fa/atharvahambir-reallocation-engine.card.md` is for the person.

## Lifecycle claim

RUNNABLE-SAMPLE is supported by the recorded sample run, 18 passing offline tests, four deliberate break mutations, and conformance evidence. The recipe does not claim RUNNABLE-LIVE because no live run has been attested. The open proposed additions are roadmap items and are not required for the demonstrated sample path.

| Evidence | Path |
|---|---|
| Sample run (exact command + output) | `course/2026fa/submissions/atharvahambir/runs/evidence-2026-10-03/03-prototype-sample-run.txt` |
| Its two outputs + the scorer's | `course/2026fa/submissions/atharvahambir/runs/evidence-2026-10-03/sample/2026-10-01/` |
| 18 offline tests | `course/2026fa/submissions/atharvahambir/runs/evidence-2026-10-03/02-prototype-tests.txt` |
| 4 break mutants, all caught | `course/2026fa/submissions/atharvahambir/runs/evidence-2026-10-03/09-break-attempts.txt` |
| Conformance / verify / doctor | `course/2026fa/submissions/atharvahambir/runs/evidence-2026-10-03/04-conformance-prototype.txt`, `05-verify.txt`, `06-doctor.txt` |
| Run-log entries | `logs/runs/2026fa-atharvahambir-1.md` (sample), `logs/runs/2026fa-atharvahambir-2.md` (live worked run on one real board — gates G4/G5 answered by a named human, reports reviewed and the worked-run attestation signed by him on 2026-10-03; one company, so no RUNNABLE-LIVE claim) |

## Handoff condition (done when)

A run is done when all of these hold. "Looks right" is not the condition.

1. The command exits `0`, and `<out-dir>/<YYYY-MM-DD>/` holds both `daily-check.json` (agent) and `daily-check.md` (person).
2. If anything was scorable, `role-scores.json` exists beside them with `"_scorer": "bayesian-role-scorer"`, so the existing scorer made the decisions.
3. Every `{value, source}` pair in `daily-check.json` has `source` ∈ {`record`, `model-judgment`, `your-input`}.
4. No posting with Held sponsorship evidence appears in `roles.json`, so no sponsorship value was invented to score it.
5. The person has read `daily-check.md`, and their decision is recorded in a `logs/runs/` entry (gate G7).

Conditions 1–4 are asserted by `test_sample_run_end_to_end`. Condition 5 is human.

## Required reads

1. `SNICKERDOODLE.md` — gates, provenance, labels.
2. `DOMAIN.md` — layout, known gaps.
3. `DATA_CONTRACT.md` §Zero-Conditions — why the committed sample runs as a fictional persona.
4. Book chapters: `book/chapters/07-who-sponsors-the-80-days-sponsorship-scorer.md` (sponsorship; Unknown ≠ Avoid), `book/chapters/08-is-the-job-real-ats-detection-and-liveness.md` (liveness), `book/chapters/10-the-visa-timeline-manager.md` (timeline factor), `book/chapters/11-the-bayesian-role-scorer.md` (votes × gates).
5. This recipe and its card.

## Purpose

Take over the *finding and first-pass research* part of the two research-and-apply hours of a 3-3-2 day. Of a company list the student already cares about, which postings opened today that are worth tailoring an application for, which companies are worth networking into because nothing fits yet, and which postings to drop now? The recipe answers from records and the student's own constraints. It does not answer from a model's opinion.

## Source inventory

| Source | Path / command | What it supplies | Label it produces | Checked |
|---|---|---|---|---|
| Sponsorship history | `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv` | H-1B approvals, denials, approval rate, ≤5 sponsored titles, median salary | `record` | 30,369 rows; 1,557 carry H-1B fields; sha256 written into every run log |
| Occupation wages | `data/bls/compact/soc_occupation_compact.csv` | national BLS median per SOC | `record`, display only | rows exist for every mapped SOC |
| Form D samples | `data/sec/form-d/processed/sample/*.sample.json` | funding | not used | 0 of 196 sample companies match the CSV by normalized name |
| Board fetcher (reused, unmodified) | `.claude/skills/greenhouse-watch/scripts/greenhouse_watch.py` → `board_url()`, `fetch_board()`, `normalize_jobs()` | job lists with text, host allow-list, redirects refused | `record` | Greenhouse + Ashby |
| Decision core (reused, not copied) | `scripts/score/role-scorer.mjs`, run as `node scripts/score/role-scorer.mjs <roles.json> --profile <p.json> --out-dir <dir>` | Apply / Consider / Skip + per-term arithmetic | scorer output on labeled inputs | `_scorer` id checked every run |
| The prototype | `scripts/contrib/2026fa/atharvahambir-reallocation-engine/daily_check.py` | this recipe, end to end | — | stdlib Python 3.10+, Node 20+ |
| Tests / break attempts | `scripts/contrib/2026fa/atharvahambir-reallocation-engine/test_daily_check.py`, `scripts/contrib/2026fa/atharvahambir-reallocation-engine/break_attempts.py`, `scripts/contrib/2026fa/atharvahambir-reallocation-engine/fixtures/BROKEN-mutants.json` | offline proof | — | 18 tests; 4 mutants |
| Sample fixtures | `scripts/contrib/2026fa/atharvahambir-reallocation-engine/fixtures/targets.sample.json`, `scripts/contrib/2026fa/atharvahambir-reallocation-engine/fixtures/boards/`, `scripts/contrib/2026fa/atharvahambir-reallocation-engine/fixtures/candidate.expired.fictional.json` | synthetic postings in the real API shapes | — | marked SYNTHETIC in each file |
| Fictional persona | `search/examples/atharva/` (`daily-check.candidate.json`, `profile.yml`, `resume.example.json`, `gaps.md`) | the sample's candidate | `your-input` | invented details, `@example.com`, 555 phone |

Network hosts, **live mode only**, only through the reused fetcher: `boards-api.greenhouse.io`, `api.ashbyhq.com`. No other host is contacted, and offline runs make no network call at all (`DAILY_CHECK_OFFLINE=1` turns any attempt into an error).

## Inputs

All inputs are `your-input`, and none has a default: a missing value stops the run at G0.

**`candidate.json`** (sample: `search/examples/atharva/daily-check.candidate.json`):

| Field | Meaning |
|---|---|
| `authorization` | text the scorer reads to decide sponsorship matters |
| `visa.opt_end_date` | clock 1 — last day of OPT |
| `visa.unemployment_days_used`, `visa.unemployment_days_as_of`, `visa.unemployment_limit_days` | clock 2 — the unemployment allowance (days used as of a date; the run adds the days since, assuming still unemployed) |
| `visa.needs_e_verify_employer` | the student's constraint for the intended STEM-OPT pathway |
| `visa.buffer_days` | slack wanted before the deadline |
| `search.titles[]` | `phrase`, `fit` (0–1), `soc` (display only) |
| `search.exclude_title_words`, `search.flag_title_words`, `search.max_years_experience` | filters |

**`targets.json`** (sample: `scripts/contrib/2026fa/atharvahambir-reallocation-engine/fixtures/targets.sample.json`): `defaults.hiring_weeks`, then per company `name`, `board` (Greenhouse or Ashby link), `e_verify` (`enrolled` true / false / null + source + date), optional `hiring_weeks`, `csv_name` (legal name in the CSV), `sponsorship_override` (tier + source).

Real inputs live in the gitignored `private/`. The committed sample uses the fictional persona.

## Phase gates

`$DAY` = `<out-dir>/<YYYY-MM-DD>`. Every check reads `$DAY/daily-check.json`, which every run writes, including stopped ones.

| Gate | Testable condition | Pass | Fail → stop / hold | What the person sees |
|---|---|---|---|---|
| **G0 intake** | every candidate field present and typed; `opt_end_date` after today; unemployment days left > 0; targets list non-empty; CSV, fetcher and scorer exist; `node` on PATH. Check: `python3 -c "import json,sys; sys.exit(json.load(open(sys.argv[1]))['stop'] is not None)" $DAY/daily-check.json` | run continues | **exit 2**, nothing fetched or scored; the report names the missing or impossible input | "stopped early: <reason>" |
| **G1 board readable** | the board link resolves to Greenhouse or Ashby, and the response has a `jobs` list | company checked | not Greenhouse/Ashby → *not checkable*; fetch error → *not checked today*; its earlier postings are **not** marked closed. No board readable at all → **exit 4** | "Companies not checked today" + "check the careers page by hand" |
| **G2 liveness — a gate** | the posting is in today's board-API response (Ashby: `isListed` not false) | liveness factor 1.0 `record`, evidence string names the response | absent today → *closed since the last check*; `isListed:false` → factor 0 → scorer Skip (gated) | "Closed since the last check" |
| **G3 visa timeline — a gate** | two clocks named separately: **clock 1, OPT end date**; **clock 2, unemployment allowance** = limit − days used (counted forward from the as-of date). Deadline = the earlier. Expected start = today + hiring weeks. Factor per Decision 2, shown with its dates | factor > 0.05 | factor ≤ 0.05 → the scorer's timeline gate closes → **Skip (gated)** | "Your clock" line naming both dates; each row shows factor → start date |
| **G4 E-Verify — your search constraint** | applies only when `needs_e_verify_employer` is true (the student's own choice for the intended STEM-OPT pathway). The program applies the constraint; it never decides immigration eligibility | `enrolled: true` | `false` → **Skip** (decided by this recipe gate, after the scorer); `null` → **Needs you**, with the scorer's view shown as a preview | "look it up and record it" |
| **G5 sponsorship evidence sufficiency** | exact employer evidence with usable H-1B fields (exact normalized-name match or your `csv_name`; one row; H-1B fields present; not an identical twin of another company's record) | the sponsorship **vote** may be calculated | missing, ambiguous, duplicate or unusable evidence → **Held / Needs you**. Never infer non-sponsorship; never substitute p = 0. Sponsorship stays a vote: only liveness and timeline are scoring gates | the exact reason, plus similar-name hints |
| **G6 scorer ran** | `node scripts/score/role-scorer.mjs …` exits 0 and `role-scores.json` has `"_scorer": "bayesian-role-scorer"` | decisions read back by `role_id` | **exit 3**, the report says the scorer failed | — |
| **G7 human decision** | the person has read `$DAY/daily-check.md`, and the decision is in `logs/runs/2026fa-atharvahambir-<n>.md` | applications tailored / networking planned | not read → nothing is acted on | the whole report |

## Workflow

Verbatim, from the repo root.

1. Offline sample (fictional persona, synthetic postings, real CSV; no network):

```bash
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/daily_check.py --sample
```

2. Offline tests, then the break attempts (each deliberately broken copy must make the tests fail):

```bash
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/test_daily_check.py
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/break_attempts.py
```

3. Live daily run on the student's real files, kept in the gitignored `private/` folder:

```bash
python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/daily_check.py --candidate private/daily-check/candidate.json --targets private/daily-check/targets.json --out-dir private/daily-check/runs
```

4. Read `daily-check.md` (G7). Decide. Record the decision and the run in `logs/runs/` using the template below. Never edit `logs/RUN_LOG.md`.

Useful flags: `--boards-dir <dir>` (saved responses, offline), `--today YYYY-MM-DD` (reproducible), `--fresh-state` (everything counts as new), `--dry-run` (don't update the state file).

## Decisions closed

Each was proposed by the AI agent while building the prototype, then reviewed and approved by Atharva Hambir on 2026-10-03. They are user-defined heuristics, not facts from DOL or the book.

1. **Sponsorship tiers.** Proven = ≥ 10 H-1B approvals and ≥ 90% approval rate. Likely = ≥ 1 approval otherwise. p = 0.9 / 0.6, copied from `data/examples/ch11-roles.json`. *Why:* Ch.7 says the tier cut-offs are unpinned; a high bar for Proven keeps the scorer's "soft tier → Consider" demotion meaningful. The scorer's own weights are not changed.
2. **Timeline curve.** Factor = 0 if the expected start is after the deadline; 1 if slack ≥ buffer days; otherwise slack ÷ buffer, a straight line. *Why:* Ch.10 gives three worked cases and no formula; a straight line is the simplest curve that hits zero at the deadline and is easy to check by hand.
3. **Title word rules.** Exclude senior / sr / staff / lead / principal / manager / director / head / vp / intern / internship / co-op / III / IV. Flag "II" for a look instead of dropping it. *Why:* the target is 0–3 years. "II" often means 2–4 years, so dropping it would lose real matches.
4. **Title → SOC mapping, display only.** Data Analyst and Analytics Engineer → 15-2051.00; BI Analyst → 15-2051.01; Business Analyst → 13-1111.00; Data Engineer → 15-1243.00. *Why:* there is no dedicated "Data Analyst" SOC; the code only labels a BLS wage shown beside the decision and never feeds the scorer.

## What it can and can't verify

| Value | Label | Comes from |
|---|---|---|
| CSV row matched, H-1B approvals / denials / rate, ≤5 sponsored titles, median salary | `record` | the CSV row (sha256 in the log) |
| Sponsorship tier and p | `record` | that row, through Decision 1 |
| Sponsorship override tier and p | `your-input` | targets file, with its stated source |
| Posting is listed today (liveness 1.0), title, link, location text, published date, age | `record` | the company's board API response (offline: a saved response) |
| Location class (us / us-remote / unverified / non-us) | `record` | fixed text rule over the location and office text; the text is kept as evidence |
| Experience class (within / mixed / not stated / above) + the matched sentences | `record` | fixed text rule over the posting text; the matched text is kept |
| Title family | `your-input` | your phrase list matched against the record title |
| Fit | `your-input` | your value per title family |
| OPT end date, unemployment days and limit, buffer, E-Verify need | `your-input` | candidate file (DSO questions) |
| E-Verify enrollment per company | `your-input` | targets file (looked up by hand) |
| Hiring weeks, expected start, deadline, timeline factor | `your-input` | computed from your dates and estimates, shown with them |
| BLS national median wage | `record`, display only | BLS compact CSV through your SOC mapping |
| "Latest funding" stage / date | `record`, display only | a CSV column with undocumented provenance |
| Apply / Consider / Skip | scorer output | `scripts/score/role-scorer.mjs` on the labeled inputs, then the G4 / G5 overlay |

No language model is called at run time, so no value carries the `model-judgment` label. Three values are fixed text rules applied to record text: title-family match, location class and experience class. They are labeled `record` with the matched text kept as evidence, and they can misread unusual wording (see below). The rules' parameters are `your-input`.

**It can verify:**
- a posting is listed on the company's own board today, and which postings left the board since the last run;
- what the CSV says about a company, matched exactly with no fuzzy guess;
- that the timeline factor follows from the stated dates;
- that the existing scorer made the decision;
- that nothing held was scored.

**It cannot verify:**
- **Whether a listed posting is actually being filled.** On the board means open on the board.
- **Whether a sponsor on record will sponsor *this* role now.** The H-1B counts are past filings, their fiscal years are not documented, and at most 5 titles per company are listed.
- **Anything about a company with no H-1B record.** Unknown is not "does not sponsor". Only 1,557 of 30,369 CSV rows carry H-1B fields at all.
- **That an exact name match is the right employer.** "Chime" matches CHIME INC (2 approvals), not CHIME FINANCIAL INC (580). The report flags similar names, but the person decides.
- **E-Verify enrollment, real hiring time, and every immigration rule.** These are inputs to confirm with a DSO.
- **Unusual wording.** The fixed text rules can keep or drop a posting wrongly. Every target-title posting that was dropped is listed with the reason, so the person can check.
- **Funding.** Not used; see Fact 3.

## Output contract

One file per reader, written to `$DAY = <out-dir>/<YYYY-MM-DD>/`:

| File | Reader | Contents |
|---|---|---|
| `daily-check.json` | agent | `_recipe`, `recipe_version`, `_prototype`, `generated_at`, `today`, `mode`, `stop`, `inputs` (paths, CSV sha256 and row counts), `config` (rules + your filters), `runway` (both clocks, deadline, buffer), `gates`, `scorer` (command, exit, stdout, output paths), `companies[]` (status, sponsorship evidence, E-Verify, hiring weeks, timeline, filter counts, excluded examples), `postings[]` (every value as `{value, source, …evidence}`, flags, `decision`), `closed_since_last_run[]`, `network_targets[]`, `not_checked[]`, `summary`, `cannot_verify[]` |
| `daily-check.md` | person | executive summary · your clock · Apply today · Consider · Needs you before a decision · Skipped · Network, don't apply · Closed since the last check · Companies not checked today · Your target list today · filtered-out postings to check · What this report cannot tell you · Run record |
| `roles.json`, `scorer-profile.json` | scorer | the scorer's input, shaped like `data/examples/ch11-roles.json`, every term carrying `source` |
| `role-scores.json`, `role-scores.md` | audit | the scorer's own output: decision + per-term arithmetic |
| `raw/<ats>-<board>.json` | audit (live only) | the untouched board responses |
| `<out-dir>/state.json` | the next run | postings seen, first seen, last seen, closed on |

## Next action per result (the 3-3-2 day)

| Result | Next action | Hours it feeds |
|---|---|---|
| **Apply** | tailor an application today | 2 research-and-apply |
| **Consider** | tailor only after the Apply roles; ask a contact about it first | 2 → 3 networking |
| **Needs you** | do the one lookup named in the reason (E-Verify search, the company's legal name for `csv_name`, a sponsorship signal from a recruiter), record it in targets, rerun | 2 |
| **Skip** | nothing; the time goes elsewhere | — |
| **Network, don't apply** | a sponsor on record with nothing open: ask for an informational chat before a role opens | 3 networking |
| **Not checked** | check that careers page by hand today | 2 |
| **Closed since last check** | drop it from the tracker | — |

## Stop conditions

- **exit 2:** G0 failed (missing or impossible input, missing data / fetcher / scorer, a corrupt state file). Nothing is fetched or scored.
- **exit 3:** the scorer failed. Decisions are not made without it.
- **exit 4:** no board could be read.
- **Never:**
  - fill a missing input with a default;
  - fuzzy-match a company name;
  - treat "no record" as "does not sponsor" or give it p = 0;
  - decide STEM, E-Verify or unemployment law;
  - copy or modify the scorer;
  - edit fixtures or weaken a rule so a role passes;
  - read `private/` from committed code (real files are passed in by flag);
  - contact a host other than the two named.

## Facts about the engine this recipe accounts for

1. **Role quality has zero weight in the scorer.** The recipe uses role quality outside the scorer, for information only: the BLS national median for the mapped SOC is shown beside each posting, labeled display-only. It proposes no weight, because the wage is national, the SOC mapping is a judgment (Decision 4), and nothing in this persona's decision depends on pay.
2. **`bls:local-wage` feeds nothing.** Not used. Metro-adjusted wages are not shown.
3. **Only SEC samples ship.** This run used the four `*.sample.json` quarters; 0 of their 196 companies match the CSV, so funding is not used. The CSV's own "latest funding" column is shown but has no documented provenance and carries no weight.
4. **Some recipe directories don't exist.** No gate or output touches `data/raw/`, `data/verified/` or `logs/gate-decisions/`. Outputs go to the `--out-dir` you pass; human decisions go to `logs/runs/`.
5. **The `snickerdoodle` CLI is not runtime.** It is never named as a command here; every command above runs today.
6. **Top-level recipes are DRAFT.** This case recipe claims RUNNABLE-SAMPLE on the evidence above, and nothing more.
7. **`bls:local-wage` fails on a fresh clone.** Not called. Related finding: `npm run verify` *itself* fails on a fresh clone when the default `python3` lacks PyYAML (manifest check). Fixed locally with a gitignored `.venv` (`python3.12 -m venv .venv && .venv/bin/pip install pyyaml`). This prototype needs neither.
8. **`validate-h1b-join-sample.py` needs full data.** Not run. The shipped CSV is read directly. The join gaps are handled in the open: exact names only, `csv_name` for legal names, similar-name hints, duplicate records held.

## Proposed additions

Each is a roadmap item outside the demonstrated sample path.

1. [TODO: DEV] **SmartRecruiters, then Lever, as board sources, one at a time.** The reused fetcher already has a SmartRecruiters path, so this is the smallest next step. Done when `resolve_board()` recognizes the link, a saved fixture exists, and a test asserts the jobs are read.
2. [TODO: DEV] **Workday / iCIMS sources.** Large sponsors often use them; today they are reported "not checkable". There is no public JSON board API comparable to Greenhouse/Ashby, so this needs its own provider and its own tests.
3. [TODO: DATA SOURCE] **E-Verify enrollment data.** Today the student looks each employer up by hand in E-Verify's public employer search and records it as `your-input`. A dated extract with provenance would turn G4 into a record.
4. [TODO: DATA SOURCE] **Per-company time-to-hire data.** Today every hiring time is the student's estimate (8-week default). Without a source, the timeline gate is only as good as that guess.
5. [TODO: DATA SOURCE] **DOL LCA disclosure records with SOC codes and fiscal years.** That would make "has this employer sponsored *this occupation* recently?" a record, instead of a reading of ≤5 title strings with undocumented years.
6. [TODO: DEV] **Funding recency inside the sponsorship evidence, as Ch.7's composite does.** Needs the full Form D quarters (gitignored) and the `scripts/sec/entity-resolution.py` join. The scorer has no separate funding term, so it belongs with the sponsorship evidence.
7. [TODO: DEV] **Optional scheduled daily run.** The student chose to run it by hand; a scheduler would only call the same command.

## Failure cases exercised

| # | Failure | Ends as | Proved by |
|---|---|---|---|
| F1 | company not in the CSV | Held (G5), hint listed | `test_f1_no_row_is_unknown_with_a_hint_never_zero`; sample: Northwind Analytics |
| F2 | row exists, no H-1B fields | Held (G5) | `test_f2_row_without_h1b_fields_is_unknown`; sample: Coinbase (`COINBASE GLOBAL INC`) |
| F3 | posting taken down | listed under "closed" | `test_second_run_reports_new_and_closed_and_leaves_unread_boards_alone` |
| F4 | OPT date already past / missing value / start after the deadline | exit 2 / exit 2 / Skip (gated) | `test_f4_past_opt_date_stops_at_the_intake_gate`, `test_missing_value_stops_instead_of_defaulting`, `test_sample_run_end_to_end` (Roblox, 12 weeks) |
| F5 | sponsor on record, no matching title in its ≤5 | flagged, not demoted | visible in the sample (Stripe, Benchling, Notion, Roblox, Databricks); **no dedicated assertion yet** |
| F6 | identical H-1B record shared with another company | Held (G5) | `test_f6_identical_records_are_not_trusted`; sample: Apricus Biosciences |
| F7 | not E-Verify enrolled / not recorded | Skip / Needs you (G4) | `test_sample_run_end_to_end` (Moloco / Pinterest) |
| F8 | board not Greenhouse or Ashby | not checkable (G1) | `test_resolve_board`; sample: Adobe (Workday) |
| F9 | board unreadable today | not checked; earlier postings not closed | `test_second_run_reports_new_and_closed_and_leaves_unread_boards_alone`; sample: Dropbox |
| F10 | asks 5+ years / 3–5 years / doesn't say | dropped with the sentence shown / kept flagged / kept flagged | `test_parse_experience`, `test_sample_run_end_to_end` |
| — | similar-name trap (CHIME INC vs CHIME FINANCIAL INC) | flagged | `test_similar_name_trap_is_flagged` |
| — | any network call in an offline run | error | `test_offline_guard_blocks_any_network_call` |

Break mutants (`scripts/contrib/2026fa/atharvahambir-reallocation-engine/fixtures/BROKEN-mutants.json`), each required to make the suite fail: past OPT date passes G0; "no record" scored as p = 0; E-Verify gate ignored; a start after the deadline gets 0.5. All four are caught (`break_attempts.py`).

## Logging

Record each run that matters (a sample run, a live run you acted on, a break test) as `logs/runs/2026fa-atharvahambir-<n>.md`. **Never edit `logs/RUN_LOG.md`.** Never log real dates, contacts or private application notes: a live run's details stay in `private/`, and its log entry describes it without personal data.

### Run-log template

```markdown
# Run <n> — data-roles daily check — YYYY-MM-DD

## Executive summary
<two or three plain sentences: what was run, on what, what it found, what was decided>

## Record
- **Recipe:** atharvahambir-reallocation-engine v<version>
- **Mode:** offline sample | live (board APIs)
- **Command:** `<exact command>`
- **Inputs:** candidate <persona path or "private">, targets <path or "private">, sponsorship CSV sha256 <first 16>…
- **Outputs:** <out-dir>/<date>/daily-check.{json,md} · role-scores.{json,md} · state.json
- **Result:** boards read <n>/<n> · listed <n> · matching <n> (new <n>) · Apply <n> · Consider <n> · Skip <n> · Needs you <n> · closed <n> · network <n> · not checked <n>
- **Gates:** G0 <pass/stop+reason> · G1 <not checkable / not checked list> · G2–G6 <notes>
- **Human decision (G7):** <who · when · what was decided> — or "pending"
- **Open issues:** <what did not work or is still missing>
```
