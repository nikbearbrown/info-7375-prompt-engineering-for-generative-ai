# Job-Search Agent 2 — The Loop, the Tools, and the Diff

Arundhati K · INFO 7375 · Fall 2026 · persona: Rohan Desai (fictional, `persona/rohan-desai.resume.example.json`)

**Started from** my JS1 agent (`../js1-contract-and-watch/`: Stripe on Greenhouse, allow-listed GET-only fetch).
Board choices were checked against the instructor's Lectern list (`../../nik-bear-brown/lectern/sources.json`).
No Lectern or Reallocation Engine code was copied.

## Order of work (each step committed before the next)

| step | commit | what |
|---|---|---|
| gate | `6833492` | [GATE.md](GATE.md): exits, budgets, repeat rule, error and permission policy, wrong versions (drafted by Claude Code, accepted by me, see its header) |
| predictions | `6fed708` | [BOUNDARY-PREDICTIONS.md](BOUNDARY-PREDICTIONS.md): my 16 predictions, before any test |
| tests first | `40d904c` | 38 tests from GATE.md; they fail, no code yet ([log](evidence/logs/00-tests-before-code.txt)) |
| code | `21db57c` | `jsagent2/`, `run.py`, `check.py`; the same 38 tests pass, unedited ([log](evidence/logs/01-tests-after-code.txt)) |
| live run + demo | `a15cbef` | [evidence/run-live-1](evidence/run-live-1/report.md), [finished-wrong-answer](evidence/logs/02-finished-wrong-answer-demo.txt) |
| review: reproduce + test | `772af22` | [review/](review/REVIEW.md): defect reproduced, test written, before the patch |
| review: patch + decision | see [review/REVIEW.md](review/REVIEW.md) | |

## Language and toolchain

- Python 3, standard library only (developed on Python 3.15.0, macOS). Nothing to install.
- Network: only `boards-api.greenhouse.io` and `api.ashbyhq.com`, GET only (`jsagent2/policy.py`).
- Claude Code (`claude` CLI) was used to write code and docs. The agent itself calls no model.

## Exact commands (from this folder, fresh clone)

```bash
python3 -m unittest discover -s tests -t .        # 43 tests, offline
python3 run.py                                    # live run; the state write is HELD
python3 run.py --approve-state-write              # live run; I approve writing out/state/seen.json
python3 check.py out/runs/<run-id>/trace.json --previous out/runs/<earlier-id>/trace.json   # independent check
python3 check.py evidence/run-live-1/trace.json --root evidence/run-live-1/root              # check the saved run
python3 demo_wrong_answer.py                      # SEEDED finished-wrong-answer demo, offline
python3 review/reproduce_defect.py                # review-packet defect: exit 1 before patch, 0 after
```

`run.py` exits 0 only when the run is `finished`. With the deliberate failure board in `config/boards.json`,
a correct run exits 1 (`incomplete`).

## What ran

| run | when | kind | result |
|---|---|---|---|
| `live-1` | 2026-11-10 ~16:36 EST | **live**, by Claude Code | exit `incomplete`: Stripe 775, Figma 143, Notion 155 (all baseline), deliberate failure `not-found (HTTP 404)` shown as `—`, 1 request (no retry), 4/8 requests, state write `held-for-approval` (no flag). `check.py`: no findings. [report](evidence/run-live-1/report.md) · [trace](evidence/run-live-1/trace.json) · raw: `evidence/run-live-1/root/out/runs/live-1/raw/` |
| A, B, C, D | 2026-11-10 | **SEEDED** replay of `live-1`; Figma replaced by a **constructed** empty board | B (wrong version 1) ends `finished`, "Figma 0 new"; C `check.py` flags `finished-with-empty-board` and `drop-to-zero` (143 → 0); D real agent: `incomplete`, Figma `empty-unverified`. [log](evidence/logs/02-finished-wrong-answer-demo.txt) · traces: `evidence/finished-wrong-answer/` |

## Where each requirement is

| requirement | where |
|---|---|
| exits, budgets, repeat rule, error policy | [GATE.md](GATE.md) §1–4 → `jsagent2/loop.py` → `tests/test_loop.py` (`Exits`, `Budgets`, `RepeatRule`, `ErrorPolicy`) |
| ≥3 boards, 2 systems, deliberate failure | `config/boards.json`; `evidence/run-live-1/` |
| record of every observation | `trace.json` → `observations` (policy decision, response with sha256 + raw file, retry, budget, state write, exit); `tests/test_loop.py::Trace` |
| finished wrong answer + independent check | `demo_wrong_answer.py`, `jsagent2/check.py`, `tests/test_check.py` |
| permission policy in code, 16 predicted cases | `jsagent2/policy.py`, [BOUNDARY-PREDICTIONS.md](BOUNDARY-PREDICTIONS.md), `tests/test_policy.py` |
| wrong versions caught | GATE.md §6 → `tests/test_wrong_versions.py` (each wrong version turns named tests red) |
| review packet | [review/REVIEW.md](review/REVIEW.md) |
| sign-off, driver's seat | [SIGNOFF.md](SIGNOFF.md) |
| sources, honest log | [SOURCES.md](SOURCES.md), [FRICTIONAL.md](FRICTIONAL.md) |

Not included: caches, `out/` scratch runs, credentials, my real résumé.
