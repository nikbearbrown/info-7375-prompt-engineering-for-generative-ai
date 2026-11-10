# Job-Search Agent 2: The Loop, the Tools, and the Diff

INFO 7375 Prompt Engineering for Generative AI, Fall 2026 · Pavithra Prasad (`pavithra-p`) · Assignment JS2

My JS1 agent watched one board. This layer makes it a bounded loop: one run checks five boards on three applicant-tracking systems, under the budgets, exits and permission policy I wrote first in `GATE.md`, and the one change to its relevance rule went through a reviewed diff. The candidate is still the fictional Rohan Mehta. The agent never applies, emails, messages anyone or logs in.

Started from: my own JS1 work, `fall-2026/pavithra-p/js1-contract-and-watch/`. The relevance rule, the résumé check, the persona and the rule's wrong versions were copied unchanged in commit `b1b415f`, with the 173 Pinterest job IDs seen in JS1 carried into the state file. I did not use the Reallocation Engine or Lectern.

## Contents

| Path | What it is |
|---|---|
| `GATE.md` | exits, budgets, repeat rule, error policy, permission policy, wrong versions, the "truth" line. My draft `034c127`, tightened `72cc186`, both before any code |
| `agent/` | `loop.py` (the bounded loop), `policy.py` (the permission policy in code), `tools.py` (the one network tool), `ats.py` (Greenhouse, Lever, Ashby), `check.py` (the independent check), `wrong_versions.py`, `rule.py` and `resume.py` (from JS1), `__main__.py` (commands) |
| `config/` | the board list, the budgets and the allowed hosts. Changing them needs my approval (`GATE.md`) |
| `tests/` | 80 offline tests (list below). Every fixture is labelled CONSTRUCTED |
| `TRACE.md`, `runs/20261110T133054Z/` | the trace of one real run, including the deliberate failure |
| `FINISHED-WRONG.md`, `runs/*WRONG-V3/` | the finished wrong answer and the independent check that catches it |
| `BOUNDARY-TESTS.md` | the permission policy's 23 boundary cases: 18 predicted before the policy code, and 5 I predicted myself before their tests |
| `REVIEW-PACKET.md`, `evidence/review/` | the review of the one change I asked Claude Code to make |
| `evidence/raw/` | every response body, saved before parsing |
| `runs/state/seen_ids.json` | the state file: job IDs seen per board, and a log of the runs |
| `CONTRACT-JS1.md` | my JS1 contract, for the relevance rule this agent still uses: copied unchanged, with one dated JS2 note at the end about year ranges; the file paths inside it refer to the JS1 folder |
| `SOURCES.md`, `FRICTIONAL.md` | what I used and what Claude contributed; my dated log |

## Toolchain

* Python 3.13.1, standard library only. Nothing to install.
* The loop makes no Claude call: each verdict comes from my written rule (a record). Claude Code 2.1.294 wrote most of the code and tests (`SOURCES.md`).
* Tested on macOS (Darwin 25.5), and from a fresh clone of this branch (69 tests at that point) with both real runs' checks passing again.

## The boards

| Board | System | Host |
|---|---|---|
| pinterest | Greenhouse | `boards-api.greenhouse.io` |
| figma | Greenhouse | `boards-api.greenhouse.io` |
| spotify | Lever | `api.lever.co` |
| ramp | Ashby | `api.ashbyhq.com` |
| no-such-board | Lever | `api.lever.co`, fails on purpose (the name does not exist) |

Each is a public job-board endpoint, read with one GET per board per run.

## Commands

Run everything from this folder.

```bash
python3 -m unittest discover -s tests
```

```bash
python3 -m agent watch
```

`watch` runs the loop once over `config/boards.json`, saves every response in `evidence/raw/`, and writes the trace, the report and the state under `runs/`. It ends with one of `finished`, `incomplete`, `budget-exhausted` or `error`. With the deliberate failure in the board list, a normal run ends `incomplete`.

| Command | What it does |
|---|---|
| `python3 -m agent check runs/<run>` | the independent check: compares a run's report with its saved raw responses. It prints "check passed", "CHECK FAILED" or "NEEDS REVIEW" (suspicious, not proven wrong) |
| `python3 -m agent watch --wrong-version 3` | runs wrong version 3 (labelled `WRONG-V3`, its own state file) for the finished-wrong-answer demonstration |
| `python3 evidence/review/compare_rule_versions.py` | the rule before and after the reviewed change, on every job of run 1 (reads the old rule with `git show`, so run it from a clone) |

## What ran

All times are UTC, in my own terminal unless noted.

| When | What | Result | Evidence |
|---|---|---|---|
| 2026-11-09 | `GATE.md`, my draft, then the tightened version | before any code | `034c127`, `72cc186` |
| 2026-11-09 | 18 boundary predictions, before `agent/policy.py` existed | | `5d145ac` |
| 2026-11-09 | The loop, the policy, the check and their tests (Claude Code) | 18 of 18 boundary tests as predicted | `485e75f`, `BOUNDARY-TESTS.md` |
| 2026-11-10 13:30:54 | Run 1 | `incomplete`: 4 boards checked, `no-such-board` failed (HTTP 404, not retried); 567 jobs, 17 new on Pinterest since JS1 | `TRACE.md`, `runs/20261110T133054Z/` |
| 2026-11-10 13:31:00 and 13:31:22 | Wrong version 3, twice (the second by accident) | ended `finished`; the check failed both runs | `FINISHED-WRONG.md` |
| 2026-11-10 13:36:50 | My year-range test, before the fix (run by Claude Code) | 2 of 4 fail | `a5fc261`, `evidence/review/1-test-before-fix.txt` |
| 2026-11-10 13:46 | The fix (Claude Code), then my review commands | 4 of 4 pass; 6 of 567 jobs change their experience part, no verdict changes; I accepted | `0ecb3d5`, `REVIEW-PACKET.md` |
| 2026-11-10 | A strict TA-style review of my draft (a separate Claude Code agent), then the fixes: the check now fails a `finished` run with a failed or missing board; the seconds budget counts the next request's timeout and any 5xx is retried, as `GATE.md` says; every read goes through the policy | 73 tests pass; the four saved runs' checks give the same results as before | `2382628` |
| 2026-11-10 | A ChatGPT review of the same draft: a single slow request could run past 60 seconds and still end `finished`. Fixed: the run now ends `budget-exhausted` | 74 tests pass; the review's tampered-report probe (run 2 changed to `finished`) now fails the check | `17f4e77` |
| 2026-11-10 | The check flags a board that answers with 0 jobs after having jobs as "suspicious, needs review" (my wording: zero alone does not prove the response is wrong) | the brief's own example, an empty board reported as "no new jobs", is now flagged | `26ec385` and the commit after `898afe3` |
| 2026-11-10 | Boundary cases 19 to 23, predicted by me before their tests existed | 5 of 5 as predicted | `898afe3`, `BOUNDARY-TESTS.md` |
| 2026-11-10 13:56:16 | Run 2 | `incomplete` again, 0 new; the check recomputed the new IDs from run 1's raw files and passed | `runs/20261110T135616Z/` |

No run was seeded. The two wrong-version runs are labelled `WRONG-V3` in every file name. Both real runs were made before the review fixes; those fixes change the check, the seconds budget and the 5xx retry, none of which either run reached.

## Tests (80, offline)

* `test_policy.py` (23): the boundary cases in `BOUNDARY-TESTS.md`, in the same order.
* `test_loop.py` (22): each exit; a 404 asked for once; a failed board never reported as 0 jobs; invalid data a failed board, not an error; a crash reported with the last action; one retry after a timeout, a 429 or any 5xx, none after another 4xx; the request, board and seconds budgets, the seconds budget counting the next request's timeout, and a request that runs past it ending the run `budget-exhausted`; a repeated board stops the loop; a host off the allow-list stops it before any request; every attempt in the trace and every body saved; the state unchanged for a failed board; the rule's relevant count.
* `test_wrong_versions.py` (3): each wrong version in `GATE.md` is caught.
* `test_check.py` (5): the independent check passes a true report and recomputes new IDs; it fails a report whose counts do not match the raw file, a `finished` report with a failed board, and a report that drops a configured board; it flags a board that answers with 0 jobs after having jobs as "suspicious, needs review".
* `test_ats.py` (6): the three systems' answers become jobs the rule can read; a Lever 404 body is bad data, not an empty list; escaped titles are shown as written.
* `test_year_ranges.py` (4): my review-packet test.
* `test_rule.py` (13) and `test_resume.py` (4): carried from JS1.

During the build, one real bug turned up: on macOS a saved file's path (`/var/...` against `/private/var/...`) did not match the project folder, so the first trial stopped with `error`. The loop's catch-all reported it instead of hiding it, and it was fixed in `agent/loop.py`. No test was weakened to get a green result.

## Credits

The relevance rule, résumé check and persona come from my JS1 folder, and the persona from the Reallocation Engine example `search/examples/aarav-patel/` (commit `d08afdd`, renamed in JS1). Claude Code wrote most of the code and tests and the first drafts of these documents. `SOURCES.md` says exactly what came from where.

## Sign-off — Job-Search Agent 2

```text
Checked:      1. The exits and the error policy: in run 1 and run 2, no-such-board was asked for
                 once, failed with HTTP 404, got no job count, and both runs ended incomplete
                 (TRACE.md, runs/20261110T133054Z/, runs/20261110T135616Z/).
              2. The finished wrong answer is caught: wrong version 3 ended finished, and
                 python3 -m agent check failed it from the saved 404 (FINISHED-WRONG.md).
              3. The new jobs: I recomputed run 1's 17 new Pinterest jobs from its saved response
                 and the 173 IDs carried from JS1 (a one-line Python set difference) and got the
                 same 17 IDs as the report. After run 2, the check recomputed the new IDs from
                 run 1's raw files and agreed (0 new).
              4. The permission policy: 23 boundary tests, all as predicted (BOUNDARY-TESTS.md):
                 test_01 to test_18 against predictions Claude Code drafted and I checked, and
                 test_19 to test_23 against predictions I wrote myself before the tests existed.
              5. The year-range fix: my test (test_year_ranges, cases a to d) failed 2 of 4 before
                 the fix and passed 4 of 4 after; compare_rule_versions.py showed 6 of 567 jobs
                 changed their experience part and no verdict changed.
              6. The full suite: 68 tests passed in my terminal after the fix. Twelve more
                 (escaped titles, the review fixes, the empty-board flag and cases 19 to 23) came after.
How:          By hand (1, 2: reading the reports and the check's output), by recomputation (3, 5),
              by a test I wrote before the fix (5), and with Claude's help: Claude Code wrote the
              loop, the policy, the check and every other test. I ran them in my own terminal on
              2026-11-10.
Not checked:  1. A real timeout, 429 or 5xx. No board failed that way, so the retry was checked only
                 on constructed answers (test_timeout_is_retried_once_after_the_wait,
                 test_5xx_twice_fails_after_one_retry, test_429_is_retried).
              2. The request, board and seconds budgets in a real run. Both real runs used 5 of 10
                 requests and about 3 of 60 seconds; the limits were reached only in tests.
              3. The repeat rule and a real redirect in a real run: only in tests
                 (test_repeated_board_stops_with_error, test_07_redirect_off_allow_list_refused).
              4. A board that answers HTTP 200 with an empty job list on its very first run. With an
                 earlier saved response the check flags it as "suspicious, needs review"; without
                 one there is nothing to compare with (FINISHED-WRONG.md).
              5. Years written as "2 to 4 years" or "3 yrs": the rule still misreads them
                 (REVIEW-PACKET.md, section 8).
              6. Each board's terms of use in full. The agent makes one GET per board per run to
                 the public posting endpoints.
Not claiming: that the agent finds every relevant job (five boards only); that "0 relevant" means
              nothing is worth applying to; that the policy protects anything the agent does not
              route through agent/policy.py; that the reviewed fix handles every way years are
              written.
Signed or withheld: Signed, Pavithra Prasad, 2026-11-10
```

## Driver's seat

| Task | What Claude should do | What I should do | Why that part stays mine | Evidence |
|---|---|---|---|---|
| The gate | tighten my draft into rules a test can check | write the draft, decide the budgets, exits and permissions | the loop obeys these rules, so they are my decision | `034c127` (my draft) → `72cc186` |
| The boundary predictions | draft 18 cases' expected results before the policy code | check them, and predict 5 more myself before their tests | a prediction made after the run proves nothing | `5d145ac` before `485e75f`; `898afe3` before tests 19 to 23 |
| The loop | write the loop, the policy, the check and the tests | run it for real and read what it reports | only a real run shows the real failure | `runs/20261110T133054Z/`, `runs/20261110T135616Z/` |
| The finished wrong answer | write the independent check from the raw files | run the wrong version and see the check fail it | the agent's own report cannot catch its own mistake | `FINISHED-WRONG.md` |
| The review test | type my cases as code | choose the cases and the expected answers before the fix | the test is what the fix is judged against | `a5fc261` before `0ecb3d5` |
| The review decision | write the patch, show the diff and its effect on real jobs | write the request, run the commands, accept or reject | accepting a change to my rule is my call | `REVIEW-PACKET.md`, `evidence/review/6-commands-i-ran.txt` |
