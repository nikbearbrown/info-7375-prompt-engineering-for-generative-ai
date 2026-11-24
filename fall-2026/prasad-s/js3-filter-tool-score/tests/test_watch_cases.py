"""Runs tests/expected/watch_cases.json through the real state boundary.

JS2 (CONTRACT v0.5 item 4, v0.6 items 1-2): state lives in state/state_<UTC>.json,
one section per board key, read and written through the tool layer. Each case
writes (or, for state_before null, does not write) a state file holding the
case's ids under greenhouse:stripe, and builds a board response whose ids are
JSON numbers, so the str(id) conversion and the string-to-string comparison are
both exercised. The table itself is unchanged.
"""

import json
import tempfile
import unittest
from pathlib import Path

from support import load_table

from agent.policy import Policy
from agent.state import commit_state, compute_watch, load_state, parse_board_response, write_state_tmp
from agent.tool_layer import ToolLayer

TABLE = load_table("watch_cases.json")
BOARD = "greenhouse:stripe"


class WatchCases(unittest.TestCase):
    def test_every_case(self):
        for row in TABLE["cases"]:
            with self.subTest(case=row["id"]), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "state").mkdir()
                if row["state_before"] is not None:
                    (root / "state" / "state_2026-11-01T000000Z.json").write_text(
                        json.dumps({BOARD: row["state_before"]}), encoding="utf-8")
                tools = ToolLayer(Policy(root, [("boards-api.greenhouse.io", "stripe")]))
                raw = json.dumps({"jobs": [{"id": i, "title": f"Job {i}"} for i in row["response_ids"]]}).encode()

                postings = parse_board_response(raw)
                _, sections = load_state(tools, "state")
                before = None if sections is None else sections.get(BOARD)
                watch = compute_watch(before, [p["posting_id"] for p in postings])
                commit_state(tools, *write_state_tmp(tools, "state", "2026-11-02T000000Z", {BOARD: watch.state_after}))

                self.assertEqual(watch.baseline, row["expect_baseline"], "baseline")
                self.assertEqual(watch.new_ids, row["expect_new"], "new ids")
                _, saved = load_state(tools, "state")
                self.assertCountEqual(saved[BOARD], row["expect_state_after"], "state after the run")


if __name__ == "__main__":
    unittest.main()
