"""CONTRACT.md Out (baseline, new since last run, raw saved first) and Refuses 5 (no made-up jobs).

Every board response here is a small CONSTRUCTED fixture, not a real Pinterest response.
"""
import io
import json
import shutil
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from agent import __main__ as cli
from agent import config, watch


def board(*ids):
    jobs = [{"id": i, "title": f"Constructed job {i}", "company_name": "Pinterest",
             "location": {"name": "Remote, US"}} for i in ids]
    return json.dumps({"_comment": "CONSTRUCTED test fixture, not a real response", "jobs": jobs}).encode()


T1 = datetime(2026, 10, 30, 12, 0, 0, tzinfo=timezone.utc)
T2 = datetime(2026, 10, 31, 12, 0, 0, tzinfo=timezone.utc)


class WatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.raw_dir, self.state = self.tmp / "raw", self.tmp / "seen_ids.json"

    def run_once(self, raw, now, seeded=False):
        return watch.run_watch(raw, raw_dir=self.raw_dir, state_path=self.state, now=now, seeded=seeded)

    def test_first_run_reports_zero_new(self):
        result = self.run_once(board(1, 2, 3), T1)
        self.assertTrue(result.baseline)
        self.assertEqual(result.new_jobs, [])
        self.assertEqual(json.loads(self.state.read_text())["seen_ids"], [1, 2, 3])

    def test_second_run_reports_only_unseen_ids(self):
        self.run_once(board(1, 2, 3), T1)
        result = self.run_once(board(2, 3, 4, 5), T2)
        self.assertFalse(result.baseline)
        self.assertEqual([j["id"] for j in result.new_jobs], [4, 5])
        self.assertEqual(json.loads(self.state.read_text())["seen_ids"], [1, 2, 3, 4, 5])

    def test_duplicate_ids_reported_once(self):
        self.run_once(board(1), T1)
        result = self.run_once(board(1, 7, 7), T2)
        self.assertEqual([j["id"] for j in result.new_jobs], [7])

    def test_raw_response_saved_before_state_update(self):
        self.run_once(board(1, 2), T1)
        before = self.state.read_text()
        with self.assertRaises(watch.NotAJobList):
            self.run_once(b"<html>maintenance page</html>", T2)
        self.assertEqual(self.state.read_text(), before, "a bad response must not change the state")
        saved = sorted(p.name for p in self.raw_dir.iterdir())
        self.assertIn("pinterest-20261031T120000Z.json", saved, "the raw response is saved even when it is bad")

    def test_report_lists_only_ids_in_raw_response(self):
        self.run_once(board(1, 2), T1)
        raw = board(2, 3, 9)
        result = self.run_once(raw, T2)
        raw_ids = {j["id"] for j in json.loads(raw)["jobs"]}
        self.assertTrue({j["id"] for j in result.new_jobs} <= raw_ids)
        report = watch.format_report(result, "test")
        for job_id in (3, 9):
            self.assertIn(f"| {job_id} |", report)
        self.assertNotIn("| 1 |", report)


class CommandLineTests(unittest.TestCase):
    """Runs `python3 -m agent watch` with every path moved into a temporary folder."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.paths = {"RAW_DIR": self.tmp / "raw", "RUNS_DIR": self.tmp / "runs",
                      "STATE": self.tmp / "seen_ids.json", "SEEDED_STATE": self.tmp / "seen_ids-SEEDED.json",
                      "CLAUDE_DIR": self.tmp / "claude"}
        self.patches = [mock.patch.object(config, k, v) for k, v in self.paths.items()]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.main(["watch", *argv])
        return code, out.getvalue(), err.getvalue()

    def test_failed_fetch_leaves_state_unchanged(self):
        self.paths["STATE"].write_text('{"board": "pinterest", "seen_ids": [1], "runs": []}\n')
        before = self.paths["STATE"].read_text()
        with mock.patch("agent.fetch.fetch", side_effect=urllib.error.URLError("network down")):
            code, _, err = self.main()
        self.assertEqual(code, 1)
        self.assertIn("state file was not changed", err)
        self.assertEqual(self.paths["STATE"].read_text(), before)
        self.assertFalse(self.paths["RAW_DIR"].exists(), "nothing is saved when the fetch itself fails")

    def test_refused_resume_stops_before_fetch(self):
        bad = self.tmp / "real.json"
        bad.write_text(json.dumps({"personal": {"name": "Someone", "email": "someone@gmail.com", "phone": "617 373 2000"}}))
        with mock.patch("agent.fetch.fetch") as fake_fetch:
            code, _, err = self.main("--resume", str(bad))
        self.assertEqual(code, 2)
        self.assertIn("refused", err)
        fake_fetch.assert_not_called()

    def test_seeded_run_is_labelled(self):
        saved = self.tmp / "earlier.json"
        saved.write_bytes(board(1, 2))
        code, out, _ = self.main("--from-file", str(saved))
        self.assertEqual(code, 0)
        self.assertIn("(SEEDED)", out)
        self.assertTrue(self.paths["SEEDED_STATE"].exists())
        self.assertFalse(self.paths["STATE"].exists(), "a seeded run never touches the live state")
        self.assertTrue(all("SEEDED" in p.name for p in self.paths["RAW_DIR"].iterdir()))
        self.assertTrue(all("SEEDED" in p.name for p in self.paths["RUNS_DIR"].iterdir()))

    def test_second_run_shows_both_judges_labelled(self):
        with mock.patch("agent.fetch.fetch", return_value=board(10, 11)):
            self.main()
        constructed = {"kind": "judgment (Claude, prompt contract)", "valid": True, "error": None,
                       "parsed": {"verdict": "Not Relevant", "reason": "constructed reply"}}
        with mock.patch("agent.fetch.fetch", return_value=board(10, 11, 12)), \
                mock.patch("agent.claude_judge.judge", return_value=constructed) as fake_judge:
            code, out, _ = self.main()
        self.assertEqual(code, 0)
        fake_judge.assert_called_once()
        self.assertIn("Rule (record, recomputable):", out)
        self.assertIn("Claude (judgment, not a fact):", out)
        self.assertTrue(list((self.paths["CLAUDE_DIR"] / "watch").rglob("12.json")), "Claude's reply is saved")

    def test_no_claude_flag_still_runs_the_rule(self):
        with mock.patch("agent.fetch.fetch", return_value=board(10)):
            self.main()
        with mock.patch("agent.fetch.fetch", return_value=board(10, 12)), \
                mock.patch("agent.claude_judge.judge") as fake_judge:
            code, out, _ = self.main("--no-claude")
        self.assertEqual(code, 0)
        fake_judge.assert_not_called()
        self.assertIn("Rule (record, recomputable):", out)
        self.assertIn("not run (`--no-claude`)", out)

    def test_live_baseline_through_the_command_line(self):
        with mock.patch("agent.fetch.fetch", return_value=board(10, 11)) as fake_fetch:
            code, out, _ = self.main()
        self.assertEqual(code, 0)
        fake_fetch.assert_called_once_with(config.BOARD_URL)
        self.assertIn("Baseline run", out)
        self.assertNotIn("SEEDED", out)


if __name__ == "__main__":
    unittest.main()
