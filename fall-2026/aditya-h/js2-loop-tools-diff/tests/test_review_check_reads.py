"""Review packet test, created and run by Aditya on 2026-11-10 BEFORE the patch.
Decision (Aditya): when a run record points outside the assignment folder, check_run must refuse and stop."""
import datetime as dt
import json
import pathlib
import tempfile
import unittest

import check_run


class CheckRefusesOutsideReads(unittest.TestCase):
    def test_record_pointing_outside_folder_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            root = d / "js2"
            (root / "runs" / "r1").mkdir(parents=True)
            (root / "checks.json").write_text(json.dumps(
                {"cross_check": {}, "min_postings": 3, "max_newest_age_days": 14}))
            outside = d / "outside.json"                      # a file NOT inside root
            outside.write_text(json.dumps({"jobs": []}))
            record = {"exit": "finished", "boards": [{"key": "greenhouse/stripe", "ats": "greenhouse",
                      "status": "ok", "fetched": 0, "raw_path": str(outside)}]}
            (root / "runs" / "r1" / "record.json").write_text(json.dumps(record))

            # refuse: the check must raise PermissionError instead of reading the outside file
            with self.assertRaises(PermissionError):
                check_run.check(root, root / "runs" / "r1", today=dt.date(2026, 11, 10))

            # stop: no verdict may be written
            self.assertFalse((root / "runs" / "r1" / "check.json").exists())


if __name__ == "__main__":
    unittest.main()


class CheckRefusesWrongFileInsideFolder(unittest.TestCase):
    """Added by Aditya on 2026-11-10 after reviewing patch v1 (decision: revise).
    A raw_path inside the folder is still wrong unless it is THIS run's raw file for THAT board."""

    def make(self, raw_rel):
        self.tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.tmp.name) / "js2"
        run = root / "runs" / "r2"
        (run / "raw").mkdir(parents=True)
        (root / "runs" / "r1" / "raw").mkdir(parents=True)
        (root / "personas").mkdir()
        (root / "checks.json").write_text(json.dumps(
            {"cross_check": {}, "min_postings": 3, "max_newest_age_days": 14}))
        body = json.dumps({"jobs": [{"id": i, "title": "X", "location": {"name": "US"}, "offices": [{"name": "US"}],
                                     "first_published": "2026-11-09T00:00:00Z"} for i in range(5)]})
        for rel in ("runs/r1/raw/greenhouse__stripe.attempt1.json", "runs/r2/raw/greenhouse__stripe.attempt1.json",
                    "runs/r2/raw/ashby__openai.attempt1.json", "personas/other.json"):
            (root / rel).write_text(body)
        (run / "record.json").write_text(json.dumps({"exit": "finished", "boards": [
            {"key": "greenhouse/stripe", "ats": "greenhouse", "status": "ok", "fetched": 5,
             "raw_path": str(root / raw_rel)}]}))
        return root, run

    def tearDown(self):
        self.tmp.cleanup()

    def refused(self, raw_rel):
        root, run = self.make(raw_rel)
        with self.assertRaises(PermissionError):
            check_run.check(root, run, today=dt.date(2026, 11, 10))
        self.assertFalse((run / "check.json").exists())

    def test_other_runs_raw_file_refused(self):
        self.refused("runs/r1/raw/greenhouse__stripe.attempt1.json")

    def test_other_boards_raw_file_refused(self):
        self.refused("runs/r2/raw/ashby__openai.attempt1.json")

    def test_non_raw_file_in_folder_refused(self):
        self.refused("personas/other.json")

    def test_this_runs_raw_for_this_board_still_works(self):
        root, run = self.make("runs/r2/raw/greenhouse__stripe.attempt1.json")
        rep = check_run.check(root, run, today=dt.date(2026, 11, 10))
        self.assertEqual(rep["verdict"], "consistent")
