# Job-Search Agent 2: The Loop, the Tools, and the Diff

This layer turns my Job-Search Agent 1 watcher into a **bounded loop** for a fictional persona, Jack Spencer. The loop watches **three real boards on three applicant-tracking systems**, plus one board that fails on purpose. A **permission policy enforced in code** governs everything the loop does, and it ends in one of four **explicit exits**.

The rules were written first: `GATE.md`, committed alone before any code (`ea61db0`, 2026-11-10 19:38 ET).

**Started from:** my own JS1 code. The rule judge (`agent2/rule.py`) and the persona validator (`agent2/resume.py`) were copied from JS1 unchanged, apart from one type hint. The loop, the three providers, the policy, the transports, and the independent check are new. I did not use the Reallocation Engine's ATS providers or Lectern.

## Language and toolchain

- **Python 3.12.10**, standard library only. There is nothing to install.
- **Tests:** `unittest`.
- **Network:** public read-only JSON endpoints on `boards-api.greenhouse.io`, `api.lever.co`, and `api.ashbyhq.com` only.
- Developed on Windows 11. Test B10 creates a Windows junction there and a symlink on POSIX.
- No Claude call is part of the agent in JS2. Claude Code was my coding assistant (see SOURCES.md).

## Exact commands (from this folder)

```bash
python -B -m unittest discover -s tests -t . -v              # 35 tests, no network
python -B -m agent2.run --resume data/resume_jack_spencer.json  # one live run over the 4 boards
python -I -B scripts/check_run.py out/runs/<run_id>.json       # independent check of any run
python -B scripts/demo_finished_wrong.py out/runs/20261111T004409Z.json   # SEEDED finished-wrong-answer demo
python -B -m agent2.run --resume data/resume_jack_spencer.json --reset-state                       # refused: needs approval
python -B -m agent2.run --resume data/resume_jack_spencer.json --reset-state --approve reset-state # allowed
```

**From a fresh clone:** the committed `out/state/seen_ids.json` makes the next live run compare against my last run. To start from a baseline, reset the state with the approved command above.

## What ran (2026-11-10, ET)

| Time | What | Result | Evidence |
|---|---|---|---|
| 19:43 | **Live run 1** (4 boards) | exit `incomplete`: the deliberate 404 was **not retried** and was marked `failed_not_found`. figma 144, spotify 86, snowflake 373 jobs, all baseline. 4/10 requests in 1.8 s. Independent check **PASS** | `out/runs/20261111T004357Z.txt` (the trace), `out/evidence/20261111T004357Z/` |
| 19:44 | **Live run 2** | `incomplete`; 0 new on every board (12 s after run 1). Check **PASS** | `out/runs/20261111T004409Z.txt` |
| 19:44 | **Finished-wrong-answer demo (SEEDED)** | Wrong version W-a: `finished`, "0 new", and the independent check **FAILS** it. Real version: `incomplete` / `suspicious_empty`, check **PASS** | `out/demo_finished_wrong/DEMO_OUTPUT.txt` |
| 19:57 | **My test run before the patch** | 35 tests, 2 failures (the review tests), all 15 boundary tests as predicted | `review/test_run_1_before_patch.txt` |
| 20:00 | **My test run after the patch** | 35 tests OK | `review/test_run_2_after_patch.txt` |
| 20:11 | **My live check after the patch** | `incomplete` as before; check **PASS** | `review/live_run_after_patch.txt`, `out/runs/20261111T011106Z.txt` |

### The loop (GATE.md §§2–5)

- **Exits:** `finished`, `incomplete`, `budget_exhausted`, `error`. `finished` requires every planned board to succeed.
- **Budgets:** 5 boards, 10 requests (retries count), 60 s, with the 1 s floor from the dated GATE.md entry.
- **Repeat rule:** an identical GET is refused and logged as `repeat_refused`.
- **Error policy:**
  - a 404 is not retried;
  - a timeout, connection error, or 5xx is retried once;
  - an empty response or malformed JSON is `suspicious_empty` or `malformed`, never "no new jobs";
  - if every board fails, the run exits `error` and escalates to me.
- Every step goes into the trace with a sequence number and a time.
- Tests: `tests/test_loop.py`.

### The finished wrong answer

The demo is **SEEDED**. A real board could not be made to go empty, so figma's response was replaced with `{"jobs": []}`, while spotify and snowflake used real saved responses.

The wrong version W-a accepts the empty list and reports `finished` with "0 new". That is a clean exit, and it is wrong. The **independent check** `scripts/check_run.py` does not trust the report:
- it imports nothing from `agent2`;
- it recounts jobs from the saved raw bytes and compares them with the state snapshot from before the run;
- it printed `FAIL: greenhouse:figma: reported ok with 0 jobs, but the board had 144 before. An empty board is not 'no new jobs'.`

The demo also runs as a test: `tests/test_wrong_versions.py`.

### The permission policy in code

`agent2/policy.py` enforces the policy. Every request and every write goes through it. There are 15 boundary cases, B01–B15. Their predicted outcomes were committed **before** the tests first ran (`ca47a41`). I reviewed them, then ran the tests myself, and all 15 matched: see `POLICY_TESTS.md`.

### The review packet

See `REVIEW_PACKET.md`. The change was defect (A), a time-budget overrun:
- the defect was reproduced by my own run, using a test written before the patch (`100ac74`);
- the patch is `4c70674`: one file, +4/−2;
- my decision: **accept**, with evidence.

## Files

- `GATE.md`
- `agent2/`:
  - `policy.py`: the permission policy
  - `fetch.py`: the transports and the redirect guard
  - `providers.py`: Greenhouse, Lever, and Ashby
  - `loop.py`: the bounded loop
  - `run.py`: the driver
  - `config.py`: boards and budgets
  - `rule.py`, `resume.py`: carried over from JS1
- `scripts/check_run.py` (the independent check), `scripts/demo_finished_wrong.py`
- `tests/`
- `POLICY_TESTS.md`, `REVIEW_PACKET.md`, `review/`
- `out/`: the agent's only writable folder:
  - `evidence/`: raw responses
  - `runs/`: traces
  - `state/`
  - `demo_finished_wrong/`
- `data/resume_jack_spencer.json`: the fictional persona
- `SOURCES.md`, `FRICTIONAL.md`

## Sign-off: Job-Search Agent 2

> Claude Code drafted these words at my request from the commits and saved outputs. I sign only after reading every line.

**Checked:**
- **The permission policy refuses what GATE.md §6 refuses.** All 15 boundary cases matched predictions committed before the first run (`tests/test_policy_boundaries.py`, B01–B15).
- **Exits, budgets, the repeat rule, and the error policy.** `tests/test_loop.py`: 14 tests, including "404 not retried", "a retry counts against the budget", and "one failed board means `incomplete`, not `finished`".
- **Both wrong versions are caught.** W-a is caught by the independent check and W-b by the real path check (`tests/test_wrong_versions.py`).
- **The deliberate failure was handled without inventing a value.** In live runs 1 and 2 and the post-patch live check, the 404 board shows `failed_not_found`, has no postings, and the exit is `incomplete`.
- **The time budget cannot be overrun by a request's timeout** (`tests/test_review_time_budget.py`).

**How:**
- **By hand:** I reviewed the 15 boundary predictions before the first run, and I read the patch diff.
- **By a test I wrote before reading Claude's code:** none. The review-packet test was drafted by Claude **from my spec**, and it was committed and failed in my run before the patch.
- **By running the tests myself:** before and after the patch (`review/`).
- **By recomputation:** `scripts/check_run.py` recounts every run from its raw evidence. Claude wrote it, and I ran it on my live check.
- **With Claude's help:** all of the code, the tests, GATE.md's wording (my decisions, accepting its suggestions), and these documents.

**Not checked:**
- **A real transient failure.** No live run hit a timeout or a 5xx, so the retry path ran only against fake transports.
- **A real empty board.** The finished-wrong-answer demo is SEEDED.
- **A real `budget_exhausted` run.** Budgets were reached only in tests.
- **A slow-drip server** that keeps one request past the budget (REVIEW_PACKET.md §6).
- **A POSIX symlink for B10.** On my machine it ran as a Windows junction only.
- **Defect (B)**, the non-atomic state write. It was found and left unfixed.
- **The JS1 rule's verdicts on Lever and Ashby postings.** No run produced a new posting to judge.
- **A line-by-line review of all the code.** I read the patch diff, not every file.

**Not claiming:**
- That the agent finds good jobs.
- That three boards represent the job market.
- That the independent check catches every wrong answer. It checks counts, ids, hosts, and exits, not content.
- That the demo's empty board happened for real.

**Signed or withheld:** ____________ (Akshit Verma, date: to sign after review)

## Driver's seat

| Part | What Claude did | What I did | Why that part stays mine | Evidence |
|---|---|---|---|---|
| The gate (GATE.md) | proposed every rule as a numbered suggestion | accepted each one ("Okay"), before any code | The rules define what counts as a correct run. Whoever writes them sets the standard the code is judged by. | `ea61db0`; the "Provenance" line in GATE.md |
| The loop | wrote the loop, the providers, and the tests | ran the tests and the live check myself | I'm the one who reports a run's exit to anyone else, so I need to have seen it run. | `review/` |
| Permission predictions | derived the 15 predictions from GATE.md | reviewed them ("ok") before the first run, then ran the tests | A prediction is a claim made before the evidence. Only I can say I made it before looking. | `ca47a41` (before the run); POLICY_TESTS.md results |
| The review: the spec and the test | found two defect candidates; drafted the test from my spec | chose (A), confirmed the spec, and ran the test to see it fail | The spec says what "fixed" means. If Claude also chose that, it would be grading its own patch. | `100ac74` committed before `4c70674` |
| The review: the decision | wrote the patch and laid out the evidence | read the diff, ran the commands, and decided "accept" in my own words | Accepting a change is accepting responsibility for it. | REVIEW_PACKET.md §§4–5 |
| Sign-off | drafted the words | sign or withhold | Only I can be held to what I say I checked. | this section |

> The "why" column was drafted by Claude Code at my request.
