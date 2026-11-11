# Job-Search Agent 2 — The Loop, the Tools, and the Diff
**Anisha Gaikar · INFO7375 · fall-2026/anisha-g/js2-loop-tools-diff**

**What I started from:** my own JS1 agent (`../js1-contract-and-watch/`). I reused its **ideas**: a Greenhouse watch, new-since-last-run by id, and saving the raw responses as evidence. I did **not** reuse its code: the JS2 code is new, written for the multi-board loop and the policy. I did not use the Reallocation Engine or Lectern.

- **Language:** Python 3. It was run with Python 3.14 on macOS. The standard library only, no packages to install.
- **Toolchain:**
  - `python3` and `unittest`;
  - `curl`, used only by the independent check's `--live` recount;
  - `git`, `shasum`;
  - Claude (this chat) for the build;
  - Claude Code on my Mac as the reviewer and for the review-packet change;
  - ChatGPT for wording and as a second reviewer (see SOURCES.md).

## Exact commands (from a fresh clone, inside this folder)
```bash
python3 -m unittest discover -s tests -t .                       # all tests (70)
bash tools/make_logs.sh                                          # test evidence -> logs/01..03 (wrong versions must FAIL)
python3 watch.py run                                             # one live run over boards.json (incl. the deliberate failure)
python3 watch.py check reports/job-watch/runs/<run-id> --live    # independent check: raw recount + live curl recount
python3 watch.py run --wrong empty_as_zero                       # finished-wrong demo A (labelled WRONG-DEMO)
python3 watch.py run --boards boards-demo.json --wrong lever_reads_nothing   # finished-wrong demo B
```
- **Budgets:** 5 boards, 15 requests and 60 seconds per run (GATE 2). They live in `watcher/loop.py`'s `Budget`, and only I change them.
- **Outputs:** the agent writes only to `reports/job-watch/`.

## What ran (all on my Mac; commits in order)
| Commit | When | What |
|---|---|---|
| `cdc62ba` | 11-09 15:08 | **GATE.md, alone, before any code** |
| `c60940c` | 11-09 15:17 | My boundary predictions + the tests, **before any implementation**: `logs/00` fails at import |
| `3ac13df` | 11-09 15:19 | Removed a parallel draft that had landed in the folder (FRICTIONAL) |
| `596fc0f` | 11-10 21:30 | The implementation, written after the frozen tests: `logs/02` shows the tests **fail** on both wrong versions (8 and 2 failures), and `logs/03` shows they **pass** |
| `24ed508` | 11-10 21:30 | My attribution correction in GATE.md and PREDICTIONS.md (ChatGPT drafted the wording) |
| `c2afaa4` | 11-10 21:30 | 17 tests for the reviewers' findings, **before the fixes**: `logs/04`, `failures=6, errors=11` |
| `8be479f` | 11-10 21:30 | The fixes: 64/64 pass |
| `d3f9778` | 11-10 21:31 | **Live runs** 1 and 2, and the **finished-wrong demos** with their independent checks (`logs/10`–`17`) |
| `21451f2` | 11-10 21:34 | Review packet: **the defect reproduced**, with the test failing before the patch (`logs/20`) |
| (final commit) | 11-10 | Review packet: the Claude Code patch accepted, 66/66 pass (`logs/21`–`23`); Lever/Greenhouse parser tests added after a final review (`logs/24`, 70/70); the write-ups |

`tests.frozen.sha256` and `tests.review-fixes.frozen.sha256` prove the tests weren't edited after they were frozen (`logs/01`). PREDICTIONS.md was changed once afterwards, for the authorship correction only; its original hash is kept in the frozen manifest.

## Where each requirement is
| Requirement | File |
|---|---|
| Exits, budgets, repeat rule, error policy, permission policy, wrong versions | [GATE.md](GATE.md) |
| The loop: 3 boards on 2 systems, budget, exit status, every observation | `watcher/loop.py`, `boards.json`, each run's `trace.json` |
| A real run's trace, with the deliberate failure | [TRACE.md](TRACE.md) §1, `reports/job-watch/runs/20261110T213125-live/` |
| A finished wrong answer, caught by an independent check | [FINISHED-WRONG.md](FINISHED-WRONG.md), [TRACE.md](TRACE.md) §2, `watcher/check.py`, `logs/14`–`17` |
| The permission policy in code, plus 18 boundary cases predicted before running | [PERMISSIONS.md](PERMISSIONS.md), `watcher/policy.py`, `tests/test_policy.py` |
| Wrong versions the tests must catch | `wrong_versions/`, `logs/02` |
| The review packet | [REVIEW-PACKET.md](REVIEW-PACKET.md) |
| Saved raw responses | `reports/job-watch/runs/*/raw/` |
| Sources, honest log | [SOURCES.md](SOURCES.md), [FRICTIONAL.md](FRICTIONAL.md) |

## Sign-off — Job-Search Agent 2
- **Checked** (each by a named test that I ran on my Mac; logs in `logs/`):
  - **Exits:** finished, incomplete, budget-exhausted and error (`tests/test_loop.py::Exits`).
  - **Budgets:** 5/15/60, with retries and redirects counted (`Budgets`, `RedirectsCount`, `Deadline`).
  - **The repeat rule** (`Repeat`).
  - **The error policy:** a bad name isn't retried; a timeout or blank body is retried once; no value is invented (`Errors`).
  - **Both of my GATE wrong versions are caught** (`WrongVersions`; `logs/02` shows 8 and 2 failures).
  - **18 boundary cases** match my predictions (`tests/test_policy.py`, PERMISSIONS.md).
  - **The independent check** catches both finished-wrong demos (`tests/test_check.py`, `IndependentCheckLive`, `logs/15`, `logs/17`).
  - **The review-packet fix** (`tests/test_review_packet.py`, `logs/20` → `logs/22`).
  - **Both parsers** (`tests/test_parsers.py`, added after the code; `logs/24` shows it failing on the wrong Lever parser).
- **How:**
  - The tests were written by Claude **from my GATE.md and my predictions, before the code existed** (commit `c60940c`, `logs/00`), and frozen (`logs/01`).
  - The tests for the reviewers' findings were written before the fixes (`logs/04`).
  - I ran every test, every live run and every check myself. With Claude's help: all the code and the test code.
  - By recomputation: the independent check recounts the jobs from the raw bytes and with curl.
- **Not checked (my choices):**
  1. Only 3 real boards were tested; other boards may answer in other ways.
  2. A real timeout or blank body never happened live; the retry was only tested with fakes.
  3. A real redirect never happened live; redirect counting was only tested with fakes.
- **Not claiming:**
  - that the agent finds jobs worth my time (JS2 has no relevance judge);
  - that it handles every Greenhouse or Lever board, or any other ATS;
  - that the live recount separates a bug from a real board change made between the run and the check;
  - that old state wiped before the review-packet fix is repaired.
- **Signed or withheld:** Signed — Anisha Gaikar, 2026-11-10

## Driver's seat
| Part | What Claude should do | What I should do | Why it stays mine (my words) | Evidence |
|---|---|---|---|---|
| The loop: budgets, exits, error rules | Implement them exactly; point out gaps (for example, that 15 requests can't bind) | Decide the rules and any change to them | "I decide the budgets, exits, and error rules because I'm responsible for how much freedom the agent has and what it tells me when something goes wrong. Claude can suggest a retry rule, but I decide how long I'm willing to wait and when I'd rather get a partial report." | `cdc62ba` (GATE.md before any code); my 15-cap decision (FRICTIONAL ~3:23 pm) |
| The review | Make the one requested change, without touching the tests | Reproduce first, read the diff as behaviour, decide | "I make the final call because I'm responsible for what goes into the project. I looked at the one-line diff, the two failures saved before the patch, and the passing output after it. That showed me the fix kept old IDs while still reporting genuinely new jobs." | `21451f2` (the test failing before the patch); `logs/20`–`23`; REVIEW-PACKET.md §6 |

