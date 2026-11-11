# Job-Search Agent 2 — The Loop, the Tools, and the Diff

Sreevarshan Sathiyamurthy, INFO 7375, 2026-11-06.

A bounded loop that checks public job boards on Greenhouse and Lever under a fixed budget, enforces a permission policy in code, picks one of four exit statuses, and writes a full trace. The rules it follows are in [GATE.md](GATE.md), written before any code.

- **Language:** Python 3.13.9, standard library only (urllib, json, time, os, argparse, unittest).
- **GitHub folder:** `fall-2026/sreevarshan-s/js2-loop-tools-diff/`
- **Final commit:** 9ecc0574

## Run commands

Run from the project folder.

```bash
python3 -m js2 --dry-run
```
Prints the four boards, the budget (4 boards, 8 requests, 90 seconds), the allowed hosts and the output folder. Fetches nothing and writes nothing.

```bash
python3 -m js2
```
Live run over the four boards in GATE.md §5. Prints the exit status, one line per board, the raw and trace file paths, and the independent check result. Exit code: 0 finished, 1 incomplete, 2 budget-exhausted, 3 error.

```bash
python3 -m js2 --from-file output/raw/<file>.json
```
Replays one saved raw response with no network. The board is taken from the file name; add `--board <token>` if the name does not follow `<stamp>-<ats>-<token>.json`. The trace is labeled SEEDED.

```bash
python3 -m unittest discover -s tests -t .
```
Runs the full test suite. No test makes a network connection; every test writes only to a temporary folder.

The wrong-answer demo is a Python function, not a CLI flag: `js2.wrong_answer_demo.run_wrong_demo(output_dir)`, where `output_dir` must be inside `output/`. It returns the trace with `exit_status` and `trace_path`; `js2.independent_check.check_trace(trace_path, raw_dir)` returns the discrepancies.

## What ran

| What | Result | Evidence |
|---|---|---|
| Live run, 2026-11-06T19:10:45Z, run by me in Terminal | `incomplete`: Databricks 929 postings, Stripe 765, Spotify 85, invalid-board-xyz HTTP 404; 4 requests, 1.5 s | commit 13e4b94, `output/raw/`, `output/traces/20261106T191047040249Z.json` |
| Wrong-answer demo, run by me in Terminal | exits `finished` when it should be `incomplete`; the independent check flags both discrepancies on demo-empty | commit 9e02c5a, `output/traces/*-WRONG-DEMO.json` |
| Boundary tests, 12 cases, run by me in Terminal | all 12 matched the predictions written beforehand | [BOUNDARY_TESTS.md](BOUNDARY_TESTS.md), commits c7fe0a5 then 59142a6 |
| Unit tests | 53 run, 53 pass | `tests/` |
| Review packet | failing test first (52 pass, 1 fail), then patch (53 pass) | [REVIEW_PACKET.md](REVIEW_PACKET.md), commits 8624b8f and 31149a6 |

## Layout

| Path | Contents |
|---|---|
| `GATE.md` | The eight decisions: exits, budgets, repeat rule, error policy, boards, permissions, wrong versions, finished-but-wrong |
| `js2/policy.py` | `allow_request`, `allow_write`, `write_bytes`; every decision logged with a reason |
| `js2/fetch.py` | `fetch_greenhouse`, `fetch_lever`, `replay_from_file`; `BoardFetchError` |
| `js2/loop.py` | `BOARDS`, budget constants, repeat rule, retry, exit status, trace |
| `js2/__main__.py` | CLI entry point |
| `js2/wrong_answer_demo.py` | Deliberately finished-but-wrong run (GATE.md Bug 1) |
| `js2/independent_check.py` | Re-reads a trace and its raw files and reports discrepancies |
| `tests/` | 53 tests: policy 13, fetch 9, loop 12, independent check 14, CLI 5 |
| `persona/` | Priya Nair resume and profile, copied from JS1 with a `_js2_source` field added |
| `output/` | Raw responses and traces from the runs above |
| `BOUNDARY_TESTS.md`, `REVIEW_PACKET.md`, `SIGN_OFF.md`, `SOURCES.md`, `FRICTIONAL.md` | Write-ups |
