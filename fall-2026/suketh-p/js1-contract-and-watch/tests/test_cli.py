"""The command a TA runs, against a constructed saved response. No network."""

import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.helpers import OTHER_1, PERSONA_PATH, RELEVANT_101, ROOT, board_bytes, persona


def cli(*args):
    return subprocess.run([sys.executable, "-m", "jobwatch", *args], cwd=ROOT,
                          capture_output=True, text=True, timeout=120)


class CommandLineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.saved = self.root / "saved.json"
        self.saved.write_bytes(board_bytes(OTHER_1, RELEVANT_101))

    def tearDown(self):
        self.tmp.cleanup()

    def test_seeded_baseline_runs_from_the_command_line(self):
        proc = cli("run", "--from-file", str(self.saved), "--resume", str(PERSONA_PATH),
                   "--state", str(self.root / "state.json"), "--out", str(self.root / "runs"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("baseline", proc.stdout.lower())
        self.assertIn("seeded", proc.stdout.lower())
        saved_state = json.loads((self.root / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(saved_state["seen_ids"], [1, 101])

    def test_rule_command_recomputes_one_record(self):
        proc = cli("rule", "--raw", str(self.saved), "--id", "101", "--resume", str(PERSONA_PATH))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["verdict"], "relevant")

    def test_rule_command_reads_a_gzipped_saved_response(self):
        packed = self.root / "saved.json.gz"
        packed.write_bytes(gzip.compress(self.saved.read_bytes()))
        proc = cli("rule", "--raw", str(packed), "--id", "101", "--resume", str(PERSONA_PATH))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["posting_id"], 101)

    def test_verify_checks_the_packed_raw_response_against_its_recorded_hash(self):
        runs = self.root / "runs"
        proc = cli("run", "--from-file", str(self.saved), "--resume", str(PERSONA_PATH),
                   "--state", str(self.root / "state.json"), "--out", str(runs))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        [run_dir] = runs.iterdir()
        raw = run_dir / "raw_response.json"
        (run_dir / "raw_response.json.gz").write_bytes(gzip.compress(raw.read_bytes()))
        raw.unlink()
        self.assertEqual(cli("verify", str(run_dir)).returncode, 0)
        (run_dir / "raw_response.json.gz").write_bytes(gzip.compress(b'{"jobs": []}'))
        self.assertNotEqual(cli("verify", str(run_dir)).returncode, 0)

    def test_a_rejected_resume_exits_nonzero_without_echoing_it(self):
        real_looking = persona()
        real_looking["email"] = "alex.realperson@gmail.com"
        path = self.root / "real.json"
        path.write_text(json.dumps(real_looking), encoding="utf-8")
        proc = cli("run", "--from-file", str(self.saved), "--resume", str(path),
                   "--state", str(self.root / "state.json"), "--out", str(self.root / "runs"))
        self.assertNotEqual(proc.returncode, 0)
        self.assertNotIn("realperson", proc.stdout + proc.stderr)
        self.assertFalse((self.root / "state.json").exists())


if __name__ == "__main__":
    unittest.main()
