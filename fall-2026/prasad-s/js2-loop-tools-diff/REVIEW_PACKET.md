# Review packet — the empty-board change (W5)

Assembled by Claude (Claude.ai) at my request, from my commits and evidence
files. The rule, the test's assertions, the commands and the decision are
mine; who did each part is stated below.

## The change, and why this one

The change: a board whose saved state holds ids and which returns zero jobs
is now a failure, "failed — empty board: 0 jobs, N ids saved before", not an
ordinary empty board (GATE.md v0.3 §4; W5 in §6).

Why this one: it fixes a wrong answer the agent actually gave, a run that
ended cleanly and was wrong (JS2-CP7), and it changes the loop's behaviour,
not just its wording. The other test-first change in this folder, the
User-Agent fix (JS2-CP5c), is a single header; this one changes what a run
reports and how it ends.

## The defect, reproduced

- The CP7 demo (JS2-CP7), run by me in a throwaway copy: four boards seeded
  from run 1's raw responses, and duolingo from a constructed empty response
  (evidence/constructed/duolingo_EMPTY_constructed_2026-11-07.json).
- The agent ended "finished", with duolingo "ok — 0 jobs, 0 new"
  (evidence/demo_finished_wrong_answer/demo_terminal.txt).
- My independent check, with no agent code: 59 duolingo jobs in run 1's
  saved raw response, and 59 on the live board at the time
  (evidence/demo_finished_wrong_answer/independent_check.txt). The check's
  commands were written by Claude.ai; I ran them on my files.

## My test, written before the patch

- The assertions are mine: W5 in GATE.md §6, committed in JS2-CP8a, before
  any test or patch existed.
- The test code was typed by Claude Code from W5, with no agent code changed
  (tests/test_review_empty_board.py). It runs through the live path, with
  the network patched, using run 1's 59 duolingo ids.
- I committed it failing, on its own, in JS2-CP8b. My run of it is saved in
  evidence/tests/cp8_W5_failing_before_patch_2026-11-08T004210Z.txt:
  "FAILED (failures=2)".
  - Check 1, the board line: 'ok — 0 jobs, 0 new' instead of
    'failed — empty board: 0 jobs, 59 ids saved before'.
  - Check 4, the exit: a plain 'finished'.
  - Checks 2 and 3 already passed on the old code: the 59 ids were kept, and
    the response was saved as evidence. So the defect was in what the agent
    reported, not in what it kept.

## The diff, read as a change in behavior

The patch (JS2-CP8c, by Claude Code) adds one branch to Loop._ok in
agent/run.py. It also moves one line, the read of the board's saved ids,
above the zero-jobs check; that line computes the same value as before.

| Case | Before | After |
|---|---|---|
| Board with saved ids returns zero jobs | "ok — 0 jobs, 0 new"; the run ends a plain "finished" | "failed — empty board: 0 jobs, N ids saved before"; the run ends "finished — with failures", naming the board |
| Board with no saved ids (first run) returns zero jobs | "ok — 0 jobs, 0 new" | Unchanged |
| Board whose saved section exists but is empty, [], returns zero jobs | ok | Unchanged: it holds no ids |
| Any board that returns jobs | Diffed against its saved ids | Unchanged |
| Saved ids and evidence in the failure case | Kept and saved | Still kept and saved: the new branch returns before touching state, and the response was saved earlier, in the fetch |

Claude.ai helped me read the diff; I checked this table against the code.

## Did it stay in scope?

- Only two files changed in code and tests: agent/run.py (+10/−2) and one
  existing test in tests/test_loop.py.
- That test, test_zero_jobs_is_ok_and_keeps_saved_ids, asserted exactly the
  old §4 row that v0.3 changed. It was renamed, and its two assertions about
  the line and the exit were updated to v0.3; its check that the saved ids
  are unchanged stayed as it was.
- No other test, no version label and no document changed in the patch. The
  labels and one stale docstring were changed later, separately (JS2-CP8e).

## Commands I ran myself

- The W5 test alone, before the patch: failing (JS2-CP8b, saved output).
- The W5 test alone, after the patch: "Ran 1 test … OK".
- The full suite after the patch: "Ran 109 tests … OK".
- The CP7 demo rerun on the patched code, in a throwaway copy, with the same
  seeds: "finished — with failures: greenhouse:duolingo", with duolingo
  "failed — empty board: 0 jobs, 59 ids saved before"
  (evidence/demo_finished_wrong_answer/after_patch_terminal.txt).

## My decision: accept

Accepted (JS2-CP8c). The evidence: W5 passes, the suite is 109/109, and the
same inputs that produced CP7's wrong answer now produce the failure GATE
v0.3 asks for. The other three boards and the saved ids are unaffected.

Two things I accepted as they are, and recorded:
- The new line has no "; attempts: n" suffix, unlike the other failed lines
  (CONTRACT v0.7 E16), because W5 fixed this exact wording. The attempts
  count is still in the line's attempts field (CONTRACT v0.8 item 2). I did
  not change W5 after seeing the patch: that would have moved the goalposts.
- No test pins the empty-[] case. Its behaviour is correct, and it is
  recorded as a known limit (CONTRACT v0.8 item 4).

The "0 jobs" in the new line is part of the failure's reason, not the
board's value: the line carries no jobs_fetched field, so GATE.md §4's
"never 0 jobs" for a failed board still holds.

## One case my test would still miss

A partial drop: a board with 59 saved ids that suddenly returns 3 jobs is
still reported "ok — 3 jobs, 0 new". The guard fires only on exactly zero,
so a board that lost most of its jobs to the same fault would pass
unnoticed. GATE.md v0.3's changelog names this in advance, along with an
empty first run.