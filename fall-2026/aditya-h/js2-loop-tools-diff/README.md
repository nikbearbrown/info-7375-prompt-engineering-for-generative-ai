# Job-Search Agent 2 — the loop, the tools, and the diff

**Author:** Aditya Hasija (INFO 7375, Fall 2026)

**What it does:** the JS1 job watcher, made into a bounded agent loop over **7 boards on 3 applicant-tracking systems** (Greenhouse, Ashby, Lever).
- Every action passes through a **permission policy enforced in code**.
- Each run ends with one exit: `finished`, `incomplete`, `budget-exhausted`, or `error`.
- A **separate checker** tests whether a clean finish was actually right.

The persona is the fictional Maya Sehgal.

**Started from:** my own [Job-Search Agent 1](../js1-contract-and-watch/), reusing its rule `title-us-v1`, its persona guard and the system-CA TLS fix. The instructor's Lectern notes (`fall-2026/nik-bear-brown/lectern/ATS.md`) were a reference for the Ashby endpoint and the "valid but empty board" lesson. No Lectern or Reallocation Engine code is used.

| | |
|---|---|
| **Gate** (written and approved before any code) | [GATE.md](GATE.md), commit `2fbfc39` |
| Permission policy + boundary-test table | [POLICY.md](POLICY.md) |
| Agent traces + the deliberate failure + the finished-wrong answer | [TRACE.md](TRACE.md) |
| Review packet | [review/REVIEW-PACKET.md](review/REVIEW-PACKET.md) |
| Provenance / honest log | [SOURCES.md](SOURCES.md) · [FRICTIONAL.md](FRICTIONAL.md) |

## Language and toolchain

- **Python 3** (tested on 3.13.3), **standard library only**; no installs.
- macOS 15.5.
- Network: only `boards-api.greenhouse.io`, `api.ashbyhq.com`, `api.lever.co`.
- No model is called by the loop or the check.
- The build was done with Claude Code 2.1.316.

## Exact commands (from a fresh clone)

```bash
cd fall-2026/aditya-h/js2-loop-tools-diff
```
```bash
python3 -m unittest discover -s tests -v
```
```bash
python3 tests/wrong_versions.py
```
```bash
python3 -m jobwatch2 run
```
```bash
python3 check_run.py runs/<run-id>
```

- **The tests:** 55 of them.
- **`tests/wrong_versions.py`:** plants each of the gate's 3 wrong versions into a temporary copy of the code and shows the tests fail on each.
- **`python3 -m jobwatch2 run`:** one live loop over `boards.json`. It prints per-board results, the trace path and the report path. The exit code is 0 for finished, 1 for incomplete, 2 for budget-exhausted and 3 for error.
- **`check_run.py`:** the independent check of one run. It exits 1 when it judges the run **wrong**.
- **Finished-wrong demo:** `python3 -m jobwatch2 run --boards boards.finished-wrong.json`. That is the same set without the deliberate-failure board.
- **Reset one board's state:** this needs your explicit approval; without the flag it is refused. `python3 -m jobwatch2 reset greenhouse/stripe --approve-reset greenhouse/stripe`
- **Review-packet reproduction:** `python3 review/repro_check_reads_outside.py`. On the accepted code it prints `OK: check refused`.

**Starting from scratch:** the committed `runs/state/` holds the Nov 10 state. Delete `runs/state/` only if you want a fresh baseline; it's your decision, outside the agent.

**Size note:** `runs/` is ~67 MB, because the raw Ashby OpenAI response is ~13 MB per run.

## What ran (all live, 2026-11-09 and 2026-11-10 EST)

| when | command | exit | key result | evidence |
|---|---|---|---|---|
| Nov 9 15:45 | `python3 -m jobwatch2 run` | **incomplete** | baseline of 5 real boards (771 / 676 / 811 / 153 / 304 postings); `stripe-js2-bad` HTTP 404, 1 attempt, counts null | `runs/20261109T204551Z-2ac7e2/` |
| Nov 9 15:46 | `… run --boards boards.finished-wrong.json` | **finished** | Ramp "ok, 1 posting" | `runs/20261109T204623Z-906e94/` |
| Nov 9 15:46 | `check_run.py` on that run | **wrong** | `greenhouse/ramp: finished-wrong`: newest posting 17 days old; Ashby lists 175 | `…906e94/check.md` |
| Nov 10 (Aditya) | review-packet commands | — | tests failed before each patch; 55 OK after v2 | `review/` |
| Nov 10 13:47 | `python3 -m jobwatch2 run` | **incomplete** | **second calendar day: 57 new postings**, 1 relevant (Stripe "Product Operations Manager"); the 404 handled again | `runs/20261110T184710Z-df53fd/` |

**Not shown in a live run:** a retry after a real timeout or 5xx, a `budget-exhausted` exit, or a permission denial. None happened. Each is shown only by tests with a fake network (`test_loop.py`, `test_policy.py`).

## Layout

```text
GATE.md                exits, budgets, repeat rule, error policy, permission policy, predicted boundary cases
boards.json            the 7 boards (5 real, 1 deliberate failure, 1 stale) · boards.finished-wrong.json (6)
checks.json            the independent check's thresholds and cross-check sources
jobwatch2/             loop.py (bounded loop, exits, budgets, trace) · policy.py (permission policy)
                       ats.py (3 ATS normalizers) · net.py (the one GET tool) · rule.py · persona.py
check_run.py           independent check (recompute from raw + cross-check suspects)
tests/                 test_policy.py (19 gate cases + edges) · test_loop.py · test_check.py
                       test_review_check_reads.py (review packet) · wrong_versions.py
runs/                  per-run folder: trace.jsonl, raw/, record.json, report.md, check.*; state/ per board
review/                review packet: repro script, step records, REVIEW-PACKET.md
personas/              maya-sehgal.resume.json (fictional)
```

---

## Sign-off — Job-Search Agent 2

*Drafted by Claude Code on 2026-11-10 for Aditya to edit, then sign or withhold.*

**Checked**
- **Exits are honest:** a failed board gives `incomplete` and an exhausted budget gives `budget-exhausted`, never `finished`. Shown by `test_loop.py::WrongVersion1_*` and `Exits`, the live 15:45 and 13:47 runs (`incomplete` with the 404), and `wrong_versions.py` (wrong version 1 caught by 4 tests).
- **No invented values:** a failed board has `null` counts and untouched state (`WrongVersion2_*`, plus the live 404 board).
- **Retries only for transient errors, and only once:** `WrongVersion3_*`. The live 404 was requested exactly once in each run.
- **Budgets match the gate:** `BudgetsMatchGate`, plus request and board-count budget tests.
- **The permission policy:** 19 gate cases predicted before the code, plus 3 extra, in `test_policy.py`; all observed results matched the predictions (POLICY.md).
- **A finished-wrong run is caught:** `test_check.py::test_finished_wrong_answer_is_caught` and the live 15:46 run with its `check.md`.
- **The review change:** `test_review_check_reads.py` (5 tests; 1 + 3 failed before their patch).

**How**
- **By hand:**
  - deciding every gate rule and the review behavior,
  - reading both diffs, and
  - choosing REVISE, then ACCEPT.
- **With tests written before the code:**
  - the gate tests were committed before the implementation (`caa5215` before `9ff7b87`), and
  - the review tests before each patch (`5293ca4` before `1567edd`; `ca8725e` before `a5dc929`).
  - Claude Code drafted the test text; I made the review decisions and ran the review tests myself.
- **By recomputation:** `check_run.py` recomputes counts from the raw files.
- **With Claude's help:** Claude Code wrote all the code, the first-round test code and the docs.

**Not checked**
1. **Real transient failures:** I never saw a live timeout, 5xx or 429, so the retry path is tested only against a fake network.
2. **The seconds budget against a slow live server:** `urllib`'s timeout applies per socket operation, so a server that drips bytes could make one request outlast its share of the 120 s. This is untested.
3. **The wrong-attempt case:** a record could cite the wrong *attempt* file for the right board (review packet, "still miss").
4. **Large-but-wrong boards:** the independent check only suspects small or stale boards.
5. **Each site's terms of use:** beyond using the documented public endpoints, I didn't review them in detail.
6. **Relevance quality:** the rule found 1 relevant posting among 57 new ones. I didn't hand-check the other 56.

**Not claiming**
- That `finished` means correct. The demo shows otherwise.
- That the agent can apply, email, message or log in. It can't; the policy blocks non-GET requests and credential headers.
- That budgets or the policy can be changed at runtime. There is no flag or prompt for that.
- That two days of runs show long-term behavior.

**Signed or withheld:** ____________ (name, date)

## Driver's seat

| Task | Claude should | I should | Why that part stays mine | Evidence |
|---|---|---|---|---|
| Exits, budgets, error and permission policy | probe the boards, draft GATE.md from my answers | decide every rule and limit; approve the gate before any code | The limits encode how much autonomy I grant; a budget changes only by my dated entry. | GATE.md provenance; `2fbfc39` comes before all code |
| The loop and the policy code | write the code and tests from the gate; run the live boards | run the tests myself; decide what counts as failure | A clean exit can be wrong. I have to judge what "finished" proves. | TRACE.md finished-wrong; `check.md` |
| Review: reproduce and test | find and reproduce the defect; draft the test text | **decide the expected behavior** ("refuse and stop"); create and run the test, and watch it fail | The test is the yardstick for Claude's patch. Claude shouldn't define its own pass mark. | `review/01-…`, `5293ca4` |
| Review: decision | patch, name a case the tests still miss | **read the diff; run the suite; REVISE v1, ACCEPT v2** | Accepting code is an authorization. Green tests alone didn't settle it; v1 was green and I still revised. | `review/02-…` ("I feel we should revise our approach"), `review/03-…`, `a5dc929` ("accept it") |
| Publishing | stop and ask | approve every push | Public posting is mine to authorize. | nothing was pushed without my approval |
