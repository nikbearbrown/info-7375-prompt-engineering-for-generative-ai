"""Whole runs on constructed fixtures: baseline, new-since-last, failures that must not move state."""
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jobwatch import board, watch
from jobwatch.persona import PersonaError
from tests.helpers import ROOT, board_bytes, make_posting

DAY1 = [make_posting(1, "Software Engineer", "<p>Python and Redis.</p>"),
        make_posting(2, "Senior Software Engineer", "<p>Python and Redis.</p>")]
DAY2 = DAY1[1:] + [make_posting(3, "Software Engineer II", "<p>Python, Docker.</p>"),
                   make_posting(4, "Sales Engineer", "<p>Python, Docker.</p>")]
T0 = datetime(2026, 10, 30, 12, 0, 0, tzinfo=timezone.utc)


class Runs(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.resume = ROOT / "data" / "supriya-sharma.resume.json"
        self.state = self.dir / "state" / "seen_ids.json"
        self.runs = self.dir / "runs"

    def tearDown(self):
        shutil.rmtree(self.dir)

    def fixture(self, name, postings=None, raw=None):
        path = self.dir / name
        path.write_bytes(raw if raw is not None else board_bytes(postings))
        return path

    def go(self, fixture, minutes=0, **kw):
        return watch.run(self.resume, self.state, self.runs, fixture=fixture,
                         collected_at="2026-10-30T12:00:00Z", now=T0 + timedelta(minutes=minutes), **kw)

    def seen(self):
        return json.loads(self.state.read_text())["seen_ids"]

    def test_first_run_is_a_baseline_with_zero_new(self):
        s = self.go(self.fixture("d1.json", DAY1))
        self.assertTrue(s["baseline"])
        self.assertEqual((s["postings_observed"], s["new_ids"]), (2, 0))
        self.assertEqual(self.seen(), ["1", "2"])
        self.assertIn("Baseline run", (Path(s["run_dir"]) / "report.md").read_text())

    def test_second_run_reports_only_new_ids_and_repeat_reports_none(self):
        self.go(self.fixture("d1.json", DAY1))
        s = self.go(self.fixture("d2.json", DAY2), minutes=1)
        report = json.loads((Path(s["run_dir"]) / "report.json").read_text())
        self.assertEqual([r["posting_id"] for r in report["results"]], ["3", "4"])
        self.assertEqual({r["posting_id"]: r["rule_record"]["verdict"] for r in report["results"]},
                         {"3": "RELEVANT", "4": "NOT_RELEVANT"})
        self.assertEqual(self.seen(), ["1", "2", "3", "4"])          # 1 disappeared but stays seen
        again = self.go(self.fixture("d2.json", DAY2), minutes=2)
        self.assertEqual(again["new_ids"], 0)

    def test_same_id_with_changed_title_is_not_new(self):
        self.go(self.fixture("d1.json", DAY1))
        renamed = [dict(DAY1[0], title="Software Engineer (renamed)"), DAY1[1]]
        self.assertEqual(self.go(self.fixture("d1b.json", renamed), minutes=1)["new_ids"], 0)

    def test_raw_bytes_are_saved_unchanged(self):
        f = self.fixture("d1.json", raw=board_bytes(DAY1) + b"\n")
        s = self.go(f)
        self.assertEqual((Path(s["run_dir"]) / "raw-response.json").read_bytes(), f.read_bytes())

    def test_invalid_response_leaves_state_unchanged(self):
        self.go(self.fixture("d1.json", DAY1))
        before = self.state.read_bytes()
        with self.assertRaises(board.BoardError):
            self.go(self.fixture("bad.json", raw=b"<html>maintenance</html>"), minutes=1)
        with self.assertRaises(board.BoardError):
            self.go(self.fixture("dup.json", DAY1 + DAY1[:1]), minutes=2)
        self.assertEqual(self.state.read_bytes(), before)

    def test_failed_report_write_does_not_advance_state(self):
        self.go(self.fixture("d1.json", DAY1))
        before = self.state.read_bytes()

        def broken_writer(run_dir, raw, report):
            raise OSError("disk full (simulated)")
        with self.assertRaises(OSError):
            self.go(self.fixture("d2.json", DAY2), minutes=1, writer=broken_writer)
        self.assertEqual(self.state.read_bytes(), before)
        self.assertEqual(self.go(self.fixture("d2.json", DAY2), minutes=2)["new_ids"], 2)   # still new next time

    def test_invalid_resume_stops_before_fetching(self):
        calls = []
        bad = self.dir / "bad.resume.json"
        bad.write_text('{"name": "Real Person"}')
        with self.assertRaises(PersonaError):
            watch.run(bad, self.state, self.runs, fetcher=lambda: calls.append(1))
        self.assertEqual(calls, [])
        self.assertFalse(self.state.exists())

    def test_seeded_and_fixture_runs_are_labeled(self):
        s = self.go(self.fixture("d1.json", DAY1), seeded=True)
        md = (Path(s["run_dir"]) / "report.md").read_text()
        self.assertEqual(s["mode"], "SEEDED REPLAY")
        self.assertIn("not a fresh live observation", md)
        self.assertIn("2026-10-30T12:00:00Z", md)
        with self.assertRaises(ValueError):
            watch.run(self.resume, self.state, self.runs, fixture=self.fixture("x.json", DAY1))  # no collected_at

    def test_live_mode_uses_the_fetcher_and_records_the_source(self):
        meta = {"url": board.ALLOWED_URL, "status": 200, "fetched_at": "2026-10-30T12:00:00Z",
                "server_date": "Fri, 30 Oct 2026 12:00:00 GMT", "content_type": "application/json"}
        s = watch.run(self.resume, self.state, self.runs, fetcher=lambda: (board_bytes(DAY1), meta), now=T0)
        self.assertEqual(s["mode"], "LIVE")
        self.assertTrue(s["source"]["network"])


if __name__ == "__main__":
    unittest.main()
