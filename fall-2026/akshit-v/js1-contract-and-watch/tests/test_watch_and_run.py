"""New-since-last by id, baseline behavior, and an end-to-end run on CONSTRUCTED saved responses."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from agent import run, watch
from agent.config import ROOT
from tests.helpers import JACK, constructed_greenhouse_job, constructed_posting

RESUME = ROOT / "data" / "resume_jack_spencer.json"


class Watch(unittest.TestCase):
    def test_baseline_reports_none(self):
        self.assertIsNone(watch.find_new(None, "figma", [constructed_posting(1, "x")]))

    def test_reports_only_unseen_ids(self):
        state = {"board": "figma", "seen_ids": [1, 2], "runs": []}
        posts = [constructed_posting(i, "x") for i in (1, 2, 3)]
        self.assertEqual(watch.find_new(state, "figma", posts), [3])

    def test_seen_ids_are_a_union(self):
        state = watch.next_state(None, "figma", [constructed_posting(1, "x")], {})
        state = watch.next_state(state, "figma", [constructed_posting(2, "x")], {})
        self.assertEqual(state["seen_ids"], [1, 2])  # 1 vanished but is still "seen"

    def test_board_mismatch_refused(self):
        with self.assertRaises(ValueError):
            watch.find_new({"board": "asana", "seen_ids": [], "runs": []}, "figma", [])


def write_constructed_response(path: Path, jobs: list[dict]) -> Path:
    path.write_text(json.dumps({"jobs": jobs}), encoding="utf-8")
    path.with_suffix(".meta.json").write_text(json.dumps({"kind": "constructed"}), encoding="utf-8")
    return path


class EndToEnd(unittest.TestCase):
    def run_agent(self, tmp: Path, raw: Path, resume: Path = RESUME):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = run.main(["--board", "figma", "--resume", str(resume), "--from-file", str(raw),
                             "--state", str(tmp / "state.json"), "--runs-dir", str(tmp / "runs"), "--no-claude"])
        return code, out.getvalue()

    def test_baseline_then_second_run(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            first = write_constructed_response(tmp / "first.json", [
                constructed_greenhouse_job(1, "Account Executive")])
            second = write_constructed_response(tmp / "second.json", [
                constructed_greenhouse_job(1, "Account Executive"),
                constructed_greenhouse_job(2, "Data Engineer", "&lt;p&gt;Python, SQL, Spark&lt;/p&gt;")])

            code, out = self.run_agent(tmp, first)
            self.assertEqual(code, 0)
            self.assertIn("BASELINE", out)
            self.assertNotIn("id 1 |", out)

            code, out = self.run_agent(tmp, second)
            self.assertIn("new since last run: 1", out)
            self.assertIn("id 2 | Data Engineer", out)
            self.assertIn("RULE (record, recomputable):  relevant", out)
            self.assertNotIn("id 1 |", out)
            self.assertIn("kind=CONSTRUCTED", out)

    def test_bad_resume_stops_before_anything(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            bad = tmp / "resume.json"
            bad.write_text(json.dumps({**JACK, "email": "a@gmail.com"}), encoding="utf-8")
            raw = write_constructed_response(tmp / "r.json", [constructed_greenhouse_job(1, "x")])
            code, out = self.run_agent(tmp, raw, resume=bad)
            self.assertEqual(code, 2)
            self.assertEqual(out, "")
            self.assertFalse((tmp / "state.json").exists())


if __name__ == "__main__":
    unittest.main()
