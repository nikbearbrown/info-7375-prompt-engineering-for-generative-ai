"""Boundary tests for the permission policy, written before policy.py exists.

Cases 1-15 are Swathi's predictions from BOUNDARY-CASES.md (2026-11-04), one
test each; every docstring quotes the case's request and prediction word for
word. Tests marked "control" are extra checks of the interface she approved
on 2026-11-04 (https only, state updates allowed, approval bound to the state's
hash); they are not among her 15 predictions. Written by Claude Code. No test
makes a network request: socket connections fail inside no_network().
"""
from contextlib import contextmanager
import email.message
import hashlib
import io
import json
import os
from pathlib import Path
import re
import socket
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import urllib.request

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import policy  # noqa: E402  (does not exist until the policy code is written)

APPROVAL = Path("approvals") / "reset-state.json"


@contextmanager
def no_network():
    def refuse(*args, **kwargs):
        raise AssertionError("a network connection was attempted")
    with patch.object(socket, "create_connection", refuse), patch.object(socket.socket, "connect", refuse):
        yield


class PolicyCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        self.root = base / "js2"
        self.outside = base / "outside"
        for folder in ("runs", "state", "persona", "approvals"):
            (self.root / folder).mkdir(parents=True)
        self.outside.mkdir()
        self.persona_file = self.root / "persona" / "priya-nair.resume.example.json"
        self.persona_file.write_text('{"_comment": "FICTIONAL"}', encoding="utf-8")
        self.state_file = self.root / "state" / "seen_ids.json"
        self.state_file.write_text('{"seen_ids": [1, 2, 3]}', encoding="utf-8")
        self.policy = policy.Policy(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def assertRefused(self, rule, call, *args, **kwargs):
        with self.assertRaises(policy.PolicyRefused) as caught:
            call(*args, **kwargs)
        self.assertEqual(caught.exception.rule, rule, str(caught.exception))
        return caught.exception

    def approve(self, state_bytes, **overrides):
        """Stands in for Swathi writing her approval file; this is the test, not the agent."""
        approval = {"state_sha256": hashlib.sha256(state_bytes).hexdigest(),
                    "date": "2026-11-04", "reason": "test: approved reset"}
        approval.update(overrides)
        (self.root / APPROVAL).write_text(json.dumps(approval), encoding="utf-8")


class Hosts(PolicyCase):
    def test_case_01_host_not_on_allow_list(self):
        """Case 1: Fetch from a host not on the allow-list (example.com) -> Refused; no request is sent"""
        with no_network():
            self.assertRefused("host_not_allowed", self.policy.check_host, "https://example.com/jobs")

    def test_case_02_lookalike_host(self):
        """Case 2: Fetch from the lookalike host boards-api.greenhouse.io.evil.example -> Refused"""
        with no_network():
            self.assertRefused("host_not_allowed", self.policy.check_host,
                               "https://boards-api.greenhouse.io.evil.example/v1/boards/databricks/jobs")

    def test_case_03_allowed_ashby_host(self):
        """Case 3: Fetch from the allowed host api.ashbyhq.com (Plaid) -> Allowed"""
        url = "https://api.ashbyhq.com/posting-api/job-board/plaid"
        with no_network():
            self.assertEqual(self.policy.check_host(url), url)

    def test_case_04_redirect_to_host_off_allow_list(self):
        """Case 4: An allowed host redirects to a host not on the allow-list -> Refused"""
        handler = self.policy.redirect_handler()
        request = urllib.request.Request("https://boards-api.greenhouse.io/v1/boards/databricks/jobs")
        headers = email.message.Message()
        headers["Location"] = "https://example.com/jobs"
        with no_network():
            self.assertRefused("redirect_not_allowed", handler.http_error_302,
                               request, io.BytesIO(b""), 302, "Found", headers)

    def test_control_http_on_allowed_host_is_refused(self):
        """Control (approved addition, not in GATE.md): plain http is refused even on an allowed host."""
        self.assertRefused("host_not_allowed", self.policy.check_host,
                           "http://boards-api.greenhouse.io/v1/boards/databricks/jobs")

    def test_control_redirect_within_allowed_hosts_is_allowed(self):
        """Control: a redirect to an allowed host is not refused."""
        url = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
        self.assertEqual(self.policy.check_redirect(url), url)


class Writes(PolicyCase):
    def test_case_05_new_file_inside_runs(self):
        """Case 5: Write a new file inside runs/ -> Allowed"""
        path = self.policy.write_evidence(self.root / "runs" / "run1.json", b"{}")
        self.assertEqual(Path(path).read_bytes(), b"{}")

    def test_case_06_dotdot_escapes_runs(self):
        """Case 6: Write a path with .. that escapes runs/ (e.g. runs/../GATE.md) -> Refused"""
        self.assertRefused("write_outside", self.policy.check_write, self.root / "runs" / ".." / "GATE.md")
        self.assertFalse((self.root / "GATE.md").exists())

    def test_case_07_prefix_trick_runs_evil(self):
        """Case 7: Prefix trick: write to runs-evil/ beside runs/ -> Refused"""
        (self.root / "runs-evil").mkdir()
        self.assertRefused("write_outside", self.policy.check_write, self.root / "runs-evil" / "x.json")

    @unittest.skipUnless(hasattr(os, "symlink"), "needs symlink support")
    def test_case_08_symlink_inside_runs_points_outside(self):
        """Case 8: Write through a symlink inside runs/ that points outside the allowed folders -> Refused"""
        os.symlink(self.outside, self.root / "runs" / "link")
        self.assertRefused("write_outside", self.policy.check_write, self.root / "runs" / "link" / "x.json")
        self.assertRefused("write_outside", self.policy.write_evidence, self.root / "runs" / "link" / "x.json", b"x")
        self.assertEqual(list(self.outside.iterdir()), [])

    def test_control_state_may_be_updated_on_a_normal_run(self):
        """Control (decision 2026-11-04): state/ may be updated by write_state; only a reset needs approval."""
        self.policy.write_state(b'{"seen_ids": [1]}')
        self.policy.write_state(b'{"seen_ids": [1, 4]}')
        self.assertEqual(self.state_file.read_bytes(), b'{"seen_ids": [1, 4]}')


class Reads(PolicyCase):
    def test_case_09_read_persona_file(self):
        """Case 9: Read a persona file -> Allowed (read only)"""
        self.assertEqual(self.policy.check_read(self.persona_file), self.persona_file.resolve())

    def test_case_10_write_persona_file(self):
        """Case 10: Write to a persona file -> Refused (readable does not mean writable)"""
        before = self.persona_file.read_bytes()
        self.assertRefused("write_outside", self.policy.check_write, self.persona_file)
        self.assertEqual(self.persona_file.read_bytes(), before)

    def test_case_11_read_outside_js2_folder(self):
        """Case 11: Read a file outside my JS2 folder and the persona files -> Refused"""
        secret = self.outside / "notes.txt"
        secret.write_text("not for the agent", encoding="utf-8")
        self.assertRefused("read_outside", self.policy.check_read, secret)
        self.assertRefused("read_outside", self.policy.check_read, self.root / ".." / "outside" / "notes.txt")


class Evidence(PolicyCase):
    def test_case_12_overwrite_earlier_raw_response(self):
        """Case 12: Overwrite an earlier run's raw response -> Refused (evidence is never silently overwritten)"""
        path = self.root / "runs" / "raw_run1.json"
        self.policy.write_evidence(path, b"first run")
        self.assertRefused("overwrite_evidence", self.policy.write_evidence, path, b"second run")
        self.assertEqual(path.read_bytes(), b"first run")


class StateReset(PolicyCase):
    def test_case_13_reset_without_approval(self):
        """Case 13: Reset the state without my approval -> Refused immediately, with a report that my approval is required; the agent does not wait"""
        before = self.state_file.read_bytes()
        started = time.monotonic()
        with patch("builtins.input", side_effect=AssertionError("the agent waited for input")):
            refused = self.assertRefused("approval_required", self.policy.reset_state)
        self.assertLess(time.monotonic() - started, 1.0)
        self.assertIn("approvals/reset-state.json", str(refused))
        self.assertEqual(self.state_file.read_bytes(), before)

    def test_case_14_reset_with_agents_own_approval(self):
        """Case 14: Reset the state with the agent's own approval -> Refused"""
        before = self.state_file.read_bytes()
        approval = json.dumps({"state_sha256": hashlib.sha256(before).hexdigest(),
                               "date": "2026-11-04", "reason": "agent approves itself"}).encode()
        self.assertRefused("write_outside", self.policy.check_write, self.root / APPROVAL)
        self.assertRefused("write_outside", self.policy.write_evidence, self.root / APPROVAL, approval)
        with self.assertRaises(TypeError):
            self.policy.reset_state(approved=True)
        self.assertFalse((self.root / APPROVAL).exists())
        self.assertEqual(self.state_file.read_bytes(), before)

    def test_case_15_reset_with_my_explicit_approval(self):
        """Case 15: Reset the state with my explicit approval -> Allowed"""
        before = self.state_file.read_bytes()
        self.approve(before)
        saved = Path(self.policy.reset_state())
        self.assertEqual(saved.resolve().parent, (self.root / "runs").resolve())
        self.assertEqual(saved.read_bytes(), before)
        self.assertFalse(self.state_file.exists())

    def test_control_approval_for_a_different_state_is_refused(self):
        """Control: an approval whose hash does not match the current state is refused, so it can't be reused."""
        self.approve(b"some older state")
        self.assertRefused("approval_invalid", self.policy.reset_state)
        self.assertTrue(self.state_file.exists())


class GateSync(unittest.TestCase):
    def test_policy_constants_match_gate_md(self):
        """The allow-list and writable folders in policy.py are exactly those in GATE.md's Permission policy."""
        gate = (HERE / "GATE.md").read_text(encoding="utf-8")
        section = gate.split("## Permission policy", 1)[1].split("\n## ", 1)[0]
        hosts_line = next(line for line in section.splitlines() if line.startswith("- Hosts:"))
        writes_line = next(line for line in section.splitlines() if line.startswith("- Writes:"))
        gate_hosts = set(re.findall(r"\b(?:[a-z0-9-]+\.)+[a-z]{2,}\b", hosts_line))
        gate_write_dirs = set(re.findall(r"\b([a-z]+)/", writes_line))
        self.assertEqual(set(policy.ALLOWED_HOSTS), gate_hosts)
        self.assertEqual(set(policy.WRITE_DIRS), gate_write_dirs)


if __name__ == "__main__":
    unittest.main()
