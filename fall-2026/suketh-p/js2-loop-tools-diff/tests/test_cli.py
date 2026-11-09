"""The command line: `python3 -m jobwatch run | verify | boards`.

main() takes the project root and the transport as arguments so these tests can use a
temporary folder and simulated requests; the real command uses the folder it lives in
and the network. Every approval here is a SIMULATED approval fixture."""

import contextlib
import gzip
import io
import unittest

from jobwatch.__main__ import main
from tests.fakes import (ANTHROPIC_URL, BAD_SLUG_URL, DATABRICKS_URL, GH_404_BODY, LINEAR_URL, FakeClock,
                         FakeTransport, Project, Reply, ashby, ashby_job, gh_job, greenhouse)


def script():
    return {ANTHROPIC_URL: Reply(body=greenhouse(gh_job(101))),
            DATABRICKS_URL: Reply(body=greenhouse(gh_job(201))),
            LINEAR_URL: Reply(body=ashby(ashby_job("u1"))),
            BAD_SLUG_URL: Reply(404, GH_404_BODY)}


class CliTest(unittest.TestCase):
    def setUp(self):
        self.project = Project()
        self.addCleanup(self.project.cleanup)
        self.clock = FakeClock()
        self.transport = FakeTransport(self.clock, script())

    def main(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = main(list(argv), root=self.project.root, fetch=self.transport, clock=self.clock,
                        wall=lambda: "2026-11-08T12:00:00Z")
        return code, out.getvalue()

    def test_a_finished_run_exits_0_and_a_failure_run_exits_3(self):
        code, out = self.main("run", "--run-id", "R1", "--approve-state", "R1:state/state.json")
        self.assertEqual(code, 0, out)
        self.assertIn("finished", out)
        code, out = self.main("run", "--run-id", "R2", "--failure-control")
        self.assertEqual(code, 3, out)
        self.assertIn("incomplete", out)

    def test_a_malformed_approval_stops_before_anything_runs(self):
        with self.assertRaises(SystemExit) as caught:
            self.main("run", "--run-id", "R1", "--approve-state", "R1")
        self.assertEqual(caught.exception.code, 2)
        self.assertEqual(self.transport.calls, [])
        self.assertFalse((self.project.root / "runs").exists())

    def test_verify_checks_each_raw_body_against_its_recorded_hash(self):
        self.main("run", "--run-id", "R1", "--approve-state", "R1:state/state.json")
        code, out = self.main("verify", "runs/R1")
        self.assertEqual(code, 0, out)
        raw = self.project.run_dir("R1") / "raw" / "greenhouse-anthropic.body.gz"
        raw.write_bytes(gzip.compress(b'{"jobs": []}'))
        code, out = self.main("verify", "runs/R1")
        self.assertEqual(code, 1, out)
        self.assertIn("greenhouse-anthropic", out)

    def test_an_invalid_run_id_never_makes_the_cli_look_outside_the_project(self):
        # Found by Claude Code's coverage audit on 2026-11-09: the CLI checked
        # (root / "runs" / run_id).exists() directly, without the policy.
        # runs/ must exist (as after any earlier run) for runs/../../x to resolve at all;
        # without it the first version of this test passed on the old code.
        (self.project.root / "runs").mkdir()
        (self.project.base / "outside-folder").mkdir()
        code, out = self.main("run", "--run-id", "../../outside-folder")
        self.assertEqual(code, 1, out)
        self.assertNotIn("evidence:", out)

    def test_boards_lists_every_configured_endpoint(self):
        code, out = self.main("boards")
        self.assertEqual(code, 0)
        for url in (ANTHROPIC_URL, DATABRICKS_URL, LINEAR_URL, BAD_SLUG_URL):
            self.assertIn(url, out)


if __name__ == "__main__":
    unittest.main()
