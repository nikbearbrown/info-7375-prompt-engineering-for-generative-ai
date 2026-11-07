# Sign-Off — Sreevarshan Sathiyamurthy, 2026-11-06

## Sign-off

| | |
|---|---|
| **Checked** | Policy blocks non-HTTPS, off-list hosts, `..`, sibling folders, symlinks, and overwrite of evidence (test_policy, 13 cases; boundary tests, 12 cases run by me in Terminal 2026-11-06, all matched predictions) |
| | Loop exits: incomplete on deliberate 404, budget-exhausted on budget hit, finished on all success (test_loop, 11 cases) |
| | Repeat rule caches successes and permanent failures (test_loop: test_permanent_failure_not_retried_on_second_appearance) |
| | Wrong-answer demo exits finished when it should be incomplete; independent check catches both discrepancies (run by me in Terminal 2026-11-06) |
| | Fetch raises BoardFetchError with correct retriable flag for 4xx, 5xx, timeout, bad JSON (test_fetch, 9 cases) |
| **How** | Boundary cases by hand in Terminal, with predictions committed before the results (c7fe0a5, then 59142a6). All other properties by tests Claude Code wrote, which I ran myself and whose results are recorded above, except the review-packet test, which I wrote before the patch but after the defect was identified. Review packet decision made by me after reading the diff line by line. |
| **Not checked** | Real retry behavior against a live server that returns 5xx (all retry tests use mocked responses) |
| | Behavior when output/ disk is full or write permission is denied mid-run |
| | Whether Lever's or Greenhouse's terms of service allow automated polling at this frequency |
| | Whether the posting counts returned by the boards are complete (the agent counts postings returned, not all open roles) |
| **Not claiming** | This agent does not apply to jobs, does not judge relevance, does not persist state between runs, and does not detect duplicate postings across boards. |

Signed: Sreevarshan Sathiyamurthy, 2026-11-06

## Driver's seat

| Area | Who did what | Evidence |
|---|---|---|
| Loop design and exits | Claude Code built; I wrote GATE.md first and approved each exit status | commit 733869b before any code |
| Permission policy | Claude Code implemented; I predicted all 12 boundary outcomes before running | commit c7fe0a5 before results |
| Review packet | Claude Code noted that the repeat rule caches only successes, while answering my question about the cache key; the chat assistant chose it as the review-packet defect; I wrote the failing test before the patch, read the diff line by line, and made the accept decision; Claude Code proposed the fix | commit 8624b8f (test) before 31149a6 (patch) |
| Wrong-answer demo | Claude Code built; I ran it and confirmed the independent check caught both discrepancies | Terminal output 2026-11-06; commit 9e02c5a |
| Live run | I ran `python3 -m js2` in Terminal and committed the evidence | commit 13e4b94 |
