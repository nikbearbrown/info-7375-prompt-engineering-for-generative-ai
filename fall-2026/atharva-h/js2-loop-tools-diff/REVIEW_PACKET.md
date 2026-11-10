# Review packet: Greenhouse board identity

**The change I asked Claude Code to make (2026-11-10):** fix the board identity defect, so the loop can no longer finish cleanly on another employer's Greenhouse board, without changing the review test's assertions.

**Commits, in order:**
1. The review test: `a81c572` (11:46 ET)
2. The patch: `b3f5adb` (12:05 ET)
3. My decision, recorded in `GATE.md`: `7641f93` (12:05 ET)

## 1. The defect, reproduced
- **Live run, 2026-11-09:** `runs/2026-11-09T205807Z_WRONG-BOARD-demo`.
  - The loop, pointed at Greenhouse `abacus` as if it were Abacus Insights, exited `finished` (code 0). It reported 46 postings that belong to another employer ("ABACUS") and saved their ids.
  - The independent check `check_identity.py` caught it (`runs/2026-11-09T205808Z_identity-check`, MISMATCH). The loop itself did not. `WRONG_ANSWER.md` has the details.
- **The review test, on the pre-patch code:** `tests/test_review_identity.py` failed at `a81c572` with:
  ```text
  FAIL: test_wrong_employer_board_does_not_finish
  AssertionError: 'finished' != 'incomplete'
  ```
  - Of the 56 tests at that commit, it was the only failure.
  - Claude Code reproduced this again on 2026-11-10 from a clean `git archive a81c572` copy, with the same result.

## 2. The review test, accepted before the patch
`tests/test_review_identity.py`, committed `a81c572`. Claude supplied the setup lines (the board, the scripted responses, `make`, `go`), and the assertions were drafted with Claude's help. I accepted the assertions before any patch existed.

- **`test_wrong_employer_board_does_not_finish`:** the board is Greenhouse `abacus`, the config says "Abacus Insights", and the scripted name response is "ABACUS". The test requires:
  - exit `incomplete`
  - the board marked `failed`
  - a reason that names both "Abacus Insights" and "ABACUS"
  - no state entry for the board
- **`test_matching_employer_board_still_succeeds`:** the right board must still finish, `ok`, with seen ids `["1", "2"]`.
- **Unchanged since it was committed:** `git diff --stat a81c572 HEAD -- tests/test_review_identity.py` prints nothing.

## 3. The diff, read as a change in behavior (`b3f5adb`)
- **One extra request per Greenhouse board.** Before fetching a Greenhouse board's job list, the loop now asks for the board's own name (`/v1/boards/{token}`). Ashby and Lever boards behave exactly as before.
  - With today's config, a run now sends 5 requests instead of 4 (day 2: 5 of 10).
  - The name response is saved as `raw/greenhouse_<token>_board.json`.
- **Name doesn't match:** the board fails.
  - The reason is `identity mismatch: the board calls itself 'ABACUS', but the config says 'Abacus Insights'`, and the trace gets an `identity mismatch` event.
  - The job list is never requested, and the board's state is left untouched.
  - The run exits `incomplete`, not `finished`.
- **Name matches:** case and punctuation are ignored. The job list is fetched and handled exactly as before.
- **The name request itself fails:**
  - It gets the same error policy as a job-list request: a 4xx is not retried, a timeout or 5xx is retried once after 2 s, and a response with no name is unparseable.
  - The board fails with a reason that starts `identity check:`.
  - **A new way to fail:** a Greenhouse board whose name endpoint is down now fails even when its job list is up. It fails toward `incomplete`, not toward a wrong `finished`.
- **The repeat rule now applies to the name request.** A board listed twice is refused at its name request, before its job list.
- **Budget effect:**
  - Today's config has one Greenhouse board, so the run stays well inside 10 requests.
  - A config with five Greenhouse boards would need all 10 requests with no retries, so any retry would end that run `budget-exhausted`.
- **Refactor:** the retry, save, and parse steps moved out of `fetch_board` into a new `fetch(url, save_as, parse)`, so both requests share one error-policy implementation.
  - For the job-list request, nothing changed: the same URL, raw file name, trace fields, and failure reasons.
  - The error-policy tests passed with only their request counts raised.
- **Matching rule:** `same_employer` lowercases both names and treats any run of non-alphanumeric characters as one space.
  - "ABACUS" ≠ "Abacus Insights".
  - "Abacus Insights, Inc." ≠ "Abacus Insights": a real alias would fail, toward `incomplete`.
  - An empty name never matches.

## 4. Did it stay in scope?
**Yes, with the test changes below, which Claude flagged before writing the patch.**

- **Files changed:**

  | File | Lines | What |
  |---|---|---|
  | `adapters.py` | +18 | `IDENTITY`, `identity_url`, `parse_board_name` |
  | `loop.py` | +30 −6 | the name check in `fetch_board`, the `fetch()` helper, `same_employer` |
  | `tests/helpers.py` | +6 −1 | `GH_NAME`, `gh_name` |
  | `tests/test_loop.py` | +13 −12 | the name response added to the shared fixture, and request counts raised |

- **Not touched:**
  - `check_identity.py`, so the independent check still shares no code with the loop.
  - `policy.py` and `tools.py`.
  - The review test.
  - `GATE.md`, which changed only after my decision, in a separate commit (`7641f93`).
- **The changes in `test_loop.py`:**
  - Six request counts rose by exactly one, the name request. Each now has a comment saying so.
  - The wrong-version-4 mutant now sends 8 requests under a budget of 4 instead of 6: four first attempts plus four retries, counting the name request. It is still caught.
  - In `test_budget_exhausted_still_saves_the_boards_that_succeeded`, the budget rose from 2 to 3 so the run still stops at the same point: after Abacus and Valon are saved, and before Lever.
  - No assertion was removed or loosened.
- **Left out on purpose:**
  - company aliases
  - name checks for Ashby and Lever, which have no public name endpoint
  - the broad `KeyError` handler (see 7)

## 5. Commands run in my review (2026-11-10, with AI help)
These two commands ran with AI help, not by me alone. I confirmed that they match what ran, including the state path and label, and that the results below are correct.

```bash
python3 -m unittest discover -s tests
```
56 tests, all passed.

```bash
python3 agent.py run --config config/wrong_board.json --state state/wrong_board_after.json --label WRONG-BOARD-after-patch
```
This was the same real wrong board, after the patch, in `runs/2026-11-10T170122Z_WRONG-BOARD-after-patch`.
- It exited `incomplete` after one request, with the identity-mismatch reason.
- `state/wrong_board_after.json` has `"boards": {}`, so no ids were saved.
- Claude made its last code edit at 11:47 ET, and this run started at 12:01 ET, so the run used exactly the code committed in `b3f5adb`.

The changed budget test was also reviewed with AI help. It still verifies what it did before: boards that succeeded are saved before the next request would go over the budget.

## 6. Decision: accepted (2026-11-10)
**Evidence:**
- The review test failed before the patch and passed after it, with 0 changed lines.
- The full suite passed (56).
- The real wrong board now ends `incomplete` after one request and saves nothing.
- The right board still finishes. The day-2 live run (`runs/2026-11-10T170553Z`) passed the name check first, then fetched Abacus Insights' 16 postings.
- The test changes only add the one real extra request. The changed budget test still tests the same property.

The decision and its limit are recorded in `GATE.md` under "Decisions after the gate".

## 7. What the review test would still miss
- **A valid Ashby or Lever board for the wrong employer.** The review test only covers Greenhouse, and the loop has no name to check on the other two systems. Pointed at the wrong Ashby board, the loop would still exit `finished`. The limit is recorded in `GATE.md`.
- **Other cases it also misses:**
  - Two different employers with the same board name would pass.
  - A real alias such as "Abacus Insights, Inc." would fail.
  - No test covers the name request itself failing: a 404, a timeout, or a 5xx on `/v1/boards/{token}`.
- **Out of scope, left as is:** `loop.run` catches every `KeyError` as "error: config or state". During this patch, a missing test fixture showed up that way, and a real bug could be hidden the same way.
