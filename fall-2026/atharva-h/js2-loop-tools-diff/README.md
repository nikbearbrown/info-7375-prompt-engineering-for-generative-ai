# Job-Search Agent 2: The Loop, the Tools, and the Diff

A bounded loop that watches three real job boards on three applicant-tracking systems (Greenhouse, Ashby, Lever), plus one board that fails on purpose. On each run it reports which postings are new and which have closed since the last run. Every request and every write goes through a permission policy enforced in code (`policy.py`). The rules for the loop were written in `GATE.md` before any code existed.

- **Started from:** my Job-Search Agent 1 code, `../js1-contract-and-watch/` at commit `f0b7a6b`. I did not use the Reallocation Engine or Lectern.
- **No judging in JS2.** The loop reports new and closed ids only. JS1's rule judge and Claude judge stay in JS1, and JS2 never calls Claude.

## Language and toolchain
- **Python 3, standard library only.** Nothing to install, no API keys, no `pip`.
- **Tested with:** Python 3.14.7 on macOS 26.5.1 (Darwin 25.5.0), git 2.55.0.
- **Tests:** `unittest`. They run offline: the network is scripted (see "Simulated vs live" below).
- **Live runs need network access** to three public hosts only: `boards-api.greenhouse.io`, `api.ashbyhq.com`, and `api.lever.co`.

## Commands
From a fresh clone:

```bash
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.git
cd info-7375-prompt-engineering-for-generative-ai
git checkout atharva-h/js2-loop-tools-diff
cd fall-2026/atharva-h/js2-loop-tools-diff
```

Offline, no network:

```bash
python3 -m unittest discover -s tests        # 56 tests, scripted network
python3 precheck.py                          # pre-submit honesty check
```

Live (each run makes at most 10 GET requests and takes about 2 seconds):

```bash
python3 agent.py run                                     # the four configured boards; adds runs/<time>/ and updates state/seen.json
python3 check_identity.py                                # independent name check on config/boards.json
python3 agent.py run --config config/wrong_board.json --state state/wrong_board_rerun.json --label WRONG-BOARD-rerun
python3 check_identity.py --config config/wrong_board.json
python3 crosscheck_days.py runs/2026-11-09T205756Z runs/2026-11-10T170553Z   # read-only recomputation of day 2
```

- **Exit codes:** 0 `finished`, 1 `incomplete`, 2 `budget-exhausted`, 3 `error`. `check_identity.py` and `crosscheck_days.py` exit 0 if they agree and 1 if they don't.
- **With the current config, a live run exits `incomplete`** (code 1). That is intended: `ashby/valonn` is misspelled on purpose and fails.
- **Commands that need approval:** `python3 agent.py reset-state` and `python3 agent.py delete-run runs/FOLDER` ask y/N in the terminal. Without a terminal, the answer is no.
- **The patched loop no longer finishes on the wrong board.** To see the original finished wrong answer, run the wrong-board command on the pre-patch code (commit `a81c572`). `WRONG_ANSWER.md` shows how.

## What ran
All live runs below hit the real public endpoints. None were seeded or simulated.

| Run folder | Date (UTC) | Command | Run by | Result |
|---|---|---|---|---|
| `runs/2026-11-09T205756Z` | 2026-11-09 | `agent.py run` (day 1) | Claude Code, in my session | `incomplete`, 4 requests, 1.7 s. Baselines: Abacus 15, Valon 31, Xsolla 185. `valonn` got a real 404. |
| `runs/2026-11-09T205807Z_WRONG-BOARD-demo` | 2026-11-09 | `agent.py run --config config/wrong_board.json` | Claude Code, in my session | `finished`, exit 0, 46 postings: **the finished wrong answer** |
| `runs/2026-11-09T205808Z_identity-check` | 2026-11-09 | `check_identity.py --config config/wrong_board.json` | Claude Code, in my session | MISMATCH ("ABACUS"), exit 1: **the independent check** |
| `runs/2026-11-09T205810Z_identity-check` | 2026-11-09 | `check_identity.py` | Claude Code, in my session | Abacus Insights matched; Ashby and Lever were "not checkable" |
| `runs/2026-11-10T170122Z_WRONG-BOARD-after-patch` | 2026-11-10 | `agent.py run --config config/wrong_board.json --state state/wrong_board_after.json --label WRONG-BOARD-after-patch` | my review, with AI help | `incomplete` after 1 request: identity mismatch, no ids saved |
| `runs/2026-11-10T170553Z` | 2026-11-10 | `agent.py run` (day 2) | Claude Code, in my session | `incomplete`, 5 requests, 1.6 s. Abacus 16 (1 new), Xsolla 186 (1 new), Valon 31, nothing closed. `valonn` got a real 404. |

- **Day-2 cross-check:** `crosscheck_days.py` recomputed new and closed from the two days' raw responses and agreed with `run.json` on all three boards.
- **The "new" Abacus posting** (`8782226002`, Software Architect) is a relisting. It was on the board on 2026-10-31 (JS1's saved responses), gone on 11-09, and back on 11-10. It is new since the last run, not a first posting.
- **Live approval prompt, 2026-11-10, with AI help.** Both answers were tested in a real terminal:
  - `python3 agent.py reset-state --state state/seen.json`, answered `N`: exit 3, `error: not approved`. `state/seen.json` was unchanged (3 boards, 233 seen ids, the same SHA-256).
  - `python3 agent.py reset-state --state state/approval_yes_demo.json`, answered `Y`: exit 0. That disposable copy of the state is now empty.
  - `FRICTIONAL.md` records both runs.
- **Every run folder** holds `trace.jsonl` (each request, response, and decision, in order), `run.json` (the summary), `report.md`, and `raw/` (every response body exactly as received, including the 404 body `Not Found`).

### Simulated vs live
- **The 56 tests are simulated.** `tests/helpers.py` replaces only the send step (`Tools._send`) with scripted responses. Every scripted request still goes through the real `Policy` first.
- **Exercised only in simulation:** timeouts, dropped connections, 5xx responses, redirects, and interrupts. None of these happened in a live run.

## Where each deliverable is

| Brief item | File |
|---|---|
| The gate | `GATE.md` (committed `1f00955`, before any code; the 2026-11-10 decision was added in `7641f93`) |
| Code | `loop.py` (the loop, exits, budgets, repeat rule, error policy), `adapters.py` (the three systems), `tools.py` (the agent's tools), `policy.py` (the permission policy), `agent.py` (CLI) |
| Tests | `tests/`: `test_policy.py`, `test_loop.py`, `test_adapters_and_gate.py`, `test_review_identity.py` (the review test: drafted with Claude's help, accepted by me before the patch) |
| Trace of a real run with the deliberate failure | `runs/2026-11-10T170553Z/trace.jsonl` (lines 13–15: `valonn` 404, not retried, board failed) and `runs/2026-11-09T205756Z/trace.jsonl` |
| Finished wrong answer and its independent check | `WRONG_ANSWER.md`, `check_identity.py` |
| Permission policy and boundary-test table | `GATE.md` "Permission policy", `policy.py`, `PERMISSIONS.md` (23 cases, predicted in `159adc2` before any test) |
| Review packet | `REVIEW_PACKET.md` |
| Sign-off and driver's seat | `SIGNOFF.md` |
| Saved raw responses | `runs/*/raw/` |
| Sources and what Claude contributed | `SOURCES.md` |
| Log | `FRICTIONAL.md` |

**Other files:**
- `config/boards.json`: the four boards.
- `config/wrong_board.json`: the wrong board, on purpose.
- `state/`: the seen and present ids for each board. `approval_yes_demo.json` is the disposable copy that was reset in the `Y` test.
- `crosscheck_days.py`: the day-2 recomputation.
- `precheck.py`: the pre-submit check.

## Privacy
- **No persona, résumé, contacts, or credentials** are in this folder. JS2 reads only public job boards.
- **The agent never applies, emails, messages, or logs in.** Its only network tool sends GET requests with no cookies and no credentials, to three allow-listed hosts.
- **My Claude Code transcripts stay on my machine.** `FRICTIONAL.md` summarizes them.
