# Review packet: the `meta.total` check (JS2 Step 8, Chapter 6)

One non-trivial change I asked Claude Code to make, reviewed against a test I committed first.
Decision: **accept** (Isaac, 2026-11-09). Decisions referenced: JS2 D6, D21 (task log `DECISIONS.md`).

## 1. The change and why

Greenhouse sends its own count, `meta.total`, beside the job list. The agent never compared the two, so a
list that is well-formed but missing postings ended `ok`. I knew about this gap when I wrote GATE.md and left
it out on purpose (D6) so it could be the finished-wrong demo (Step 7) and then be fixed here.

## 2. The defect, reproduced

`demo/finished_wrong/` (Step 7, commit 73bb84a): the real Stripe response from the Step 6 run with the 86
postings new since 10/31 removed, and `meta.total` left at 766. I ran it:

| | Got |
|---|---|
| Agent | `finished`, Stripe fetched 680, **new 0** |
| Truth | 86 new (Step 6 run, recomputed from raw) |
| `checks/total_check.py` (imports nothing from the agent) | 680 vs 766, **MISMATCH** |

## 3. The test, written before the patch

Before any test was written, I chose the expected behaviour (D21):

1. List length ≠ `meta.total`, **either direction** → that board ends `failed` with a new code `203`
   (validate stage, no retry, board scope): no job count, state unchanged, run not `finished`.
2. No `meta.total` (every Ashby response, or a Greenhouse response without it) → can't check, handled as before.
3. Claude drafts the test; I read it, run it red, and commit it alone before the patch.

`tests/test_meta_total.py`, 7 tests:

| Test | Before the patch | Role |
|---|---|---|
| `test_list_length_not_equal_to_meta_total_fails_the_board[list-shorter]` (1 job, total 2) | red: `('ok', None, 1, 0)` | the defect |
| `…[list-longer]` (2 jobs, total 1) | red | the defect, other direction |
| `test_code_203_is_a_board_scoped_validation_error_with_no_retry` | red: `KeyError: '203'` | the code table |
| `test_step7_seeded_response_now_fails_instead_of_finishing` (real 680 / 766 file) | red: `('ok', None, 680)` | the Step 7 input |
| `test_missing_meta_total_is_not_checked[no-meta]`, `[meta-without-total]` | green | guard: must stay green |
| `test_equal_total_is_still_ok` | green | guard: must stay green |

Red run: `evidence/step8_test_red.txt` → **4 failed, 3 passed**, each failure for the reason above, not an
import or fixture error. Committed alone as **3c4aa5a**, before any change under `job_agent/`.

Check the order in `evidence/git-history.txt` (in the course repo this folder is a single commit, so
`git log` there can't show it): commit 3c4aa5a (the test, 2026-11-08 19:32 -0500) comes before ee3018e
(the patch, 19:56), and 3c4aa5a changes no file under `job_agent/`.

What went wrong on the way: my first commit of the test (e4b2aa0, never pushed) had the test file and
`FRICTIONAL.md` overwritten with pytest output, because a pasted `tee` line ran together with the `git add`
line. Claude noticed it when it checked the commit, restored both files, and I amended the commit to 3c4aa5a.

## 4. The diff, read as a change in behaviour

5 files, +26 −2 (`git diff --stat` before the patch commit).

My reading (Isaac, 11/09, translated): "After the change, the agent checks `meta.total` if it exists. If the
number of jobs fetched is different, it reports an error. If it doesn't exist, it's ignored, because not
every ATS has it."

Made precise:

| File | Behaviour change |
|---|---|
| `job_agent/watch/boards/greenhouse.py` | `parse()` now ends with `_check_total`: an integer `meta.total` that differs from the number of jobs raises `CountMismatchError`. No `meta`, no `total`, or a total that isn't an integer → no check. |
| `job_agent/common/errors.py` | new `CountMismatchError`, a kind of `WatchError`, so the loop can tell "right shape, wrong count" (203) from "wrong shape" (202) |
| `job_agent/loop/runner.py` | `CountMismatchError` → board `failed` with `203`, caught before `WatchError` so it isn't reported as 202 |
| `job_agent/loop/codes.py`, `ERROR_CODES.md` | + `203 validate`, no retry, board scope |

"Reports an error" means **that board** fails; the other boards still run, so a four-board run ends
`incomplete`, not stopped. Only Greenhouse is checked; `ashby.py` is not touched.

## 5. Scope check

In scope: every changed line serves D21 (1) or (2). My call: "looks like it's within scope".

Seen during the review and deliberately **not** changed (old behaviour, outside D21):
- a failed board's trace row has `source: null`, so a replayed (seeded) run isn't marked as seeded once it fails (also true for 201 / 202);
- the summary prints the `skill_aliases` hint even when no posting was judged;
- a seeded replay shows `attempts 0` / `requests 0/10` (no request was made, which is correct).

Docs updated with the change (dated, not rewritten): GATE.md §1 (code 203), §4 (row), §6 (wrong version 5);
CONTRACT.md JS2 note; `demo/finished_wrong/README.md` "After the Step 8 patch"; my Chinese project map (kept in the working repo, not in this submission).

## 6. Commands I ran myself

| Command | Evidence | Result |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_meta_total.py -q` (before the patch) | `evidence/step8_test_red.txt` | 4 failed, 3 passed |
| `git diff` | read, §4 | 5 files |
| `.venv/bin/python -m pytest -q` (after the patch) | `evidence/step8_test_green.txt` | 279 passed |
| agent on the Step 7 seeded file (`--board stripe --from-raw …`, output under `demo/finished_wrong/out/`) | `evidence/step8_demo_after_patch.txt`, `demo/finished_wrong/out/runs/2026-11-09T004354Z/` | Stripe `failed 203`, "680 jobs but … 766", fetched / new `—`, exit `error`, exit status 1; state file unchanged |

Checked by Claude, not by me: 6 bugs planted one at a time into the patch (only a shorter list fails; 202
instead of 203; check never called; a missing total also fails; except order wrong; mismatch only warns) →
each turned at least one test in `test_meta_total.py` red (6/6), then the patch was restored (279 passed).

## 7. Decision: accept

| Evidence | Points to |
|---|---|
| The 4 red tests are green, the 3 guards stayed green | the change does what D21 says and no more |
| Full suite 279 passed | nothing else broke (WV3's `{"jobs": []}` is still 201) |
| Same seeded input, before → after: `finished`, 0 new → `failed 203`, no count | the Step 7 finished-wrong case is now reported, by the agent itself |
| State unchanged after the failed board | an untrustworthy list doesn't advance what the agent has "seen" |
| Diff touches only the 5 files in §4 | in scope |

## 8. One case this test still misses

**A list that is short and whose `meta.total` is short in the same way.** If the board's index is stale, the
list and the count can both come from the same stale data: 680 jobs, `meta.total` 680. The check compares the
board with itself, not with the truth, so it passes, the board ends `ok`, and the run can still say `finished`,
0 new. No test here can catch that, because every test feeds the agent a response whose count is the only
evidence it has. Catching it needs a source outside the response (for example, comparing with the previous
run's count, or the board's public job page).

Smaller gaps in the same area: Ashby has no total, so an Ashby list missing postings is never checked; and a
non-integer `meta.total` (`"766"`, `true`) is silently skipped, with no test pinning that.
