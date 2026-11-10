# Frictional: Job-Search Agent 2

Pavithra Prasad · INFO 7375 · JS2 The Loop, the Tools, and the Diff

Commits (`fall-2026/pavithra-p/js2-loop-tools-diff/`), oldest first: `034c127` my GATE draft · `72cc186` tightened GATE · `b1b415f` start from JS1 · `5d145ac` boundary predictions · `485e75f` loop, policy and tests · `3700113` run 1 and the demo · `a5fc261` my year-range test · `0ecb3d5` the fix · `9d3c595` review packet · `a18ab88` title fix · `3dbcda7` trace summary · `99bd578` run 2 · final commit: the hash in the Canvas submission.

My main prompts and inputs to Claude Code (quotation marks show my exact words; the rest is summarised):

- 2026-11-09: Asked for the deliverables and a step-by-step plan matched to the marks before any building.
- 2026-11-09: Asked to include my JS1 TA's label tip in the gate, and wrote my seven GATE answers.
- 2026-11-10: Gave my four expected answers for the year-range test before the fix.
- 2026-11-10: "Fix experience ranges so they use the lowest number, for example, `2–12+` should count as 2 years, and don't change anything else."
- 2026-11-10: Asked Claude Code to check every part against the TA's possible deductions before the final review.

## 2026-11-09: The gate first

- Wrote my GATE draft: four exits, budgets of 5 boards, 10 requests and 60 seconds, the repeat rule, the error policy, the permission policy, two wrong versions and a truth line (`034c127`).
- Claude Code tightened it: the five boards by name, the exact folders, a 10-second timeout, a third wrong version (a failed board reported as 0 jobs) and a dated failure sentence (`72cc186`). Both were committed before any code.
- Friction: my draft named "invalid response format" as an `error` exit, but my error policy says a failed board is recorded and the loop continues. I accepted the clarification: invalid data is a failed board (`incomplete`), and `error` is kept for the loop itself breaking.
- My JS1 TA said to decide whether the labels or the rule is the truth before labelling. The gate now says my written rule decides.

## 2026-11-09: The boards

- Checked the public endpoints: Greenhouse (Pinterest, Figma), Lever (Spotify) and Ashby (Ramp) all answered, and a wrong name gave HTTP 404 on all three systems. That made `no-such-board` on Lever the deliberate failure.

## 2026-11-09: The build

- The 18 boundary predictions were committed before the policy code existed (`5d145ac`). I checked them on 2026-11-10, and all 18 tests matched (`test_01` to `test_18`).
- Friction: the first trial run stopped with `error`. A saved file's path on macOS (`/var/...`) did not match the project folder (`/private/var/...`). The loop's catch-all reported it instead of hiding it; the fix was in `agent/loop.py`, and no test was weakened (`485e75f`).

## 2026-11-10: Run 1 and the finished wrong answer

- Expected before run 1: I expected four real boards to return jobs, the deliberately wrong board to return 404 without a retry, and the run to end `incomplete` with that failure recorded. I did not know the job counts in advance.
- Ran the watch in my own terminal: `incomplete`, with `no-such-board` failed after one request (HTTP 404, not retried) and 17 new Pinterest jobs since JS1 (`3700113`, `TRACE.md`).
- Ran wrong version 3: it ended `finished` and called the missing board "checked, 0 jobs". The independent check failed it from the saved 404 (`FINISHED-WRONG.md`, `test_catches_wrong_version_3_failed_board_reported_as_empty`). I ran it twice by accident; both runs are kept.
- Wrong version 3 showed me that a loop can finish its work and still produce a wrong result. It reported the missing board as checked with zero jobs, even though the saved response was HTTP 404. The independent check caught that contradiction. I learned that “finished” must describe both completion and a valid result, not only the fact that the loop stopped.

## 2026-11-10: The review packet

- Wrote my four cases before the fix; two failed on the old rule (`a5fc261`, `evidence/review/1-test-before-fix.txt`).
- Claude Code made the change I asked for (`0ecb3d5`): one file, `agent/rule.py`. I ran the commands myself: my test 4 of 4, all 68 tests OK, and 6 of 567 real jobs changed only their experience part, with no verdict changed (`evidence/review/6-commands-i-ran.txt`).
- I accepted it. Claude Code pointed out that "2 to 4 years" and "3 yrs" are still misread; I kept the fix to what I asked for and listed them in the review packet instead.
- Writing the four expected cases before the fix turned my intended behavior into a testable contract. Two cases failed on the old rule, which proved that the defect was real. After the narrow fix, my test passed 4 of 4 and all 68 tests passed. Six of 567 real jobs changed in their experience parsing, but none changed their final relevance verdict. I accepted the fix because the evidence matched the requested scope.

## 2026-11-10: Run 2

- Ran the watch again: `incomplete` again and 0 new. This time the check recomputed the new IDs from run 1's saved raw files and passed (`99bd578`).

## 2026-11-10: A strict review of my draft

- A separate strict TA-style review (a Claude Code agent) graded the draft 87–89 and found real gaps: the check passed a report changed to `finished` with a failed board; the code checked only the time already used, not the next request, and retried only some 5xx answers, unlike `GATE.md`; some reads skipped the policy; and my pasted command output had lost unittest's dot and dash lines.
- All of these were fixed, with 4 new tests (73 in all). The saved runs' checks gave the same results after the fix.
- One finding stays as it is: Claude Code drafted the 18 predictions, and I checked them after the tests had run. That is written in `BOUNDARY-TESTS.md`.
- A ChatGPT review of the same draft found the same two gaps and one more: a single slow request could run past 60 seconds and the run would still end `finished`. Now such a run ends `budget-exhausted` (`test_a_request_that_runs_past_the_time_budget_ends_budget_exhausted`).

## What is unresolved

- The parser still does not correctly handle verbal ranges such as “2 to 4 years” or shorthand such as “3 yrs.” I left those unresolved because my request was limited to numeric ranges and I did not want to change other behavior without new expected cases. Next time, I would define those formats in the written rule first, add held-out tests before changing the code, and rerun the full evaluation and fresh-clone check after the fix.

## Human and AI contributions

- I did: wrote the GATE draft, chose the boards, checked the boundary predictions, ran run 1, the wrong-version demo and run 2, chose the four test cases and their answers, wrote the request for the fix, ran the review commands and decided to accept it.
- Claude Code: tightened the gate, wrote the loop, the policy, the check and the tests, made the fix I asked for, ran a strict review of my draft and fixed what it found, and drafted the reports.
- Accepted: the tightened gate, the invalid-data clarification, the third wrong version, the year-range fix, the fixes from the strict review.
- Changed: my draft's `error` example (invalid data became a failed board).
- Rejected: widening the year-range fix to "2 to 4 years" and "3 yrs", because my request was to change nothing else.
