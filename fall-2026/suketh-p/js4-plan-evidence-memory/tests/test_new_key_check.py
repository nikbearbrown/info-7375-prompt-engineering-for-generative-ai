"""The new-key check: the New claim in PLAN.md v0.2's evidence matrix.

PLAN.md v0.2: "Subtract the prior seen-key set from the verified current set. A first capture
establishes a baseline. A returning key keeps its first-seen history." Its "Still listed or gone"
row: absence from a list "leaves liveness unresolved".

The independent route: the prior seen keys come from the raw bodies of earlier saved captures,
read by checks/independent_check.py's own code, not from the agent's state file or its memory
code. --earlier names those captures, oldest first. These tests run the checker in isolated mode
(python -I). The capture folders are built by hand in a temporary folder. Claude Code wrote these
tests on 2026-11-25, before changing the checker."""

import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "checks" / "independent_check.py"


def run_check(run_dir, *args):
    done = subprocess.run([sys.executable, "-I", str(CHECKER), str(run_dir), *args],
                          capture_output=True, text=True, cwd=run_dir.parent)
    return done.returncode, done.stdout + done.stderr


def gh(*ids):
    return json.dumps({"jobs": [{"id": i, "title": "t"} for i in ids]}).encode()


def write_capture(folder, at, boards):
    """boards: {board: {"body": bytes, "new": [keys], "baseline": bool, "md_new": int}}. Every board
    is usable; the trace, results.json and results.md all carry the job count of the body."""
    (folder / "raw").mkdir(parents=True)
    events, rows = [], []
    md = ["| Board | Role | Outcome | Jobs | Baseline | New | Reason |", "|---|---|---|---:|---|---:|---|"]
    for seq, (board, spec) in enumerate(boards.items(), 1):
        raw = f"raw/{board.replace('/', '-')}.body.gz"
        body = spec["body"]
        (folder / raw).write_bytes(gzip.compress(body, mtime=0))
        jobs = len(json.loads(body)["jobs"])
        new, baseline = spec.get("new", []), spec.get("baseline", False)
        events.append({"seq": seq, "at": at, "event": "request", "board": board, "status": 200, "raw": raw,
                       "sha256": hashlib.sha256(body).hexdigest(), "jobs": jobs})
        rows.append({"board": board, "role": "normal", "outcome": "usable", "jobs": jobs,
                     "baseline": baseline, "new_keys": new})
        md.append(f"| {board} | normal | usable | {jobs} | {baseline} | {spec.get('md_new', len(new))} | — |")
    (folder / "trace.json").write_text(json.dumps({"events": events}))
    (folder / "results.json").write_text(json.dumps({"status": "incomplete", "state_advanced": False,
                                                     "boards": rows}))
    (folder / "results.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return folder


class NewKeyCheckTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runs = Path(self._tmp.name) / "runs"

    def capture(self, name, at, boards):
        return write_capture(self.runs / name, at, boards)

    def test_a_correct_new_key_claim_passes(self):
        self.capture("R0", "2026-11-01T00:00:00Z", {"greenhouse/anthropic": {"body": gh(1, 2, 3), "baseline": True}})
        r1 = self.capture("R1", "2026-11-02T00:00:00Z",
                          {"greenhouse/anthropic": {"body": gh(2, 3, 4, 5), "new": ["4", "5"]}})
        code, out = run_check(r1, "--earlier", str(self.runs / "R0"))
        self.assertEqual(code, 0, out)
        self.assertIn("  greenhouse/anthropic: against 1 earlier capture(s): 2 new, "
                      "1 missing from this list (liveness unresolved), 0 returned", out)
        self.assertIn("PASS", out)

    def test_a_wrong_new_key_claim_is_flagged(self):
        self.capture("R0", "2026-11-01T00:00:00Z", {"greenhouse/anthropic": {"body": gh(1, 2, 3), "baseline": True}})
        r1 = self.capture("R1", "2026-11-02T00:00:00Z", {"greenhouse/anthropic": {"body": gh(2, 3, 4, 5), "new": ["4"]}})
        code, out = run_check(r1, "--earlier", str(self.runs / "R0"))
        self.assertEqual(code, 1, out)
        self.assertIn("FLAG greenhouse/anthropic: results.json reports new postings ['4']; recomputed from the "
                      "saved body and the earlier captures: ['4', '5']", out)

    def test_a_returning_key_is_not_new(self):
        self.capture("R0", "2026-11-01T00:00:00Z", {"greenhouse/anthropic": {"body": gh(1, 2), "baseline": True}})
        self.capture("R1", "2026-11-02T00:00:00Z", {"greenhouse/anthropic": {"body": gh(2)}})
        right = self.capture("R2", "2026-11-03T00:00:00Z", {"greenhouse/anthropic": {"body": gh(1, 2, 3), "new": ["3"]}})
        earlier = ("--earlier", str(self.runs / "R0"), "--earlier", str(self.runs / "R1"))
        code, out = run_check(right, *earlier)
        self.assertEqual(code, 0, out)
        self.assertIn("  greenhouse/anthropic: against 2 earlier capture(s): 1 new, "
                      "0 missing from this list (liveness unresolved), 1 returned", out)
        wrong = self.capture("R2-wrong", "2026-11-03T00:00:00Z",
                             {"greenhouse/anthropic": {"body": gh(1, 2, 3), "new": ["1", "3"]}})
        code, out = run_check(wrong, *earlier)
        self.assertEqual(code, 1, out)
        self.assertIn("reports new postings ['1', '3']; recomputed from the saved body and the earlier captures: ['3']",
                      out)

    def test_a_board_that_no_earlier_capture_lists_is_a_baseline(self):
        self.capture("R0", "2026-11-01T00:00:00Z", {"greenhouse/anthropic": {"body": gh(1), "baseline": True}})
        right = self.capture("R1", "2026-11-02T00:00:00Z", {
            "greenhouse/anthropic": {"body": gh(1, 2), "new": ["2"]},
            "greenhouse/databricks": {"body": gh(8, 9), "baseline": True}})
        code, out = run_check(right, "--earlier", str(self.runs / "R0"))
        self.assertEqual(code, 0, out)
        wrong = self.capture("R1-wrong", "2026-11-02T00:00:00Z", {
            "greenhouse/anthropic": {"body": gh(1, 2), "new": ["2"]},
            "greenhouse/databricks": {"body": gh(8, 9), "new": ["9"]}})
        code, out = run_check(wrong, "--earlier", str(self.runs / "R0"))
        self.assertEqual(code, 1, out)
        self.assertIn("FLAG greenhouse/databricks: no earlier capture lists this board, so this snapshot is a "
                      "baseline with no new postings, but the report says baseline=False, new=['9']", out)

    def test_a_baseline_claim_for_a_board_with_history_is_flagged(self):
        self.capture("R0", "2026-11-01T00:00:00Z", {"greenhouse/anthropic": {"body": gh(1), "baseline": True}})
        r1 = self.capture("R1", "2026-11-02T00:00:00Z", {"greenhouse/anthropic": {"body": gh(1), "baseline": True}})
        code, out = run_check(r1, "--earlier", str(self.runs / "R0"))
        self.assertEqual(code, 1, out)
        self.assertIn("FLAG greenhouse/anthropic: the report says baseline=True, but an earlier capture lists this "
                      "board", out)

    def test_the_new_count_shown_in_results_md_is_checked(self):
        self.capture("R0", "2026-11-01T00:00:00Z", {"greenhouse/anthropic": {"body": gh(1, 2, 3), "baseline": True}})
        r1 = self.capture("R1", "2026-11-02T00:00:00Z",
                          {"greenhouse/anthropic": {"body": gh(2, 3, 4, 5), "new": ["4", "5"], "md_new": 3}})
        code, out = run_check(r1, "--earlier", str(self.runs / "R0"))
        self.assertEqual(code, 1, out)
        self.assertIn("FLAG greenhouse/anthropic: results.md shows 3 new; recomputed from the saved body and the "
                      "earlier captures: 2", out)

    def test_an_earlier_capture_that_does_not_match_its_hash_is_flagged(self):
        r0 = self.capture("R0", "2026-11-01T00:00:00Z", {"greenhouse/anthropic": {"body": gh(1, 2, 3), "baseline": True}})
        (r0 / "raw" / "greenhouse-anthropic.body.gz").write_bytes(gzip.compress(gh(1, 2), mtime=0))
        r1 = self.capture("R1", "2026-11-02T00:00:00Z", {"greenhouse/anthropic": {"body": gh(2, 3, 4), "new": ["4"]}})
        code, out = run_check(r1, "--earlier", str(r0))
        self.assertEqual(code, 1, out)
        self.assertIn("FLAG earlier capture R0: greenhouse/anthropic: raw/greenhouse-anthropic.body.gz does not match "
                      "the sha256 recorded in its trace", out)

    def test_captures_given_out_of_time_order_are_flagged(self):
        r_late = self.capture("R-late", "2026-11-05T00:00:00Z", {"greenhouse/anthropic": {"body": gh(1), "baseline": True}})
        r_now = self.capture("R-now", "2026-11-02T00:00:00Z", {"greenhouse/anthropic": {"body": gh(1, 2), "new": ["2"]}})
        code, out = run_check(r_now, "--earlier", str(r_late))
        self.assertEqual(code, 1, out)
        self.assertIn("FLAG the captures are not in time order: R-late (2026-11-05T00:00:00Z) is given before "
                      "R-now (2026-11-02T00:00:00Z)", out)

    def test_without_earlier_captures_or_state_files_new_keys_are_not_checked(self):
        r1 = self.capture("R1", "2026-11-02T00:00:00Z", {"greenhouse/anthropic": {"body": gh(1, 2), "new": ["1"]}})
        code, out = run_check(r1)
        self.assertEqual(code, 0, out)
        self.assertIn("new postings not checked (no --earlier capture and no state files)", out)


class RealCapturesNewKeyTest(unittest.TestCase):
    """Nov 24 against Nov 8: the two real captures the replays use. The JS3 run claimed 93, 99 and 1 new
    postings against a state file advanced by the Nov 8 run. Claude Code's count of 2026-11-25
    (evidence/2026-11-25-memory-vs-nov-24-lists.txt, read from state.json) found 93 / 99 / 1 new and
    137 / 131 / 3 remembered keys missing from the Nov 24 lists."""

    def test_nov_24_against_nov_8(self):
        code, out = run_check(ROOT / "runs" / "2026-11-24-js3-corpus", "--earlier",
                              str(ROOT / "runs" / "2026-11-08-normal-1"))
        self.assertEqual(code, 0, out)
        for board, new, missing in (("greenhouse/anthropic", 93, 137), ("greenhouse/databricks", 99, 131),
                                    ("ashby/linear", 1, 3)):
            self.assertIn(f"  {board}: against 1 earlier capture(s): {new} new, {missing} missing from this list "
                          "(liveness unresolved), 0 returned", out)


if __name__ == "__main__":
    unittest.main()
