"""The independent check (check.py) reads the saved trace + raw files, not the agent's summary line."""

import gzip
import json
import unittest

from jsagent2.check import check_run
from tests.fakes import gh_body, tmp_root


def write_run(root, run_id, boards, exit_status="finished"):
    """boards: name -> (status, reported_postings, raw_bytes or None)."""
    run_dir = root / "out" / "runs" / run_id
    (run_dir / "raw").mkdir(parents=True)
    obs, report = [], {}
    for name, (status, reported, raw) in boards.items():
        if raw is not None:
            rel = f"out/runs/{run_id}/raw/{name}.json.gz"
            (root / rel).write_bytes(gzip.compress(raw))
            obs.append({"event": "response", "board": name, "ats": "greenhouse", "http_status": 200, "raw_file": rel})
        report[name] = {"status": status, "postings": reported}
    trace = {"run_id": run_id, "exit": exit_status, "boards": report, "observations": obs}
    (run_dir / "trace.json").write_text(json.dumps(trace))
    return run_dir / "trace.json"


class IndependentCheck(unittest.TestCase):
    def test_clean_run_has_no_findings(self):
        root = tmp_root()
        t = write_run(root, "r1", {"Figma": ("ok", 2, gh_body(2))})
        self.assertEqual(check_run(root, t), [])

    def test_finished_with_empty_board_is_flagged(self):
        root = tmp_root()
        t = write_run(root, "r1", {"Figma": ("ok", 0, gh_body(0))})
        kinds = [f["kind"] for f in check_run(root, t)]
        self.assertIn("finished-with-empty-board", kinds)

    def test_drop_to_zero_against_previous_run(self):
        root = tmp_root()
        prev = write_run(root, "r0", {"Figma": ("ok", 143, gh_body(143))})
        t = write_run(root, "r1", {"Figma": ("ok", 0, gh_body(0))})
        kinds = [f["kind"] for f in check_run(root, t, previous=[prev])]
        self.assertIn("drop-to-zero", kinds)

    def test_reported_count_differs_from_raw(self):
        root = tmp_root()
        t = write_run(root, "r1", {"Figma": ("ok", 5, gh_body(2))})
        self.assertIn("count-mismatch", [f["kind"] for f in check_run(root, t)])

    def test_failed_board_with_a_number_is_flagged(self):
        root = tmp_root()
        t = write_run(root, "r1", {"Bad": ("not-found", 0, None)}, exit_status="incomplete")
        self.assertIn("value-for-failed-board", [f["kind"] for f in check_run(root, t)])

    def test_raw_file_tampered_is_flagged(self):
        root = tmp_root()
        t = write_run(root, "r1", {"Figma": ("ok", 2, gh_body(2))})
        trace = json.loads(t.read_text())
        trace["observations"][0]["sha256"] = "0" * 64
        t.write_text(json.dumps(trace))
        self.assertIn("raw-hash-mismatch", [f["kind"] for f in check_run(root, t)])


if __name__ == "__main__":
    unittest.main()
