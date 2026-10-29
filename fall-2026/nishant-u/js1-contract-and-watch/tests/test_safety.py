"""The safety claims in experiment/ACTION-SURFACE.md: redirect refusal, atomic state write, and a judge
with no tools.

Added 2026-10-29, after the implementation: these behaviours were in the code but untested.
No real network and no real `claude` call: the server and the CLI are fakes.
"""
import email.message
import io
import json
import os
import subprocess
import tempfile
import unittest
import urllib.request
import urllib.response
from pathlib import Path
from unittest import mock

from tests import helpers

ALLOWED_URL = "https://boards-api.greenhouse.io/v1/boards/faire/jobs?content=true"


class FakeServer(urllib.request.BaseHandler):
    """Answers every request itself, recording its URL. The allowed host redirects to `location`."""
    handler_order = 100  # ahead of the real HTTP(S) handlers, so nothing reaches the network

    def __init__(self, location):
        self.location = location
        self.requests = []

    def https_open(self, req):
        self.requests.append(req.full_url)
        headers = email.message.Message()
        if req.full_url == ALLOWED_URL:
            headers["Location"] = self.location
            response = urllib.response.addinfourl(io.BytesIO(b""), headers, req.full_url, 302)
            response.msg = "Found"
        else:
            response = urllib.response.addinfourl(io.BytesIO(b'{"jobs": []}'), headers, req.full_url, 200)
            response.msg = "OK"
        return response

    http_open = https_open


class RedirectRefusal(helpers.ContractTest):
    modules = ("agent.watch",)

    def opener(self, server):
        # The module's own opener, rebuilt from its handler classes, with the fake server in front.
        classes = [type(h) for h in self.watch._OPENER.handlers]
        return urllib.request.build_opener(*classes, server)

    def test_redirect_to_another_host_is_refused_before_any_request_to_it(self):
        server = FakeServer("https://evil.example/v1/boards/faire/jobs")
        with self.assertRaises(self.watch.RefusedHost):
            self.watch.fetch(ALLOWED_URL, opener=self.opener(server).open)
        self.assertEqual(server.requests, [ALLOWED_URL], "no request may be made to the redirect target")

    def test_redirect_within_the_allow_list_is_followed(self):
        target = "https://boards-api.greenhouse.io/v1/boards/faire/jobs?content=true&page=1"
        server = FakeServer(target)
        body = self.watch.fetch(ALLOWED_URL, opener=self.opener(server).open)
        self.assertEqual(body, b'{"jobs": []}')
        self.assertEqual(server.requests, [ALLOWED_URL, target])


class AtomicStateWrite(helpers.ContractTest):
    modules = ("agent.watch",)

    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.tmp.name) / "state" / "seen_ids.json"
        self.state.parent.mkdir()
        self.state.write_text(json.dumps({"last_run": "old", "seen_ids": [1, 2, 3]}), encoding="utf-8")
        self.before = self.state.read_bytes()

    def tearDown(self):
        self.tmp.cleanup()

    def assert_state_untouched(self):
        self.assertEqual(self.state.read_bytes(), self.before, "the old seen_ids.json must be unchanged")
        self.assertEqual(sorted(p.name for p in self.state.parent.iterdir()), ["seen_ids.json"],
                         "no temporary or partial file may be left behind")

    def test_failure_after_temp_written_before_replace_leaves_old_state(self):
        written = []

        def failing_replace(src, dst):
            written.append(json.loads(Path(src).read_text(encoding="utf-8")))  # the temp file is complete
            raise OSError("simulated failure before os.replace")

        with mock.patch.object(self.watch.os, "replace", side_effect=failing_replace), \
                self.assertRaises(OSError):
            self.watch.save_seen(self.state, [4, 5], "new")
        self.assertEqual(written, [{"last_run": "new", "seen_ids": [1, 2, 3, 4, 5]}])
        self.assert_state_untouched()

    def test_failure_partway_through_writing_leaves_old_state(self):
        def half_dump(obj, f, **kwargs):
            f.write(json.dumps(obj)[:10])
            raise OSError("simulated failure partway through the write")

        with mock.patch.object(self.watch.json, "dump", side_effect=half_dump), self.assertRaises(OSError):
            self.watch.save_seen(self.state, [4, 5], "new")
        self.assert_state_untouched()


class JudgeHasNoTools(helpers.ContractTest):
    modules = ("agent.claude_judge",)

    def run_judge(self):
        seen = {}

        def runner(cmd, **kwargs):
            seen["cmd"] = cmd
            seen["cwd_files"] = os.listdir(kwargs["cwd"])
            reply = {"type": "result", "is_error": False, "result": "{}", "session_id": "fake",
                     "modelUsage": {"fake-model": {}}}
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(reply), stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            self.claude_judge.judge(helpers.posting(9000000008), helpers.resume(), tmp,
                                    runner=runner, which=lambda name: "claude")
        return seen

    def test_command_always_has_tools_set_to_none(self):
        cmd = self.run_judge()["cmd"]
        self.assertEqual(cmd[0], "claude")
        self.assertIn("-p", cmd)
        self.assertEqual(cmd.count("--tools"), 1)
        self.assertEqual(cmd[cmd.index("--tools") + 1], "", 'the judge must run with --tools ""')

    def test_judge_runs_in_an_empty_folder(self):
        # So no repository file, such as CLAUDE.md, is in the judge's context.
        self.assertEqual(self.run_judge()["cwd_files"], [])


if __name__ == "__main__":
    unittest.main()
