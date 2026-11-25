"""The command line's exit codes: 0 done, 2 broken input, 3 refused. Offline: runs use --replay."""

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from job_agent import __main__ as cli

from .helpers import PERSONA, board_bytes, job


def call(*argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = cli.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        self.saved = self.dir / "saved" / "response.json"
        self.saved.parent.mkdir()
        self.saved.write_bytes(board_bytes([job("a-1"), job("a-2")]))

    def test_check_resume_accepts_jane(self):
        code, out, _ = call("check-resume", str(PERSONA))
        self.assertEqual(code, 0)
        self.assertIn("valid fictional persona", out)
        self.assertNotIn("Jane Doe", out)

    def test_check_resume_refuses_a_real_looking_resume_with_exit_3(self):
        data = json.loads(PERSONA.read_text(encoding="utf-8"))
        data["fictional"] = False
        path = self.dir / "r.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        code, _, err = call("check-resume", str(path))
        self.assertEqual(code, 3)
        self.assertIn("fictional", err)

    def test_a_replay_into_the_live_state_is_refused(self):
        code, _, err = call("run", "--replay", str(self.saved))
        self.assertEqual(code, 3)
        self.assertIn("own --state and --runs", err)

    def test_a_replay_runs_offline_into_its_own_folders(self):
        code, out, _ = call("run", "--replay", str(self.saved), "--state", str(self.dir / "s.json"),
                            "--runs", str(self.dir / "runs"))
        self.assertEqual(code, 0)
        self.assertIn("baseline: 2 postings recorded, 0 new", out)

    def test_a_broken_saved_response_exits_2(self):
        self.saved.write_bytes(b"not json")
        code, _, err = call("run", "--replay", str(self.saved), "--state", str(self.dir / "s.json"),
                            "--runs", str(self.dir / "runs"))
        self.assertEqual(code, 2)
        self.assertIn("not JSON", err)

    def test_a_missing_prompt_file_stops_before_any_fetch_with_exit_2(self):
        code, _, err = call("run", "--replay", str(self.saved), "--state", str(self.dir / "s.json"),
                            "--runs", str(self.dir / "runs"), "--prompt", str(self.dir / "no-such-prompt.txt"))
        self.assertEqual(code, 2)
        self.assertIn("prompt file", err)
        self.assertFalse((self.dir / "runs").exists())

    def test_a_resume_with_a_broken_rule_field_exits_2(self):
        data = json.loads(PERSONA.read_text(encoding="utf-8"))
        del data["experience"]["full_time_years"]
        path = self.dir / "broken.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        code, _, err = call("check-resume", str(path))
        self.assertEqual(code, 2)
        self.assertIn("experience.full_time_years", err)
        self.assertNotIn("broken.json", err)  # the file's name is never printed


if __name__ == "__main__":
    unittest.main()
