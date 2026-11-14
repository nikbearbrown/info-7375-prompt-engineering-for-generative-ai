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

## Nov 10, 2026

* **What happened:**
  1. Closed three final audit gaps across `SIGNOFF.md` and `REVIEW_PACKET.md`: added the explicit "How" verification breakdown (distinguishing checks performed by hand, by tests written before code, by raw recomputation, and with Claude's help), expanded the driver's seat matrix with "What Claude should do" and "What I should do" columns, and documented the exact edge cases our test suite still misses ("Go build something people love" and "Go-based").
  2. Prepared the submission branch for the course repository. The commits were applied to a feature branch on my fork (`atharva-js2-loop-tools-diff`) with a pull request targeting `nikbearbrown/info-7375-prompt-engineering-for-generative-ai#43` (`fall-2026/atharva-c: JS2 loop…`). Nothing is merged into the course repo.
  3. Added `COMMIT_MAP.md` to map our local feature branch commit hashes to the corresponding branch commits in the course structure so all evidence and sign-off references remain traceable.
  4. Local commits: `c33b5a8` (the three gap fixes) and `4d00a96` (the `COMMIT_MAP.md` addition). Branch head on the fork is `a86930d`.

* **Friction & What went wrong:**
  1. The initial `git push` was rejected by GitHub because GitHub's "Block command line pushes that expose my email" setting was active. All 22 original JS2 commits were already using my `users.noreply.github.com` address, but the new `COMMIT_MAP` commit created by Claude in the fresh clone picked up my global personal email. Claude updated the clone's `user.email` to the noreply address and recommitted that single commit to unblock the push.
  2. The course GitHub Actions `validate` check failed on the pull request. Rather than ignoring the red check, I asked whether it was caused by my code. Claude read the logs: the failure was caused by another student's file (`shubham-b/.../cli.py` using Python 3.12 syntax on a Python 3.11 runner), which also fails on upstream `main` and on my JS1 PR. Claude ran the course validator's checks against my `fall-2026/atharva-c/js2-loop-tools-diff` directory specifically, and all checks passed cleanly.

* **What Claude did / what I accepted:**
  Claude reconstructed the commit series in the course monorepo layout, drafted `COMMIT_MAP.md`, resolved the Git email issue on the `COMMIT_MAP` commit, executed the push, and ran the validator checks locally against our folder. I asked for an audit against the brief, then wrote all three gap-fix sections, authorized posting the branch, inspected the opened pull request (#43) across the Conversation, Commits, and Checks tabs, and questioned the failing CI check to ensure it did not stem from our code.

* **Reference:** Pull Request #43 (`nikbearbrown/info-7375-prompt-engineering-for-generative-ai#43`), fork branch head `a86930d`, local commits `c33b5a8` and `4d00a96`.
