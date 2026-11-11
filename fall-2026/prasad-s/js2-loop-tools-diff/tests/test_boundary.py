"""GATE.md v0.2 §7: boundary tests B01-B11, predicted 2026-11-05, run against
agent/policy.py through agent/tool_layer.py.

Each test builds its own project folder in a temporary directory. The network
is patched shut: any request that got past the check would fail the test.
"""

import io
import os
import socket
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

import support  # noqa: F401  (puts the project folder on sys.path)

from agent import policy as P
from agent import tool_layer
from agent.policy import Policy, PolicyRefusal
from agent.tool_layer import ToolLayer

PROBE = "evidence/gate_probes/gh_stripe_probe.json"
PROBE_BYTES = b'{"jobs": []}\n'
CONFIG_BYTES = b'{"boards": []}\n'
STRIPE_URL = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"
# GATE.md §0's five boards, as CP5b will read them from config.json.
BOARDS = [("boards-api.greenhouse.io", name) for name in ("stripe", "duolingo", "robinhood")] + \
         [("api.ashbyhq.com", name) for name in ("notion", "js2nosuchboard")]


class _FakeResponse:
    status = 200
    headers = {"Content-Type": "application/json"}

    def read(self):
        return b'{"jobs": []}'

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class BoundaryCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name).resolve()
        self.root = self.base / "project"
        self.outside = self.base / "elsewhere"
        for folder in ("evidence/gate_probes", "evidence/snapshots", "state", "output", "output-evil"):
            (self.root / folder).mkdir(parents=True)
        self.outside.mkdir()
        (self.root / PROBE).write_bytes(PROBE_BYTES)
        (self.root / "config.json").write_bytes(CONFIG_BYTES)
        (self.root / "GATE.md").write_bytes(b"# GATE\n")
        os.symlink(self.outside, self.root / "output" / "link")

        # The tool layer's one opener, and below it any socket at all.
        self.send = mock.Mock(side_effect=AssertionError("a request would have been sent"))
        no_socket = mock.Mock(side_effect=AssertionError("a socket would have been opened"))
        for patcher in (mock.patch.object(tool_layer, "_send", self.send),
                        mock.patch.object(socket, "create_connection", no_socket)):
            patcher.start()
            self.addCleanup(patcher.stop)

    def tools(self, approvals=()):
        return ToolLayer(Policy(self.root, BOARDS, approvals=approvals))

    def assert_fetch_refused(self, url):
        with self.assertRaises(PolicyRefusal) as caught:
            self.tools().fetch(url)
        self.send.assert_not_called()
        return caught.exception

    def snapshot(self):
        """Every file under the temporary directory, with its bytes."""
        return {p: p.read_bytes() for p in self.base.rglob("*") if p.is_file() and not p.is_symlink()}


class BoundaryTests(BoundaryCase):
    def test_B01_host_off_the_allow_list(self):
        """B01 | Host off the allow-list | Fetch https://example.com/jobs |
        Refused; no request is sent; the refusal names the host |
        example.com is not an exact match for any allow-listed host (§5)"""
        refusal = self.assert_fetch_refused("https://example.com/jobs")
        self.assertIn(P.R_FETCH_HOST, refusal.rules)
        self.assertIn("'example.com'", str(refusal))

    def test_B02_path_with_dotdot(self):
        """B02 | Path with `..` | Write output/../../outside.txt |
        Refused; nothing is written | The resolved path leaves the writable
        folders; paths are judged after resolution, not as written (§5)"""
        before = self.snapshot()
        with self.assertRaises(PolicyRefusal) as caught:
            self.tools().write("output/../../outside.txt", b"x")
        self.assertEqual(caught.exception.rules, [P.R_WRITE_INSIDE])
        self.assertFalse((self.base / "outside.txt").exists())
        self.assertEqual(self.snapshot(), before)

    def test_B03_prefix_trick_host(self):
        """B03 | Prefix trick (`boards-api.greenhouse.io-evil` beside
        `boards-api.greenhouse.io`) | Fetch
        https://boards-api.greenhouse.io-evil.example/jobs | Refused; no request
        is sent | A host that merely starts with an allow-listed host is a
        different host; matching is exact and whole (§5)"""
        refusal = self.assert_fetch_refused("https://boards-api.greenhouse.io-evil.example/jobs")
        self.assertIn(P.R_FETCH_HOST, refusal.rules)

    def test_B04_symlink_out_of_output(self):
        """B04 | Symlink leading out of the output folder | Write
        output/link/report.txt, where output/link points outside the project
        folder | Refused; nothing is written | The check resolves the real
        path, and the real path is outside the writable folders (§5)"""
        before = self.snapshot()
        with self.assertRaises(PolicyRefusal) as caught:
            self.tools().write("output/link/report.txt", b"x")
        self.assertEqual(caught.exception.rules, [P.R_WRITE_INSIDE])
        self.assertFalse((self.outside / "report.txt").exists())
        self.assertEqual(self.snapshot(), before)

    def test_B05_read_in_an_allowed_folder(self):
        """B05 | Read request in an allowed folder | Read a file under
        evidence/gate_probes/ | Allowed; the content is returned | Reads inside
        the project folder are permitted (§5)"""
        self.assertEqual(self.tools().read(PROBE), PROBE_BYTES)

    def test_B06_write_to_the_same_path(self):
        """B06 | Write request to the same path | Write to that same
        evidence/gate_probes/ path | Refused; nothing is written | gate_probes/
        is read-only in §5, and overwriting an existing file would need approval
        besides. That a read is allowed says nothing about writes"""
        before = self.snapshot()
        with self.assertRaises(PolicyRefusal) as caught:
            self.tools().write(PROBE, b"overwritten")
        self.assertEqual(caught.exception.rules, [P.R_WRITE_READ_ONLY])
        self.assertEqual(self.snapshot(), before)

    def test_B07_config_write_without_approval(self):
        """B07 | Write that needs approval, without approval | Write
        config.json, with no --approve flag on the run | Refused; the file is
        unchanged | The config is named in §5 as approval-only, and no flag
        means no approval reached the program"""
        with self.assertRaises(PolicyRefusal) as caught:
            self.tools().write("config.json", b"changed")
        self.assertEqual(set(caught.exception.rules), {P.R_WRITE_APPROVAL})
        self.assertEqual((self.root / "config.json").read_bytes(), CONFIG_BYTES)

    def test_B08_config_write_with_approval(self):
        """B08 | The same write, with approval | Write config.json, with
        --approve config.json on that run | Allowed; the file is written, and
        the report records the flag | §5: approval is per path and per write,
        and the flag is how it reaches the program"""
        tools = self.tools(approvals=["config.json"])
        permit = tools.write("config.json", b"changed")
        self.assertEqual((self.root / "config.json").read_bytes(), b"changed")
        self.assertEqual(permit.approval, "config.json")
        self.assertEqual(tools.policy.approval_record(),
                         [{"flag": "config.json", "path": str(self.root / "config.json"), "used": True}])

    def test_B09_right_host_wrong_scheme(self):
        """B09 | Right host, wrong scheme | Fetch
        http://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true |
        Refused; no request is sent | The allow-list entry is https; the scheme
        is part of the match (§5, and JS1's U05)"""
        refusal = self.assert_fetch_refused("http://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true")
        self.assertEqual(refusal.rules, [P.R_FETCH_SCHEME])

    def test_B10_userinfo_trick(self):
        """B10 | Userinfo trick | Fetch
        https://boards-api.greenhouse.io@evil.example/jobs | Refused; no
        request is sent | The real host is evil.example; what stands before the
        @ is userinfo, not the host (§5)"""
        refusal = self.assert_fetch_refused("https://boards-api.greenhouse.io@evil.example/jobs")
        self.assertIn(P.R_FETCH_USERINFO, refusal.rules)
        self.assertIn(P.R_FETCH_HOST, refusal.rules)
        self.assertIn("'evil.example'", str(refusal))

    def test_B11_sibling_folder_prefix_trick(self):
        """B11 | Sibling-folder prefix trick | Write output-evil/report.txt,
        where output-evil/ sits beside output/ | Refused; nothing is written |
        The path is judged on whole folder names after resolution, not on a
        string prefix: output-evil is not output, just as in B03 (§5)"""
        before = self.snapshot()
        with self.assertRaises(PolicyRefusal) as caught:
            self.tools().write("output-evil/report.txt", b"x")
        self.assertEqual(caught.exception.rules, [P.R_WRITE_APPROVAL])
        self.assertIn("outside state/, evidence/, output/", str(caught.exception))
        self.assertEqual(self.snapshot(), before)


class PolicyRuleTests(BoundaryCase):
    """§5 rules the B rows do not reach, and the 2026-11-06 decisions."""

    def test_allowed_fetches_reach_the_opener(self):
        self.send.side_effect = None
        self.send.return_value = _FakeResponse()
        tools = self.tools()
        for url in (STRIPE_URL, "https://api.ashbyhq.com/posting-api/job-board/notion?includeCompensation=true",
                    "https://BOARDS-API.greenhouse.io:443/v1/boards/stripe/jobs?content=true"):
            with self.subTest(url=url):
                self.assertEqual(tools.fetch(url).status, 200)
        self.assertEqual(self.send.call_count, 3)

    def test_fetch_refusals(self):
        cases = {
            "https://boards-api.greenhouse.io:8443/v1/boards/stripe/jobs?content=true": P.R_FETCH_PORT,
            "https://evil.boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true": P.R_FETCH_HOST,
            "https://boards-api.greenhouse.io/v1/boards/stripe/jobs": P.R_FETCH_FORM,
            "https://boards-api.greenhouse.io/v1/boards/../jobs?content=true": P.R_FETCH_FORM,
            "https://api.ashbyhq.com/posting-api/job-board/notion": P.R_FETCH_FORM,
            "https://api.ashbyhq.com/v1/boards/notion/jobs?content=true": P.R_FETCH_FORM,
        }
        for url, rule in cases.items():
            with self.subTest(url=url):
                self.assertIn(rule, self.assert_fetch_refused(url).rules)

    def test_unconfigured_board_is_refused(self):
        refusal = self.assert_fetch_refused("https://boards-api.greenhouse.io/v1/boards/notconfigured/jobs?content=true")
        self.assertEqual(refusal.rules, [P.R_FETCH_BOARD])
        self.assertIn("'notconfigured'", str(refusal))

    def test_writes_inside_the_working_folders_need_no_approval(self):
        tools = self.tools()
        for path in ("state/state_2026-11-06T120000Z.json", "evidence/greenhouse_stripe.json", "output/run.json"):
            with self.subTest(path=path):
                tools.write(path, b"{}")
                self.assertEqual((self.root / path).read_bytes(), b"{}")

    def test_overwrite_needs_approval_and_an_approval_is_used_once(self):
        (self.root / "state" / "state.json").write_bytes(b"[]")
        with self.assertRaises(PolicyRefusal) as caught:
            self.tools().write("state/state.json", b"[1]")
        self.assertEqual(caught.exception.rules, [P.R_WRITE_APPROVAL])
        tools = self.tools(approvals=["state/state.json"])
        tools.write("state/state.json", b"[1]")
        with self.assertRaises(PolicyRefusal) as caught:
            tools.write("state/state.json", b"[2]")
        self.assertEqual(caught.exception.rules, [P.R_WRITE_APPROVAL_USED])
        self.assertEqual((self.root / "state" / "state.json").read_bytes(), b"[1]")

    def test_never_written_even_with_approval(self):
        (self.root / "evidence" / "snapshots" / "s.json").write_bytes(b"{}")
        cases = {
            "GATE.md": P.R_WRITE_GATE,
            "gate.md": P.R_WRITE_GATE,
            "evidence/snapshots/s.json": P.R_WRITE_READ_ONLY,
            "evidence/gate_probes/new.json": P.R_WRITE_READ_ONLY,
            str(self.outside / "x.txt"): P.R_WRITE_INSIDE,
        }
        before = self.snapshot()
        for path, rule in cases.items():
            with self.subTest(path=path):
                with self.assertRaises(PolicyRefusal) as caught:
                    self.tools(approvals=[path]).write(path, b"x")
                self.assertEqual(caught.exception.rules, [rule])
        self.assertEqual(self.snapshot(), before)

    def test_reads_outside_the_project_are_refused(self):
        (self.outside / "secret.txt").write_bytes(b"s")
        for path in ("../elsewhere/secret.txt", "output/link/secret.txt", str(self.outside / "secret.txt")):
            with self.subTest(path=path):
                with self.assertRaises(PolicyRefusal) as caught:
                    self.tools().read(path)
                self.assertEqual(caught.exception.rules, [P.R_READ_INSIDE])

    def test_redirect_is_returned_not_followed(self):
        self.send.side_effect = urllib.error.HTTPError(
            STRIPE_URL, 301, "Moved", {"Location": "https://evil.example/", "Content-Type": "text/html"}, io.BytesIO(b""))
        result = self.tools().fetch(STRIPE_URL)
        self.assertEqual((result.status, result.location), (301, "https://evil.example/"))
        self.assertEqual(self.send.call_count, 1)


if __name__ == "__main__":
    unittest.main()
