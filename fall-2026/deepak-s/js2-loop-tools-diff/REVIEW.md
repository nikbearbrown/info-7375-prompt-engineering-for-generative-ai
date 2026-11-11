# REVIEW.md: review packet for one Claude Code change

One non-trivial change I asked Claude Code to make, reviewed on evidence (Chapter 6).

## 1. The change I asked for
- Date and time (ET): 2026-11-10. I sent the request after committing my test (7309446, 15:40 ET). Claude Code committed the patch as 3a4c1fb at 15:41 ET.
- Model: claude-opus-5-5 (Claude Code)
- Prompt excerpt (my exact words):
  - "Fix the cause, which is the order of the state replace and the run-record write."
  - "Write the smallest patch that makes both tests pass without catching more exceptions or hiding the failure."
  - "Do not modify my test file in any way."

## 2. The defect, reproduced before any patch
- Repro command (SEEDED fault injection: the summary.json write raises OSError; fake transport, temp folder): `.venv/bin/python -I evidence/review/SEEDED_repro_state_then_error.py $PWD`, run from js2-loop-tools-diff/. Script and README: `evidence/review/`.
- Output (failing):

      jobwatch: ERROR: could not write the run record: OSError: SEEDED: disk full
      exit 1 | state/seen.json exists: True | summary.json exists: False

  The run exited ERROR (1) but state/seen.json had been created, and no summary.json was written. GATE.md section 1: state changes only on FINISHED or INCOMPLETE; on ERROR it reports "the fact that state was not updated"; summary.json and the exit code always agree.
- Commit the repro ran against: f9af923 at Gate 5a (from Claude Code's scratchpad), and again from evidence/review/ at 231bd1f (15:27 ET), with the same output. jobwatch/loop.py is identical at both and up to the test commit 7309446 (`git diff --quiet 9d5f957 7309446 -- jobwatch/loop.py` exit 0). Cause in the code: Loop.run replaced state (jobwatch/loop.py:269 at 7309446) before _finish wrote the run record (:385-389), and _finish returned ERROR at :392 when that write failed.

## 3. My test, written before the patch
- Test names and file: `test_error_exit_does_not_create_state` and `test_error_exit_leaves_existing_state_byte_identical`, in `tests/js2/test_review_state_on_error.py`.
- Commit hash (must be earlier than the patch commit): 7309446 (15:40 ET). The patch is 3a4c1fb.
- Written by: my first attempt was an outline-only commit (49ce61d, 15:37 ET). It held the test's structure as comments and no Python, so pytest ran no tests. The Python test was then drafted in the claude.ai chat (Claude Opus 5.5, 2026-11-10). I read it, ran it red, and committed it (7309446) before the patch (3a4c1fb). The test did not come from Claude Code because the patch author should not also write the test that judges it.
- Output against the unpatched code (red): `evidence/review/red-before-patch.txt`, committed with the test in 7309446: 2 failed. I reran it myself at 15:52 ET in a separate git worktree checked out at 7309446: `evidence/review/deepak-red-at-7309446.txt` (commit 7ebb3ba), 2 failed in 0.28s. Both failures are on the state assertions.

## 4. The diff, read as a change in behavior
- Patch commit hash: 3a4c1fb (15:41 ET), written by Claude Code.
- `git diff 7309446..3a4c1fb --stat`:

      .../js2-loop-tools-diff/jobwatch/loop.py           | 25 +++++++++++++---------
      1 file changed, 15 insertions(+), 10 deletions(-)

- Hunk by hunk, behavior before and after:
  - Loop.run (@@ -263): before, run() replaced state/seen.json for FINISHED or INCOMPLETE before the run record existed, and turned a failed state write into ERROR. After, run() only decides the exit and passes the new state document to _finish; it writes nothing.
  - _finish signature (@@ -354): before, _finish received state_updated, already true when state had been written. After, it receives state_doc and sets state_updated from the exit (FINISHED or INCOMPLETE). summary.json records that intended outcome, and the write follows in hunk 3.
  - After the run-record write (@@ -390): before, nothing ran after manifest.json, summary.json and trace.md were written. After, the state replace runs only once all three are written. If the record write fails, _finish returns ERROR at the existing line before this point, and state is not touched: this is the fix the two tests check. If the replace itself fails, summary.json is written again with exit ERROR, exit_code 1, state_updated false, needs_deepak true and the error; one stderr line is printed and 1 is returned. Before the patch, a failed state write also ended with an ERROR summary, so this keeps that behavior.

## 5. Scope
- Files I expected the patch to touch: jobwatch/loop.py only.
- Files it actually touched: jobwatch/loop.py only.
- Anything outside the requested change: the summary.json rewrite branch and the trace.md change were beyond the requested scope and contradicted GATE §3. They are now covered by GATE.md Amendments A-3 (commit 6b12eef) and by the suite test `tests/js2/test_review_state_replace_failure.py` (commit f39ce0d), which Claude Code wrote during review, after the patch.

## 6. Commands I ran myself
All at 15:52 ET. Outputs are committed in 7ebb3ba as `evidence/review/deepak-red-at-7309446.txt` and `evidence/review/deepak-green-and-diff.txt`.

1. `git worktree add /tmp/js2-red 7309446`, then in that worktree's js2-loop-tools-diff/: `.venv/bin/python -m pytest -q -p no:cacheprovider tests/js2/test_review_state_on_error.py` (using my working folder's venv). Output: 2 failed in 0.28s. Then `git worktree remove /tmp/js2-red`.
2. In my working folder, with the patch: `.venv/bin/python -m pytest -q -p no:cacheprovider tests/js2/test_review_state_on_error.py`. Output: 2 passed in 0.26s.
3. `.venv/bin/python -m pytest -q -p no:cacheprovider`. Output: 445 passed in 2.60s. The 445 includes the A-3 suite test (f39ce0d). At the patch commit alone the suite was 444 (Claude Code's `evidence/review/full-suite-after-patch-20261110T204159Z.txt`).
4. `git diff 7309446..3a4c1fb --stat`. Output: jobwatch/loop.py only, 15 insertions, 10 deletions.

Also run by me, outside this review: `pytest -q` at 15:07:18 ET, 442 passed (recorded in my private session log, not committed), and my curl check of the Lever EU and US hosts (`evidence/finished-wrong-answer/deepak-curl-check.txt`, commit 196853e).

## 7. Decision
Revise.

Evidence for the fix: red at 7309446 (2 failed, rerun by me at 15:52 ET, 7ebb3ba); green after 3a4c1fb (2 passed); full suite 445 passed; the diff touches only jobwatch/loop.py.

Evidence for revising rather than accepting: the patch also added a second summary.json write when the state replace fails. That was beyond the requested scope, contradicted GATE §3 ("written once, at the end of the run"), and had no suite test. It also left trace.md without the state write.

What I did: I kept the branch, because without it a failed state replace would leave summary.json saying FINISHED next to exit code 1. I made it legitimate with amendment A-3 (6b12eef) and had Claude Code turn its ad-hoc check into a suite test (f39ce0d). That test passed with no further change to loop.py. The trace.md gap is stated in A-3 and in my sign-off.

## 8. A case my test would still miss
Window (c): the process is killed between the summary.json write and the state replace. summary.json then says state was updated, but it was not. No exception is raised when the OS terminates the process, so a monkeypatched exception inside the same Python process cannot simulate it. Checking it would need a subprocess that is killed at that exact point.

The red output also shows that state/seen.json stores a run timestamp (`...200500Z` against `...200000Z`), so the state bytes change on every run even when no posting is new. The new posting in my second test was therefore not the only thing making the bug visible.
