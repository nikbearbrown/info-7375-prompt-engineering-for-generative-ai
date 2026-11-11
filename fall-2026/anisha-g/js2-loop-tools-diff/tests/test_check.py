"""The independent check (assignment: 'a finished wrong answer ... caught by an independent check, not the agent's own report').
check.py ignores the agent's verdicts: it re-reads the saved raw responses and recounts the jobs itself."""
import json, tempfile, unittest
from pathlib import Path
from watcher.check import check_run

def make_run(boards, raws):
    d = Path(tempfile.mkdtemp()); (d / "raw").mkdir()
    for name, (status, body) in raws.items():
        (d / "raw" / name).write_bytes(body); (d / "raw" / (name + ".status")).write_text(str(status))
    (d / "trace.json").write_text(json.dumps({"exit": "finished", "boards": boards}))
    return d

def ok(board, jobs, raw): return {"board": board, "status": "ok", "jobs": jobs, "attempts": [{"raw_file": "raw/" + raw}]}

class IndependentCheck(unittest.TestCase):
    def test_consistent_run_passes(self):
        d = make_run([ok("greenhouse:klaviyo", 2, "k1")], {"k1": (200, b'{"jobs":[{"id":1},{"id":2}]}')})
        self.assertEqual(check_run(d), [])
    def test_valid_empty_board_passes(self):
        d = make_run([ok("greenhouse:klaviyo", 0, "k1")], {"k1": (200, b'{"jobs":[]}')})
        self.assertEqual(check_run(d), [])
    def test_catches_failed_board_reported_as_zero_jobs(self):
        # the finished-wrong answer: a 404 reported as 'ok, 0 jobs' in a run that says 'finished'
        d = make_run([ok("greenhouse:no-such-board-7375", 0, "b1")], {"b1": (404, b'{"status":404,"error":"Job board not found"}')})
        problems = check_run(d)
        self.assertEqual(len(problems), 1); self.assertIn("404", problems[0])
    def test_catches_blank_body_reported_as_zero(self):
        d = make_run([ok("greenhouse:klaviyo", 0, "k1")], {"k1": (200, b"")})
        self.assertEqual(len(check_run(d)), 1)
    def test_catches_wrong_count_on_lever(self):
        d = make_run([ok("lever:palantir", 0, "p1")], {"p1": (200, b'[{"id":"a"},{"id":"b"},{"id":"c"}]')})
        problems = check_run(d)
        self.assertEqual(len(problems), 1); self.assertIn("3", problems[0])
    def test_missing_raw_evidence_is_a_problem(self):
        d = make_run([ok("greenhouse:klaviyo", 1, "gone")], {})
        self.assertEqual(len(check_run(d)), 1)

if __name__ == "__main__": unittest.main()
