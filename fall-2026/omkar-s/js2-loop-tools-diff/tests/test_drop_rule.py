"""Second review (REVIEW-PACKET.md, "Second review"): Omkar's drop rule, GATE.md change log 2026-11-10.

Written BEFORE the change to agent/loop.py and run against the unchanged loop first; that failing
run is saved in review/drop-rule/test-before.txt.

Omkar's rule:
- a board that answers ok with MORE than 50% fewer postings than its last recorded run -> warning
  `suspicious_drop`, but only if the last run had at least 10 postings;
- the first run of a board (no state yet) -> warning `no_baseline`;
- warnings do not change the exit: a run where every board answered is still `finished` (0),
  and every warning is shown in report.md, report.json and the trace.
"""
import json
import os
import unittest

from tests.helpers import TempBase, ok, rd
from tests.test_loop import by_key, run, trace

B = {"ats": "greenhouse", "slug": "dropco"}
KEY = "greenhouse:dropco"


def board(n, start=1):
    """A Greenhouse body with n postings, ids start..start+n-1."""
    jobs = [{"id": i, "title": f"Engineer {i}", "location": {"name": "Boston, MA"},
             "offices": [{"location": "Boston, Massachusetts, United States"}],
             "content": "Python.", "absolute_url": f"https://example.invalid/gh/{i}"}
            for i in range(start, start + n)]
    return json.dumps({"jobs": jobs}).encode()


def two_runs(tb, before, after):
    """Run once with `before` postings (the baseline), then again with `after` postings."""
    run(tb, [B], {"/boards/dropco/": [ok(board(before))]}, label="first")
    return run(tb, [B], {"/boards/dropco/": [ok(board(after))]}, label="second")


def codes(rec):
    return [w["code"] for w in rec.get("warnings") or []]


class DropRule(unittest.TestCase):
    def test_drop_over_half_is_flagged(self):  # the Webflow-like case: 27 -> 1
        with TempBase() as tb:
            res, _, _, _ = two_runs(tb, 27, 1)
            self.assertEqual(codes(by_key(res)[KEY]), ["suspicious_drop"])

    def test_warning_does_not_change_exit(self):  # Omkar chose (b): finished + warning
        with TempBase() as tb:
            res, _, _, _ = two_runs(tb, 27, 1)
            self.assertEqual(res["exit"]["status"], "finished")
            self.assertEqual(res["exit"]["code"], 0)
            self.assertEqual(by_key(res)[KEY]["status"], "ok")

    def test_exactly_half_is_not_flagged(self):  # "more than 50%": 20 -> 10 is exactly 50%
        with TempBase() as tb:
            res, _, _, _ = two_runs(tb, 20, 10)
            self.assertEqual(codes(by_key(res)[KEY]), [])

    def test_just_over_half_is_flagged(self):  # 20 -> 9 is a 55% drop
        with TempBase() as tb:
            res, _, _, _ = two_runs(tb, 20, 9)
            self.assertEqual(codes(by_key(res)[KEY]), ["suspicious_drop"])

    def test_small_board_is_not_flagged(self):  # last run had 9 (< 10): 9 -> 1 is ignored
        with TempBase() as tb:
            res, _, _, _ = two_runs(tb, 9, 1)
            self.assertEqual(codes(by_key(res)[KEY]), [])

    def test_minimum_size_is_inclusive(self):  # last run had exactly 10: 10 -> 4 is flagged
        with TempBase() as tb:
            res, _, _, _ = two_runs(tb, 10, 4)
            self.assertEqual(codes(by_key(res)[KEY]), ["suspicious_drop"])

    def test_first_run_warns_no_baseline(self):
        with TempBase() as tb:
            res, _, _, _ = run(tb, [B], {"/boards/dropco/": [ok(board(5))]}, label="only")
            self.assertEqual(codes(by_key(res)[KEY]), ["no_baseline"])
            self.assertEqual(res["exit"]["status"], "finished")

    def test_growth_is_not_flagged(self):
        with TempBase() as tb:
            res, _, _, _ = two_runs(tb, 12, 30)
            self.assertEqual(codes(by_key(res)[KEY]), [])

    def test_warning_is_in_report_and_trace(self):
        with TempBase() as tb:
            res, _, _, r = two_runs(tb, 27, 1)
            md = rd(os.path.join(tb.path("runs"), res["run_id"], "report.md"))
            self.assertIn("## Warnings", md)
            self.assertIn("suspicious_drop", md)
            self.assertIn("27", md)
            warn = [e for e in trace(r) if e["event"] == "warning"]
            self.assertEqual([(e["board"], e["code"]) for e in warn], [(KEY, "suspicious_drop")])
            self.assertEqual(warn[0]["previous"], 27)
            self.assertEqual(warn[0]["now"], 1)


if __name__ == "__main__":
    unittest.main()
