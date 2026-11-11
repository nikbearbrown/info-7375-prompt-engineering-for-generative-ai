# RUNS.md: every run I cite

This lists every agent run of Job-Search Agent 2, plus the one cross-check I ran outside the agent. Nothing was discarded or deleted.
Each run folder holds:
- `console.txt`: the loop's own output
- `trace.jsonl`: one line per step
- `report.json`
- `raw/`: every raw response, saved before parsing
- `state_update.json`
- `verifier.txt`: the independent check

The commands came from `scripts/run_and_verify.py`. Every run used `--no-claude`.

*Who wrote this file:* the JS2 agent (the runtime) never writes it, as GATE.md requires. Claude Code wrote it at my direction from the
run outputs on 2026-11-10.

*What I checked myself:* on 2026-11-10 at 17:31 EST I reran `scripts/verify_run.py` on runs A, B and D (FAIL / FAIL / PASS, matching
the rows below) and grepped run A's trace for the deliberate 404 (1 attempt, HTTP 404). I have **not** rechecked rows X (the
cross-check) and C (the seeded run) by hand. Their outputs are in the folders listed.

| Run | When (ET) | Kind | Boards file | Loop exit | Verifier | Requests / seconds | Folder |
|---|---|---|---|---|---|---|---|
| A | 2026-11-10 17:15:00 | **live**. Samsara compared with the real 2026-10-31 baseline; the other 8 boards baselined | `config/boards.json` (10) | **incomplete (1)**: the deliberate 404 | **FAIL**: kraken empty | 10 / 11.5 | `out/runs/2026-11-10T171500_live/` |
| B | 2026-11-10 17:15:27 | **live**, same day, 27 s after A | `config/boards_no_failure.json` (9) | **finished (0)**, and wrong | **FAIL**: kraken empty | 9 / 25.9 | `out/runs/2026-11-10T171527_live/` |
| X | 2026-11-10 17:15:53 | **my cross-check, outside the agent**: one GET to Kraken's Ashby board | — | — | 92 postings (32 US or remote) | 1 / — | `evidence/crosscheck/2026-11-10T171553_ashby_kraken.com.json` (sha256 `985c7087…`) |
| C | 2026-11-10 17:16:05 | **SEEDED** replay, no network. Samsara's list replaced by `tests/fixtures/seeded/empty-samsara.json` | `config/boards_seeded.json` (1) | **finished (0)**, and wrong | **FAIL**: empty, and 0 vs 323 on Oct 31 | 1 / 0.0 | `evidence/seeded/empty-samsara/runs/2026-11-10T171605_seeded/` |
| D | 2026-11-10 17:16:11 | **live**, same day, 71 s after A | `config/boards_clean.json` (8) | **finished (0)** | **PASS** | 8 / 12.8 | `out/runs/2026-11-10T171611_live/` |

## What each run shows

- **A:**
  - `greenhouse:samsara-does-not-exist` returned HTTP 404 once and was **not retried** (1 attempt). Its count is `null`, and the
    report says "count unknown, not zero."
  - Nine successful boards plus one failure gave `incomplete`, as the gate predicted.
  - Samsara: 314 postings now against 323 on 2026-10-31. **80 are new** since Oct 31, and 89 have disappeared. **None of the 80 has a
    data title**, so nothing was judged. Claude Code checked that against the raw file with a broader match (`data|analytic`) than
    the rule uses, and found no hits.
- **B (the live finished-wrong answer):**
  - Every board answered in its provider's shape, so the loop said `finished`. `lever:kraken` was reported as 0 postings and 0 new.
  - The verifier failed it as empty, needing review.
  - Cross-check X, 26 s later, shows Kraken listing 92 postings on Ashby. So "0 new jobs at Kraken" is wrong, not just suspicious.
  - Samsara went from 314 to 313 between A and B. One posting disappeared, which the loop handles because it reports only new ids.
- **C (SEEDED, clearly labeled):** an offline version of the same failure that doesn't depend on Kraken staying empty. The loop said
  `finished`, 0 new. The verifier failed it twice: the board is empty, and it fell from 323 (baseline) to 0.
- **D (the clean run):** eight boards, `finished` and PASS. Toast had **1 new posting** since run A, and it is not data-titled.

## Limits of these runs, stated plainly

- **Only Samsara has a real earlier day** (2026-10-31). Boards 2–9 were first seen in run A, and B and D came **27 s and 71 s
  later**, the same day. That is not a second day.
- **No new data-titled posting appeared live**, so the rule judge never ran on a live posting in JS2. That path is covered only by the
  offline tests (`test_second_run_reports_new_and_judges_data_titles`, `test_lever_needs_no_detail_request`, W14).
- **No live retry, redirect or 429 happened.** Those paths are covered only by offline tests.
- The board picks come from read-only probes on 2026-11-10 that were **not** agent runs, and their raw responses were not saved.
