"""Removal detection (REVIEW-PACKET.md), written BEFORE the patch.

A posting present in a board's previous successful fetch and absent from the
current one must be reported in a separate "removed" list on that board's
report entry. It must be distinct from "new" (the repeat rule) and from
board_status "failed" (the error policy).

Interface fixed here, before the code:
    report["boards"][board]["removed"]  sorted list of posting ids
    format_report(): the board's line says "<n> removed", and the ids are
                     listed under their own "removed postings" heading

All responses are CONSTRUCTED fixtures (tests/fakes.py); no network.
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agent import loop
from tests.fakes import FakeFetch, greenhouse_body, http_error

GITLAB_URL = "https://boards-api.greenhouse.io/v1/boards/gitlab/jobs?content=true"


class RemovalDetection(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="js2_removal_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.state_file = self.root / "state" / "gitlab_seen.json"

    def _run(self, outcome):
        return loop.run(["gitlab"], root=self.root, fetch=FakeFetch({"/boards/gitlab/": outcome}),
                        approved_new_boards={"gitlab"}, sleep=lambda s: None)

    def _ids(self, *ids):
        return self._run(greenhouse_body(*ids))

    def test_posting_absent_from_second_fetch_is_reported_removed(self):
        self._ids(1, 2, 3)
        report = self._ids(1, 3)
        gitlab = report["boards"]["gitlab"]

        self.assertEqual(gitlab["board_status"], "ok")  # not "failed"
        self.assertEqual(gitlab["removed"], [2])
        self.assertEqual(gitlab["new"], [])
        self.assertEqual(report["exit"], "finished")

        text = loop.format_report(report)
        line = next(l for l in text.splitlines() if l.strip().startswith("gitlab"))
        self.assertIn("1 removed", line)
        self.assertNotIn("FAILED", line)
        self.assertIn("removed postings", text)
        self.assertIn("[gitlab] id 2", text)
        self.assertNotIn("new postings", text)

    def test_removed_and_new_in_the_same_run_stay_separate(self):
        self._ids(1, 2, 3)
        gitlab = self._ids(1, 3, 4)["boards"]["gitlab"]
        self.assertEqual(gitlab["removed"], [2])
        self.assertEqual([p["id"] for p in gitlab["new"]], [4])

    def test_baseline_run_reports_no_removals(self):
        gitlab = self._ids(1, 2, 3)["boards"]["gitlab"]
        self.assertTrue(gitlab["baseline"])
        self.assertEqual(gitlab["removed"], [])

    def test_unchanged_board_reports_no_removals(self):
        self._ids(1, 2, 3)
        self.assertEqual(self._ids(1, 2, 3)["boards"]["gitlab"]["removed"], [])

    def test_a_removal_is_reported_once_not_on_every_later_run(self):
        self._ids(1, 2, 3)
        self.assertEqual(self._ids(1, 3)["boards"]["gitlab"]["removed"], [2])
        self.assertEqual(self._ids(1, 3)["boards"]["gitlab"]["removed"], [])

    def test_removed_id_that_reappears_is_not_reported_new(self):
        # Repeat rule (GATE.md): an id already in seen-state is never re-reported as new.
        self._ids(1, 2, 3)
        self._ids(1, 3)
        gitlab = self._ids(1, 2, 3)["boards"]["gitlab"]
        self.assertEqual(gitlab["new"], [])
        self.assertEqual(gitlab["removed"], [])

    def test_failed_board_reports_no_removals_and_keeps_state(self):
        self._ids(1, 2, 3)
        before = self.state_file.read_bytes()
        report = self._run(http_error(GITLAB_URL, 404, "Not Found"))
        gitlab = report["boards"]["gitlab"]
        self.assertEqual(gitlab["board_status"], "failed")
        self.assertEqual(gitlab["removed"], [])
        self.assertEqual(self.state_file.read_bytes(), before)

    def test_state_written_before_this_change_falls_back_to_seen_ids(self):
        # State files from earlier runs have seen_ids but no record of the
        # last fetch's ids; for those, the previous set is seen_ids.
        self.state_file.parent.mkdir(parents=True)
        self.state_file.write_text(json.dumps({"board": "gitlab", "ats": "greenhouse",
                                               "seen_ids": [1, 2, 3], "runs": []}))
        self.assertEqual(self._ids(1, 3)["boards"]["gitlab"]["removed"], [2])


if __name__ == "__main__":
    unittest.main()
