"""The independent check reads only the saved raw responses. All runs here are CONSTRUCTED."""
import json
import unittest
from datetime import datetime, timezone

from agent import check
from tests.fakes import FakeNet, Project, greenhouse, url

GH = {"name": "acme", "system": "greenhouse"}
DAY1 = datetime(2026, 11, 9, 12, 0, tzinfo=timezone.utc)
DAY2 = datetime(2026, 11, 10, 12, 0, tzinfo=timezone.utc)


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.p = Project(self)
        _, self.state, _ = self.p.run([GH], FakeNet({url("greenhouse", "acme"): [(200, greenhouse(1, 2))]}), now=DAY1)

    def test_a_true_report_passes_and_new_ids_are_recomputed_from_raw_files(self):
        _, _, run_dir = self.p.run([GH], FakeNet({url("greenhouse", "acme"): [(200, greenhouse(1, 2, 3))]}),
                                   state=self.state, now=DAY2)
        problems, notes = check.check(run_dir, self.p.root)
        self.assertEqual(problems, [])
        self.assertEqual(notes, [], "the earlier raw file was there, so new IDs were recomputed")

    def test_a_report_whose_counts_do_not_match_the_raw_file_fails(self):
        _, _, run_dir = self.p.run([GH], FakeNet({url("greenhouse", "acme"): [(200, greenhouse(1, 2, 3))]}),
                                   state=self.state, now=DAY2)
        report = json.loads((run_dir / "report.json").read_text())
        report["boards"][0]["jobs"], report["boards"][0]["new_ids"] = 2, []
        (run_dir / "report.json").write_text(json.dumps(report))
        problems, _ = check.check(run_dir, self.p.root)
        self.assertIn("the run ended `finished`, but its report does not match its own evidence", problems)
        self.assertEqual(len(problems), 3)


if __name__ == "__main__":
    unittest.main()
