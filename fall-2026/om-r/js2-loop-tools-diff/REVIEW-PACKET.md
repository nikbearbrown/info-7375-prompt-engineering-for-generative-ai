# REVIEW-PACKET.md — removal detection

**Change under review:** `d3e2e8a` (patch + passing tests), on top of
`8bb6a17` (failing test, written first).
**Date:** 2026-11-10 (UTC).
**Author of the patch:** Claude Code. This packet is also written by Claude
Code, so the decision in step 6 is the author's recommendation, not an
independent review. Step 5 is for Om's own verification.

Every input below that is not a live response is labeled SEEDED, in its
filename and in the log output.

---

## Step 1 — Defect reproduced before any fix

The three real gitlab responses on disk are byte-identical (same sha256, 251
ids each), so no real removal was available. So a seeded pair was built.

- **Before (REAL):** `evidence/gitlab_20261109T232631Z.json`, 251 postings.
- **After (SEEDED):** `evidence/gitlab_SEEDED_minus_one_20261110T000619Z.json`.
  It is constructed from the real response, with posting `8858174002`
  ("Regional Sales Director, National Security Group") dropped and the long
  `content` field stripped from every posting. The file says so in its own
  `_SEEDED_NOTICE` field.

The seeded file was replayed through the loop as it was at `b908dbf`, using
`tools/replay_from_file.py`. That script copies the real
`state/gitlab_seen.json` into a scratch root, so the real state is never
written. Output from `logs/review_packet_01_defect_reproduced.txt`:

```
## (a) what the input pair actually contains (plain set difference, outside the loop)
real response ids: 251   seeded response ids: 250   real state seen_ids: 251
in real, absent from seeded: [8858174002]
in seeded, absent from real: []
removed id is in real state seen_ids: True

## (b) the CURRENT loop on the seeded later fetch (real state copied to scratch)
JS2 loop run 2026-11-10T00:06:38+00:00  EXIT: finished
  gitlab               ok           250 postings in response, 0 new  (1 request(s))
real state/gitlab_seen.json unchanged: True

## (c) does the loop's output mention the missing posting at all?
# grep -c -i -e 8858174002 -e 'Regional Sales Director, National Security Group' -e removed -e missing <output of (b)>
0
```

The posting disappeared, and the loop said nothing about it. It reports new
ids only.

## Step 2 — Test written first, failing against the unpatched loop

`tests/test_removal_detection.py` has 8 tests, committed in `8bb6a17` before
any loop change. The central one is
`test_posting_absent_from_second_fetch_is_reported_removed`. Fetch ids
`{1,2,3}` and then `{1,3}`, and it expects:

- `board_status == "ok"` (not `failed`);
- `removed == [2]`;
- `new == []`;
- the board's line says `1 removed` and not `FAILED`;
- the id is listed under its own `removed postings` heading, with no
  `new postings` heading.

The other seven pin the edges:

- new and removed in the same run stay separate;
- a baseline run reports no removals;
- an unchanged board reports no removals;
- a removal is reported **once**, not on every later run;
- a removed id that reappears is not reported as new (GATE.md's repeat
  rule);
- a failed board reports no removals and its state is unchanged;
- a state file written before this change falls back to `seen_ids`.

Against the unpatched loop (`logs/review_packet_02_test_before_patch.txt`):
**`FAILED (errors=8)`**, every test with `KeyError: 'removed'`.

**A caveat on that result:** every test fails only because the field doesn't
exist yet. That proves the test runs against the real loop. It does not, on
its own, prove the tests would catch a hollow patch. Step 4 checks that
separately.

## Step 3 — Patch, then the same test passing, then the full suite

- `logs/review_packet_03_test_after_patch.txt`: `Ran 8 tests ... OK`.
- `logs/review_packet_04_full_suite.txt`: `Ran 43 tests ... OK`. That is the
  wrong-version tests, the permission boundary tests, the retry-budget
  tests, and the removal tests. `tests/mutation_check.py` still reports
  `5/5 mutations caught, 0 survived`.

## Step 4 — The diff, read as a change in behavior

### The real diff (`git diff 8bb6a17 d3e2e8a -- agent/loop.py`)

```diff
@@ -173,16 +173,22 @@ def _record_board(policy, board, raws, postings, state, stamp, at):
     baseline = state is None
     if baseline:
         state = {"board": board, "ats": boards_mod.ats_of(board), "seen_ids": [], "runs": []}
-        new = []
+        new, removed = [], []
     else:
         seen = set(state["seen_ids"])
         new = [p for p in unique if p["id"] not in seen]
+        # Removal: in the previous successful fetch, absent from this one.
+        # State written before last_fetch_ids existed falls back to seen_ids.
+        previous = set(state.get("last_fetch_ids", state["seen_ids"]))
+        removed = sorted(previous - ids, key=str)
 
     state["seen_ids"] = sorted(set(state["seen_ids"]) | ids, key=str)
+    state["last_fetch_ids"] = sorted(ids, key=str)
     state["runs"].append({"at": at, "baseline": baseline, "evidence_files": evidence,
-                          "postings_in_response": len(unique), "new_ids": [p["id"] for p in new]})
+                          "postings_in_response": len(unique), "new_ids": [p["id"] for p in new],
+                          "removed_ids": removed})
     policy.write_bytes(policy.state_path(board), (json.dumps(state, indent=2) + "\n").encode())
-    return {"board_status": "ok", "error": None, "baseline": baseline, "new": new,
+    return {"board_status": "ok", "error": None, "baseline": baseline, "new": new, "removed": removed,
             "postings_in_response": len(unique), "evidence_files": evidence}
@@ -213,7 +219,7 @@ def run(...):
-                report["boards"][b] = {"board_status": "refused", "new": [],
+                report["boards"][b] = {"board_status": "refused", "new": [], "removed": [],
@@ -235,7 +241,7 @@ def run(...):
-                    report["boards"][b] = {"board_status": "interrupted", "new": [],
+                    report["boards"][b] = {"board_status": "interrupted", "new": [], "removed": [],
@@ -244,7 +250,7 @@ def run(...):
-                report["boards"][b] = {"board_status": "failed", "new": [], "error": e.error,
+                report["boards"][b] = {"board_status": "failed", "new": [], "removed": [], "error": e.error,
@@ -295,7 +301,8 @@ def format_report(report):
-                detail = f"{r['postings_in_response']} postings in response, {len(r['new'])} new"
+                detail = (f"{r['postings_in_response']} postings in response, {len(r['new'])} new, "
+                          f"{len(r['removed'])} removed")
@@ -311,6 +318,10 @@ def format_report(report):
+    removed = [(n, i) for n, r in report["boards"].items() for i in r.get("removed", [])]
+    if removed:
+        out.append("  removed postings (in the previous fetch, absent from this one):")
+        out.extend(f"    - [{n}] id {i}" for n, i in removed)
```

(The context lines in the `run()` hunks are shortened here; the full,
unshortened diff is `git diff 8bb6a17 d3e2e8a -- agent/loop.py`.)

### What behavior actually changed

1. **The report has a new per-board field, `removed`.** For an `ok` board
   that is not a baseline, it holds the ids that were in the previous
   successful fetch and are missing from this one. Every other status
   (baseline, `failed`, `refused`, `interrupted`) gets `[]`, so every board
   entry has the same shape.
2. **The state file gains `last_fetch_ids`**, rewritten on every successful
   fetch, and each `runs[]` entry gains `removed_ids`. `seen_ids` and the
   repeat rule are unchanged: an id that comes back is still not "new".
   - Older state files have no `last_fetch_ids`, so their first post-patch
     run compares against `seen_ids`.
   - For all three real state files today, that is exactly the last fetch,
     because nothing has changed since the baseline. Replay (a) below ran
     against the real gitlab state, so it took this fallback path.
3. **The printed report changes.** Every non-baseline `ok` line now ends in
   `N new, M removed`, even when M is 0. Removed ids get their own section,
   printed after "new postings". There are no titles for removed ids,
   because state stores ids only.
4. **Not changed:** exit codes and exit selection, `board_status` values,
   budgets, the retry/error policy, permissions, and what gets written where.
   A removal never makes a run `error`, `incomplete`, or anything other than
   `finished`.

Observed on the same SEEDED inputs after the patch
(`logs/review_packet_05_behavior_after_patch.txt`):

```
(a) gitlab, SEEDED minus one:
  gitlab               ok           250 postings in response, 0 new, 1 removed  (1 request(s))
  removed postings (in the previous fetch, absent from this one):
    - [gitlab] id 8858174002

(b) stripe, SEEDED empty response (the FINISHED-WRONG-ANSWER.md input):
  stripe               ok           0 postings in response, 0 new, 771 removed  (1 request(s))
  removed postings (in the previous fetch, absent from this one):
    - [stripe] id 5416444  ... (771 removed-id lines in total)
```

(b) is a side effect worth naming. The silent empty-response case from
FINISHED-WRONG-ANSWER.md is now loud: 771 removals. But it is still
classified as a normal `ok`/`finished` run, with every posting reported as
genuinely removed. The loop still can't tell "the board broke" from
"everything was taken down" (step 7).

### Do the tests reject plausible wrong patches?

Each variant was applied to a scratch copy of the project
(`tools/weak_patch_check.py`, `logs/review_packet_06_wrong_patch_check.txt`).
The project tree was confirmed unchanged afterwards.

| Wrong patch | Result | Tests that fail |
|---|---|---|
| A. `removed` field added, always `[]` | CAUGHT | 4 of 8 |
| B. Compare against `seen_ids` (the literal "previously-seen state") | CAUGHT | **1 of 8**: `test_a_removal_is_reported_once_not_on_every_later_run` |
| C. Removals merged into `new` | CAUGHT | 4 of 8 |

Variant A shows the four guard tests (baseline, unchanged, reappears,
failed) pass against a do-nothing patch. They guard edges; they don't detect
removals. Variant B is caught by exactly one test. If that test were deleted, a
patch that re-reports every removal on every later run would pass.

### Scope: did the diff touch anything outside loop.py and the test file?

- **The patch commit (`d3e2e8a`)** touches `agent/loop.py` and two log files
  (`logs/review_packet_03_*`, `logs/review_packet_04_*`). No other code.
- **The test-first commit (`8bb6a17`)** adds the test file, the SEEDED
  gitlab fixture, and logs 01–02.
- `git diff --name-only b908dbf d3e2e8a -- agent/ tests/ tools/ GATE.md`
  lists only `agent/loop.py` and `tests/test_removal_detection.py`.
- **This packet's commit** adds `tools/weak_patch_check.py`, a review-only
  script that never runs inside the loop, and logs 05–06.
- **GATE.md was not touched.** That is itself a finding: see below.

### Did it stay in scope for "detect removals"?

Mostly, with two judgment calls Om should make knowingly.

1. **`last_fetch_ids` goes beyond the literal spec.** The spec said to
   compare against "the board's previously-seen state", which in this
   codebase is `seen_ids`. `seen_ids` only ever grows, so comparing against
   it would report the same removal on every later run, forever.
   `last_fetch_ids` limits each removal to one report. It is a state-schema
   addition, made to keep removal detection correct rather than to add a
   feature. It is still a design decision the spec did not make.
2. **`"removed": []` on `refused`/`interrupted` entries** is for a uniform
   shape only, and no test requires it.

There is no creep into anything broader: no titles for removed postings, no
alerting, no exit changes, no GATE.md or permission changes.

**Process gap:** GATE.md says code is implemented against it, but GATE.md
defines neither "removed" nor `last_fetch_ids`. This change was implemented
from the task request, not from GATE.md.

## Step 5 — Commands Om ran himself

I ran the full test suite myself (python3 -m unittest discover -v -s
tests -t .) and confirmed 43 tests passing, then 46 after the
tool-invocation fix. I tried to replay the seeded gitlab fixture myself
(python3 tools/replay_from_file.py gitlab evidence/gitlab_SEEDED_minus_one_...)
and hit a real ModuleNotFoundError that wasn't in any log Claude Code had
shown me -- the script only ever worked when invoked with -m, which is
how Claude Code had always run it, not how I naturally ran it as a file
path. This is a real finding: the script worked in Claude Code's own
execution context but not in mine, which is exactly the kind of gap the
"a TA must be able to run this from a fresh clone" requirement is meant
to catch. Claude Code found the exact cause (different sys.path depending
on invocation style), fixed it, added a regression test
(tests/test_tool_invocation.py) that starts every tools/ script both ways,
and I re-ran the corrected command myself:

```
python3 tools/replay_from_file.py --board gitlab --from-file evidence/gitlab_SEEDED_minus_one_20261110T000619Z.json
```

and saw:

```
JS2 loop run 2026-11-10T00:42:14+00:00  EXIT: finished
  gitlab               ok           250 postings in response, 0 new, 1 removed  (1 request(s))
  removed postings (in the previous fetch, absent from this one):
    - [gitlab] id 8858174002
real state/gitlab_seen.json unchanged: True
```

confirming the fix works for me, not just for Claude Code. I also
independently ran tools/count_drift_check.py on the real and seeded
stripe files myself and confirmed the 771->0 drop is flagged SUSPICIOUS,
and inspected the real git diff between 8bb6a17 and d3e2e8a myself rather
than only reading the packet's quoted excerpt.

## Step 6 — Decision

My decision: ACCEPT, with the required follow-up (amend GATE.md to define
"removed" and last_fetch_ids). I verified the core evidence myself: the
defect reproduces, the test fails before the patch and passes after, the
full suite stays green, and the tests catch three plausible wrong
patches. I also found and had fixed a real gap Claude Code's own testing
had missed (the invocation-mode bug), which gives me more confidence in
this verification than if everything had simply worked on the first try.

### Earlier recommendation from Claude Code (the patch's author), written before Om's verification

**Recommendation (Claude Code, as the patch's author): ACCEPT, with one
required follow-up.**

Evidence:

- **Defect existed:** before the patch, a posting missing from a later fetch
  was never mentioned (log 01: `0` matches for the id, its title,
  "removed", or "missing").
- **Test came first:** written before the patch and failing against it (log
  02: `FAILED (errors=8)`), then passing after it (log 03: `8 tests OK`).
- **No regression:** full suite 43/43 and permission mutations 5/5 (log 04).
- **Works on a real-shaped input:** the posting missing from the gitlab
  input is reported by id, separately from `new`, with exit `finished` (log
  05a). The real state file is unchanged.
- **Tests reject wrong patches:** all three plausible wrong patches are
  caught (log 06).
- **Scope:** the code diff is `agent/loop.py` only, and nothing outside the
  removal path changed behavior (step 4).

**Required follow-up:** amend GATE.md to define `removed`, `last_fetch_ids`,
and the once-only reporting rule, so the spec covers the behavior again.
That is a spec change, and it is Om's call, so it is not done here.

**Recommended, not blocking:**

- Make `test_a_removal_is_reported_once_not_on_every_later_run` a second
  line of defense, so it is not the only thing standing between the code
  and variant B.
- Decide whether a mass removal (log 05b: 771 lines) should be capped or
  summarized in the printed report.

Final accept/revise/reject is Om's, after step 5.

## Step 7 — Cases this test still misses

1. **Removed and re-added between runs.** A posting taken down and put back
   with the **same id** before the next run is never seen as a removal. Only
   two successive snapshots are compared, and both contain the id.
2. **An ATS reusing ids.** If an id is reused for a different posting, the
   real removal of the old posting is masked: the id is still present, so
   nothing is reported.
3. **A broken board looks like a mass removal.** A 200 OK with an empty or
   truncated list (FINISHED-WRONG-ANSWER.md) is reported as every posting
   being genuinely removed, still `ok`/`finished`. No test asserts that the
   loop can tell "the board broke" from "the postings were removed", because
   it can't. The independent count check (`tools/count_drift_check.py`) is
   still the only thing that flags it.
4. **Lever is untested for removals.** Every removal test uses Greenhouse
   integer ids in a single response. Lever's string ids and multi-page
   fetches are not covered. A partially paginated Lever fetch is discarded
   as `interrupted` with state unchanged, so it shouldn't produce false
   removals, but no removal test asserts that.
