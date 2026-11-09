# Sign-off and driver's seat

> **Original draft by Claude Code, 2026-11-08. Sign-off withheld, 2026-11-09.** The "Checked" and "Not checked" lists
> below say what the tests and runs in this folder show. They do not say what Smit verified,
> because Claude Code cannot know that. Before signing, Smit should run the commands in
> REVIEW_PACKET.md section 7, rewrite the "How" line to match what Smit actually did, and
> either sign or write "withheld" with a reason.

```text
Sign-off — Job-Search Agent 2

Checked:
  - Exits: finished / incomplete / budget_exhausted / error, each with its exit code
      tests/test_loop.py: Exits.*, Budgets.test_W6_board_budget_stop_is_not_finished
  - Budgets (boards, requests incl. retries, seconds) stop the loop and say which one
      Budgets.test_request_budget_counts_retries, Budgets.test_seconds_budget
  - Repeat rule: duplicate boards requested once; a third identical request blocked
      Repeats.test_duplicate_board_in_config_requested_once, Repeats.test_third_identical_request_blocked
  - Error policy: 404/403/bad body not retried; timeout retried once; failures report null
      Exits.test_W2_not_found_is_null_not_zero, test_W5_404_is_not_retried,
      test_timeout_retried_once_then_succeeds, test_timeout_twice_is_unreachable_null
  - Empty board after a non-empty baseline is suspect, escalated, baseline kept
      tests/test_empty_after_nonempty.py (7 + 1 tests)
  - Permission policy: 25 predicted boundary cases, all matched
      tests/test_policy.py P01–P25; table in POLICY.md
  - Redirects are not followed
      tests/test_redirect.py
  - The tests fail on each of the 10 wrong versions named in GATE.md
      tests/mutation_check.py, evidence/mutation-check.txt
  - Live counts match an independent recount from the saved raw bytes
      verify_run.py on runs 2026-11-08T00-43-54Z, T00-47-30Z, T00-48-58Z

How: Original tests and runs were produced by Claude Code. The extracted archive was
       subsequently checked automatically on macOS with Python 3.14.5: all 59 tests
       passed, all 10 mutants were caught, and a fresh three-step replay passed its
       independent checks. See LOCAL_VERIFICATION.md and the local-* evidence files.
       Smit P supplied the archive and requested completion; no personal command
       execution or independent code review has been reported.

Not checked:
  - A board that collapses but does not reach zero (145 -> 3). Not flagged; the suite
    even asserts that shrinking is fine. (REVIEW_PACKET.md section 9)
  - DNS rebinding: an allow-listed name resolving to an unexpected address.
  - A symlink swapped in between the policy check and the write (time-of-check race).
  - Windows paths. Original tests ran on Linux, Python 3.13; the full suite also
    passed locally on macOS, Python 3.14.5. Filesystem case behavior was not separately audited.
  - Live behavior across days. The three live runs were minutes apart and saw no
    posting changes; "new posting" detection is shown only on seeded and unit-test data.
  - A real live timeout or 5xx. Retry is shown with seeded timeouts only.
  - Whether the boards' terms of use allow this polling rate over weeks; robots.txt was
    read for each host on 2026-11-08 (Lever: Crawl-delay 1; Greenhouse: /embed/ disallowed;
    Ashby: robots.txt returned "Unauthorized").

Not claiming:
  - That any posting is relevant to anyone. This layer watches; it does not judge fit.
  - That "0 new" means nothing changed on a board that failed or is suspect.
  - That the agent is safe against a hostile server; the policy limits where it goes and
    what it writes, not what a response body contains.
  - That a seeded run shows live behavior. Every seeded run is labeled in its output,
    its trace, and its summary.

Signed or withheld: WITHHELD — Smit P — 2026-11-09
Reason: Personal review and policy confirmations have not been established.
This entry records the withheld status; it is not a signature or approval.
```

## Driver's seat

| Part | Claude should | Smit should | Why that part stays Smit's | Evidence |
|---|---|---|---|---|
| Exits and budgets | Draft the exit table, propose limits, write the code that enforces them. | Decide what counts as `finished`, and own every budget number. Change one only by a dated Decision. | A budget is a choice about how much load to put on someone else's server and how much a run may cost. The agent must not be able to raise its own limit, which is why `config/` writes need approval (P19). | GATE.md committed alone in `f150426`, before any code; GATE.md Decisions log |
| Error policy and retries | Implement the table; write tests for each row. | Decide which failures are worth a retry and which should escalate. | Whether a retry is "sound" depends on facts about the server Claude does not hold. The 403 from Ashby (below) is one of them. | GATE.md error-policy table; `tests/test_loop.py::Exits` |
| Permission policy | Write the enforcement code and the boundary tests; hunt for gaps. | Write the allow-list, predict each boundary case before it runs, and approve config writes. | The allow-list is authority to touch the outside world on Smit's behalf. | POLICY.md predictions committed in `2b3563e`, before the code in `f2c97b4` |
| The independent check | Write a checker that shares no code with the agent. | Decide what "wrong" means, and read the checker's failures instead of the agent's summary. | A check the agent controls is the agent grading itself. | `verify_run.py` imports nothing from `agent/`; WRONG_ANSWER.md |
| The review | Reproduce the defect, write the test first, patch, run the suite, show the diff, and recommend. | Re-run the commands, read the diff as behavior, and make the accept/revise/reject call. | The decision commits Smit's name to the change. In this packet the first patch passed every test and was still wrong (count 0 vs null), which only showed up by reading the checker's output against GATE.md. | REVIEW_PACKET.md sections 5 and 8; commits `66d0cbc` (test) → `1b7f999` (patch) |
| GATE.md conflicts | Point out contradictions it finds. | Resolve them. | The two GATE.md Decisions rows added on 2026-11-08 are marked "Smit to confirm" for this reason. | GATE.md Decisions log |

### Things Claude Code found that a human should weigh

These came up in the 2026-11-08 session and are recorded so Smit can check them, not as
Smit's own findings:

1. Ashby's API returned **HTTP 403** to Python's default User-Agent but 200 to curl. The
   agent now sends an explicit, honest User-Agent (`agent/fetch.py`). Whether that is within
   Ashby's terms is a human judgment.
2. The first design let **seeded runs overwrite the live baseline**. It was caught before any
   seeded run happened and fixed in `45480d2`.
3. Python's `urlopen` **follows redirects** to any host, past the allow-list. Found while
   writing POLICY.md, tested first, and fixed in `1bfbb6d`.
