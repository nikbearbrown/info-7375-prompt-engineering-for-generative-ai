# APPENDIX — DataSentry: methods and evaluation in detail

Ethan Gomes · INFO 7375 · project film · 2026-11-23

This appendix holds the detail the film keeps out of its executive summary. Past tense is used only for what ran
(recorded in `first-run/results/2026-10-25/` and `first-run/loop-runs/2026-11-23_182418/`); everything else is the plan.

---

## 1. What DataSentry is

An AI agent that writes data-quality checks for a table, tests them against known bad rows planted in copies of the
table, revises them, and stops for a person to approve the final set. The scorer is the independent check: it is not
part of the agent, it holds the answer keys, and it decides whether a set of checks passes. A clean copy of the same
table is the control: a check that rejects known-good rows is penalised, not rewarded.

## 2. Data

| Item | Detail |
|---|---|
| Source | NYC Taxi & Limousine Commission, yellow taxi trip records, January 2025 (public, Parquet): `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet` (59,158,238 bytes, sha256 `9af277e4c0d3f9de…`) |
| Columns kept | `tpep_pickup_datetime`, `tpep_dropoff_datetime`, `passenger_count`, `trip_distance`, `fare_amount` |
| Clean sample | rows that already break the two first-piece rules are dropped, then 10,000 rows are sampled with seed 7375 (`first-run/get_data.py`) |
| The real month | 3,475,226 rows, of which 144,118 have a negative fare and 124 a drop-off before pick-up (`results/2026-10-25/data.json`) |
| Privacy | public, de-identified trip records; no personal data is used |

## 3. Method, step by step

### Step 1 — plant the defects (built)
`first-run/plant_five.py <seed>` writes one broken copy per defect type and an answer key that no check reads:

| Defect type | What is planted |
|---|---|
| `negative_fare` | 25 fares made negative |
| `dropoff_before_pickup` | 25 drop-offs moved 5–59 minutes before their pick-up |
| `missing_value` | 25 trip distances blanked (NaN) |
| `duplicate_rows` | 25 existing trips appended again |
| `wrong_type` | the whole `fare_amount` column stored as text, like a bad import |

Seed 25 is the main planting; seed 99 is a held-out planting used only to confirm a result.

### Step 2 — Claude writes the checks; the scorer grades them (built, run twice by hand)
- **The contract** (`first-run/claude-checks/PROMPT-round1.md`): Claude sees only the five column names and types,
  never the data, the defects or the answer key. It must return one Python file with a pandera 0.29
  `DataFrameSchema` named `schema`, one rule per property, a one-line comment per rule, and no hard-coded values.
- **The scorer** (`first-run/score_checks.py`) runs the checks lazily on the clean copy and on every broken copy:
  - clean copy: PASS, or FAIL with the number of good rows flagged (false alarms), any column-level failure, and any
    check that crashed (reported as CHECK ERROR, never counted as a catch);
  - each defect type: CAUGHT (every planted row flagged), PARTLY CAUGHT, or MISSED; `wrong_type` counts as caught
    only through a real (non-crashing) column-level failure on `fare_amount`.
- **The feedback rule** (`first-run/explain_clean.py`): between rounds Claude is told only which of its rules flagged
  good trips on the clean copy, and how many. It is never told anything about the planted defects
  (`PROMPT-round2.md`).
- Both rounds so far ran in the Claude desktop app (model Opus 5.5, effort High) on 2026-10-25; the replies are saved
  verbatim and dated in `first-run/claude-checks/`.

### Step 3 — the loop that runs on its own (built and run, 2026-11-23)
`first-run/run_loop.sh` → `first-run/loop.py`. Tests first: `first-run/tests/test_loop.py` (13 tests) was written before
`loop.py` and runs before every loop; the loop does not start if a test fails. Each round:

1. **act** — ask Claude Code in headless mode (`claude -p --output-format json --tools "" --strict-mcp-config`, model
   `claude-opus-5-5`, effort high, in an empty working folder) for one checks file. Round 1 sends the contract
   (`PROMPT-round1.md`); rounds 2–3 continue the same conversation (`--resume <session>`) with only the clean copy's
   results.
2. **check** — the reply must hold exactly one Python block, and `check_policy()` must allow the code before the scorer
   imports it: only pandas / pandera / numpy / re / math / datetime / typing imports; no `open`, `eval`, `exec`,
   `__import__`, dunder attributes, `read_*` / `to_*` file I/O (except `to_datetime`, `to_numeric`, `to_timedelta`),
   `system`, `remove`, …; a top-level `schema` is required.
3. **act** — run the scorer on the clean copy and on both plantings (seed 25, seed 99).
4. **record** — prompt, raw reply (with model usage), code, scores and decision under `loop-runs/<timestamp>/round<N>/`;
   `state.json` holds the mode, model, CLI version, session id and every round's result.
5. **decide** — stop on the pass line (section 5); a reply with no single code block; code refused by the policy; a
   clean copy that already passes (clean-copy feedback then has nothing left to report); or the budget of 3 rounds.
   Never on "the model said it was done".

What Claude saw: the contract, then the clean-copy results (rules that rejected good trips, with counts; rules that
crashed). It never saw the data, the plantings, the answer keys or any score. The feedback builder is tested to
reproduce the hand-written round-2 prompt exactly, and never to mention defects.

`./run_loop.sh --fixture claude-checks` replays the two saved hand-run replies instead of calling Claude; it reproduces
the recorded 2026-10-25 scores exactly (no login needed).

### Step 4 — tools the agent chooses (planned, for the final project)
Today Claude has no tools at all; the loop's code does every action. Next, each turn Claude picks one action from a
small menu, and the code checks the choice against the policy before doing anything:

| Tool | What it does | Policy in code |
|---|---|---|
| `profile_column(name)` | summary statistics (min, max, percentiles, nulls) of the development clean copy | development data only; one of the five column names |
| `write_checks(code)` | propose a checks file | must pass `check_policy()` |
| `run_dev_scorer()` | score on the development planting | development data only; counts against the budget |
| `read_dev_report()` | what the last development run caught, missed and falsely flagged | development results only |
| `submit_for_review()` | propose the checks are ready | does **not** stop the loop: the held-out check decides, then the human gate |

Every call is logged; a per-tool and a total call budget (and a time limit) end the run when used up.

### Step 5 — the human gate (planned, for the final project)
A command shows the person the scorecard (development and held-out), the code, and the file's SHA-256. They approve,
refuse or defer; the decision is stored with that hash, and an approval does not count if the file changed after it was
shown. Only approved check sets are copied to `approved/`. Nothing is kept without approval.

### Step 6 — the public repository (still to build)
One public GitHub repo with the planter, the scorer, the prompts, every round's checks and logs, and a README whose
first command (`./score_round.sh`) prints the scorecard.

## 4. Resources

| Need | What I have |
|---|---|
| Data | public NYC TLC trip records; no account or access request needed |
| Compute | my laptop; scoring one round takes seconds (`claude-round1.txt`–`claude-round2.txt` written 17:25:21–17:25:23) |
| AI | my existing Claude subscription (Claude desktop app for the hand rounds; Claude Code 2.1.330, headless, for the loop); no API key and no token credits to buy. The live loop used 3 model calls, 32 + 25 + 15 s. It has to stay within the subscription's usage limits, which is one reason it stops at three rounds. The loop's raw replies (`loop-runs/2026-11-23_182418/round*/reply.json`) include Claude Code's `total_cost_usd` estimate (about $0.49 for the three rounds): that is what the calls would cost at API rates; on my subscription there is no per-call charge, and the usage counts against the plan's limits. |
| Software | Python 3.11, pandas, pyarrow, pandera, (for the comparison) dbt-core + dbt-duckdb and GX Core; all free and open source |
| Film | the Brutalist toolkit (Kokoro, Manim), run locally for free |

## 5. Evaluation

**What is measured, for every set of checks:**

| Measure | How |
|---|---|
| defect types caught | CAUGHT / PARTLY / MISSED per type, out of 5 |
| false alarms | good rows flagged on the 10,000-row clean copy |
| crashing checks | checks that raise instead of returning a result (CHECK ERROR) |
| held-out | the same scoring on a second planting (seed 99), and false alarms on a second, disjoint clean copy (`first-run/heldout_clean.py`: 10,000 good trips from the same month, seed 2026, 0 rows shared with the feedback copy) |

**The pass line** (coded in `loop.py`, `passes()`). A round passes only if, on both plantings:
5 of 5 defect types are CAUGHT, 0 good trips are flagged, and 0 checks crash. Anything less is a fail and is recorded.

**What tells me it worked.** The loop reaches the pass line within three rounds. **What tells me it did not.** No
round passes by round 3; then the finding is where the AI's checks failed (which defect types, which rules caused
false alarms, which checks crashed), and that is published in the repo.

**Results — by hand (recorded 2026-10-25, seed 25; seed 99 identical):**

| Checks | Clean copy | Defect types caught | Pass line |
|---|---|---|---|
| my one hand-written rule (`fare_amount >= 0`) | PASS | 2 of 5 | fail |
| Claude, round 1 | 220 good trips flagged | 5 of 5 | fail |
| Claude, round 2 | 0 flagged, but one check crashes (`NotImplementedError`) | 4 of 5 (negative fares 0/25) | fail |

**Results — the loop (live run by Ethan, 2026-11-23 18:24–18:25, `loop-runs/2026-11-23_182418/`):**

| Round | Feedback Claude got | Clean copy | Caught, seed 25 / seed 99 | Second clean copy | Pass line |
|---|---|---|---|---|---|
| 1 | the contract | 94 good trips flagged | 5 / 5 of 5 | 96 flagged | fail |
| 2 | 5 rules rejected 94 good trips | 1 flagged | 5 / 5 of 5 | 0 flagged | fail |
| 3 | 1 rule rejected 1 good trip | **PASS** | **5 / 5 of 5** | **0 flagged** | **met** — loop stopped |

Round 3 kept a rule for every defect type (fare between 0 and 1000, drop-off not before pick-up, no duplicates, no
missing values, fare stored as a number) and dropped only the fare-versus-distance rule that rejected one good trip.
The second-clean-copy column was computed by Claude Code after the run (`heldout_clean.py`), with the checks unchanged.

**Planned failure cases (for the final project).** At least five deliberate failures, each with the check that must
catch it: a forbidden import (the code policy refuses it); a crashing check (the scorer reports CHECK ERROR); hard-coded
values (a contract check); an empty or code-less reply (the loop refuses it); an attempt to read the answer key (the
policy, and later the tool permissions, refuse it); a used-up budget (the loop stops).

**The controlled failure (planned).** Predicted first, in a premortem: when only false alarms are fed back, Claude can
drop a protective rule, as it did by hand on 2026-10-25 (negative fares 0/25). It will be triggered on purpose; the
held-out scorer must catch it; the person refuses it at the gate; then a reviewed recovery run.

**A frozen held-out month (planned, for the final project).** Seed 99 and the second clean copy were never used to make
feedback, but they come from the same month and the second clean copy was drawn after the run. For the final, a
February 2025 sample will be downloaded, cleaned and planted once, hashed, and frozen before the next run, so the
held-out test is set aside before any tuning and comes from data the checks were never near.

## 6. Limits and risks

- One table and five defect types: a pass here does not prove the checks are good for any table.
- Planted defects are simpler than real ones; the real month's 144,118 negative fares are a reminder that real data
  has its own patterns.
- The pass is one run on one table and five planted defect types. The plantings come from the same generator as each
  other, so they test those five defect types, not defects in general; real, unplanted defects are not tested.
- "0 good trips flagged" on the feedback copy is in-sample (the loop tuned against it); the second clean copy is the
  out-of-sample check, and it is from the same month.
- The model is not deterministic: a rerun may take a different number of rounds, or fail. One run is one result.
- The thresholds Claude chose (e.g. fares up to $1,000, trips up to 24 hours) are judgement calls the scorer does not test.
- Usage limits on the subscription may slow the loop; three rounds keeps it within reach.
- The clean copy is "clean" by the two first-piece rules only; a stricter check could flag real problems in it, which
  the false-alarm count would then overstate.
