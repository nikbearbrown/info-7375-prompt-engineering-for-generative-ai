# first-run — DataSentry's first pieces

Real public data, planted defects, and a scorer that grades any set of pandera checks: my one hand-written rule, and
two rounds of checks written by Claude. Plus the same rule in dbt and Great Expectations for comparison. Free and
local: no API keys, no accounts.

```bash
./run_all.sh          # the data, the one-check first piece, dbt and GX; about a minute after the first run
./score_round.sh 1    # score Claude's round-1 checks (and the hand-written baseline)
./score_round.sh 2    # score Claude's round-2 checks
./run_loop.sh         # the loop: Claude writes, the scorer grades, clean-copy feedback goes back, up to 3 rounds
```

## The loop (`run_loop.sh` → `loop.py`)

Each round, `loop.py` asks Claude Code (headless, `claude -p`, on the logged-in Claude subscription; no API key) for one
checks file, checks the code against a policy before running it, scores it on the clean copy and both plantings, and
records everything under `loop-runs/<timestamp>/round<N>/`. Round 1 sends the contract (`claude-checks/PROMPT-round1.md`);
later rounds send only the clean copy's results in the same conversation (which rules rejected good trips, which crashed).

| Part | Where |
|---|---|
| budget | `--rounds 3` (default), `--timeout` seconds per Claude call |
| stop conditions | pass line met (5 of 5 caught, 0 good rows flagged, 0 crashes, on seeds 25 and 99) · budget used · reply with no single code block · code refused by the policy · clean copy already passes, so clean-copy feedback has nothing left to report — never "the model said it was done" |
| what Claude can do | answer in text only: `--tools ""`, `--strict-mcp-config`, an empty working folder (`loop-runs/<run>/work/`) |
| code policy (enforced before the scorer imports the file) | `check_policy()`: only pandas / pandera / numpy / re / math / datetime / typing imports; no `open`, `eval`, `exec`, `__import__`, dunder attributes, `read_*` / `to_*` file I/O (except `to_datetime`, `to_numeric`, `to_timedelta`), `system`, `remove`, …; a top-level `schema` is required |
| state | `loop-runs/<run>/state.json` (mode, model, CLI version, session id, every round's result and decision) |
| tests (written before the loop) | `tests/test_loop.py`, 13 tests, run by `run_loop.sh` before every loop; the loop does not start if they fail |

`./run_loop.sh --fixture claude-checks` replays the two saved replies instead of calling Claude (no login needed); it
reproduces the recorded round-1 and round-2 scores exactly.

All three write to `results/<today>/`.

## The first piece (`run_all.sh`)

| Step | Script | What it does |
|---|---|---|
| 1 | `get_data.py` | Downloads NYC TLC yellow taxi trips, January 2025 (public). Keeps 5 columns, drops rows that already break the two rules, samples 10,000 rows (seed 7375) → `data/clean.parquet`. Records how many rows in the real month break the rules. |
| 2 | `plant_defects.py` | Copies the clean sample and plants 25 negative fares + 25 drop-offs before pick-up (seed 25) → `data/broken.parquet`. Writes the answer key to `data/planted/`; no check reads it. |
| 3 | `run_first_piece.py` + `checks/fare_check.py` | One pandera check, `fare_amount >= 0`, on both copies. Then opens the answer key to score each defect type CAUGHT or MISSED. |
| 4 | `dbt_compare/` | The same rule as a dbt test (dbt-core + dbt-duckdb). dbt's built-in tests have no range rule, so it's a small custom generic test, `not_negative`. |
| 5 | `gx_check.py` | The same rule in Great Expectations (GX Core): `ExpectColumnValuesToBeBetween(fare_amount, min_value=0)`. |
| 6 | `summarize.py` | The three tools side by side, plus package versions. |

The check deliberately covers one property, so the run shows both outcomes: the negative fares are caught, and the
drop-offs before pick-up get through every tool, because no rule asked about them.

## Scoring AI-written checks (`score_round.sh N`)

| Script | What it does |
|---|---|
| `plant_five.py <seed>` | One broken copy per defect type: `negative_fare` (25 rows), `dropoff_before_pickup` (25 rows, 5–59 minutes early), `missing_value` (25 trip distances blanked), `duplicate_rows` (25 trips appended again), `wrong_type` (the whole fare_amount column stored as text, like a bad import). Answer key → `data/planted/<seed>/answer_key.json`. Seed 25 is the main planting, seed 99 the held-out one. |
| `score_checks.py <checks.py> <label> <out> [seed]` | Runs a checks file on the clean copy and every broken copy. Clean copy: PASS, or FAIL with the false-alarm rows, column-level failures, and any check that crashed (reported as CHECK ERROR, never as a catch). Each defect type: CAUGHT, PARTLY CAUGHT or MISSED, against the answer key. |
| `explain_clean.py <checks.py> <label> <out>` | Which rules flag the clean copy, and how many rows each. Clean copy only, so it says nothing about the defects; this is the only feedback allowed into the next round. |
| `score_round.sh N` | Scores the hand-written baseline, `claude-checks/roundN_checks.py` on seed 25 and on the held-out seed 99, runs `explain_clean.py`, and copies the checks file next to its results. |

`claude-checks/` holds the prompts (`PROMPT-round1.md`, `PROMPT-round2.md`), Claude's replies saved verbatim and dated
(`round*-reply-2026-10-25.md`; Claude desktop app, Opus 5.5, effort "High"), and the extracted code
(`round*_checks.py`, unedited). Claude saw only the five column names and types, never the data or the defects.

## Recorded runs

`results/2026-10-25/`, run by Ethan Gomes on 2026-10-25: `run_all.sh` at 06:16, both scoring rounds at 17:25.

| Checks | Clean copy (10,000 good trips) | Defect types fully caught (of 5) |
|---|---|---|
| Hand-written baseline | PASS | 2 |
| Claude, round 1 | FAIL: 220 rows flagged | 5 |
| Claude, round 2 | 0 rows flagged; one check crashes (`NotImplementedError`) | 4 (negative fares 0/25) |

The held-out planting (seed 99) gave the same results. Not committed: `.venv/` and `data/` (the 59 MB raw month and
the copies), which `run_all.sh` and `plant_five.py` re-create. The data hashes are in `results/2026-10-25/data.json`.
