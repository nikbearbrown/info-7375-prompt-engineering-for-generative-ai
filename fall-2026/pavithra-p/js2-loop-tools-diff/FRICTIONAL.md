# Frictional: Job-Search Agent 2

Pavithra Prasad · INFO 7375 · JS2 The Loop, the Tools, and the Diff

Commits (`fall-2026/pavithra-p/js2-loop-tools-diff/`), oldest first: `034c127` my GATE draft · `72cc186` tightened GATE · `b1b415f` start from JS1 · `5d145ac` boundary predictions · `485e75f` loop, policy and tests · `3700113` run 1 and the demo · `a5fc261` my year-range test · `0ecb3d5` the fix · `9d3c595` review packet · `a18ab88` title fix · `99bd578` run 2 · `2382628` fixes from the strict review · `17f4e77` time-budget fix · `26ec385` empty-board flag · `898afe3` my predictions 19 to 23 · `c76fd5f` tests 19 to 23 · `b7e474b` run 3 · final commit: the hash in the Canvas submission.

My main prompts and inputs to Claude Code (quotation marks show my exact words; the rest is summarised):

- 2026-11-09: Asked for the deliverables and a step-by-step plan matched to the marks before any building.
- 2026-11-09: Asked to include my JS1 TA's label tip in the gate, and wrote my seven GATE answers.
- 2026-11-10: Gave my four expected answers for the year-range test before the fix.
- 2026-11-10: "Fix experience ranges so they use the lowest number, for example, `2–12+` should count as 2 years, and don't change anything else."
- 2026-11-10: "Commit these predictions before writing the tests."
- 2026-11-10: "For the new empty-board check, report “suspicious,needs review” if a previously populated board returns zero jobs; zero alone does not prove the response is wrong."

## 2026-11-09: The gate first

- Wrote my GATE draft: four exits, budgets of 5 boards, 10 requests and 60 seconds, the repeat rule, the error policy, the permission policy, two wrong versions and a truth line (`034c127`).
- Claude Code tightened it: the five boards by name, the exact folders, a 10-second timeout, a third wrong version and a dated failure sentence (`72cc186`). Both were committed before any code.
- Friction: my draft named "invalid response format" as an `error` exit, but my error policy says a failed board is recorded and the loop continues. I accepted the clarification: invalid data is a failed board (`incomplete`), and `error` is kept for the loop itself breaking.
- My JS1 TA said to decide whether the labels or the rule is the truth. The gate now says my written rule decides.

## 2026-11-09: The boards

- Greenhouse (Pinterest, Figma), Lever (Spotify) and Ashby (Ramp) all answered, and a wrong name gave HTTP 404 on all three systems. So `no-such-board` on Lever became the deliberate failure.

## 2026-11-09: The build

- The 18 boundary predictions were committed before the policy code existed (`5d145ac`).
- Friction: the first test run had 20 failures. In a macOS temporary folder, a saved file's path (`/var/...`) did not match the resolved folder (`/private/var/...`), so the loop ended with `error`. The catch-all reported it instead of hiding it. The fix was in `agent/loop.py`, and no test was weakened (`485e75f`).

## 2026-11-10: Run 1 and the finished wrong answer

- Expected before run 1: I expected four real boards to return jobs, the deliberately wrong board to return 404 without a retry, and the run to end `incomplete` with that failure recorded. I did not know the job counts in advance.
- Run 1 in my own terminal: `incomplete`, `no-such-board` asked for once, and 17 new Pinterest jobs since JS1 (`3700113`, `TRACE.md`).
- Wrong version 3 ran twice (the second time by accident; both are kept), and the check failed both from the saved 404 (`FINISHED-WRONG.md`, `test_catches_wrong_version_3_failed_board_reported_as_empty`).
- Wrong version 3 showed me that a loop can finish its work and still produce a wrong result. It reported the missing board as checked with zero jobs, even though the saved response was HTTP 404. The independent check caught that contradiction. I learned that “finished” must describe both completion and a valid result, not only the fact that the loop stopped.

## 2026-11-10: The review packet

- My JS1 TA asked for a test on the year-range reading where my record and Claude disagreed ("2–12+ years"). My four cases went in first, in `tests/test_year_ranges.py`, and two failed on the old rule (`a5fc261`).
- Claude Code made the change I asked for in one file, `agent/rule.py` (`0ecb3d5`), and I ran the review commands myself (`evidence/review/6-commands-i-ran.txt`).
- Claude Code pointed out that "2 to 4 years" and "3 yrs" are still misread. I kept the fix to what I asked for.
- Writing the four expected cases before the fix turned my intended behavior into a testable contract. Two cases failed on the old rule, which proved that the defect was real. After the narrow fix, my test passed 4 of 4 and all 68 tests passed. Six of 567 real jobs changed in their experience parsing, but none changed their final relevance verdict. I accepted the fix because the evidence matched the requested scope.
- My written rule now says the same: a dated JS2 note at the end of `CONTRACT-JS1.md`, with the JS1 rule left as it was.

## 2026-11-10: Run 2

- `incomplete` again and 0 new. This time the check recomputed the new IDs from run 1's saved raw files and passed (`99bd578`).
- I also recomputed run 1's 17 new Pinterest jobs myself, from its saved response and the IDs carried from JS1, and got the same 17.

## 2026-11-10: Two reviews of my draft

- A separate strict review (a Claude Code agent) found four gaps. The check passed a report changed to `finished` while a board had failed. The time budget did not count the next request. Only some 5xx answers were retried. Some reads skipped the policy.
- It also found that my pasted command output had lost unittest's dot and dash lines. It is now restored exactly.
- All of these were fixed, with 4 new tests (`2382628`).
- A ChatGPT review found one more: one slow request could run past 60 seconds and the run would still end `finished`. Now such a run ends `budget-exhausted` (`17f4e77`).
- One finding could not be fixed: Claude Code had drafted the 18 predictions, and I checked them after the tests ran. So I predicted the next five cases myself.

## 2026-11-10: My own predictions, and the empty board

- I predicted five more boundary cases before their tests existed (`898afe3`): 19 allowed, 20 refused, 21 allowed, 22 refused, 23 allowed. For 21, my GATE allows an HTTPS request to an approved hostname and does not restrict ports. All five matched (`c76fd5f`).
- Claude Code first made an empty board after a full one fail the check. I changed it to "suspicious, needs review", because zero alone does not prove the response is wrong (`test_an_empty_board_after_a_full_one_is_flagged_suspicious`).

## 2026-11-10: Run 3, on the final code

- `incomplete` again, and 2 new Spotify jobs had appeared since run 2. The check recomputed them from run 2's saved raw files and passed (`b7e474b`, `runs/20261110T154407Z/`).

## What is unresolved

- The parser still does not correctly handle verbal ranges such as “2 to 4 years” or shorthand such as “3 yrs.” I left those unresolved because my request was limited to numeric ranges and I did not want to change other behavior without new expected cases. Next time, I would define those formats in the written rule first, add held-out tests before changing the code, and rerun the full evaluation and fresh-clone check after the fix.

## Human and AI contributions

- I did: wrote the GATE draft, chose the boards, checked the 18 predictions and predicted five more myself, ran runs 1 to 3 and the wrong-version demo, recomputed run 1's new jobs, chose the four test cases and their answers, wrote the request for the fix, ran the review commands, decided to accept it, and decided how the check reports an empty board.
- Claude Code: tightened the gate, wrote the loop, the policy, the check and the tests, made the fix I asked for, ran a strict review and fixed what both reviews found, and drafted the reports.
- Accepted: the tightened gate, the invalid-data clarification, the third wrong version, the year-range fix, the fixes from both reviews.
- Changed: my draft's `error` example (invalid data became a failed board); the empty-board check, from a failure to "suspicious, needs review".
- Rejected: widening the year-range fix to "2 to 4 years" and "3 yrs", because my request was to change nothing else.
