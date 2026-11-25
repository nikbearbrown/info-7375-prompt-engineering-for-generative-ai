# JS2 — Loop, Tools, and Diff

INFO 7375 Prompt Engineering & Agentic AI, Fall 2026 (Prof. Nik Bear Brown)
Student: Rithika Sankar Rajeswari (GitHub: rithika-sr)
Builds on JS1 (`fall-2026/rithika-s/js1-contract-and-watch`, commit `aa7c870`).

A bounded job-search agent for the persona Priya Nair. It checks four job
boards (Greenhouse and Ashby), finds new postings, and stops with one of four
exits. Every rule it follows was decided in `GATE.md` before any code was written.

## Setup

- Python 3.11 or newer (tested on Python 3.14, macOS). No third-party packages, no API key.
- Run every command from this folder (`js2-loop-tools-diff/`).

## Run the tests (offline)

```bash
python3 -m unittest discover -s tests                        # full suite: 142 tests
python3 -m unittest discover -s tests -p 'test_mutants.py' -v # every GATE wrong version (W1–W11) is caught
python3 -m unittest discover -s tests -p 'test_policy.py' -v  # boundary tests B01–B20
python3 -m unittest discover -s tests -p 'test_review_empty_board.py' -v  # review-packet test
```

## Run the agent

```bash
python3 -m agent.loop                                     # LIVE: all 4 boards in config/boards.json (needs network)
python3 -m agent.loop --boards config/boards_demo_3.json  # LIVE: 3 real boards only
python3 -m agent.loop --boards config/boards_demo_3.json --replay data/seeded_demo/day2  # SEEDED replay, offline
python3 -m checks.independent_check out/runs/<run_id>     # independent check; imports nothing from agent/
```

Exit codes: `finished` 0, `incomplete` 1, `budget_exhausted` 2, `error` 3.
Runs made with `--replay` are labeled SEEDED in the run ID, report and trace.
Two runs started in the same second get the same run ID, and the second one
stops with `error (3)` rather than overwrite the first. Wait a second between runs.

## Contents

| Path | What it is |
|---|---|
| `GATE.md` | My decisions: exits, budgets, repeat rule, error policy, permissions, wrong versions W1–W11, and dated decision logs |
| `BOUNDARY_TESTS.md` | Boundary cases B01–B20, predicted before the policy code, with actual results |
| `REVIEW_PACKET.md` | Review of the `empty_after_nonempty` patch: defect, test before patch, scope, diff, decision |
| `FRICTIONAL.md` | Dated learning log |
| `SIGNOFF.md` | Driver's-seat table and my sign-off |
| `SOURCES.md` | Sources and contribution statement |
| `JS1_CONTRACT.md` | JS1 contract, carried over unchanged |
| `agent/` | `loop.py` (bounded loop), `policy.py` (network, path and approval checks), `adapters.py` (Greenhouse, Ashby), `transport.py` (real and replay), plus JS1 modules |
| `checks/independent_check.py` | Checker that reads the run's files without importing the agent |
| `config/` | `boards.json` (4 boards, one deliberately missing), `boards_demo_3.json`, `budgets.json` |
| `tests/` | 142 offline tests, `mutants.py` (W1–W11), `js2_harness.py` (fake transport and clock) |
| `data/` | Persona files; `seeded_demo/` holds the hand-made SEEDED demo inputs (see its README) |
| `out/` | Real run outputs: `raw/` responses, `state/`, `runs/` (trace, summary, report per run) |
| `evidence/` | Saved terminal output for every test run, live run and demo, the patch diff, and the scope-approval screenshot |

## Runs included

| Run | Kind | Result |
|---|---|---|
| `20261110T183029Z` | LIVE, 4 boards | `incomplete (1)`: 3 baselines, deliberate 404 handled; checker PASS |
| `20261110T193514Z-SEEDED` | SEEDED day 1 | `finished (0)` |
| `20261110T193722Z-SEEDED` | SEEDED day 2, before patch | `finished (0)` but wrong (Scale AI 0); checker FLAG, exit 1 |
| `20261110T200439Z-SEEDED` | SEEDED day 2, after patch | `incomplete (1)`, Scale AI `failed (empty_after_nonempty)`; checker PASS |

## What was and was not verified

Verified by me: the full suite, the mutant check and the boundary tests (saved
in `evidence/`), live run 1, and the before/after SEEDED demo. Not verified:
the `empty_after_nonempty` rule on an Ashby board, and on a live board that
really goes empty; it has only been exercised with fakes and SEEDED data.

## License

MIT
