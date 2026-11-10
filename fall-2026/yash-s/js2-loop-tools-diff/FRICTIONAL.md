# FRICTIONAL — Job-Search Agent 2

## 2026-11-09: Planning the Loop and Writing the Gate

### What I Am Building

In Job-Search Agent 1, I built a watcher for the Databricks Greenhouse job board.

It saved raw responses, remembered posting IDs, and reported only new jobs.

For Job-Search Agent 2, I want to extend that system into a bounded multi-board agent.

The agent will watch several boards, follow request and time limits, use a permission policy, and report why each run stopped.

I am starting from my JS1 code rather than building everything again.

I will use the instructor's Lectern collector as a reference for other applicant-tracking systems, but I will record what code or ideas I actually reuse.

### My Board Choices

I chose four boards for the first version:

1. Databricks on Greenhouse
2. Anthropic on Greenhouse
3. OpenAI on Ashby
4. A deliberately misspelled Greenhouse board, `databricks-misspelled`

This gives me three intended working boards across two applicant-tracking systems, plus one deliberate failure.

I selected the misspelled board because I want to see whether my agent correctly handles a failed request.

### My Prediction Before Running

I predict that the three real boards will return job postings.

I expect the misspelled board to return an HTTP 404 error because the board name should not exist.

My agent should record this as a failed board, not as a board with zero new postings.

Since one planned board fails, I expect the overall run to be marked incomplete rather than finished, assuming the other boards succeed and no budget is exhausted.

For Databricks, I predict approximately 10 new postings since the last JS1 watch on October 31.

This is only a prediction. I have not run the JS2 agent yet.

### My Budget Decision

I decided to start with a limit of 4 boards, 6 HTTP requests, and 120 seconds per run.

I want the loop to have clear limits instead of continuing indefinitely.

I will allow one retry for a timeout or temporary server error, but no retry for an HTTP 404.

Retries must count toward the request budget.

If a budget is reached, the agent must stop and explain what work is unfinished.

### My Permission Decisions

I will allow HTTPS requests only to the Greenhouse and Ashby API hosts used by my selected boards.

I will allow the program to read the fictional resume and write evidence to its approved folders.

It must not write outside those folders, modify the fictional resume, or reset state without the required approval.

I want the permission restrictions implemented in code because prompt instructions alone are not enough.

### What I Think Could Go Wrong

One problem I expect is the loop treating a failed board as an empty board.

This would be misleading because the agent might report zero new jobs even though it never received a valid response.

Another problem could be an incorrect path check that allows writes to a folder with a similar name, such as `runs-evil`.

I will write tests for these cases.

### What I Learned From JS1

My JS1 project received 100/100.

The TA appreciated that I wrote predictions before testing, checked Claude's claims against real data, and recorded failures instead of hiding them.

The TA also suggested that I find some genuinely relevant postings so I can measure false negatives.

For JS2, I want to pay more attention to that limitation if I find suitable early-career postings.

The TA also suggested rerunning planted-bug checks after changes.

I plan to save those checks as part of this project instead of running them only once in a temporary folder.

### Decisions After Reviewing My Gate

Before implementing the agent, Claude reviewed my gate and pointed out two areas that needed clearer rules. I agreed with the feedback and updated my decisions before starting the implementation.

First, I decided that a well-formed empty job list can initially be treated as a successful observation. A separate checker will compare it with an earlier saved response and flag a suspicious drop to zero. This will help me demonstrate that an agent can finish normally but still give a wrong answer.

Second, I decided to start Databricks from my final JS1 state containing 924 seen IDs. Anthropic and OpenAI will start with new baseline states.

I also clarified how invalid responses affect exit status, how evidence files are protected from overwriting, and what the approval flag can and cannot prove.

I made these decisions before building or testing the JS2 implementation.

### What I Will Do Next

I will commit GATE.md, BOUNDARY-TESTS.md, and this FRICTIONAL entry before Claude Code writes the new implementation.

After that, I will ask Claude to implement the loop and permission checks according to the written gate.

I will run the tests myself and record the actual results next to my original predictions.

I will keep the original decisions in Git history if I need to revise them later.

## 2026-11-09: First Offline Tests

### What I did

After committing my gate and boundary-test predictions, I asked Claude Code to implement the multi-board loop, the permission policy, and the automated tests.

I ran all 63 tests myself, and all of them passed.

I also ran `wrong_versions.py`, which tested three intentionally incorrect implementations.

All three wrong versions were caught by the tests.

### What I checked

The tests covered the exit statuses, request and time budgets, retries, saved evidence, state updates, and my 15 permission-boundary predictions.

The planted-bug checks confirmed that the tests caught a failed board being treated as zero new jobs, an incorrect folder-prefix check, and retries not being counted.

### What I learned

Passing the normal tests is useful, but I also want to know whether the tests can detect incorrect behavior.

The wrong-version check gave me more confidence in the tests because each deliberately broken implementation caused a failure.

I have not run the live JS2 agent yet, so I cannot claim that the three real job boards work successfully.

### Evidence

- `tests/`
- `wrong_versions.py`
- `GATE.md`
- `BOUNDARY-TESTS.md`

## 2026-11-09: First Live Run and Unexpected Results

### What I did

After the offline tests passed, I committed my JS2 implementation and ran the agent with:

`python3 agent.py --config config/live.json`

The agent checked four boards: Databricks, Anthropic, OpenAI, and the deliberately misspelled Greenhouse board.

The run finished with the status `INCOMPLETE`. It used 4 requests and took 3.166 seconds, staying within my limits of 6 requests and 120 seconds.

### My predictions compared with the results

Before running the agent, I predicted that the three real boards would return postings, the misspelled board would return HTTP 404, and the overall run would be incomplete.

Those predictions were correct.

The actual results were:

| Board | Result | New postings |
|---|---|---|
| Databricks | 915 postings | 80 new |
| Anthropic | 675 postings | Baseline |
| OpenAI | 825 postings | Baseline |
| Deliberate failure | HTTP 404 | Unknown |

I predicted approximately 10 new Databricks postings since October 31, but the agent found 80.

This was much higher than I expected. My Databricks state grew from 924 previously seen IDs to 1,004.

I kept my original prediction unchanged so the difference is visible.

### What I checked

I checked the saved raw responses, trace, and summary from the live run.

All four raw responses were saved, including the HTTP 404 response.

The SHA-256 fingerprints of the saved responses matched the values recorded in the trace.

The posting counts in the successful raw responses matched the agent's reported counts.

I also checked that Anthropic and OpenAI created their first baseline states.

The failed board did not create a state file.

I ran the independent checker on the live run, and it found no posting-count mismatches.

### What went wrong

The live run revealed a problem that my offline tests had missed.

The deliberately failing board was correctly marked `failed`, and the overall run was correctly marked `INCOMPLETE`.

However, the console displayed `new=0` for that board, and `summary.json` recorded `"new_count": 0`.

This was wrong because the board returned HTTP 404. The agent never received a valid job list, so the number of new postings was unknown, not zero.

My `GATE.md` specifically says that a failed board must not be reported as having zero new jobs.

The Markdown report showed `-` for the failed board, but the console and JSON summary did not.

This showed me that my earlier tests did not check every output format.

### What I learned

All 63 offline tests passed, and the three planted wrong versions were caught, but the real run still exposed a defect.

The original wrong-version check tested the board status, error, posting count, and report output, but it did not catch the incorrect `new_count` field or console output.

I learned that tests can pass while an important part of the program's output is still misleading.

I also inspected the 80 new Databricks postings. My deterministic RECORD rule marked 3 as relevant, but those jobs had seniority or location restrictions that would make them not relevant under my fuller JS1 labeling rules.

This is another limitation of my RECORD rule. I will not claim these three postings are suitable matches for the fictional persona.

### Evidence

- Live run: `runs/run-2026-11-10T025118Z/`
- Raw responses, `trace.jsonl`, `summary.json`, and `report.md`
- Implementation commit: `841dbce`
- Live-run commit: `dd8e287`


## 2026-11-09: Finished-Wrong-Answer Demonstration and Review Decision

### What I decided

The assignment requires me to show an agent that finishes normally but still gives a wrong answer.

I decided to use a three-board seeded demonstration.

The demonstration uses saved copies of the real Databricks and OpenAI responses, but replaces the Anthropic response with a constructed, well-formed empty job list.

The real Anthropic response contained 675 postings. The constructed response contains zero.

I chose this example because the original agent accepts a valid empty list without checking whether a sudden drop to zero makes sense.

### What the demonstration is meant to show

My expected result is that the agent will report `FINISHED` because every response is structurally valid.

A separate checker should compare Anthropic's zero postings with the earlier saved response containing 675 postings and flag `DROP-TO-ZERO`.

This is a seeded demonstration, not a real live result. The Anthropic empty response was constructed for this experiment.

Claude prepared the replay files and rehearsed the demonstration in a scratch copy. That rehearsal reported `FINISHED`, and the independent checker flagged the Anthropic drop from 675 to zero.

I will record my own execution separately after running the demonstration in my project folder.

### My Chapter 6 review decision

My original gate said I would investigate the empty-board limitation in the review packet.

However, the real live run revealed a more direct defect: a failed board was reported as having zero new postings in two outputs.

I decided to use this actual defect for my Chapter 6 review packet instead.

I accepted Claude's suggestion to use the `new=0` problem because I could reproduce it with the saved live evidence and write a specific regression test.

The empty-board limitation will remain documented through the separate finished-wrong-answer demonstration.

### Test-first plan

I asked Claude to prepare only the test setup for the failed-board count defect.

Claude created temporary replay responses, a temporary state and runs directory, and console-output capture.

I reserved the assertions for myself.

My tests will require:

1. A failed board to have `new_count: null` in `summary.json`, instead of zero.
2. The console to display `new=unknown`, instead of `new=0`.

I will run the tests against the existing implementation and save the failing output before asking Claude to patch the code.

After the patch, I will inspect the diff, rerun the tests and planted-bug checks, and record whether I accept the change.

### What is still not checked

I have not yet verified that the patched agent handles all failure types correctly.

These new tests focus on an HTTP 404 board. They may not catch the same problem for boards skipped because of budget exhaustion or other failures.

I will keep this limitation in my review packet rather than claiming complete coverage.

### Evidence

- `demo/replay/`
- `demo/README.md`
- `config/demo-finished-wrong.json`
- `independent_check.py`
- `tests/test_review_failed_board_count.py`
- `review/test-before-patch.txt` (to be created when I run the failing assertions)

### Follow-up: My Own Verification

After Claude's scratch rehearsal, I ran the three-board seeded demonstration myself.

The agent reported `FINISHED` with a successful exit, even though the constructed Anthropic response contained zero postings.

I ran the independent checker, which compared the constructed response with the earlier live Anthropic response containing 675 postings.

It flagged `DROP-TO-ZERO: 675 -> 0`.

I saved this output in `demo/independent-check-output.txt` and committed the demonstration separately.

I also completed my regression-test assertions and ran them before the patch. Both failed as expected, and I saved the failures in `review/test-before-patch.txt`.

## 2026-11-09: Reviewing and Accepting the Failed-Board Count Fix

### What I did

During my first live JS2 run, I found that the deliberately failing board returned HTTP 404 but was still reported as having zero new postings.

The overall run correctly finished as `INCOMPLETE`, but `summary.json` contained `"new_count": 0`, and the console printed `new=0`.

I wanted to fix this because my GATE.md says that a failed board must not be reported as having zero new jobs.

Before asking Claude to change the implementation, I wrote two regression-test assertions.

The first required the failed board's `new_count` to be `null` in `summary.json`.

The second required the console to display `new=unknown` instead of `new=0`.

I ran both tests against the original code, and both failed with assertion failures.

I saved the output in `review/test-before-patch.txt` and committed the failing tests before Claude made the patch.

### What Claude changed

I asked Claude Code to make the smallest possible fix, without changing my tests or previous evidence.

Claude changed two places in `agent.py`.

First, `new_count` is now calculated only for boards with status `ok`. For unsuccessful boards, the value is `null`.

Second, the console now displays `new=unknown` when the new-job count is not known.

I asked Claude to cover all boards that were not successfully observed, not just HTTP 404 failures.

This includes failed, unavailable, and not-checked boards.

The patch also applies to boards stopped by an error because they do not have status `ok`.

Claude did not modify my regression tests or overwrite the earlier live-run evidence.

### What I checked myself

I reviewed the patch using:

`git diff -- agent.py`

I checked that the changes were limited to the two places responsible for the JSON summary and console output.

I then ran:

`python3 -m unittest discover -s tests -v`

All 65 tests passed, including the two new regression tests that had failed before the patch.

I also reran:

`python3 wrong_versions.py`

The unmodified baseline passed all 65 tests.

The three deliberately incorrect versions were caught again:

| Wrong version | Result | Tests that caught it |
|---|---|---|
| WV1: Failed board reported as zero new jobs | Caught | 7 |
| WV2: Incorrect string-prefix folder check | Caught | 1 |
| WV3: Retries not counted toward the budget | Caught | 2 |

This was important because my TA suggested rerunning planted-bug checks after code changes.

### My decision

I decided to accept Claude's patch.

The change directly fixes the problem I found during my live run.

My tests failed before the patch and passed afterward.

The diff was limited to `agent.py`, and the change did not alter the request budgets, permission policy, state-update rules, or original run evidence.

I also accepted the broader fix for every unsuccessful board because a board that was never successfully observed cannot have a verified new-job count.

I did not ask Claude to change the tests to make them pass.

### What is still not checked

My two new regression tests directly reproduce the HTTP 404 case.

They do not separately verify the displayed counts for timeout-exhausted, budget-skipped, or stopped-by-error boards.

The patch uses the same condition for these cases, but I cannot claim that every failure status was independently tested by my new regression tests.

I also have not repeated the original live network run after this patch.

The old live evidence remains unchanged because it documents the original defect.

### What I learned

My first 63 tests passed, and the three wrong versions were caught, but the actual live run still revealed misleading output.

This showed me that passing tests do not guarantee that every output is correct.

Writing failing tests before Claude changed the code helped me define what the correct behavior should be.

Reviewing the diff and rerunning the wrong-version checks helped me make my own decision instead of accepting Claude's patch only because it said the fix worked.

### Evidence

- Original live run: `runs/run-2026-11-10T025118Z/`
- Failing regression tests: `tests/test_review_failed_board_count.py`
- Saved failures: `review/test-before-patch.txt`
- Full test suite: 65 passing tests
- Wrong-version check: 3 of 3 caught
- Failing-test commits: `bca5bb6` and `3bdca8b`
- Patch: `agent.py` (two changed locations)

## 2026-11-09: Final Documentation and Boundary-Test Review

### What I checked

After accepting the Chapter 6 patch, I reviewed the documentation prepared by Claude Code.

All 15 permission-boundary predictions matched the actual test results. I kept the original predictions unchanged and added the results separately in BOUNDARY-TESTS.md.

The full test suite passed with 65 tests, and all three planted wrong versions were caught again.

### My documentation decisions

Claude drafted the README, SOURCES, and boundary-test results using the evidence already saved in the repository.

I reviewed the documents and completed my sign-off and driver's-seat explanations myself.

I also made sure to distinguish the real live run from the constructed seeded demonstration and to document how I used AI tools.

### What I am not claiming

I have not tested every possible failure condition. The review regression tests directly cover the HTTP 404 case, and I have not repeated the live network run after the patch.

The seeded demonstration also shows that an agent can finish normally while giving an answer that needs independent checking.

### What I learned

I learned that it is important to preserve predictions, tests, run evidence and review decisions separately.

This makes it possible to see what I expected, what happened, what Claude changed, and what I personally verified.

## 2026-11-09: Second Live Run After the Review Patch

### Why I decided to run it again

During my final review, I noticed that my only live run had happened before Claude fixed the failed-board count problem.

Although my regression tests passed after the patch, I wanted evidence that the corrected behavior also worked during a real network run.

I asked Claude Code to perform a second live run with the same four boards and verify the saved evidence.

### What happened

Claude ran:

`python3 agent.py --config config/live.json`

The agent finished as `INCOMPLETE`, using 4 requests in 2.805 seconds.

The results were:

| Board | Postings | New postings |
|---|---:|---:|
| Databricks | 915 | 1 |
| Anthropic | 677 | 2 |
| OpenAI | 825 | 0 |
| Deliberate failure | HTTP 404 | Unknown |

The important difference was the deliberately failing board.

This time, the console displayed `new=unknown`, and `summary.json` recorded `"new_count": null`.

OpenAI also showed a genuine zero new postings, so the patch did not incorrectly replace every zero with an unknown value.

### What was verified

Claude checked the raw-response fingerprints, posting counts, saved state, and trace.

The SHA-256 hashes matched the trace, and the independent checker found no posting-count inconsistencies.

The run found three new postings across Databricks and Anthropic. The RECORD rule marked all three as not relevant.

I kept the first live run unchanged because it documents the original defect before the patch.

### What is still not checked

Neither live run triggered a timeout retry, HTTP 5xx response, or budget exhaustion. Those paths were tested offline.

My regression tests also do not separately check every unsuccessful board status through the JSON and console outputs.

### What I learned

I learned that a passing regression test is useful, but checking the corrected behavior with real responses provides stronger evidence.

Keeping the original run and the second run separately makes the before-and-after behavior clear.

### Evidence

- Original live run: `runs/run-2026-11-10T025118Z/`
- Post-patch live run: `runs/run-2026-11-10T043813Z/`
- Review packet: `review/REVIEW-PACKET.md`
