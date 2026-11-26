"""JS3 Step 6: wrong version W8 (tuning on the held-out labels) and the one-change-at-a-time measurement, on made-up labels."""
import json
import tempfile
import unittest
from pathlib import Path

from jsagent import filter as flt, measure

P = {("t", "1"): {"board": "t", "id": "1", "title": "Data Engineer", "location": {"name": "Boston, MA"},
                  "content": "3 years of experience. You have strong Python and SQL."},
     ("t", "2"): {"board": "t", "id": "2", "title": "Account Executive", "location": {"name": "Boston, MA"},
                  "content": "Sell things. 2 years of experience."},
     ("t", "3"): {"board": "t", "id": "3", "title": "Software Engineer - Data Systems", "location": {"name": "Remote - US"},
                  "content": "3 years of experience. Python, SQL, Spark."}}
ROWS = [{"split": "tuning", "board": "t", "posting_id": "1", "human_label": "relevant"},
        {"split": "tuning", "board": "t", "posting_id": "2", "human_label": "not_relevant"},
        {"split": "heldout", "board": "t", "posting_id": "3", "human_label": "relevant"},
        {"split": "heldout", "board": "t", "posting_id": "2", "human_label": "not_relevant"}]


class W8(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.lock = self.d / "lock.json"
        self.lock.write_text(json.dumps({"heldout_sha256": measure.heldout_hash(ROWS)}))
        self.log = self.d / "log.jsonl"

    def test_W8_choose_refuses_heldout_results(self):
        held = measure.evaluate_split(P, ROWS, "heldout")
        with self.assertRaises(measure.HeldoutViolation):
            measure.choose([held])
        self.assertEqual(len(measure.choose([measure.evaluate_split(P, ROWS, "tuning")])), 1)

    def test_W8_changed_heldout_labels_refused(self):
        tampered = [dict(r, human_label="not_relevant") if r["posting_id"] == "3" else r for r in ROWS]
        with self.assertRaises(measure.HeldoutViolation):
            measure.measure_heldout(P, "baseline", rows=tampered, log_path=self.log, lock_path=self.lock)

    def test_W8_one_look_per_change(self):
        measure.measure_heldout(P, "baseline", rows=ROWS, log_path=self.log, lock_path=self.lock)
        with self.assertRaises(measure.HeldoutViolation):
            measure.measure_heldout(P, "baseline", rows=ROWS, log_path=self.log, lock_path=self.lock)
        self.assertEqual(len(self.log.read_text().splitlines()), 1)


class OneChangeAtATime(unittest.TestCase):
    def test_change_is_undone_after_use(self):
        before = (flt.THRESHOLD, dict(flt.POINTS), flt.check_f1)
        for change in measure.CHANGES:
            measure.evaluate_split(P, ROWS, "tuning", change)
        self.assertEqual((flt.THRESHOLD, flt.POINTS, flt.check_f1), before)

    def test_change_A_moves_only_f1(self):
        base = measure.evaluate_split(P, ROWS, "heldout")
        a = measure.evaluate_split(P, ROWS, "heldout", "A_f1_engineer_data")
        self.assertEqual((base["kept_and_relevant"], a["kept_and_relevant"]), (0, 1))

    def test_metrics(self):
        r = measure.evaluate_split(P, ROWS, "tuning")
        self.assertEqual((r["kept"], r["kept_and_relevant"], r["precision"], r["recall"], r["score_auc"]), (1, 1, 1.0, 1.0, 1.0))


if __name__ == "__main__":
    unittest.main()
