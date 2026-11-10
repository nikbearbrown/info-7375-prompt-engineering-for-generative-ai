# Sign-off — Job-Search Agent 2

## Checked

| Property | Checked by | How |
|---|---|---|
| A Greenhouse board for the wrong employer cannot finish or save ids, and the right board still finishes | `test_wrong_employer_board_does_not_finish`, `test_matching_employer_board_still_succeeds` | By a test drafted with Claude's help that I accepted before the patch existed (`a81c572` came before `b3f5adb`). On real data, by the after-patch run `runs/2026-11-10T170122Z_WRONG-BOARD-after-patch`, run with AI help. |
| The changed budget test still tests the same property | `test_budget_exhausted_still_saves_the_boards_that_succeeded` | With Claude's help: the change from a budget of 2 to 3 was reviewed with AI help |
| The live y/N approval prompt refuses on `N` and acts only on `Y` | `python3 agent.py reset-state --state state/seen.json`, answered `N`: exit 3, `error: not approved`, and `state/seen.json` unchanged (3 boards, 233 seen ids, the same SHA-256 before and after). `python3 agent.py reset-state --state state/approval_yes_demo.json`, answered `Y`: exit 0, and the copy is now empty. | With AI help, in a real terminal on 2026-11-10. `Y` was tested only on a disposable copy of the state, never on the real state. Both runs are recorded in `FRICTIONAL.md`. |
| Day 2's new and closed postings are right | `crosscheck_days.py runs/2026-11-09T205756Z runs/2026-11-10T170553Z` agreed on all three boards | By recomputation from the saved raw responses. Claude wrote the script with its own id extraction, not the loop's code. |
| The deliberate failure is handled without inventing a value | `runs/2026-11-10T170553Z/trace.jsonl` lines 13–15; `state/seen.json` has no `ashby/valonn`; `test_deliberate_404_with_plain_text_body_is_a_failed_board_not_a_crash` | With Claude's help: Claude pulled the trace lines and the state for me, and a test Claude wrote covers the same case |
| The finished wrong answer is caught by a check that doesn't read the loop's report | `check_identity.py` → `runs/2026-11-09T205808Z_identity-check` (MISMATCH) | With Claude's help: Claude wrote the check and ran it in my session. It shares no code with the loop. |
| The permission policy matches the 23 predicted boundary cases | `test_P1_…` to `test_P23_…` in `tests/test_policy.py`; predictions in `PERMISSIONS.md`, committed in `159adc2` before any test | With Claude's help: Claude wrote the predictions and the tests, and the suite was run with AI help |
| Each of the four wrong versions is caught | `test_wrong_version_1_…` to `test_wrong_version_4_…` (mutants) | With Claude's help: Claude wrote the mutant tests, and each checks that the mutant really gives the wrong result and that the real code doesn't |
| The budgets in the code are the gate's | `test_budgets_match_gate`, `precheck.py` | With Claude's help |

All 56 tests passed when `python3 -m unittest discover -s tests` was run with AI help on 2026-11-10.

## Not checked
1. **Identity of Ashby and Lever boards.** Only Greenhouse names its own board. A valid Ashby or Lever board for the wrong employer would finish cleanly, and neither the loop nor `check_identity.py` would notice.
2. **Network failures in a live run.** Timeouts, dropped connections, 5xx responses, and redirects never happened live. They were exercised only with scripted responses, and the redirect check was tested by calling its handler directly. No test covers a failure of the Greenhouse name request itself.
3. **The live prompt for the other approval actions.** Only `reset-state` was answered live. Deleting a run, changing the board list, and writing over 5 MB use the same prompt function, but they were exercised only in tests that force "no terminal" or inject an answer.
4. **The broad `except KeyError` in `loop.run`.** It turns any `KeyError` into "error: config or state", so a real bug could be hidden that way. I left it out of scope in review.
5. **"New" means new since the last run, not first posted.** JS2's state only goes back to 2026-11-09. The day-2 "new" Abacus posting `8782226002` had been on the board on 2026-10-31 (JS1's saved responses), was gone on 11-09, and came back on 11-10.
6. **Other platforms.** It ran only on macOS 26.5.1 with Python 3.14.7. I did not try older Python versions, Linux, or Windows.
7. **A wording leftover in the gate.** `GATE.md`'s `error` row mentions "an invalid persona". JS2 has no persona because it does no judging, so only bad config or state can reach that exit. I did not amend the gate for this.

## Not claiming
- **That the agent judges fit.** JS2 reports new and closed posting ids only. It says nothing about whether a job is relevant to anyone.
- **That a "new" posting is newly created.** A relisted posting counts as new.
- **That a configured board belongs to the employer I named,** except on Greenhouse.
- **That it watches continuously.** There is no scheduler. Each of the two daily live runs (2026-11-09 and 2026-11-10) was started by a command in my session.
- **That the tests show how the real sites behave.** They use scripted responses. They show the loop's logic, not the endpoints' behavior.
- **That it scales.** Three real boards and one bad one is all it has watched.

## Signed or withheld
Signed or withheld: Signed (Atharva, 10 Nov 2026)

## Driver's seat

| Part | What Claude should do | What I should do | Why that part stays mine | Evidence |
|---|---|---|---|---|
| Loop: the gate | Ask one section at a time, offer options, and point out gaps | Choose every exit, budget, rule, and limit | These rules decide what counts as success and what the agent may touch. Those are my risks, and Claude would be grading its own work if it set them. | `1f00955` (gate) before `350a997` (code). FRICTIONAL 2026-11-01: I switched my exit choice after Claude pointed out that `incomplete` was undefined. |
| Loop: boundary cases | Draft the cases and predict their outcomes before writing any policy code | Accept the cases, and check the results against the predictions | A prediction only counts if it comes before the result | `159adc2` (predictions) before `350a997` (tests); `e32740e` (actual outcomes) |
| Loop: code, tests, and live runs | Write the code and tests, run them, and flag anomalies | Decide what the runs show and what to claim | Claude can run and report, but whether a run is evidence for a claim is my call | `62afbe5`; the relisting under "Not checked" |
| Review: the test | Supply the setup lines and help draft the assertions | Decide what the test must require, and accept it before any patch exists | The test defines what "fixed" means. Because I accepted it before the patch and it stayed unchanged, the patch could not redefine success. | `a81c572` before `b3f5adb`; the review test has 0 changed lines since |
| Review: the patch | Write the patch, flag the changes it forces in other tests, stay in scope, and help run the review commands | Read the diff as behavior, confirm the commands and results of the suite and the real wrong-board run, and decide | Accepting a change is the decision I sign. It rests on evidence I confirmed, not on Claude's account of its own patch. | `b3f5adb`; `runs/2026-11-10T170122Z_WRONG-BOARD-after-patch`; `7641f93`; `REVIEW_PACKET.md` |
| Review: the limit | Name what the test misses | Record the limit, and decide what stays out of scope | Leaving something unfixed is a decision about risk, not about code | `GATE.md` "Decisions after the gate"; aliases and the `KeyError` handler left as is |
