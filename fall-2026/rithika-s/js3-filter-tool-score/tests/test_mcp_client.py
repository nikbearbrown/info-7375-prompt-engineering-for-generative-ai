"""mcp.client end to end against the real mcp.server process, on a
CONSTRUCTED corpus in a temporary folder. Offline: no network, no real MCP
client, no `claude`."""

import functools
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from mcp import client
from tests.shortlist_fixtures import DECISIONS, make_root


QUIET_SPAWN = functools.partial(client.spawn_server,
                                stderr=subprocess.DEVNULL)


class ClientTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_root(Path(self._tmp.name) / "project")
        self.transcripts = Path(self._tmp.name) / "transcripts"

    def tearDown(self):
        self._tmp.cleanup()

    def run_client(self, spawn=QUIET_SPAWN):
        out = io.StringIO()
        code = client.main(["--root", str(self.root), "--transcripts",
                            str(self.transcripts)], spawn=spawn, out=out)
        return code, out.getvalue().splitlines()

    def test_first_kept_posting(self):
        self.assertEqual(client.first_kept(self.root / DECISIONS),
                         ("constructed", "100000"))

    def test_script_runs_every_step_as_expected(self):
        code, lines = self.run_client()
        self.assertEqual(code, 0, "\n".join(lines))
        steps = [line for line in lines if line.startswith("step ")]
        self.assertEqual(len(steps), 8)
        self.assertTrue(all(": OK (" in line for line in steps), steps)
        self.assertIn("tools/call constructed/100000", steps[3])
        self.assertIn("-32602", steps[5])
        self.assertIn("-32602", steps[6])
        self.assertIn("-32601", steps[7])

    def test_both_transcripts_log_both_directions(self):
        self.run_client()
        client_log = next(self.transcripts.glob("client-*.jsonl"))
        server_log = next(self.transcripts.glob("server-*.jsonl"))
        sent = [json.loads(line) for line in
                client_log.read_text("utf-8").splitlines()]
        got = [json.loads(line) for line in
               server_log.read_text("utf-8").splitlines()]
        # 8 messages sent (7 requests + 1 notification), 7 replies
        self.assertEqual(sum(e["direction"] == "out" for e in sent), 8)
        self.assertEqual(sum(e["direction"] == "in" for e in sent), 7)
        self.assertEqual([e["message"] for e in sent
                          if e["direction"] == "out"],
                         [e["message"] for e in got
                          if e["direction"] == "in"])
        path_call = [e["message"] for e in sent if e["direction"] == "out"
                     and "path" in json.dumps(e["message"])]
        self.assertEqual(path_call[0]["params"]["arguments"]["path"],
                         "../../etc/passwd")

    def test_dead_server_is_reported_not_crashed(self):
        def spawn_dead(config, root, transcripts):
            return QUIET_SPAWN(root / "no-such-config.json", root,
                               transcripts)
        code, lines = self.run_client(spawn=spawn_dead)
        self.assertEqual(code, 1)
        self.assertIn("UNEXPECTED", lines[0])


if __name__ == "__main__":
    unittest.main()
