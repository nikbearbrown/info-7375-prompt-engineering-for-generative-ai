"""The independent check (jsagent/check.py): it reads only saved files, never the loop's code."""
import json
import pathlib
import re
import tempfile
import unittest

from jsagent import check, loop, persona, policy, providers
from tests import fakes

GH = providers.board_url("greenhouse", "oscar")


class Check(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = pathlib.Path(self.tmp.name).resolve()
        self.runs = self.project / "runs"
        self.runs.mkdir()
        self.view = persona.public_view(json.loads((pathlib.Path(__file__).parent.parent / "persona" / "alex_morgan.json").read_text()))

    def tearDown(self):
        self.tmp.cleanup()

    def run_loop(self, run_id, response):
        return loop.run([{"name": "oscar", "ats": "greenhouse", "token": "oscar"}],
                        {"max_boards": 6, "max_requests": 12, "max_seconds": 120},
                        fakes.FakeTransport({GH: [response]}), policy.Files(self.project, self.runs),
                        run_id=run_id, resume=self.view, clock=fakes.FakeClock())

    def test_clean_run_has_no_findings(self):
        self.run_loop("r1", fakes.gh(*range(1, 11)))
        self.assertEqual(check.check_run(self.runs / "r1", self.project), [])

    def test_finished_wrong_answer_truncated_response(self):
        """The loop finishes cleanly on a response that lists 3 jobs while the board says 10 exist."""
        self.run_loop("r1", fakes.gh(*range(1, 11)))
        r2 = self.run_loop("r2", fakes.gh(1, 2, 3, total=10))
        self.assertEqual(r2["exit"], "finished", "the agent's own report looks fine")
        findings = check.check_run(self.runs / "r2", self.project)
        self.assertTrue(any("meta.total" in f for f in findings), findings)
        self.assertTrue(any("disappeared" in f for f in findings), findings)

    def test_tampered_summary_caught(self):
        self.run_loop("r1", fakes.gh(1, 2))
        s = json.loads((self.runs / "r1" / "summary.json").read_text())
        s["boards"][0]["fetched"] = 99
        (self.runs / "r1" / "summary.json").write_text(json.dumps(s))
        self.assertTrue(any("fetched" in f for f in check.check_run(self.runs / "r1", self.project)))

    def test_finished_with_a_failed_board_caught(self):
        self.run_loop("r1", (404, b"{}"))
        s = json.loads((self.runs / "r1" / "summary.json").read_text())
        s["exit"] = "finished"
        (self.runs / "r1" / "summary.json").write_text(json.dumps(s))
        self.assertTrue(any("finished" in f for f in check.check_run(self.runs / "r1", self.project)))

    def test_check_does_not_use_the_agent_code(self):
        src = (pathlib.Path(check.__file__)).read_text()
        self.assertEqual(re.findall(r"^\s*(?:from|import)\s+jsagent\b.*$", src, re.M), [])


if __name__ == "__main__":
    unittest.main()
