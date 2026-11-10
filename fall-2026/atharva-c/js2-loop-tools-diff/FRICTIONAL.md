# Frictional

<!-- Dated entries, in my own words, written the same day. -->

## Nov 8, 2026

* **What I got wrong at first:** I initially defined `finished` in a way that would have counted runs that returned suspicious results, zero jobs, or even applied to jobs as successes. My early drafts were full of bracketed alternatives and invented details—like paginating endpoints and retrying 429 rate limits—which the review flagged for not reflecting the actual agent.
* **What I changed and why:** In commit `777cef4`, I locked down `GATE.md` before writing code in `agent/`. I narrowed `finished` to require at least one job so empty boards trigger `incomplete`, since an empty response cannot distinguish an empty board from an archived one or a broken API. I rewrote the explanation for the 15-request budget to match reality, dropping the pagination and 429 claims so it strictly reflects 1 request per board, up to 1 retry, and spare capacity. I also specified that only I change these limits by committing edits to `GATE.md`.
* **What Claude did / what I accepted:** I made all the core operational decisions: the two systems (Greenhouse + Lever), the budget numbers, the single-retry rule, treating empty boards as incomplete, requiring `--approve`, and going with Option A for `out/seen.json`. Claude asked the guiding questions, caught inconsistencies and padded text in my drafts, and synthesized a few sentences directly from my choices, which I kept as written (including the other-4xx bullet, the out/seen.json sentence, the `--approve` sentences, and the exception in the error exit). Claude also caught the contradiction between the strict "writes only in out/" rule and modifying protected files, which led me to add the explicit `--approve` exception.
* **What’s still open:** Selecting and verifying 3 real boards plus 1 deliberately bad board to test the 404 path, and writing tests for the 2-second retry wait, which hasn't been tested yet.
* **Reference commit:** `777cef4`

## Nov 8, 2026 (Step 6)

* **What happened:** I ran the boundary test suite locally against `agent/policy.py`, and all 12 of 12 tests passed on the first run. The complete output log is saved in `evidence/policy-tests-20261108.txt`, matching policy commit `f357831`.
* **What Claude did / what I accepted:** Claude generated the initial implementations for `agent/policy.py` and `tests/test_policy.py` based on the predicted cases in my boundary table, then filled in the `Actual Result` and `Pass/Fail` columns directly from the test run results in my evidence file.
* **What's still open:** These unit tests verify that the policy functions raise the expected exceptions, but the "run exits error" behavior—where a policy violation actually halts the entire agent loop and writes the fatal exit report—still needs to be verified during the Step 7 loop integration tests.
* **Reference commit:** `f357831`

## Nov 8, 2026 (Step 7 — Loop Implementation & First Live Run) (written Nov 9)

* **What happened:** Claude wrote all of `agent/loop.py`, `budget.json`, and `tests/test_loop.py`. I ran the test suite locally (29 tests total: 12 policy tests and 17 loop tests), and all 29 passed. Claude ran the first live run (`run-20261109-041358Z`, UTC timestamp for 11:14 PM Nov 8 my time) against our 4 configured boards. I inspected the generated trace log to verify our 404 handling: the fake board recorded exactly 1 attempt, performed no retries, and listed no job count, while the 3 real boards succeeded and saved their raw payloads. I then copied the run folder into `evidence/`.
* **Friction & What's open:** Claude's first mutant for WRONG_VERSIONS #12 (checking time budget only at the end) wasn't caught by our tests because elapsed time is checked in two places. Deciding whether to set an explicit per-request timeout (10 seconds) remains open to add to `GATE.md`.
* **What Claude did / what I accepted:** Claude wrote the loop, budget configuration, and loop test suite. I verified the behavior by running the tests to evidence, reviewing the trace output for the deliberate 404 failure, and verifying the exit status was `incomplete`.
* **Reference commit:** `4369abf`

---

## Nov 9, 2026 (Review Packet, Budget Mislabel Bug, & Finished Wrong Answer Demo)

* **What happened:**
  1. For the review packet, I manually labeled the 5 real Wealthfront postings and picked the extra test cases. I initially judged "react to new insights", "go-to designer", and lowercase "go" as real skills, but re-evaluated and corrected them to false positives after Claude challenged the reasoning. Claude converted my labels into `tests/test_skills.py` (failing with 7 failures in `e5a4ebc`). Claude then provided the patch in `agent/skills.py` (`80e4fa1`), which I reviewed and accepted with its known trade-offs (missing "Go-based" and all-caps "REACT"). I ran the full test suite green, re-ran `reproduce_skills`, and confirmed the 3 real engineering roles remained while the 2 false matches were gone.
  2. I ran the second live run on a fresh day, followed by a budget-exhausted demonstration with a lowered request limit.
  3. Claude wrote `naive_demo.py`, `independent_check.py`, and the seeded input. I ran all three commands for the finished-wrong-answer demo; the naive loop marked the run finished, and the independent check flagged the dropped count by printing `"FINISHED WRONG ANSWER… robinhood dropped from 153 to 0"`.
* **Friction & The Real Bug Found:** During the budget-exhausted run, the loop correctly exited as `budget-exhausted`, but the summary report mislabeled Wealthfront as "stopped mid-board" and claimed 3 boards were used, even though zero requests had actually been dispatched to Wealthfront. I didn't spot this mislabel myself—Claude caught it in the terminal output I provided. Claude wrote the failing regression test and the patch to record untouched boards as "not reached" and accurately report 2 boards used. I re-ran the demo to confirm the fix produced "not reached" and 2 boards used.
* **What Claude did / what I accepted:** Claude turned my skill labels into tests, wrote the skill patch, spotted the budget-exhausted reporting bug, wrote the loop bug fix, and wrote the naive demo scripts. I evaluated the skill patch trade-offs, ran the Nov 9 live run, ran both demo commands, and re-ran the fixed demo to verify the report output.
* **Reference commits:** `e5a4ebc` (RED skill tests), `80e4fa1` (skills patch), `f982c6a` (reproduction evidence), `47a5e5d` (second live run & RED bug test), `27483af` (budget mislabel fix), `b166b17` (finished wrong answer demo)
