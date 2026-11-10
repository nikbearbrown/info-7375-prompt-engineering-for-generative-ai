# Review packet — Job-Search Agent 2 (Chapter 6)

## Defect

A board that returns HTTP 200 with an empty `jobs` list is treated as a clean result:

- The board's status is `parsed`, and its `new_ids` is `[]`.
- If the board was seen before, `report.md` says "0 postings, 0 new", the same words it uses for a board
  with postings and nothing new.
- If the board was never seen, it is reported as a baseline and recorded in the state as a seen board.
  The next run then reports it as "0 new".
- If every other board parsed, the run's exit is `finished`.

The rule broken is GATE.md's amendment "2026-11-10, before the review-packet patch". An empty board's
status must be `unverified-empty`, it must never be reported as "0 new", its (zero) IDs must not be
merged into state, and the run's exit must be `incomplete`.

Why it matters: on 2026-11-10 Greenhouse `poshmark` returned `{"jobs":[],"meta":{"total":0}}`, while
Poshmark's Ashby board listed 22 postings in the same run. "0 new" for Poshmark on Greenhouse reads as
"nothing new at Poshmark", and the raw responses do not support that (FINISHED-WRONG.md).

The fault is in `agent2/loop.py`, in `Loop._do_board`: any HTTP 200 body that parses becomes
`status="parsed"` whatever its length. `exit_status` and `render_markdown` then treat it like any other
parsed board. That location comes from reading the source. The behaviour below is what was observed.

## Reproduction

**Live, run `2026-11-10-2`** (second demo run, against the state run `2026-11-10-1` wrote). Started
2026-11-10T17:46:28+00:00.

```bash
python -m agent2.loop --profile demo --out out/demo
```

Printed:

```text
2026-11-10-2: exit finished; 4 requests, 0.672 s; report in out/demo/runs/2026-11-10-2/report.md
outcome check (separate): python -m agent2.check out/demo/runs/2026-11-10-2
```

`out/demo/runs/2026-11-10-2/report.json`, line 11 and lines 61–66 (Greenhouse poshmark):

```json
  "exit": "finished",
```

```json
      "status": "parsed",
      "reason": null,
      "http_status": 200,
      "postings": 0,
      "new_ids": [],
      "baseline": false
```

`report.md`, line 13:

```text
- `greenhouse:poshmark` — parsed, HTTP 200, 0 postings, 0 new
```

Raw body `raw/04-greenhouse-poshmark.body`, 30 bytes, sha256
`09aefc0c2d96e9c065aab057f04eaa352d63f19114f01783cfa12c890427f7f8`:

```json
{"jobs":[],"meta":{"total":0}}
```

The independent check (`out/demo/check-2026-11-10-2.json`) flagged `zero-postings greenhouse:poshmark`
and `cross-system poshmark {"ashby": 22, "greenhouse": 0}`.

**Run `2026-11-10-1`**, the first demo run on fresh state, showed the never-seen form. Its `report.md`
said "`greenhouse:poshmark` — parsed, HTTP 200, 0 postings, baseline (ids saved; none reported as new)",
and the state it wrote lists `greenhouse:poshmark` among the seen boards.

**Offline, before the patch:** the regression test `tests/test_js2_review.py` (below) reproduces both
forms with fakes. Before any patch, on the current code (commit `c050acd` plus this test), it observed:

| Case | exit | status | new_ids | "0 new" in report.md | poshmark in state (before → after) |
|---|---|---|---|---|---|
| seen | `finished` | `parsed` | `[]` | yes: "0 postings, 0 new" | seen → seen |
| fresh | `finished` | `parsed` | `[]` | no: "baseline (ids saved; none reported as new)" | not seen → **seen** |

## Allowed-file list for the patch

- `agent2/loop.py`
- `tests/test_js2_review.py` (the new regression test, written before the patch)

Nothing else changes unless this list is widened here, dated, with the reason.

**2026-11-10:** Widened before the patch to include tests/test_js2_loop.py and tests/test_js2_check.py, only for the 4 tests named below, because they encode the pre-amendment behavior (an empty 200 board counted as clean). For each: the test keeps its original purpose and no assertion is removed without a replacement.

| # | Test (file:line at `4ba8bd3`) | Pre-amendment behaviour it encodes | Planned change | Why this isn't a weakening |
|---|---|---|---|---|
| 1 | `Exits.test_finished_when_every_board_parsed` (`tests/test_js2_loop.py:52`) | Demo profile with `ok_responses()`, where Greenhouse poshmark is `{"jobs":[],...}`. Asserts `exit == "finished"` and `requests == 4`. | Give Greenhouse poshmark one constructed posting (`gh_body([gh_job(4)])`) and keep both assertions: `finished`, 4 requests. Add a second run on the unchanged `ok_responses()` that asserts `exit == "incomplete"` and Greenhouse poshmark `status == "unverified-empty"`. | It still tests what its name says: every board parsed, with postings, gives `finished` within 4 requests. The empty board is no longer treated as passing. It gets its own assertion of the amended result, so nothing is dropped. |
| 2 | `Records.test_baseline_then_only_new_ids` (`tests/test_js2_loop.py:242`) | First run asserts every board is `baseline` with `new_ids == []`, including the empty Greenhouse poshmark. | Narrow the first-run assertion to the three boards with postings (faire, instacart, Ashby poshmark): each is `baseline` with `[]`. Replace the empty board's part with Greenhouse poshmark `status == "unverified-empty"`, `new_ids is None`, and `greenhouse:poshmark` absent from the state's boards. Keep every second-run assertion unchanged: faire's one new id, instacart `[]`, the rule verdict, both state ids. | The baseline-then-new behaviour is tested on the same three boards and the same second run as before. The one assertion that encoded the defect (empty board = baseline `[]`) is replaced by the amendment's stronger one, which includes "not merged into state". |
| 3 | `ErrorPolicy.test_connection_error_then_success` (`tests/test_js2_loop.py:152`) | The retry succeeds with an empty body, `gh_body([])`, and the test asserts `status == "parsed"`. | Make the successful retry body `gh_body([gh_job(1)])`. Keep `len(calls) == 2` and `status == "parsed"`. Add `postings == 1` and `clock.sleeps == [2]`. | Its purpose is the error policy: a connection error is retried once and the retry can succeed. That path is unchanged. The empty body was incidental, and under the amendment it would test a different rule. The two added assertions make the retry check stricter. |
| 4 | `FinishedWrongAnswer.test_demo_finishes_and_the_check_flags_poshmark` (`tests/test_js2_check.py:78`) | Asserts the demo profile ends `finished` with Greenhouse poshmark `parsed`, 0 postings, and that the check flags `cross-system`. | Rename to `test_demo_empty_board_is_incomplete_and_the_check_still_flags_poshmark`. Replace the `finished` and `parsed` assertions with `exit == "incomplete"` and Greenhouse poshmark `status == "unverified-empty"`. Keep the `cross-system` assertion and add `zero-postings greenhouse:poshmark`. Record the old name in its docstring. | Its purpose is that the independent check catches the empty board from the raw responses alone. That assertion is unchanged and gains one flag. The pre-patch `finished` wrong answer is not lost: it stays as live evidence in `out/demo/runs/2026-11-10-1` and `-2`, produced by commit `5e3e3d0`, and in FINISHED-WRONG.md. |

No other test in these two files is to change. Prediction, written before the patch: after the patch the
two failing tests in `tests/test_js2_review.py` and these four (as changed) pass, and every other test
still passes unchanged.

## Regression test

`tests/test_js2_review.py`, committed in `4ba8bd3` before the patch existed:

- `SeenEmptyBoard.test_seen_empty_board_is_unverified_empty_not_0_new`
- `FreshEmptyBoard.test_fresh_empty_board_is_unverified_empty_and_not_recorded_as_seen`
- `SeenEmptyBoard.test_control_board_with_postings_reports_normally` (the control)

The two regression tests failed on `bccbc41` in my own run (see "Commands I ran myself", before the
patch), and the control passed. The test file was not changed by the patch.

## Diff

The patch as reviewed: `agent2/loop.py` and the four planned test changes, against `bccbc41`.

```diff
diff --git a/fall-2026/nishant-u/js2-loop-tools-diff/agent2/loop.py b/fall-2026/nishant-u/js2-loop-tools-diff/agent2/loop.py
index ccf93fe..f263812 100644
--- a/fall-2026/nishant-u/js2-loop-tools-diff/agent2/loop.py
+++ b/fall-2026/nishant-u/js2-loop-tools-diff/agent2/loop.py
@@ -2,7 +2,8 @@
 exactly one exit status. Every network call and file write goes through agent2.policy.
 
     python -m agent2.loop --profile full          # boards 1-5, live; ends incomplete (board 5 fails)
-    python -m agent2.loop --profile demo          # boards 1-4, live; the finished-wrong-answer run
+    python -m agent2.loop --profile demo          # boards 1-4, live (the finished-wrong-answer run before
+                                                  # the review-packet patch; now ends incomplete)
     python -m agent2.loop --profile demo --replay-dir out/runs/<run>   # no network
     python -m agent2.loop --profile demo --claude # also the optional Claude judge (JS1)
 
@@ -95,7 +96,8 @@ class Loop:
     def exit_status(self, stopped_by_budget):
         if stopped_by_budget:
             return "budget-exhausted"
-        if any(e["status"] == "failed" for e in self.entries):
+        # GATE.md amendment (before the review-packet patch): an empty 200 board is not a clean result.
+        if any(e["status"] in ("failed", "unverified-empty") for e in self.entries):
             return "incomplete"
         return "finished"
 
@@ -238,6 +240,13 @@ class Loop:
                 self._fail(entry, "bad-response", status)
                 self._trace(name, b, f"failed: bad-response ({exc}; no retry)", host, status, body)
                 return None
+            if not postings:
+                # Not a clean result: no new ids (unknown, not []), nothing merged into state.
+                entry.update(status="unverified-empty", reason="empty-200", http_status=status, postings=0,
+                             new_ids=None, baseline=None)
+                self._trace(name, b, "unverified-empty: HTTP 200 with 0 postings (not a clean result); escalated",
+                            host, status, body)
+                return None
             entry.update(status="parsed", reason=None, http_status=status, postings=len(postings))
             entry["_postings"] = postings
             self._trace(name, b, f"parsed: {len(postings)} postings", host, status, body)
@@ -309,6 +318,8 @@ class Loop:
             "boards": self.entries,
             "not_attempted": [f"{e['system']}:{e['board']}" for e in self.entries if e["status"] == "not-attempted"],
             "failed": [f"{e['system']}:{e['board']}" for e in self.entries if e["status"] == "failed"],
+            "unverified_empty": [f"{e['system']}:{e['board']}" for e in self.entries
+                                 if e["status"] == "unverified-empty"],
             "new_ids": {f"{e['system']}:{e['board']}": e["new_ids"] for e in self.entries},
             "used": {"requests": self.requests, "boards": self.boards_attempted, "seconds": self._seconds()},
             "trace": self.trace,
@@ -384,6 +395,9 @@ def render_markdown(report):
             code = f", HTTP {e['http_status']}" if e["http_status"] else ""
             lines.append(f"- `{name}` — failed: {e['reason']}{code}. New postings: unknown (no value invented). "
                          "Escalated to me.")
+        elif e["status"] == "unverified-empty":
+            lines.append(f"- `{name}` — unverified-empty: HTTP {e['http_status']} with an empty jobs list. "
+                         "Not a clean result; new postings: unknown, ids not saved. Escalated to me.")
         else:
             lines.append(f"- `{name}` — not attempted ({e['reason'] or 'run ended before it'})")
     lines += ["", "## New postings, rule verdicts [record]", ""]
diff --git a/fall-2026/nishant-u/js2-loop-tools-diff/tests/test_js2_check.py b/fall-2026/nishant-u/js2-loop-tools-diff/tests/test_js2_check.py
index a9aba53..3880f7b 100644
--- a/fall-2026/nishant-u/js2-loop-tools-diff/tests/test_js2_check.py
+++ b/fall-2026/nishant-u/js2-loop-tools-diff/tests/test_js2_check.py
@@ -72,20 +72,27 @@ class OutcomeCheck(helpers.ContractTest):
 
 
 class FinishedWrongAnswer(helpers.ContractTest):
-    """The demo profile, on CONSTRUCTED responses: the loop ends `finished`, the check disagrees."""
+    """The demo profile, on CONSTRUCTED responses: the independent check flags the empty board.
+
+    REVIEW-PACKET.md scope change 4. Before the review-packet patch this test was
+    test_demo_finishes_and_the_check_flags_poshmark and asserted that the loop ended `finished`;
+    that pre-patch behaviour is kept as live evidence in out/demo/runs/2026-11-10-1 and -2.
+    """
     modules = ("agent2.loop", "agent2.policy", "agent2.check")
 
-    def test_demo_finishes_and_the_check_flags_poshmark(self):
+    def test_demo_empty_board_is_incomplete_and_the_check_still_flags_poshmark(self):
         with tempfile.TemporaryDirectory() as tmp:
             out = Path(tmp) / "out"
             clock = h.FakeClock()
             report = self.loop.Loop(self.loop.PROFILES["demo"], policy=self.policy.Policy(out),
                                     client=h.FakeClient(h.ok_responses()), clock=clock, sleep=clock.sleep).run()
-            self.assertEqual(report["exit"], "finished")
+            self.assertEqual(report["exit"], "incomplete")
             gh_posh = next(b for b in report["boards"] if (b["system"], b["board"]) == ("greenhouse", "poshmark"))
-            self.assertEqual((gh_posh["status"], gh_posh["postings"]), ("parsed", 0))
+            self.assertEqual(gh_posh["status"], "unverified-empty")
             result = self.check.check_run(out / "runs" / report["run"])
-            self.assertIn("cross-system", [f["kind"] for f in result["flags"]])
+            kinds = [(f["kind"], f.get("board") or f.get("company")) for f in result["flags"]]
+            self.assertIn(("cross-system", "poshmark"), kinds)
+            self.assertIn(("zero-postings", "greenhouse:poshmark"), kinds)
 
 
 if __name__ == "__main__":
diff --git a/fall-2026/nishant-u/js2-loop-tools-diff/tests/test_js2_loop.py b/fall-2026/nishant-u/js2-loop-tools-diff/tests/test_js2_loop.py
index ff09769..b42dd4d 100644
--- a/fall-2026/nishant-u/js2-loop-tools-diff/tests/test_js2_loop.py
+++ b/fall-2026/nishant-u/js2-loop-tools-diff/tests/test_js2_loop.py
@@ -50,9 +50,16 @@ class Profiles(LoopTest):
 
 class Exits(LoopTest):
     def test_finished_when_every_board_parsed(self):
-        report = self.run_loop(self.profile("demo"), h.ok_responses())
+        # REVIEW-PACKET.md scope change 1: every board, Greenhouse poshmark included, has postings.
+        responses = h.ok_responses()
+        responses[h.URLS["gh_poshmark"]] = [(200, h.gh_body([h.gh_job(4)]))]
+        report = self.run_loop(self.profile("demo"), responses)
         self.assertEqual(report["exit"], "finished")
         self.assertEqual(report["used"]["requests"], 4)
+        # The empty board (unchanged ok_responses) is now incomplete, not finished.
+        report = self.run_loop(self.profile("demo"), h.ok_responses())
+        self.assertEqual(report["exit"], "incomplete")
+        self.assertEqual(self.entry(report, "greenhouse", "poshmark")["status"], "unverified-empty")
 
     def test_incomplete_with_a_404_board(self):
         report = self.run_loop(self.profile("full"), h.ok_responses())
@@ -150,9 +157,12 @@ class ErrorPolicy(LoopTest):
         self.assertEqual(report["used"]["requests"], 2)
 
     def test_connection_error_then_success(self):
-        report, b = self.one([self.providers.Transient("connection-error"), (200, h.gh_body([]))])
+        # REVIEW-PACKET.md scope change 3: the successful retry body has a posting.
+        report, b = self.one([self.providers.Transient("connection-error"), (200, h.gh_body([h.gh_job(1)]))])
         self.assertEqual(len(self.client.calls), 2)
         self.assertEqual(self.entry(report, "greenhouse", "faire")["status"], "parsed")
+        self.assertEqual(self.entry(report, "greenhouse", "faire")["postings"], 1)
+        self.assertEqual(self.clock.sleeps, [2])
 
     def test_invalid_json_or_wrong_shape_no_retry(self):
         for body in (b"<html>oops</html>", b'{"jobs": "x"}', b"{}"):
@@ -241,7 +251,16 @@ class Records(LoopTest):
 
     def test_baseline_then_only_new_ids(self):
         first = self.run_loop(self.profile("demo"), h.ok_responses())
-        self.assertTrue(all(b["baseline"] and b["new_ids"] == [] for b in first["boards"]))
+        # REVIEW-PACKET.md scope change 2: the three boards with postings are baselines with [];
+        # the empty Greenhouse poshmark board is unverified-empty and not merged into state.
+        with_postings = [b for b in first["boards"] if (b["system"], b["board"]) != ("greenhouse", "poshmark")]
+        self.assertEqual(len(with_postings), 3)
+        self.assertTrue(all(b["baseline"] and b["new_ids"] == [] for b in with_postings))
+        gh_posh = self.entry(first, "greenhouse", "poshmark")
+        self.assertEqual(gh_posh["status"], "unverified-empty")
+        self.assertIsNone(gh_posh["new_ids"])
+        state = json.loads((self.out / "state" / "seen_ids.json").read_text(encoding="utf-8"))
+        self.assertNotIn("greenhouse:poshmark", state["boards"])
         responses = h.ok_responses()
         relevant = helpers.posting(9000000008)
         responses[h.URLS["faire"]] = [(200, h.gh_body([h.gh_job(1), h.gh_job(2), relevant]))]
```

## Diff read as behavior

| | Before the patch | After the patch |
|---|---|---|
| An HTTP 200 board with an empty jobs list | `status: "parsed"`, `new_ids: []`. Reported as "0 new" (or as a baseline on first sight) and saved in the state as a seen board | `status: "unverified-empty"`, `new_ids: null`: new postings unknown. Nothing saved to the state for that board |
| The run's exit when that is the only problem | `finished` | `incomplete` |
| `report.md` line for the empty board | Shown like a real board: "parsed, HTTP 200, 0 postings, 0 new" | "unverified-empty: HTTP 200 with an empty jobs list. Not a clean result; new postings: unknown, ids not saved. Escalated to me." |
| A board with postings | Parsed, new ids, merged into the state | Unchanged (the control test) |

## Scope check

Only `agent2/loop.py` changed, plus the 4 test changes planned in the table above before the patch
(`tests/test_js2_loop.py`, `tests/test_js2_check.py`). There was one unplanned edit inside the allowed
file: the module docstring of `agent2/loop.py`. I accepted it because it corrects a statement that the
patch made false (the demo profile is no longer "the finished-wrong-answer run").

`tests/js2_helpers.py`, `tests/test_js2_review.py`, `agent2/check.py` and `agent2/policy.py` are
untouched (`git status`).

## Commands I ran myself

### Before the patch (run by Nishant in his own Git Bash, 2026-11-10)

```
$ git log --oneline -3
bccbc41 (HEAD -> nishant-u-js2) JS2: review packet — scope widened before patch
4ba8bd3 JS2: review packet — gate amendment, reproduction, regression test (failing, before patch)
c050acd JS2: second demo run — finished, 0 new on an empty board
$ python -m unittest tests.test_js2_review -v
test_fresh_empty_board_is_unverified_empty_and_not_recorded_as_seen ... FAIL
test_control_board_with_postings_reports_normally ... ok
test_seen_empty_board_is_unverified_empty_not_0_new ... FAIL
AssertionError: 'finished' != 'incomplete' (both failures)
Ran 3 tests in 0.143s
FAILED (failures=2)
```

### After the patch (run by Nishant in his own Git Bash, 2026-11-10)

```
$ python -m unittest tests.test_js2_review -v
test_fresh_empty_board_is_unverified_empty_and_not_recorded_as_seen ... ok
test_control_board_with_postings_reports_normally ... ok
test_seen_empty_board_is_unverified_empty_not_0_new ... ok
Ran 3 tests in 0.129s
OK
$ python -m unittest discover -s tests -t .
Ran 131 tests in 1.190s
OK (skipped=1)
$ git diff --stat
 REVIEW-PACKET.md | 16 ++++++++++++++
 agent2/loop.py   | 18 ++++++++++++++--
 tests/test_js2_check.py | 17 ++++++++++-----
 tests/test_js2_loop.py  | 25 +++++++++++++++++++---
 4 files changed, 66 insertions(+), 10 deletions(-)
```

## Decision

ACCEPT, 2026-11-10, Nishant U. Evidence: the regression tests failed before the patch (my run on bccbc41) and pass after (my run); the full suite passes, 131 tests with 1 known skip (case 8, Windows symlink privilege); the diff stays inside the allowed list; the 4 test changes match the table written before the patch, and none removes an assertion without a replacement.

## What this test would still miss

1. An empty Ashby board: the fix is generic, but every test uses a Greenhouse empty body.
2. A truly empty board, from a company that genuinely isn't hiring, now makes every run incomplete, a false alarm the agent can't tell apart from a wrong board.
3. A board that is stale but not empty (e.g. 1 posting left) still passes.
