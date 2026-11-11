# Review packet — one change made by Claude Code

**The change:** a valid empty job list wiped a board's seen ids. The next run then reported every returning job as new.
- **Found by:** Claude Code on my Mac, when it reviewed stage B on 2026-11-09 at ~3:30 pm (its problem 1).
- **Patched by:** Claude Code on my Mac, on 2026-11-10 at ~9:35 pm.

## 1. My rule, before any test or patch (2026-11-09 ~3:38 pm)
> "Keep the IDs. A valid empty list tells me the board has zero postings right now. It doesn't erase what the agent saw before. If job 123 was already seen, disappears during an empty run, and comes back tomorrow, I'd treat it as a returning posting. A job ID the agent has never seen would count as new. The empty run should still report success, zero current postings, and zero new jobs."

## 2. Defect reproduced, test written before the patch
- **The test:** `tests/test_review_packet.py`, written by Claude (this chat) from my rule, then committed by me while it **failed**, as commit `21451f2b`.
- **What it does:** it runs the real `watch.py` three times on one board: 3 jobs, then a valid empty list, then the same 3 jobs.
- **Result before the patch** (`logs/20_packet_test_before_patch.txt`), `FAILED (failures=2)`:
  - The returning jobs 1, 2 and 3 were reported as **new**.
  - The never-seen-id test got `['1','2','9']` instead of `['9']`.

## 3. The diff, read as a change in behaviour (`logs/21_packet_diff.txt`)
```diff
-            if b["status"] == "ok": seen[b["board"]] = set(b.pop("all_ids"))
+            if b["status"] == "ok": seen.setdefault(b["board"], set()).update(b.pop("all_ids"))   # keep every id ever seen
```
- **Before:** each successful board's seen set was *replaced* by the ids in this run. An empty list therefore made it empty, and so did any posting that dropped off.
- **After:** the ids in this run are *added* to what was already seen. Nothing is forgotten. An empty run still reports `ok`, 0 jobs, 0 new. A never-seen id is still new.
- **Unchanged:**
  - Failed boards still change nothing, because the line only runs for `status == "ok"`.
  - The wrong-version demos never touch the state.
  - The trace output is the same.

## 4. Scope
One line, in one file (`watch.py`). No test file was edited: `git status` showed only `watch.py` modified. The asked-for change and no more.

## 5. Commands I ran myself, on my Mac (2026-11-10)
| Command | Result | Log |
|---|---|---|
| `python3 -m unittest tests.test_review_packet -v` (before) | `FAILED (failures=2)` | `logs/20_packet_test_before_patch.txt` |
| `git diff watch.py` | the one-line diff above | `logs/21_packet_diff.txt` |
| `python3 -m unittest tests.test_review_packet -v` (after) | `Ran 2 tests … OK` | `logs/22_packet_test_after_patch.txt` |
| `python3 -m unittest discover -s tests -t .` (after) | `Ran 66 tests … OK` | `logs/23_all_tests_after_patch.txt` |

## 6. My decision: **ACCEPT** (2026-11-10, ~9:40 pm)
What I looked at myself, on my Mac, before deciding:
- **Log 20:** the unchanged test **failed twice** before the patch. The returning jobs 1, 2 and 3 were called new, and `[1, 2] → [] → [1, 2, 9]` gave `['1','2','9']` instead of `['9']`.
- **Log 21:** the diff is **one line** in `watch.py`, from *replace* the seen ids to *add to* them.
- **Logs 22 and 23:** the same test **passes** (2/2), and the whole suite passes (66/66).

**Why only 9 is new now:** in the empty run, the old code set the remembered ids to "what I see now", which was nothing. The new code keeps what it knew before and adds what it sees, so ids 1 and 2 are still remembered and only 9 is new.

(My first two answers about this decision said "I haven't seen that output here" and "your local output"; I gave the decision again after looking at the logs myself. See FRICTIONAL ~9:40 pm.)

## 7. One case my test would still miss
A state snapshot written by the **old** code may already have lost its ids, for example after an empty run before this patch. The fix keeps the history it *loads*, but it can't bring back ids that were already erased. So one old posting could still be flagged as new one more time. My test starts from a clean state, so it can't see this. Two other gaps:
- Nothing checks the saved snapshot file itself; the test only checks the "new" lists.
- The seen set now grows forever, with no limit.
