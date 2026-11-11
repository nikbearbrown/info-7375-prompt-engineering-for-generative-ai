"""Review-packet test (REVIEW-PACKET.md). Written BEFORE the patch to agent/loop.py, and run
against the pre-patch code first; that failing run is saved in review/test-before-patch.txt.

Defect (reproduced live 2026-11-09, runs/wrong-answer-demo/*prepatch*): Webflow's Greenhouse
board answers HTTP 200 {"jobs": []}. The loop reported it as ok, 0 postings, 0 new, and the run
exited `finished` (code 0), though Webflow had 22 postings on Ashby at that moment.

GATE.md section 4 requires: HTTP 200 with zero postings -> board status `empty_unverified`,
`new` is null (not "0 new jobs"), the run is not `finished`, and the board's state is not updated.
"""
import os
import unittest

from tests.helpers import TempBase, fixture_bytes, ok, rd
from tests.test_loop import B_AS, B_GH, by_key, run

EMPTY = fixture_bytes("greenhouse-empty.json")
B_EMPTY = {"ats": "greenhouse", "slug": "webflowx"}


class EmptyBoard(unittest.TestCase):
    def script(self):
        return {"/boards/alpha/": [ok(fixture_bytes("greenhouse-2.json"))],
                "job-board/beta": [ok(fixture_bytes("ashby-2.json"))],
                "/boards/webflowx/": [ok(EMPTY)]}

    def test_empty_board_is_not_finished(self):
        with TempBase() as tb:
            res, _, _, _ = run(tb, [B_GH, B_AS, B_EMPTY], self.script())
            self.assertNotEqual(res["exit"]["status"], "finished")
            self.assertNotEqual(res["exit"]["code"], 0)
            self.assertEqual(res["exit"]["status"], "incomplete")
            self.assertIn("greenhouse:webflowx", res["exit"]["why"])

    def test_empty_board_status_and_null_new(self):
        with TempBase() as tb:
            res, _, _, _ = run(tb, [B_EMPTY], self.script())
            e = by_key(res)["greenhouse:webflowx"]
            self.assertEqual(e["status"], "empty_unverified")
            self.assertEqual(e["postings"], 0)  # observed: the board really returned 0 ...
            self.assertIsNone(e["new"])           # ... but "0 new jobs" is not claimed
            md = rd(os.path.join(tb.path("runs"), res["run_id"], "report.md"))
            self.assertNotIn("| `greenhouse:webflowx` | ok |", md)
            self.assertIn("empty_unverified", md)

    def test_empty_board_does_not_write_state(self):
        with TempBase() as tb:
            run(tb, [B_EMPTY], self.script(), label="a")
            self.assertFalse(os.path.exists(tb.path("runs", "state", "greenhouse-webflowx.state.json")))

    def test_empty_board_trace_and_report_agree(self):
        """Added during review of patch v1 (REVIEW-PACKET.md, 'Revise'): v1 passed the three tests
        above, but its trace still said outcome 'ok' for the empty board, and report.md said
        'Postings: 0 (null = not observed ...)'. Written and run against v1 before patch v2."""
        import json
        with TempBase() as tb:
            res, _, _, r = run(tb, [B_EMPTY], self.script())
            with open(r.trace_path) as f:
                obs = [json.loads(l) for l in f if '"observation"' in l]
            self.assertEqual([o["outcome"] for o in obs], ["empty"])
            md = rd(os.path.join(tb.path("runs"), res["run_id"], "report.md"))
            self.assertNotIn("Postings: 0 (null = not observed", md)
            self.assertIn("Postings: 0 observed; new: null", md)

    def test_non_empty_board_still_ok(self):  # the patch must not break the normal path
        with TempBase() as tb:
            res, _, _, _ = run(tb, [B_GH, B_AS], self.script())
            self.assertEqual(res["exit"]["status"], "finished")


if __name__ == "__main__":
    unittest.main()
