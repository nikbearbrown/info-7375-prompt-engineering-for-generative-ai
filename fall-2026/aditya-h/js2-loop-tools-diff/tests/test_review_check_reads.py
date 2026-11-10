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
