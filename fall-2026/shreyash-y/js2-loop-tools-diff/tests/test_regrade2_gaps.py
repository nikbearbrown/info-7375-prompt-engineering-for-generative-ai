"""Three gaps a second independent regrade found on 2026-11-10, written as tests before the fix.

Gap 1 (GATE.md section 7, wrong version 3): `--runs-dir runs-evil` made runs-evil/ the write root,
so the command line could write outside runs/. Only runs/ or a folder inside it may be the root.
Gap 2: a posting with no id crashed the run with a KeyError, ending in none of the four exits; a
write refused mid-run ended in a traceback.
Gap 3: the independent check trusted the summary's board list and new counts.
Every response here is CONSTRUCTED for the test; no test touches the network."""
import contextlib
import io
import json
import pathlib
import shutil
import tempfile
import unittest
from unittest import mock

from jsagent import __main__ as cli
from jsagent import check, loop, persona, policy, providers
from tests import fakes

FOLDER = pathlib.Path(__file__).resolve().parent.parent
BUDGETS = {"max_boards": 6, "max_requests": 12, "max_seconds": 120}


class AllNotFound:
    """Stands in for the network: every board answers 404, so a run ends `incomplete` offline."""

    def get(self, url, timeout=20):
        policy.check_request("GET", url)
        return 404, b'{"constructed": "not found"}'


class RunsDirOnTheCommandLine(unittest.TestCase):
    """The network is replaced, and for the refusal cases the loop itself is replaced by a stub that
    fails the test if it is ever reached, so even the code before the fix writes nothing anywhere."""

    def setUp(self):
        self.net = mock.patch.object(cli.transport, "Live", AllNotFound)
        self.net.start()
        self.inside = FOLDER / "runs" / "_test-regrade2"
        shutil.rmtree(self.inside, ignore_errors=True)

    def tearDown(self):
        self.net.stop()
        shutil.rmtree(self.inside, ignore_errors=True)

    def refused(self, runs_dir):
        def reached(*a, **k):
            raise AssertionError(f"the run started with --runs-dir {runs_dir}")
        with mock.patch.object(cli.loop, "run", reached), self.assertRaises(policy.PolicyViolation) as e:
            cli.main(["run", "--runs-dir", runs_dir, "--run-id", "never-made"])
        self.assertEqual(e.exception.kind, "outside-runs")

    def test_runs_evil_is_refused(self):
        """GATE.md wrong version 3, through the command line."""
        self.refused("runs-evil")
        self.assertFalse((FOLDER / "runs-evil").exists(), "nothing was written")

    def test_the_assignment_folder_itself_is_refused(self):
        self.refused(".")
        self.assertFalse((FOLDER / "never-made").exists())

    def test_a_folder_outside_the_project_is_refused(self):
        with tempfile.TemporaryDirectory() as t:
            self.refused(t)
            self.assertEqual(list(pathlib.Path(t).iterdir()), [], "nothing was written")

    def test_a_folder_inside_runs_is_allowed_and_a_second_run_with_the_same_id_needs_approval(self):
        code = cli.main(["run", "--runs-dir", "runs/_test-regrade2", "--run-id", "r1"])
        self.assertEqual(code, 2, "all boards 404, so the run is incomplete")
        self.assertTrue((self.inside / "r1" / "summary.json").exists())
        with self.assertRaises(policy.NeedsApproval):
            cli.main(["run", "--runs-dir", "runs/_test-regrade2", "--run-id", "r1"])

    def test_the_command_stops_cleanly_with_exit_4_not_a_traceback(self):
        """`python3 -m jsagent` goes through cli.entry, which turns a refusal into exit 4 and one line."""
        err = io.StringIO()
        with mock.patch.object(cli.loop, "run", side_effect=AssertionError("the run started")), \
                contextlib.redirect_stderr(err):
            code = cli.entry(["run", "--runs-dir", "runs-evil"])
        self.assertEqual(code, 4)
        self.assertIn("stopped", err.getvalue())
        self.assertFalse((FOLDER / "runs-evil").exists())


class MalformedPosting(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = pathlib.Path(self.tmp.name).resolve()
        self.runs = self.project / "runs"
        self.runs.mkdir()
        self.view = persona.public_view(persona.load(FOLDER / "persona" / "alex_morgan.json"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_posting_with_no_id_fails_its_board_and_the_run_still_ends_properly(self):
        url = providers.board_url("lever", "x")
        body = json.dumps([{"id": "a1", "text": "Software Engineer"}, {"text": "no id here"}]).encode()
        rep = loop.run([{"name": "x", "ats": "lever", "token": "x"}], BUDGETS,
                       fakes.FakeTransport({url: [(200, body)]}), policy.Files(self.project, self.runs),
                       run_id="r1", resume=self.view, clock=fakes.FakeClock())
        self.assertEqual(rep["exit"], "incomplete")
        b = rep["boards"][0]
        self.assertEqual((b["status"], b["error"], b["fetched"], b["new"]), ("failed", "bad-shape", None, None))
        self.assertTrue((self.runs / "r1" / "summary.json").exists())
        last = json.loads((self.runs / "r1" / "trace.jsonl").read_text().splitlines()[-1])
        self.assertEqual((last["event"], last["exit"]), ("exit", "incomplete"))


class CheckDoesNotTrustTheSummary(unittest.TestCase):
    GH = providers.board_url("greenhouse", "oscar")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = pathlib.Path(self.tmp.name).resolve()
        self.runs = self.project / "runs"
        self.runs.mkdir()
        self.view = persona.public_view(persona.load(FOLDER / "persona" / "alex_morgan.json"))
        boards = [{"name": "oscar", "ats": "greenhouse", "token": "oscar"},
                  {"name": "gone", "ats": "lever", "token": "gone"}]
        for run_id, ids in (("r1", range(1, 11)), ("r2", range(1, 14))):
            loop.run(boards, BUDGETS, fakes.FakeTransport({self.GH: [fakes.gh(*ids)]}),
                     policy.Files(self.project, self.runs), run_id=run_id, resume=self.view, clock=fakes.FakeClock())
        self.summary = self.runs / "r2" / "summary.json"

    def tearDown(self):
        self.tmp.cleanup()

    def edit(self, change):
        s = json.loads(self.summary.read_text())
        change(s)
        self.summary.write_text(json.dumps(s))
        return check.check_run(self.runs / "r2", self.project)

    def test_the_untouched_run_has_no_findings(self):
        self.assertEqual(check.check_run(self.runs / "r2", self.project), [])

    def test_a_new_count_that_the_raw_ids_do_not_support_is_flagged(self):
        def zero_new(s):
            s["boards"][0]["new"] = 0
        findings = self.edit(zero_new)
        self.assertTrue(any("new" in f and "3" in f for f in findings), findings)

    def test_a_board_dropped_from_the_summary_is_flagged(self):
        def drop_failed(s):
            s["boards"] = [b for b in s["boards"] if b["name"] != "gone"]
            s["exit"] = "finished"
        findings = self.edit(drop_failed)
        self.assertTrue(any("gone" in f for f in findings), findings)

    def test_an_exit_that_differs_from_the_trace_is_flagged(self):
        def say_finished(s):
            s["exit"] = "error"
        findings = self.edit(say_finished)
        self.assertTrue(any("trace" in f for f in findings), findings)


if __name__ == "__main__":
    unittest.main()
