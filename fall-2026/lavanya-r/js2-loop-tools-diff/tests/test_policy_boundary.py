"""Boundary tests for the permission policy (GATE.md section 5).

The decision table is tested, AND enforcement is tested: a refused write
leaves no file anywhere, a refused URL never reaches the network.
"""

import shutil
import unittest

from agent import net
from agent.policy import (ASK, NeedsApproval, Refused, always_approve,
                          no_approval)
from tests.boundary_cases import CASES, EXTRA, outcome, sandbox


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp, self.policy, self.outside = sandbox()
        self.root = self.policy.root

    def tearDown(self):
        shutil.rmtree(self.tmp)


class TestFourteenCases(Base):
    def test_each_case_matches_gate(self):
        for n, op, target, expected in CASES:
            with self.subTest(case=n, target=target):
                self.assertEqual(outcome(self.policy, self.outside, op,
                                         target), expected)

    def test_extra_cases(self):
        for op, target, expected in EXTRA:
            with self.subTest(target=target):
                self.assertEqual(outcome(self.policy, self.outside, op,
                                         target), expected)


class TestRedirects(Base):
    """GATE 5: a redirect is checked against the same allow-list."""

    def redirect(self, newurl):
        import urllib.request
        get = net.make_get(self.policy)
        req = urllib.request.Request(
            "https://api.lever.co/v0/postings/palantir?mode=json")
        return get.redirect_handler.redirect_request(
            req, None, 302, "Found", {}, newurl)

    def test_redirect_off_the_list_is_refused(self):
        for url in ["https://evil.example/jobs",
                    "http://api.lever.co/v0/postings/palantir",
                    "https://api.lever.co.evil.example/x"]:
            with self.subTest(url=url), self.assertRaises(Refused):
                self.redirect(url)

    def test_redirect_within_the_list_is_followed(self):
        new = self.redirect("https://api.lever.co/v0/postings/palantir2")
        self.assertEqual(new.full_url,
                         "https://api.lever.co/v0/postings/palantir2")


class TestEnforcement(Base):
    def test_refused_writes_leave_nothing_behind(self):
        for target in ["runs/../GATE.md", "runs-evil/x.json",
                       "runs/link/x.json", f"{self.outside}/x.json",
                       "../js1-contract-and-watch/state/x.json",
                       "runs/finallink"]:
            with self.subTest(target=target):
                with self.assertRaises(Refused):
                    self.policy.write_bytes(target, b"EVIL")
        self.assertEqual((self.root / "GATE.md").read_text(), "gate\n")
        self.assertEqual(sorted(p.name for p in self.outside.iterdir()),
                         ["secret.txt"])
        self.assertEqual(list((self.root / "runs-evil").iterdir()), [])

    def test_allowed_write_lands_inside(self):
        real = self.policy.write_bytes("runs/x/trace.json", b"ok")
        self.assertEqual(real, self.root / "runs" / "x" / "trace.json")
        self.assertEqual(real.read_bytes(), b"ok")

    def test_state_overwrite_needs_approval(self):
        path = "state/greenhouse-databricks.json"
        self.assertEqual(self.policy.decide_write(path).outcome, ASK)
        with self.assertRaises(NeedsApproval):
            self.policy.write_bytes(path, b"NEW", approver=no_approval)
        with self.assertRaises(NeedsApproval):
            self.policy.write_bytes(path, b"NEW")          # no approver at all
        self.assertEqual((self.root / path).read_text(), "{}\n")
        self.policy.write_bytes(path, b"NEW", approver=always_approve)
        self.assertEqual((self.root / path).read_bytes(), b"NEW")

    def test_approver_is_only_asked_when_needed(self):
        asked = []
        self.policy.write_bytes("runs/a.json", b"x",
                                approver=lambda p: asked.append(p) or True)
        self.assertEqual(asked, [])

    def test_read_outside_refused(self):
        with self.assertRaises(Refused):
            self.policy.read_bytes(self.outside / "secret.txt")
        with self.assertRaises(Refused):
            self.policy.read_bytes("runs/link/secret.txt")   # via symlink

    def test_never_actions_raise(self):
        for name in ["apply", "email", "message", "login"]:
            with self.subTest(name=name), self.assertRaises(Refused):
                self.policy.check_action(name)

    def test_refused_url_never_opens_a_socket(self):
        import urllib.request
        called = []
        real_open = urllib.request.OpenerDirector.open
        urllib.request.OpenerDirector.open = \
            lambda *a, **k: called.append(a) or (_ for _ in ()).throw(
                AssertionError("network was reached"))
        try:
            get = net.make_get(self.policy)
            for url in ["https://www.linkedin.com/jobs/",
                        "http://api.lever.co/v0/postings/palantir",
                        "https://boards-api.greenhouse.io.evil.example/x"]:
                with self.subTest(url=url), self.assertRaises(Refused):
                    get(url, 5)
        finally:
            urllib.request.OpenerDirector.open = real_open
        self.assertEqual(called, [])


if __name__ == "__main__":
    unittest.main()
