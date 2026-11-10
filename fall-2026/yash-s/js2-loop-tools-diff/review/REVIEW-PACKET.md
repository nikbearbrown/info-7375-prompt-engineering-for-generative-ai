# Review packet (Chapter 6): failed boards reported as "0 new"

**The change I asked Claude Code to make:** stop the agent from reporting a new-job count for any board it never successfully observed. Before the patch, the deliberately misspelled board returned HTTP 404 and was correctly marked `failed`, but `summary.json` said `"new_count": 0` and the console printed `new=0`. GATE.md section 1 says: *"A failed board must not be reported as having zero new jobs."*

**What was done by whom.** I found the defect in my live run, decided what the correct behavior is, wrote the test assertions, ran every command below and made the decision. Claude wrote the test setup (temporary folders, replayed responses, console capture), wrote the patch I asked for, and drafted this packet from the commits and saved outputs.

## Order of events

Commit times come from git (UTC). The patch time is the file's save time.

| When (UTC) | Step | Evidence |
|---|---|---|
| 2026-11-10 02:51:18 | Live run: the misspelled board returns 404, and the output says "new=0" | `runs/run-2026-11-10T025118Z/` |
| 02:57:38 | Live run committed, unchanged since | commit `dd8e287` |
| 03:31:21 | **My failing test committed, with its failing output**, plus my GATE.md note changing the review topic | commit `bca5bb6`: `tests/test_review_failed_board_count.py`, `review/test-before-patch.txt`, GATE.md |
| 03:35:15 | My FRICTIONAL entry on the plan | commit `3bdca8b` |
| about 03:38 | Claude's patch to `agent.py`, after my written request | `review/agent-patch.diff` |
| 03:43 | I reviewed the diff and ran the tests and the wrong-version check, on screen | (my terminal) |
| 03:49 | I reran them and saved the outputs and the diff | `review/agent-patch.diff`, `review/tests-after-patch.txt`, `review/wrong-versions-after-patch.txt` |

The patch and this packet are committed together in the commit after `3bdca8b`. A commit cannot contain its own hash, so that hash is recorded in README.md and on Canvas.

## 1. The defect, reproduced

**In the live run** (`runs/run-2026-11-10T025118Z/`, commit `dd8e287`), the console printed:

```text
  Deliberate failure       failed       postings=None  new=0  (HTTP 404)
```

`summary.json` held:

```json
"status": "failed", "error": "HTTP 404", "postings": null, "baseline": false, "new_count": 0
```

Only `report.md` was right: it showed `-` for that board, because it checks the status before printing the count.

**Why my tests had missed it.**
- The wrong-version test for this case (`test_wrong_version_1_failed_board_is_not_zero_new`) checked the board's status, its error, its posting count, the new-postings list and the report row. It did not check `new_count` or the console.
- So all 63 tests passed and `wrong_versions.py` reported WV1 as caught, yet the agent still printed "0 new" for a board it never saw.

**Where it came from in `agent.py`.**
- **Line 249:** `"new_count": len(r["new"])` gave every board a count. A failed board's list of new postings is empty, so its count came out as 0.
- **Line 325:** printed that count with no status check.

## 2. My test, written before the patch

`tests/test_review_failed_board_count.py`, committed in `bca5bb6` before any change to `agent.py`.
- **Setup (written by Claude):** it runs the real command line on `config/live.json` with replayed responses. The misspelled board has no replay file, so it answers 404, the same status as the live run.
- **Assertions (written by me):**

```python
self.assertIsNone(self.failed_board["new_count"], "A failed board should have new_count=null, not 0.")

self.assertIn("new=unknown", self.failed_console_line,
              "The console should display new=unknown for a failed board.")
self.assertNotIn("new=0", self.failed_console_line,
                 "The console must not report zero new jobs for a failed board.")
```

**Before the patch, both tests failed on their assertions** (`review/test-before-patch.txt`):

```text
AssertionError: 'new=unknown' not found in '  Deliberate failure       failed       postings=None  new=0  (HTTP 404)' : The console should display new=unknown for a failed board.
AssertionError: 0 is not None : A failed board should have new_count=null, not 0.
FAILED (failures=2)
```

My two design decisions are in those assertions: a count that was never observed is `null`, and the console says `unknown`.

## 3. What I asked for

My request to Claude Code, on 2026-11-10 after commit `3bdca8b`, word for word:

> I've reproduced the live-run defect and committed my failing tests before the patch.
>
> I want to fix the issue for every board that was not successfully observed, not just the HTTP 404 case.
>
> Please make the smallest possible change to `agent.py` so that:
>
> 1. A board with status `failed`, `unavailable`, or `not checked` has `new_count: null` in `summary.json`.
> 2. The console displays `new=unknown` for those boards instead of `new=0`.
> 3. Successfully observed boards continue to report their correct new counts, including a genuine zero.
> 4. Baseline boards continue to display `baseline`.
> 5. Existing raw responses, state files, traces, and past run evidence remain unchanged.
>
> Do not edit my tests, GATE.md, FRICTIONAL.md, or previously saved results. Do not commit or push.
>
> After making the patch, show me the exact diff and explain how the behavior changed. Also identify whether anything outside the requested scope was modified.
>
> I will review the diff, run the tests and `wrong_versions.py` myself, and decide whether to accept the patch.

## 4. The diff

From `review/agent-patch.diff`, saved from `git diff`:

```diff
@@ -246,7 +246,8 @@ def run(config_path, runs_dir, state_dir, read_dirs, persona_path, get=http_get,
-        "boards": [{k: v for k, v in r.items() if k != "new"} | {"new_count": len(r["new"])} for r in boards],
+        "boards": [{k: v for k, v in r.items() if k != "new"} | {"new_count": len(r["new"]) if r["status"] == "ok" else None}
+                   for r in boards],
@@ -322,7 +323,7 @@ def main(argv=None):
-        print(f"  {b['name']:24} {b['status']:12} postings={b['postings']}  new={'baseline' if b['baseline'] else b['new_count']}"
+        print(f"  {b['name']:24} {b['status']:12} postings={b['postings']}  new={'baseline' if b['baseline'] else ('unknown' if b['new_count'] is None else b['new_count'])}"
```

**Read as a change in behavior:**

| Board | `new_count` in summary.json, before → after | Console, before → after |
|---|---|---|
| failed (for example 404) | 0 → **null** | `new=0` → **`new=unknown`** |
| unavailable (two timeouts) | 0 → **null** | `new=0` → **`new=unknown`** |
| not checked (a budget was reached) | 0 → **null** | `new=0` → **`new=unknown`** |
| stopped by error | 0 → **null** | `new=0` → **`new=unknown`** |
| ok, with new postings | n → n | `new=n` (unchanged) |
| ok, genuinely 0 new | 0 → 0 | `new=0` (unchanged) |
| ok, baseline | 0 → 0 | `new=baseline` (unchanged) |

The rule is now: a count exists only for a board whose status is `ok`. `report.md` behaves as before; it already printed `-` for these boards.

## 5. Scope

- **Files.** Only `agent.py` changed. Before I reviewed, Claude checked two things: the pre-patch `agent.py` was byte for byte the version in commit `3bdca8b`, so the diff is exactly the patch; and no file in the folder other than `agent.py` had changed since that commit. The only files added since are the review outputs I saved in `review/`. My `git diff -- agent.py` showed the same two hunks.
- **Lines.** Two places: building `summary.json` (line 249) and the console summary (line 325).
- **Not changed:** the budgets, the permission policy, the providers, the state-update rules, the trace, `report.md`, my tests, GATE.md, FRICTIONAL.md, and every saved run. The live run's `summary.json` still says `"new_count": 0`, which is the record of the defect.
- **One step beyond my numbered list.** I named `failed`, `unavailable` and `not checked`. The patch keys on "status is not `ok`", so a board **stopped by error** also gets `null` and `unknown`. Claude pointed this out with the diff. I accepted it, because it matches what I asked for in the first place, "every board that was not successfully observed": a board that was never observed cannot have a verified count.

## 6. The commands I ran

From the `js2-loop-tools-diff` folder, after the patch:

```bash
git diff -- agent.py > review/agent-patch.diff
python3 -m unittest discover -s tests -v 2>&1 | tee review/tests-after-patch.txt
python3 wrong_versions.py | tee review/wrong-versions-after-patch.txt
```

| Check | Before the patch | After the patch |
|---|---|---|
| My review tests | 2 failures (`review/test-before-patch.txt`) | **pass** |
| All tests | 63 passed at commit `841dbce`, before my new test existed. I did not run the full suite between my test and the patch. | **65 passed** (`review/tests-after-patch.txt`) |
| Wrong-version check | baseline passed and all 3 were caught, at `841dbce`. Not run between my test and the patch. | **baseline passes; all 3 caught** (`review/wrong-versions-after-patch.txt`) |
| WV1: failed board reported as zero new | caught by 5 tests (at `841dbce`) | **caught by 7 tests**: my 2 review tests now catch it too |
| WV2: string-prefix folder check | caught by 1 (at `841dbce`) | caught by 1 |
| WV3: retries not counted | caught by 2 (at `841dbce`) | caught by 2 |

This reran the planted-bug check after a change, as my TA asked after JS1. My new tests also made the check stronger: WV1 is now caught by 7 tests.

## 7. My decision: ACCEPT

> I accept the patch because it fixes the misleading counts, keeps the changes within agent.py, and preserves earlier evidence.

**The evidence behind it:**
- my tests failed before the patch and pass after it;
- the whole suite passes, and no test was changed to get there;
- the diff touches only the two places where the defect lived;
- the wrong-version check passes, with WV1 caught by more tests than before;
- the live run's evidence is untouched.

## 8. A case my test would still miss

My two regression tests reproduce only the **HTTP 404** case. They do not separately check the count or the console line for a board that is **unavailable** after two timeouts, **not checked** because a budget was reached, or **stopped by error**. The patch uses the same condition for all of them, but no test of mine runs those paths through `summary.json` and the console. I have also not repeated the live network run since the patch.
