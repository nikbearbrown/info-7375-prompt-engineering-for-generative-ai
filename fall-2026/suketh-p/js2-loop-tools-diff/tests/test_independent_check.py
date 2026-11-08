"""The independent check (GATE.md wrong version 1: "check the saved body and
before-and-after state separately from the loop's report").

checks/independent_check.py does not import jobwatch. It recounts jobs and keys from
the saved raw bodies, compares two state files, and flags any claim in results.json
that they contradict. These tests build run folders by hand, so they test the check,
not the agent. It runs in isolated mode (python -I), as a TA would run it."""

import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).resolve().parent.parent / "checks" / "independent_check.py"


def gh(*ids):
    return json.dumps({"jobs": [{"id": i, "title": "t"} for i in ids], "meta": {"total": len(ids)}}).encode()


def state_with(boards):
    return {"schema": "jobwatch-state/2", "runs": [],
            "boards": {name: {"ats": name.split("/")[0], "slug": name.split("/")[1], "first_snapshot_run": "R0",
                              "last_snapshot_run": "R0", "seen": {k: "R0" for k in keys}}
                       for name, keys in boards.items()}}


class CheckCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name)
        self.run_dir = self.base / "runs" / "R1"
        (self.run_dir / "raw").mkdir(parents=True)

    def write_run(self, status, state_advanced, boards):
        """boards: list of dicts with name, outcome, jobs, baseline, new_keys, body, http."""
        events, rows = [], []
        for b in boards:
            raw_name = f"raw/{b['name'].replace('/', '-')}.body.gz"
            body = b["body"]
            (self.run_dir / raw_name).write_bytes(gzip.compress(body))
            events.append({"event": "request", "board": b["name"], "status": b.get("http", 200), "raw": raw_name,
                           "sha256": b.get("sha256", hashlib.sha256(body).hexdigest())})
            rows.append({"board": b["name"], "role": "normal", "outcome": b["outcome"], "jobs": b["jobs"],
                         "baseline": b["baseline"], "new_keys": b["new_keys"]})
        (self.run_dir / "trace.json").write_text(json.dumps({"events": events}))
        (self.run_dir / "results.json").write_text(json.dumps({"status": status, "state_advanced": state_advanced,
                                                               "boards": rows}))

    def write_state(self, name, data):
        path = self.base / name
        path.write_text(json.dumps(data))
        return str(path)

    def check(self, before="none", after="none"):
        done = subprocess.run([sys.executable, "-I", str(CHECKER), str(self.run_dir),
                               "--state-before", before, "--state-after", after],
                              capture_output=True, text=True, cwd=self.base)
        return done.returncode, done.stdout + done.stderr


class IndependentCheckTest(CheckCase):
    def test_a_consistent_finished_baseline_passes(self):
        self.write_run("finished", True, [dict(name="greenhouse/anthropic", outcome="usable", jobs=2,
                                               baseline=True, new_keys=[], body=gh(101, 102))])
        after = self.write_state("after.json", state_with({"greenhouse/anthropic": ["101", "102"]}))
        code, out = self.check(after=after)
        self.assertEqual(code, 0, out)
        self.assertIn("PASS", out)

    def test_an_empty_board_reported_as_checked_is_flagged(self):
        self.write_run("finished", True, [dict(name="ashby/linear", outcome="usable", jobs=0,
                                               baseline=False, new_keys=[], body=b'{"apiVersion":"1","jobs":[]}')])
        before = self.write_state("before.json", state_with({"ashby/linear": ["u1"]}))
        code, out = self.check(before=before, after=before)
        self.assertEqual(code, 1, out)
        self.assertIn("0 jobs", out)

    def test_a_state_change_by_a_run_that_did_not_finish_is_flagged(self):
        self.write_run("incomplete", False, [dict(name="greenhouse/anthropic", outcome="usable", jobs=2,
                                                  baseline=True, new_keys=[], body=gh(101, 102))])
        before = self.write_state("before.json", state_with({}))
        after = self.write_state("after.json", state_with({"greenhouse/anthropic": ["101", "102"]}))
        code, out = self.check(before=before, after=after)
        self.assertEqual(code, 1, out)
        self.assertIn("did not finish", out)

    def test_a_raw_file_that_does_not_match_its_hash_is_flagged(self):
        self.write_run("incomplete", False, [dict(name="greenhouse/anthropic", outcome="usable", jobs=1,
                                                  baseline=True, new_keys=[], body=gh(101), sha256="0" * 64)])
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("sha256", out)

    def test_wrongly_reported_new_keys_are_flagged(self):
        self.write_run("finished", True, [dict(name="greenhouse/anthropic", outcome="usable", jobs=2,
                                               baseline=False, new_keys=[], body=gh(101, 102))])
        before = self.write_state("before.json", state_with({"greenhouse/anthropic": ["101"]}))
        after = self.write_state("after.json", state_with({"greenhouse/anthropic": ["101", "102"]}))
        code, out = self.check(before=before, after=after)
        self.assertEqual(code, 1, out)
        self.assertIn("new", out)

    def test_a_finished_run_that_left_the_state_unchanged_is_flagged(self):
        self.write_run("finished", True, [dict(name="greenhouse/anthropic", outcome="usable", jobs=2,
                                               baseline=False, new_keys=["102"], body=gh(101, 102))])
        before = self.write_state("before.json", state_with({"greenhouse/anthropic": ["101"]}))
        code, out = self.check(before=before, after=before)
        self.assertEqual(code, 1, out)
        self.assertIn("unchanged", out)

    def test_a_board_saved_with_an_empty_history_is_flagged(self):
        self.write_run("finished", True, [dict(name="ashby/linear", outcome="usable", jobs=0,
                                               baseline=True, new_keys=[], body=b'{"apiVersion":"1","jobs":[]}')])
        after = self.write_state("after.json", state_with({"ashby/linear": []}))
        code, out = self.check(after=after)
        self.assertEqual(code, 1, out)
        self.assertIn("empty", out)


if __name__ == "__main__":
    unittest.main()
