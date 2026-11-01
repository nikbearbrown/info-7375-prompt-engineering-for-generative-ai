import json
import tempfile
import unittest
from pathlib import Path

from js1 import watch

FIXTURES = Path(__file__).parent / "fixtures"


def _board(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class WatchTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.state = Path(self._tmp.name) / "state" / "seen_ids.json"

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, fixture):
        result = watch.diff(_board(fixture), watch.load_seen(self.state))
        watch.save_seen(self.state, result.seen_after)
        return result

    def test_baseline_reports_zero_new_and_records_all_ids(self):
        self.assertIsNone(watch.load_seen(self.state))
        result = self._run("constructed_board_run1.json")
        self.assertTrue(result.baseline)
        self.assertEqual(result.new_postings, [])
        self.assertEqual(watch.load_seen(self.state), {9000001, 9000002, 9000003})

    def test_new_since_last_by_id(self):
        self._run("constructed_board_run1.json")
        result = self._run("constructed_board_run2.json")
        self.assertFalse(result.baseline)
        self.assertEqual([job["id"] for job in result.new_postings], [9000004, 9000005])
        self.assertEqual(watch.load_seen(self.state), {9000001, 9000002, 9000003, 9000004, 9000005})

    def test_same_response_twice_reports_nothing_new(self):
        self._run("constructed_board_run1.json")
        self._run("constructed_board_run2.json")
        self.assertEqual(self._run("constructed_board_run2.json").new_postings, [])

    def test_new_postings_are_the_input_postings_unchanged(self):
        self._run("constructed_board_run1.json")
        board2 = _board("constructed_board_run2.json")
        by_id = {job["id"]: job for job in board2["jobs"]}
        for job in watch.diff(board2, watch.load_seen(self.state)).new_postings:
            self.assertEqual(job, by_id[job["id"]])


if __name__ == "__main__":
    unittest.main()
