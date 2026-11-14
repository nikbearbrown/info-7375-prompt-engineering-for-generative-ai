"""Two gaps an independent regrade found on 2026-11-10, written as tests before the fix.

Gap 1: GATE-NOTES says reads stay inside this assignment folder, and Files.read enforces that,
but the command line read --boards and --replay (and the replay's saved responses) without it.
Gap 2: an empty board list ran as `finished` with nothing checked, and the independent check
said "no findings". Every path and response here is CONSTRUCTED for the test."""
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from jsagent import __main__ as cli
from jsagent import check, loop, persona, policy, transport
from tests import fakes

FOLDER = pathlib.Path(__file__).resolve().parent.parent
BUDGETS = {"max_boards": 6, "max_requests": 12, "max_seconds": 120}


class NoNetwork:
    def get(self, url, timeout=20):
        raise AssertionError(f"the test tried the network: {url}")


class CommandLineReads(unittest.TestCase):
    """The command line reads its input files through Files.read, so a path outside the folder is refused.
    The network is replaced and runs go to a temp folder, so even the code before the fix cannot
    fetch anything or write into runs/ (the first run of this file, before that guard, did both)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.outside = pathlib.Path(self.tmp.name).resolve()
        self.runs = self.outside / "runs"
        self.net = mock.patch.object(cli.transport, "Live", NoNetwork)
        self.net.start()

    def tearDown(self):
        self.net.stop()
        self.tmp.cleanup()

    def test_boards_file_outside_the_folder_is_refused(self):
        boards = self.outside / "boards.json"
        boards.write_text(json.dumps({"boards": [{"name": "oscar", "ats": "greenhouse", "token": "oscar"}]}))
        with self.assertRaises(policy.PolicyViolation) as e:
            cli.main(["run", "--boards", str(boards), "--runs-dir", str(self.runs), "--run-id", "never-made"])
        self.assertEqual(e.exception.kind, "read-outside")
        self.assertFalse(self.runs.exists(), "nothing was written")

    def test_replay_map_outside_the_folder_is_refused(self):
        m = self.outside / "map.json"
        m.write_text("{}")
        with self.assertRaises(policy.PolicyViolation) as e:
            cli.main(["run", "--boards", "demo/boards-four-good.json", "--replay", str(m), "--runs-dir", str(self.runs),
                      "--run-id", "never-made"])
        self.assertEqual(e.exception.kind, "read-outside")
        self.assertFalse(self.runs.exists(), "nothing was written")


class ReplayResponseFiles(unittest.TestCase):
    """A replay map inside the folder may not point at a saved response outside it."""

    def test_response_file_outside_the_project_is_refused(self):
        with tempfile.TemporaryDirectory() as proj, tempfile.TemporaryDirectory() as elsewhere:
            proj, elsewhere = pathlib.Path(proj).resolve(), pathlib.Path(elsewhere).resolve()
            (elsewhere / "secret.json").write_text('{"jobs": [], "meta": {"total": 0}}')
            url = "https://boards-api.greenhouse.io/v1/boards/oscar/jobs?content=true"
            (proj / "map.json").write_text(json.dumps({url: {"status": 200, "file": str(elsewhere / "secret.json")}}))
            files = policy.Files(proj, proj / "runs")
            t = transport.Replay(proj / "map.json", read=files.read)
            with self.assertRaises(policy.PolicyViolation) as e:
                t.get(url)
            self.assertEqual(e.exception.kind, "read-outside")


class EmptyBoardList(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = pathlib.Path(self.tmp.name).resolve()
        self.runs = self.project / "runs"
        self.runs.mkdir()
        self.view = persona.public_view(persona.load(FOLDER / "persona" / "alex_morgan.json"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_board_list_is_an_error_not_finished(self):
        t = fakes.FakeTransport({})
        rep = loop.run([], BUDGETS, t, policy.Files(self.project, self.runs), run_id="r0",
                       resume=self.view, clock=fakes.FakeClock())
        self.assertEqual(rep["exit"], "error")
        self.assertIn("no boards", rep["fatal"])
        self.assertEqual(t.calls, [], "no request is made")

    def test_check_flags_finished_with_no_board_checked(self):
        """What the old loop wrote for an empty list: exit finished, no boards. The check must not pass it."""
        run_dir = self.runs / "old-empty"
        run_dir.mkdir()
        (run_dir / "summary.json").write_text(json.dumps(
            {"run_id": "old-empty", "exit": "finished", "state_sequence": 1, "boards": []}))
        findings = check.check_run(run_dir, self.project)
        self.assertTrue(any("no board" in f for f in findings), findings)


if __name__ == "__main__":
    unittest.main()
