# Review packet (Chapter 6): an empty board must not read as "no new jobs"

**The change Hemanth asked Claude Code to make:** the loop must follow `GATE.md`'s error policy, last row. A board that returns an empty list after an earlier run had postings is **unverified**. It never reports "0 new", its state is not updated, and the run is **incomplete**.

This is also wrong version 1 in `GATE.md`. JS2's loop inherited the behavior unchanged from JS1's agent.

## 1. The defect, reproduced first

- **Run:** `runs/2026-10-31T191312-seeded-wrong-answer/`, labeled **SEEDED**. Notion's response was replaced by the saved file `evidence/seeded/notion-empty.json` (`{"jobs": []}`), and the run started from `evidence/seeded/state-before-wrong-answer-demo.json` (Notion: 148 postings).
- **What the agent said:**
  - `exit finished`, process exit code 0;
  - `ashby:notion ok 0 postings, 0 new`.

  It ended cleanly and it was wrong.
- **The independent check:** `python scripts/check_run.py runs/2026-10-31T191312-seeded-wrong-answer evidence/seeded/state-before-wrong-answer-demo.json`. It reads the saved raw responses itself; it never reads the agent's report. It printed:
  ```
  ashby:notion: raw holds 0 postings; state before the run said 148  <-- EMPTY BOARD: 'no new jobs' here is not evidence
  ```
  It exited with code 1.
- **A second effect, found while reproducing:** the defect also overwrote Notion's `last_good_count` with **0** in that run's state file. So a second empty response would have looked normal.

## 2. The test, written before the patch

- **File:** `tests/test_review_empty_board.py`, committed alone as `998e487` (authored Oct 31, 2026, 19:13:43 ET). No patch existed then.
  - `test_empty_board_after_postings_is_unverified_not_zero_new`
  - `test_empty_board_does_not_overwrite_last_good_state`
  - `test_empty_board_on_first_ever_run_is_a_baseline`: guards the other side, so a brand-new empty board isn't flagged.
- **Before the patch: 2 failed, 1 passed.**
  - Claude Code ran it at 19:13.
  - **Hemanth reported running it with the same result** ("ran it, 2 failed 1 passed"). That output wasn't captured in the session, so the evidence for Hemanth's run is that report.

## 3. The diff, read as a change in behavior

Commit `bd2bc05` (authored 19:34:34 ET): `jsagent/loop.py`, **+8 lines, 0 removed, no other file**.

```diff
         board_state = state["boards"].get(label)
+        last_good = (board_state or {}).get("last_good_count")
+        if not postings and last_good:
+            # GATE.md error policy: a board that suddenly returns nothing is more likely a broken
+            # fetch than an empty board. No "0 new", no state update; the run is incomplete.
+            res.update(status="unverified",
+                       reason=f"empty response; the last good run had {last_good} postings (raw saved, state kept)")
+            trace.log("board-unverified", board=label, postings=0, last_good_count=last_good)
+            continue
         if board_state is None:
```

| Input | Before | After |
|---|---|---|
| Empty response; the board had postings last time | "ok, 0 new"; state count overwritten with 0; the run can be **finished** | **unverified**, no count claimed; state kept; the run is **incomplete** |
| Empty response; the board was never seen before | baseline, 0 postings | unchanged |
| Any non-empty response | new postings by key | unchanged |
| Failed fetches (404, timeout, bad JSON) | handled earlier in the loop | unchanged (that code path ends before this line) |

The raw response is still saved before this check, so the evidence is kept either way.

## 4. Scope

- **In scope.** One rule, from the accepted gate, in the one place postings are counted.
- **No test changed or weakened.** The 49 earlier tests were untouched. The suite went from 49 to 52 passing, with the 3 new tests.
- **No new hosts, writes or permissions.** The policy module is untouched.

## 5. Commands run

| Who | Command | Result |
|---|---|---|
| Claude Code | `.venv/bin/python -m pytest -q tests/test_review_empty_board.py` (before the patch) | 2 failed, 1 passed |
| **Hemanth** | the same command, before the patch | reported "2 failed, 1 passed" |
| Claude Code | `.venv/bin/python -m pytest -q` (after the patch) | 52 passed |
| **Hemanth** | `.venv/bin/python -m pytest -q` (after the patch) | reported "52" passed |
| Claude Code | `.venv/bin/python -m jsagent run --config boards-wrong-answer.json --state state/after-patch-demo.json --label seeded-after-patch --no-claude` (same seeded scenario, same starting state) | `exit incomplete`; `ashby:notion unverified … last good run had 148`; state kept at 148 (`runs/2026-10-31T193432-seeded-after-patch/`) |

## 6. Decision

**Accept**: Hemanth, Oct 31, 2026, "accept because tests pass".

## 7. A case this test would still miss

A board that **drops sharply but not to zero**, for example 148 postings to 3:
- the patch only checks for an empty list, so this board is trusted;
- the 145 missing postings simply look "removed", and the run can still be **finished**.

The test never tries a partial response. Chosen by Hemanth from Claude's suggestion.
