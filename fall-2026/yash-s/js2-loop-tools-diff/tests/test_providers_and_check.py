"""Tests for providers.py (structure checks) and independent_check.py (the finished-wrong-answer catch).

run from the js2-loop-tools-diff folder:
  python3 -m unittest discover -s tests -v
"""
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
sys.path.insert(0, str(FOLDER))
import agent  # noqa: E402
import independent_check  # noqa: E402
import providers  # noqa: E402


class Providers(unittest.TestCase):
    def test_board_urls(self):
        self.assertEqual(providers.board_url("greenhouse", "databricks"),
                         "https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true")
        self.assertEqual(providers.board_url("ashby", "openai"),
                         "https://api.ashbyhq.com/posting-api/job-board/openai?includeCompensation=true")

    def test_bad_board_names_and_systems_are_refused(self):
        for ats, slug in (("lever", "x"), ("greenhouse", "Data Bricks"), ("greenhouse", "../x"), ("greenhouse", "")):
            with self.assertRaises(providers.ConfigError):
                providers.board_url(ats, slug)

    def test_greenhouse_and_ashby_parse(self):
        g = providers.parse("greenhouse", json.dumps({"jobs": [{"id": 5, "title": " ML Engineer ", "content": "c",
                                                                "location": {"name": "NYC"}, "absolute_url": "u"}]}))
        a = providers.parse("ashby", json.dumps({"jobs": [{"id": "a-1", "title": "AI", "descriptionHtml": "<p>x</p>",
                                                           "location": "SF", "secondaryLocations": [{"location": "NYC"}],
                                                           "jobUrl": "u"}]}))
        self.assertEqual((g[0]["id"], g[0]["title"], g[0]["location"]), (5, "ML Engineer", "NYC"))
        self.assertEqual((a[0]["id"], a[0]["location"]), ("a-1", "SF · NYC"))
        self.assertEqual(g[0]["original"]["absolute_url"], "u")

    def test_a_well_formed_empty_list_is_valid(self):
        self.assertEqual(providers.parse("greenhouse", '{"jobs": []}'), [])

    def test_malformed_responses_raise_and_are_never_empty(self):
        for ats, raw in (("greenhouse", "not json"), ("greenhouse", "[]"), ("greenhouse", '{"error": "x"}'),
                         ("greenhouse", '{"jobs": [{"title": "no id"}]}'), ("greenhouse", '{"jobs": [{"id": "5"}]}'),
                         ("ashby", '{"jobs": [{"id": 5}]}'), ("ashby", '{"jobs": [{"id": ""}]}')):
            with self.assertRaises(providers.ResponseError, msg=raw):
                providers.parse(ats, raw)


class IndependentCheck(unittest.TestCase):
    """GATE.md section 4: a run that finishes cleanly and is wrong, caught by a separate check."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for d in ("config", "runs", "state", "persona"):
            (self.root / d).mkdir()
        shutil.copy(FOLDER / "persona" / "priya-nair.resume.example.json", self.root / "persona" / "r.json")
        (self.root / "config" / "c.json").write_text(json.dumps({"boards": [{"name": "Anthropic", "ats": "greenhouse",
                                                                             "slug": "anthropic"}]}))

    def run_with(self, body, minute):
        def get(url, timeout, board, pol):
            return 200, body
        return agent.run(self.root / "config" / "c.json", self.root / "runs", self.root / "state",
                         [self.root / "persona", self.root / "config"], self.root / "persona" / "r.json",
                         get=get, clock=lambda: 0.0, now=datetime(2026, 11, 9, 12, minute, tzinfo=timezone.utc))

    def check(self, run_dir):
        with redirect_stdout(io.StringIO()) as out:
            code = independent_check.main([str(run_dir)])
        return code, out.getvalue()

    def test_an_empty_board_finishes_but_the_independent_check_flags_it(self):
        self.run_with(json.dumps({"jobs": [{"id": i, "title": "t"} for i in range(1, 4)]}).encode(), 0)
        summary, run_dir = self.run_with(b'{"jobs": []}', 1)
        self.assertEqual(summary["exit_status"], "finished")              # the agent's own report looks fine
        code, out = self.check(run_dir)
        self.assertEqual(code, 1)
        self.assertIn("DROP-TO-ZERO: 3 postings", out)

    def test_a_steady_board_is_not_flagged(self):
        body = json.dumps({"jobs": [{"id": 1, "title": "t"}]}).encode()
        self.run_with(body, 0)
        _, run_dir = self.run_with(body, 1)
        self.assertEqual(self.check(run_dir)[0], 0)

    def test_a_report_that_disagrees_with_its_raw_response_is_flagged(self):
        _, run_dir = self.run_with(json.dumps({"jobs": [{"id": 1, "title": "t"}]}).encode(), 0)
        s = json.loads((run_dir / "summary.json").read_text())
        s["boards"][0]["postings"] = 99
        (run_dir / "summary.json").write_text(json.dumps(s))
        code, out = self.check(run_dir)
        self.assertEqual(code, 1)
        self.assertIn("MISMATCH", out)

    def test_the_checker_does_not_use_the_agents_code(self):
        source = (FOLDER / "independent_check.py").read_text()
        for name in ("import agent", "import providers", "import policy", "from agent", "from providers"):
            self.assertNotIn(name, source)


if __name__ == "__main__":
    unittest.main()
