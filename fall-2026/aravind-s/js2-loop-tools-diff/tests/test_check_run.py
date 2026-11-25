"""The independent check (tools/check_run.py) agrees with a correct run and catches the finished wrong
answer: wrong version 1a planted in the running code, so a 404 board is reported read with 0 new."""

import ast
import importlib.util
import io
import json
import unittest
from contextlib import redirect_stdout
from unittest import mock

from job_agent import providers

from .loop_helpers import FakeNet, REPO, Workspace, answer, greenhouse_job, lever_job, url

spec = importlib.util.spec_from_file_location("check_run", REPO / "tools" / "check_run.py")
check_run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_run)

VERKADA, PALANTIR, BAD = ("greenhouse", "verkada"), ("lever", "palantir"), ("greenhouse", "no-such-board-js2-test")
NOT_FOUND = b'{"status":404,"error":"Job not found"}'


def planted_404_as_zero(system, status, body):
    """Wrong version 1a, planted for this test only: a board that answers HTTP 404 is read as zero postings."""
    if status == 404:
        return []
    return REAL_READ(system, status, body)


REAL_READ = providers.read


class CheckRunTest(unittest.TestCase):
    def setUp(self):
        self.ws = Workspace()
        self.addCleanup(self.ws.cleanup)
        self.ws.boards(VERKADA, PALANTIR, BAD + ({"deliberate_failure": True},))
        self.plan = {url(*VERKADA): [answer(*VERKADA, [greenhouse_job(101)])],
                     url(*PALANTIR): [answer(*PALANTIR, [lever_job("l-1"), lever_job("l-2")])],
                     url(*BAD): [answer(*BAD, status=404, raw=NOT_FOUND)]}

    def test_the_check_imports_nothing_from_the_agent(self):
        tree = ast.parse((REPO / "tools" / "check_run.py").read_text(encoding="utf-8"))
        imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        imported |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertFalse([name for name in imported if name.startswith("job_agent")])

    def test_a_correct_run_with_the_deliberate_failure_has_no_disagreement(self):
        summary = self.ws.run(FakeNet(self.plan))
        self.assertEqual(summary["exit"], "incomplete")
        lines, flags = check_run.check(self.ws.run_dirs()[0])
        self.assertEqual(flags, [])
        self.assertIn("No disagreement", "\n".join(lines))

    def test_the_planted_wrong_version_ends_finished_and_the_check_catches_it(self):
        with mock.patch.object(providers, "read", planted_404_as_zero):
            summary = self.ws.run(FakeNet(self.plan))
        # The planted run ends cleanly and is wrong: finished, exit 0, the made-up board "read" with 0 new.
        self.assertEqual((summary["exit"], summary["exit_code"]), ("finished", 0))
        bad = next(b for b in summary["boards"] if b["key"] == "greenhouse-no-such-board-js2-test")
        self.assertEqual((bad["status"], bad["postings"], len(bad["new"])), ("read", 0, 0))
        lines, flags = check_run.check(self.ws.run_dirs()[0])
        self.assertTrue(any("greenhouse-no-such-board-js2-test: the report says 'read'" in f for f in flags))
        self.assertTrue(any(f.startswith("exit: the report says finished") for f in flags))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(check_run.main([str(self.ws.run_dirs()[0])]), 1)

    def test_an_edited_report_is_caught_too(self):
        self.ws.run(FakeNet(self.plan))
        run_dir = self.ws.run_dirs()[0]
        report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
        palantir = next(b for b in report["boards"] if b["key"] == "lever-palantir")
        palantir["postings"] = 5
        palantir["gone"] = [{"id": "l-1", "title": "still listed"}]
        (run_dir / "report.json").write_text(json.dumps(report), encoding="utf-8")
        _, flags = check_run.check(run_dir)
        self.assertTrue(any("counts 5 postings" in f for f in flags))
        self.assertTrue(any("gone posting l-1 is still in the saved answer" in f for f in flags))

    def test_a_folder_that_is_not_a_loop_run_exits_2(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(check_run.main([str(self.ws.root)]), 2)


if __name__ == "__main__":
    unittest.main()
