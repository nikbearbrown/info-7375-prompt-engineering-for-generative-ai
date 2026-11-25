"""CONTRACT.md In (State) and Out (new, gone, ids never removed)."""

import json
import tempfile
import unittest
from pathlib import Path

from job_agent import state
from job_agent.errors import BrokenInput

from .helpers import job

RUN = {"run_id": "r1", "started_at": "2026-10-30T12:00:00Z", "response_sha256": "x", "postings": 0, "source": "test"}


class StateTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.path = self.dir / "state" / "seen.json"

    def test_no_state_file_means_baseline(self):
        self.assertIsNone(state.load(self.path))
        found = state.diff(None, [job("a-1")])
        self.assertTrue(found.baseline)
        self.assertEqual((found.new, found.gone), ([], []))

    def test_unreadable_state_files_stop_the_run(self):
        for text in ("{not json", json.dumps({"schema": 99}), json.dumps({"schema": 1, "seen_ids": "a-1"}),
                     json.dumps({"schema": 1, "seen_ids": [], "last_run": {}, "runs": []})):
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(text, encoding="utf-8")
            with self.subTest(text=text), self.assertRaises(BrokenInput):
                state.load(self.path)

    def test_new_is_never_seen_before_and_gone_is_missing_since_last_run(self):
        first = state.next_state(None, [job("a-1"), job("a-2"), job("a-3")], RUN)
        found = state.diff(first, [job("a-1"), job("a-2"), job("b-4")])
        self.assertFalse(found.baseline)
        self.assertEqual([j["id"] for j in found.new], ["b-4"])
        self.assertEqual(found.gone, [("a-3", "Software Engineer, Example Team")])

    def test_ids_are_never_removed_so_a_returning_posting_is_not_new(self):
        first = state.next_state(None, [job("a-1"), job("a-2")], RUN)
        second = state.next_state(first, [job("a-1")], dict(RUN, run_id="r2"))
        self.assertEqual(second["seen_ids"], ["a-1", "a-2"])
        self.assertEqual(state.diff(second, [job("a-1"), job("a-2")]).new, [])
        self.assertEqual([r["run_id"] for r in second["runs"]], ["r1", "r2"])

    def test_a_duplicated_id_counts_once(self):
        first = state.next_state(None, [job("a-1")], RUN)
        found = state.diff(first, [job("b-1"), job("b-1")])
        self.assertEqual([j["id"] for j in found.new], ["b-1"])

    def test_save_then_load_round_trips_and_leaves_no_temporary_file(self):
        data = state.next_state(None, [job("a-1")], RUN)
        state.save(self.path, data)
        self.assertEqual(state.load(self.path), data)
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), ["seen.json"])


if __name__ == "__main__":
    unittest.main()
