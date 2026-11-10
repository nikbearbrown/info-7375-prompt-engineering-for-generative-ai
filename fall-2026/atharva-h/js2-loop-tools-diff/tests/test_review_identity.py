"""Review packet: board identity regression test written before the patch (2026-11-10).

Defect: runs/2026-11-09T205807Z_WRONG-BOARD-demo finished on another employer's board.
"""
import json
import unittest

from helpers import GH, board, gh_body, make, read_state
from test_loop import go

NAME = "https://boards-api.greenhouse.io/v1/boards/{}"


class LoopChecksBoardIdentity(unittest.TestCase):
    def test_wrong_employer_board_does_not_finish(self):
        boards = [board("greenhouse", "abacus", "Abacus Insights")]
        script = {GH.format("abacus"): [(200, gh_body(1, 2, 3))],
                  NAME.format("abacus"): [(200, json.dumps({"name": "ABACUS"}).encode())]}
        root, tools = make(boards, script)
        run_dir, s = go(tools)

        self.assertEqual(s["exit"], "incomplete")
        result = s["results"]["greenhouse/abacus"]
        self.assertEqual(result["status"], "failed")
        self.assertIn("Abacus Insights", result["reason"])
        self.assertIn("ABACUS", result["reason"])
        self.assertNotIn("greenhouse/abacus", read_state(root)["boards"])

    def test_matching_employer_board_still_succeeds(self):
        boards = [board("greenhouse", "abacusinsights", "Abacus Insights")]
        script = {GH.format("abacusinsights"): [(200, gh_body(1, 2))],
                  NAME.format("abacusinsights"): [(200, json.dumps({"name": "Abacus Insights"}).encode())]}
        root, tools = make(boards, script)
        run_dir, s = go(tools)

        self.assertEqual(s["exit"], "finished")
        self.assertEqual(s["results"]["greenhouse/abacusinsights"]["status"], "ok")
        self.assertEqual(read_state(root)["boards"]["greenhouse/abacusinsights"]["seen"], ["1", "2"])


if __name__ == "__main__":
    unittest.main()
