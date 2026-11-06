"""Runs tests/expected/watch_cases.json through the real state.json boundary.

Each case writes (or, for state_before null, does not write) a state.json in a
temporary folder and builds a board response whose ids are JSON numbers, so
the str(id) conversion and the string-to-string comparison are both exercised.
"""

import json
import tempfile
import unittest
from pathlib import Path

from support import load_table

from agent.state import compute_watch, load_state, parse_board_response, write_state

TABLE = load_table("watch_cases.json")


class WatchCases(unittest.TestCase):
    def test_every_case(self):
        for row in TABLE["cases"]:
            with self.subTest(case=row["id"]), tempfile.TemporaryDirectory() as tmp:
                state_path = Path(tmp) / "state.json"
                if row["state_before"] is not None:
                    state_path.write_text(json.dumps(row["state_before"]), encoding="utf-8")
                raw = json.dumps({"jobs": [{"id": i, "title": f"Job {i}"} for i in row["response_ids"]]}).encode()

                postings = parse_board_response(raw)
                watch = compute_watch(load_state(state_path), [p["posting_id"] for p in postings])
                write_state(state_path, watch.state_after)

                self.assertEqual(watch.baseline, row["expect_baseline"], "baseline")
                self.assertEqual(watch.new_ids, row["expect_new"], "new ids")
                saved = json.loads(state_path.read_text(encoding="utf-8"))
                self.assertCountEqual(saved, row["expect_state_after"], "state.json after the run")


if __name__ == "__main__":
    unittest.main()
