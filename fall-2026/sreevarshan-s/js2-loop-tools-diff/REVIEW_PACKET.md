# Review Packet — Sreevarshan Sathiyamurthy, 2026-11-06

## The change
Asked Claude Code to fix a defect in the repeat rule: a permanently-failed board appearing twice in the BOARDS list was fetched a second time, because only successes were cached (js2/loop.py line 182: `successes[key] = record` runs only after success). This wasted a request from the budget and contradicted GATE.md §4's rule that permanent failures should not be retried.

## Defect reproduced first
Before any patch, I added a failing test to tests/test_loop.py (commit 8624b8f). The test places the same board twice in the BOARDS list, makes the fetcher raise a non-retriable BoardFetchError, and asserts the fetcher was called exactly once. Running the suite at that commit gives:

    AssertionError: 2 != 1 : permanent failure fetched twice — repeat rule does not cache failures

The defect is confirmed. Ran 53 tests: 52 passed, 1 failed.

## The diff (commit 31149a6)
The patch adds a `failures` set next to `successes = {}`. After a permanent failure (non-retriable error or invalid response), the board's key is added to `failures`. Before fetching, if the key is already in `failures`, the board is skipped immediately with outcome `repeat_failed` and no request is made.

Change in behavior:
- Before: a permanently-failed board appearing twice consumed two requests and produced two failed records.
- After: the second appearance is skipped with no request, logged in the trace as `kind="repeat_failed"`, and still counted as failed so the run stays `incomplete`.

The success cache is untouched. The skip does not count toward `requests_used`.

## Stayed in scope
The diff adds 12 lines to js2/loop.py and touches nothing else. It does not change the success path, the budget logic, the error policy for new boards, or any test other than the one I wrote. I checked the diff line by line before applying it.

## Commands I ran myself
    # Confirmed defect before patch
    python3 -m unittest discover -s tests -t . 2>&1 | tail -8
    # Result: 52 passed, 1 failed (2 != 1)

    # Confirmed fix after patch
    python3 -m unittest discover -s tests -t . 2>&1 | tail -5
    # Result: 53 passed, 0 failed

## Decision
Accept. The fix matches the stated behavior in GATE.md §3 and §4, stays within the scope of the defect, and all 53 tests pass. The diff introduces no new side effects.

## One case the test would still miss
If the same board appears twice and the first attempt is retriable, the retry is skipped because the budget ran out, and then the board appears a third time — it is not in `failures` (retry was never exhausted) and not in `successes`, so it would be fetched again. The test only covers the non-retriable case.
