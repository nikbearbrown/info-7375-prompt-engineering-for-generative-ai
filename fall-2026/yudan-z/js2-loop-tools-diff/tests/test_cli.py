"""Found 2026-11-10 by trying the README commands: '--workdir ../outside' fetched a board first and only then
had its writes refused, and the CLI crashed with a traceback (exit 1, not a GATE exit code).
Written before the fix: a workdir outside runs/ must stop with 'error' (code 2) before any request."""
import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from agent import cli  # noqa: E402


class CliTests(unittest.TestCase):
    def test_workdir_outside_runs_refused_before_any_request(self):
        calls = []
        with mock.patch("agent.tools.http_get", side_effect=lambda u, t: calls.append(u) or (200, b"{}")), \
                mock.patch("agent.loop.http_get", side_effect=lambda u, t: calls.append(u) or (200, b"{}")):
            code = cli.main(["--workdir", os.path.join(ROOT, "..", "outside-js2-test")])
        self.assertEqual(code, 2)
        self.assertEqual(calls, [])
        self.assertFalse(os.path.exists(os.path.join(ROOT, "..", "outside-js2-test")))


if __name__ == "__main__":
    unittest.main()
