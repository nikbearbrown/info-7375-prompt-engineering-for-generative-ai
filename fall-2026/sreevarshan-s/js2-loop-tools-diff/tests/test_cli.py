import io
import json
import os
import unittest
from unittest import mock

from js2 import __main__ as cli
from tests.helpers import SandboxTestCase, greenhouse_body

URLOPEN = "js2.fetch.urllib.request.urlopen"


class CliTest(SandboxTestCase):
    def run_cli(self, *argv):
        out = io.StringIO()
        with mock.patch(URLOPEN) as urlopen:
            code = cli.main(list(argv), out=out)
        return code, out.getvalue(), urlopen

    def saved_file(self, name, body):
        path = os.path.join(self.tmp, name)
        with open(path, "wb") as f:
            f.write(body)
        return path

    def test_dry_run_prints_plan_and_fetches_nothing(self):
        code, text, urlopen = self.run_cli("--dry-run")
        self.assertEqual(code, 0)
        urlopen.assert_not_called()
        for word in ("Databricks", "Stripe", "Spotify", "invalid-board-xyz",
                     "max_boards=4", "max_requests=8", "max_seconds=90"):
            self.assertIn(word, text)
        self.assertFalse(os.path.exists(os.path.join(self.output, "traces")))

    def test_from_file_replays_one_board_labeled_seeded(self):
        body = greenhouse_body(11, 12)
        src = self.saved_file("20261106T120000123456Z-greenhouse-stripe.json", body)
        code, text, urlopen = self.run_cli("--from-file", src)
        urlopen.assert_not_called()
        self.assertEqual(code, 0)
        self.assertIn("Exit status: finished [SEEDED]", text)
        self.assertIn("Stripe", text)
        self.assertIn("Independent check: passed", text)

        traces = os.listdir(os.path.join(self.output, "traces"))
        self.assertEqual(len(traces), 1)
        self.assertTrue(traces[0].endswith("-SEEDED.json"))
        with open(os.path.join(self.output, "traces", traces[0])) as f:
            trace = json.load(f)
        self.assertEqual(trace["label"], "SEEDED")
        self.assertEqual(trace["boards"][0]["posting_ids"], ["11", "12"])
        self.assertEqual(trace["attempts"][0]["source"], "SEEDED")
        self.assertEqual(trace["attempts"][0]["seeded_from"], src)

        with open(trace["boards"][0]["raw_path"], "rb") as f:
            self.assertEqual(f.read(), body)
        self.assertIn(trace["boards"][0]["raw_path"], text)

    def test_from_file_with_empty_board_is_incomplete(self):
        src = self.saved_file("x.json", b'{"jobs": []}')
        code, text, _ = self.run_cli("--from-file", src, "--board", "databricks")
        self.assertEqual(code, 1)
        self.assertIn("Exit status: incomplete [SEEDED]", text)

    def test_from_file_rejects_unknown_board(self):
        src = self.saved_file("x.json", greenhouse_body(1))
        with mock.patch("sys.stderr", io.StringIO()), self.assertRaises(SystemExit):
            self.run_cli("--from-file", src)

    def test_normal_run_prints_status_boards_and_paths(self):
        out = io.StringIO()
        with mock.patch("js2.loop.FETCHERS", {
            "greenhouse": lambda token, timeout: {"status_code": 200, "raw_path": None,
                                                  "raw_write_decision": True,
                                                  "data": json.loads(greenhouse_body(1))},
            "lever": lambda token, timeout: {"status_code": 200, "raw_path": None,
                                             "raw_write_decision": True, "data": [{"id": "s"}]},
        }):
            code = cli.main([], out=out)
        text = out.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("Exit status: finished", text)
        self.assertIn("4 planned, 4 checked", text)
        self.assertIn("trace: " + os.path.join(self.output, "traces"), text)


if __name__ == "__main__":
    unittest.main()
