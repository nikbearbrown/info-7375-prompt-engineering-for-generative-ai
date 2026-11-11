"""Independent checker tests: W4 (empty board = fine), floors, 80% drop, independence."""
import importlib.util
import json
import unittest
from pathlib import Path

from helpers import HERE, gh, temp_root

spec = importlib.util.spec_from_file_location("check", HERE / "checker/check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def make_run(root, name, files):
    d = root / "runs" / name / "raw"
    d.mkdir(parents=True)
    for fname, body in files.items():
        (d / fname).write_bytes(body)
    return root / "runs" / name


class Classify(unittest.TestCase):
    def test_W4_empty_board_is_suspect(self):
        self.assertEqual(check.classify(0, 200, None, None, 0.8)[0], "suspect")

    def test_below_floor_is_suspect(self):
        self.assertEqual(check.classify(5, 200, 20, None, 0.8)[0], "suspect")

    def test_drop_over_80_percent_is_suspect(self):
        self.assertEqual(check.classify(15, 200, None, 100, 0.8)[0], "suspect")
        self.assertEqual(check.classify(25, 200, None, 100, 0.8)[0], "ok")

    def test_error_and_missing_responses_flagged(self):
        self.assertEqual(check.classify(None, 404, None, None, 0.8)[0], "error-response")
        self.assertEqual(check.classify(None, None, None, None, 0.8)[0], "no-response")

    def test_unknown_floor_is_not_guessed(self):
        v, why = check.classify(3, 200, None, None, 0.8)
        self.assertEqual(v, "ok")
        self.assertIn("floor unknown", why)


class EndToEnd(unittest.TestCase):
    def test_reads_raw_not_report(self):
        root = temp_root()
        run = make_run(root, "2026-11-10T00-00-01Z", {"greenhouse__hubspot__a1__200.json": b'{"jobs": []}',
                                                      "greenhouse__anthropic__a1__200.json": gh(*range(150))})
        # The agent's report claims HubSpot is fine; the checker must ignore that claim.
        (run / "report.json").write_text(json.dumps({"exit": "finished", "results": [
            {"board": "greenhouse/hubspot", "result": "ok", "postings": 0, "new": [], "baseline": False}]}))
        (root / "config/plan.json").write_text(json.dumps({"plan": [{"ats": "greenhouse", "slug": "hubspot"}, {"ats": "greenhouse", "slug": "anthropic"}]}))
        check.HERE = root
        rc = check.main([str(run), "--plan", "config/plan.json"])
        out = json.loads((run / "check.json").read_text())
        self.assertEqual(rc, 3)
        self.assertEqual(out["boards"]["greenhouse/hubspot"]["verdict"], "suspect")
        self.assertEqual(out["boards"]["greenhouse/anthropic"]["verdict"], "ok")
        self.assertEqual(out["needs_mayank"], ["greenhouse/hubspot"])

    def test_checker_does_not_import_the_agent(self):
        src = (HERE / "checker/check.py").read_text()
        self.assertNotIn("import jsa", src)
        self.assertNotIn("from jsa", src)
        self.assertNotIn("src/jsa", src.split('"""', 2)[2])  # outside the docstring


if __name__ == "__main__":
    unittest.main()
