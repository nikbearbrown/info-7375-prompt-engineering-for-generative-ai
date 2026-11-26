"""WV5 (FILTER.md answer 12): the agent treats a failed board as a board with zero jobs.
Uses the REAL live run of 2026-11-25 (runs/20261125T220655Z), where oscarhealth-doesnotexist failed
(not-found) and whoop returned an empty list. Written by Claude Code before js3/filtering.py."""
import json
import pathlib
import unittest

from js3 import corpus, filtering

HERE = pathlib.Path(__file__).resolve().parent.parent
RUN = HERE / "runs" / "20261125T220655Z"
PERSONA = json.loads((HERE / "persona" / "alex_morgan.json").read_text())


class FailedBoardIsNotZeroJobs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.postings, cls.manifest = corpus.build([RUN])
        cls.result = filtering.run(cls.postings, cls.manifest, PERSONA,
                                   filtering.load_config(HERE / "filter-v1.json"))

    def test_the_failed_board_is_named_as_not_checked(self):
        b = self.result["boards"]["oscarhealth-doesnotexist"]
        self.assertFalse(b["checked"])
        self.assertEqual(b["status"], "failed")
        self.assertNotIn("kept", b, "a failed board has no kept count, not a zero")
        lines = corpus.board_report(self.manifest)
        self.assertIn("oscarhealth-doesnotexist: NOT CHECKED, the board failed (not-found); its postings are unknown",
                      lines)

    def test_the_empty_board_is_checked_and_empty(self):
        b = self.result["boards"]["whoop"]
        self.assertTrue(b["checked"])
        self.assertEqual(b["status"], "empty")
        self.assertNotIn("kept", b)

    def test_counts_come_only_from_checked_boards(self):
        ok = {n for n, b in self.manifest["boards_in_latest_run"].items() if b["status"] == "ok"}
        self.assertEqual(ok, {"oscar", "klaviyo", "linear", "palantir"})
        self.assertEqual(sum(self.result["boards"][n]["postings"] for n in ok), len(self.postings))
        self.assertEqual(len(self.postings), 637)

    def test_every_posting_has_one_verdict(self):
        self.assertEqual(len(self.result["records"]), len(self.postings))
        verdicts = {r["verdict"] for r in self.result["records"]}
        self.assertLessEqual(verdicts, {"Relevant", "Not Relevant", "I cannot tell"})


if __name__ == "__main__":
    unittest.main()
