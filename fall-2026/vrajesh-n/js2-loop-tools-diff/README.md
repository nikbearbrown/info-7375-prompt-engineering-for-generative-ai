# Early Bird - Job-Search Agent 2: The Loop, the Tools, and the Diff

Vrajesh N. · INFO 7375 Fall 2026 · Chapters 4-6

**Starting point:** my JS1 agent ([`../js1-contract-and-watch/`](../js1-contract-and-watch/), commit d19465d). `rule.py`, `validate.py` and `resume.py` are copied unchanged (byte-identical, checked with `cmp`). JS1's single-board fetch and watch are replaced by a bounded loop over ten boards on three ATS platforms, with every network and disk action going through a permission policy in code.

| File | What it is |
|---|---|
| [GATE.md](GATE.md) | exits, budgets, repeat rule, error policy, permission policy, boundary cases B1-B16, wrong versions. Committed alone, before any code (`6a2e07e`) |
| `earlybird/loop.py` | the loop: decide → fetch → parse → record → next, with four designed exits |
| `earlybird/gate.py` | budgets (12 boards, 15 requests, 180 s); a run may lower them, never raise them |
| `earlybird/policy.py` | the permission policy: host allow-list, https/GET only, readable and writable folders, approval for the board list |
| `earlybird/tools.py` | the only code that touches the network or the disk: policy, budget, repeat rule, error policy, trace |
| `earlybird/boards.py` | one parser per ATS (Ashby, Greenhouse, Lever), normalized to the field names JS1's rule reads |
| `earlybird/check.py` | the **independent check**: recounts the raw files with its own code; imports only `json` and `pathlib` |
| `config/boards.json` | the 10 boards (9 real + 1 deliberately bad). Changing it needs a typed `yes` |
| `tests/` | 61 tests: `test_js2.py` (loop, budgets, B1-B16, wrong versions, check), `test_review_r3.py` (the review fix), `test_js1_carryover.py` (rule, validator, resume) |
| `tests/wrong_versions.py` | the 5 wrong implementations from GATE.md |
| `experiments/finished_wrong.py` | the finished-but-wrong demonstration |
| [review/REVIEW-PACKET.md](review/REVIEW-PACKET.md) | Chapter 6 review of one Claude Code change, with evidence files |
| `data/raw/` | every raw response: `2026-10-14/`, `2026-10-23/` (fetched by my pitch-film probe, same bytes as JS1), `2026-11-01/` (fetched by this agent, plus the saved 404 body) |
| `data/state/` | `seen.json` (after run1 + run2), `demo-budget.json`, `after-fix.json` |
| `reports/` | one `.md`, `.json` and `-trace.jsonl` per run |
| [SOURCES.md](SOURCES.md) · [FRICTIONAL.md](FRICTIONAL.md) | who did what · my honest log |

## Language and toolchain
- **Python 3.13.3**, standard library only (no `pip install`). No Claude call anywhere in the JS2 agent.
- Tested on Windows 11 (Git Bash and PowerShell). Commands below use forward slashes.
- `data/raw/2026-11-01/` is 37 MB, because Greenhouse sends full descriptions with `?content=true`.

## Exact commands (from a fresh clone, inside this folder)
```bash
# 1. tests: no network. Expected: Ran 61 tests ... OK
python -m unittest discover -s tests -v

# 2. replay both saved days into a fresh state file (no network; leaves the submitted state alone)
python -m earlybird run --replay 2026-10-23 --label repro-day1 --state data/state/repro.json --only ashby:commure,greenhouse:stripe,greenhouse:figma,greenhouse:databricks,lever:palantir
python -m earlybird run --replay 2026-11-01 --label repro-day2 --state data/state/repro.json
#    expected day 2: 7 / 91 / 17 / 69 / 6 new on commure / stripe / figma / databricks / palantir,
#    4 baselines, stripe-typo ERROR "no saved response for this day", exit incomplete
python -m earlybird check --trace reports/repro-day2-trace.jsonl --state data/state/repro.json   # verdict: PASS

# 3. the finished-but-wrong demonstration and the independent check that catches it
python experiments/finished_wrong.py

# 4. budgets: lowering works, raising is refused
python -m earlybird run --replay 2026-11-01 --label repro-budget --max-requests 3 --state data/state/repro-budget.json   # exit budget-exhausted
python -m earlybird run --replay 2026-11-01 --label x --max-requests 20                                                 # REFUSED

# 5. the board list needs a typed yes
python -m earlybird boards list
python -m earlybird boards add lever someboard      # type anything but "yes" and nothing changes

# 6. a live run (needs network; writes data/raw/<today>/)
python -m earlybird run --live --label my-live-run --state data/state/repro.json
```
In a replay, the deliberately bad board has no saved response, so it ends `error: no saved response for this day`. The real 404 is in run2-live below.

## What ran (2026-11-01)

| Run | Source | Exit | What it shows |
|---|---|---|---|
| [run1](reports/run1-2026-10-23-replay-baseline.md) | **replay** of the 10-23 responses, 5 boards | `finished` | baseline: 81 / 726 / 141 / 898 / 308 postings, 0 new |
| [run2-live](reports/run2-live.md) | **live**, all 10 boards, 00:09 EDT | `incomplete` | the deliberate 404; 190 new postings on the 5 boards with a baseline; 4 new baselines; **the R3 defect** (0 relevant on Greenhouse) |
| [demo-finished-wrong](reports/demo-finished-wrong.md) | replay 10-23 with **deliberate wrong version 1** | `finished` (wrong) | Palantir reported as 0 postings; the independent check says FAIL: raw file holds 308 |
| [demo-budget-exhausted](reports/demo-budget-exhausted.md) | replay 11-01, requests lowered to 3 | `budget-exhausted` | stops before request 4; lists the 7 boards not attempted |
| [review-after-fix-day1/2](reports/review-after-fix-day2.md) | replay 10-23 then 11-01, patched code | `finished` | same 190 new postings; Greenhouse relevant 0 → 4 |
| my review run (11-10) | replay 10-23 then 11-01, **run by me** | `finished` | same numbers; my pasted output in [review/6-my-run-2026-11-10.txt](review/6-my-run-2026-11-10.txt) |
| [review-revision-day1/2](reports/review-revision-day2.md) | replay, after **my revision** (11-10) | `finished` | 119 postings re-classified; this week's 4 relevant unchanged |

### Trace with the deliberate failure (run2-live, last three events)
```
37 greenhouse:stripe-typo  decide  board 10/10: fetch greenhouse board            requests 9/15
38 greenhouse:stripe-typo  fetch   attempt 1 -> error, http 404, "4xx: retrying cannot fix it"
                                   raw_path data/raw/2026-11-01/greenhouse_stripe-typo.error.txt   requests 10/15
39 exit  status incomplete, not_attempted []                                       seconds 9.1/180
```
Error policy shown without inventing values: one request, no retry, the 404 body is saved (`{"status":404,"error":"Job not found"}`), the board's count is `null` in the JSON and "error" in the report (never "0 new"), it gets no seen-state, and the other 9 boards still ran. The independent check on run2-live recounted all 9 raw files: PASS.

### Finished, but wrong, and caught by something other than the agent
`python experiments/finished_wrong.py` ([console output](reports/demo-finished-wrong-console.txt)):
```
lever:palantir   ok  0 postings
exit: finished   <- looks clean
BAD lever:palantir   trace 0 | raw file 308
PROBLEM: lever:palantir: trace claims 0 postings, but data/raw/2026-10-23/lever_palantir.json holds 308
verdict: FAIL
```
The check is independent because it shares no code with the loop or the parser (a test asserts that `check.py` imports only `json` and `pathlib`), it reads the raw bytes rather than the agent's report, and it counts with a different method (`len()` of the top-level list or `jobs`, with no field access). Its limit: it only catches count errors. A parser that kept the right number of postings but scrambled their fields would pass it.

## Permission policy: boundary cases (expected written in GATE.md before the tests)

| # | Request | Expected | Result (test) |
|---|---|---|---|
| B1 | fetch an allowed Greenhouse URL | allowed | allowed (`test_B01`) |
| B2 | host `evil.example.com` | refused | refused (`test_B02`) |
| B3 | `api.lever.co.evil.com` (allowed host as prefix) | refused | refused (`test_B03`) |
| B4 | plain `http://` | refused | refused (`test_B04`) |
| B5 | `me:pw@` credentials in URL | refused | refused (`test_B05`) |
| B6 | write `reports/run.md` | allowed | allowed (`test_B06`) |
| B7 | `reports/../GATE.md` | refused | refused (`test_B07`) |
| B8 | `reports-evil/x.md` sibling prefix | refused | refused (`test_B08`); wrong version 3 lets it through |
| B9 | `reports/link/x.md`, link → outside | refused | refused (`test_B09`). This machine cannot make symlinks without Developer Mode, so the test ran with a **directory junction**, which escapes the same way |
| B10 | read `config/boards.json` | allowed | allowed (`test_B10`) |
| B11 | read outside the project | refused | refused (`test_B11`) |
| B12 | write board list, no approval | refused | refused (`test_B12`) |
| B13 | write board list, typed `yes` | allowed | allowed (`test_B13`, `test_boards_cli_approval`) |
| B14 | typed `y`, empty, `Yes please` | refused | refused (`test_B14`) |
| B15 | write `data/state/seen.json` | allowed | allowed (`test_B15`) |
| B16 | `POST` to an allowed host | refused | refused (`test_B16`) |

All five wrong versions are caught: `test_wrong_version_1` to `_5`. Separately, Claude broke the real code three ways (string-prefix path check, retry on every HTTP error, budget off by one). Each mutant failed exactly the two matching tests, and the code was restored.

## Sign-off - Job-Search Agent 2
> Checked / How / Not checked were drafted by Claude from what was actually run, and I read them. **Why I sign** and **Not claiming** are my own words (2026-11-10), placed verbatim.

- **Checked:**
  - the loop reaches each of the four exits: `finished` (run1), `incomplete` (run2-live, `test_404_*`), `budget-exhausted` (demo, `test_request_budget_*`, `test_board_budget`, `test_seconds_budget`), `error` (`test_permission_refusal_stops_whole_run_with_error`)
  - error policy: 404 not retried; timeout and 5xx retried once with a 5 s wait; a wrong shape is an error, not an empty board (`test_404_*`, `test_timeout_*`, `test_5xx_*`, `test_wrong_shape_*`)
  - repeat rule (`test_repeat_rule_*`); budgets only lowered (`test_budget_can_be_lowered_never_raised`, `test_cli_refuses_a_raised_budget`)
  - B1-B16 and the board-list approval (`test_B01`-`test_B16`, `test_boards_cli_approval`)
  - all 5 wrong versions caught; parse counts equal the saved responses for all 3 ATS (`test_parse_counts_match_saved_responses`)
  - the independent check passes a correct run and fails wrong version 1 (`test_independent_check_*`, `test_wrong_version_1_*`)
  - the R3 fix on real Greenhouse data (`tests/test_review_r3.py`)
- **How:** GATE.md was written and committed before code. Claude wrote the code and tests and ran them (61 passed). On 2026-11-10 I ran the review tests (4 ok), the full suite (57 ok, before my revision) and the two-day replay myself; my terminal output is saved verbatim in `review/6-my-run-2026-11-10.txt`. After my revision I ran the full suite again myself: 61 ok (`review/10-my-full-suite-2026-11-10.txt`). Run counts can be recomputed from `data/raw/` with the replay commands.
- **Not checked:**
  1. A real timeout or 5xx. Retry is tested only with a CONSTRUCTED fake network; no board timed out in a real run.
  2. Whether "new" is right beyond counts. The check recounts postings but does not recompute new ids against the previous state.
  3. The location rule beyond the 2026-11-01 strings. After my revision, lower-case `'sf, nyc'`, `'USCA'` and `'AMER'` are still missed and bare `'Remote'` is unknown (review packet step 7). The city list covers only well-known US tech cities.
  4. Symlinks on Linux/macOS. B9 ran only with a Windows junction on this machine.
  5. Greenhouse, Lever and Ashby terms of use beyond reading the public job-board APIs at one request per board per run.
- **Not claiming (my words):** "I do not claim that these 5 jobs are worth applying to, that every location is classified correctly, or that a "finished" run is correct. The agent only applies its rules and produces candidates for human review."
  [Claude's note: nor that these 9 boards stand for the market. The agent does not apply, email, message, or log in anywhere, and has no tool that could.]
- **Why I sign (my words):** "I sign because my own run found 5 relevant jobs, including 4 Greenhouse jobs that were previously rejected. The revision tests failed before the fix and passed afterward, and the full recorded test suite passed 61 tests."
- **Signed or withheld:** Signed: Vrajesh Nasit - 11/10/2026 - 9:45 PM

## Driver's seat

| Part | Claude did | I did | Why it stays mine | Where it shows |
|---|---|---|---|---|
| GATE.md | asked multiple-choice questions using live board counts and 404s; drafted exits, repeat rule, policy, B1-B16, wrong versions | picked the 9 boards, the budget, the error policy, the approval target and the bad board; raised the budget when it didn't fit; accepted the draft | what the agent may touch and how much it may spend is my call | GATE.md *(chosen 10-31)* marks; my accept note; commit `6a2e07e` |
| The loop and tools | wrote all code and tests; ran runs and mutants | ran the tests and the two-day replay myself on 11-10 and read `reports/my-review-day2.md`; asked for the revision | I have to be able to explain why it stopped | `reports/*-trace.jsonl` |
| Choosing the defect | showed my first pick did not reproduce (0 of 72); named alternatives | switched to the Greenhouse location bug | which bug is worth reviewing is a judgment about my agent | REVIEW-PACKET.md header |
| The review decision | reproduced it, wrote the test first, patched, audited 740 strings | ran the commands myself; accepted, revised or rejected | the patch changes which jobs reach me | REVIEW-PACKET.md steps 5-6 |
| Sign-off | drafted it | *(read, edit, sign or withhold)* | my name goes on it | this section |
