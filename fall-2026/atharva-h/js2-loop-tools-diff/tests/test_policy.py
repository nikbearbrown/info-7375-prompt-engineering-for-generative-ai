"""Boundary cases P1-P23 from PERMISSIONS.md, whose predictions were committed (159adc2)
before this file existed, plus wrong versions 1 and 3 from GATE.md run as mutants."""
import os
import tempfile
import unittest
import urllib.request
from unittest import mock

from helpers import workspace

import policy
from policy import Policy, PolicyViolation
from tools import Tools, _CheckedRedirect

OK_URL = "https://boards-api.greenhouse.io/v1/boards/abacusinsights/jobs"


class Network(unittest.TestCase):
    def setUp(self):
        self.p = Policy(workspace([]))

    def test_P1_allow_listed_https_get(self):
        self.p.check_request("GET", OK_URL)

    def test_P2_host_off_the_allow_list(self):
        with self.assertRaises(PolicyViolation):
            self.p.check_request("GET", "https://example.com/jobs")

    def test_P3_plain_http(self):
        with self.assertRaises(PolicyViolation):
            self.p.check_request("GET", OK_URL.replace("https://", "http://"))

    def test_P4_suffix_trick_host(self):
        with self.assertRaises(PolicyViolation):
            self.p.check_request("GET", "https://boards-api.greenhouse.io.evil.example/v1/boards/x/jobs")

    def test_P5_post(self):
        with self.assertRaises(PolicyViolation):
            self.p.check_request("POST", "https://api.lever.co/v0/postings/xsolla")

    def test_P6_cookie_header(self):
        with self.assertRaises(PolicyViolation):
            self.p.check_request("GET", OK_URL, {"Cookie": "session=1"})

    def test_P7_authorization_header(self):
        with self.assertRaises(PolicyViolation):
            self.p.check_request("GET", OK_URL, {"Authorization": "Bearer x"})

    def test_P8_redirect_off_the_allow_list(self):
        handler = _CheckedRedirect(self.p)
        req = urllib.request.Request("https://api.lever.co/v0/postings/xsolla")
        with self.assertRaises(PolicyViolation):
            handler.redirect_request(req, None, 302, "Found", {}, "https://example.com/")

    def test_P9_credentials_in_url(self):
        with self.assertRaises(PolicyViolation):
            self.p.check_request("GET", "https://user:pw@api.lever.co/v0/postings/xsolla")


class Files(unittest.TestCase):
    def setUp(self):
        self.root = workspace([])
        self.tools = Tools(Policy(self.root, approve=lambda action: False))

    def test_P10_write_inside_runs(self):
        self.tools.make_run_dir("runs/r1")
        self.tools.write_text("runs/r1/trace.jsonl", "{}\n")
        self.assertTrue(os.path.exists(os.path.join(self.root, "runs/r1/trace.jsonl")))

    def test_P11_dot_dot_escape(self):
        with self.assertRaises(PolicyViolation):
            self.tools.write_text("runs/../GATE.md", "x")
        self.assertFalse(os.path.exists(os.path.join(self.root, "GATE.md")))

    def test_P12_prefix_trick_sibling(self):
        with self.assertRaises(PolicyViolation):
            self.tools.write_text("runs-evil/x.json", "x")
        self.assertFalse(os.path.exists(os.path.join(self.root, "runs-evil")))

    def test_P13_symlink_escape(self):
        outside = tempfile.mkdtemp(prefix="js2-outside-")
        os.makedirs(os.path.join(self.root, "runs"))
        os.symlink(outside, os.path.join(self.root, "runs", "link"))
        with self.assertRaises(PolicyViolation):
            self.tools.write_text("runs/link/x.json", "x")
        self.assertEqual(os.listdir(outside), [])

    def test_P14_read_inside_the_folder(self):
        self.assertIn("boards", self.tools.read_text("config/boards.json"))

    def test_P15_readable_is_not_writable(self):
        self.tools.read_text("config/boards.json")
        with self.assertRaises(PolicyViolation):
            self.tools.write_text("config/boards.json", "{}", overwrite=True)

    def test_P16_read_outside_the_folder(self):
        with self.assertRaises(PolicyViolation):
            self.tools.read_text("../js1-contract-and-watch/CONTRACT.md")

    def test_P17_no_overwrite_of_a_run_folder(self):
        self.tools.make_run_dir("runs/r1")
        with self.assertRaises(PolicyViolation):
            self.tools.make_run_dir("runs/r1")
        self.tools.write_text("runs/r1/report.md", "first")
        with self.assertRaises(PolicyViolation):
            self.tools.write_text("runs/r1/report.md", "second")


class Approvals(unittest.TestCase):
    OLD = {"boards": {"ashby/valon": {"seen": ["a", "b"], "present": ["a", "b"]}}}
    DROPPED = {"boards": {"ashby/valon": {"seen": ["a"], "present": ["a"]}}}

    def test_P18_dropping_seen_ids_without_a_terminal(self):
        p = Policy(workspace([]), approve=policy.ask_in_terminal)
        with mock.patch("sys.stdin.isatty", return_value=False), self.assertRaises(PolicyViolation):
            p.check_state_update(self.OLD, self.DROPPED)
        self.assertEqual(p.decisions[-1]["approved"], False)

    def test_P19_dropping_seen_ids_when_approved(self):
        p = Policy(workspace([]), approve=lambda action: True)
        p.check_state_update(self.OLD, self.DROPPED)
        self.assertEqual(p.decisions[-1]["approved"], True)

    def test_P20_write_over_5_mb_without_a_terminal(self):
        root = workspace([])
        tools = Tools(Policy(root, approve=policy.ask_in_terminal))
        tools.make_run_dir("runs/r1")
        with mock.patch("sys.stdin.isatty", return_value=False), self.assertRaises(PolicyViolation):
            tools.write_bytes("runs/r1/big.json", b"x" * (6 * 1024 * 1024))
        self.assertFalse(os.path.exists(os.path.join(root, "runs/r1/big.json")))

    def test_P21_board_list_change_without_a_terminal(self):
        p = Policy(workspace([]), approve=policy.ask_in_terminal)
        with mock.patch("sys.stdin.isatty", return_value=False), self.assertRaises(PolicyViolation):
            p.check_board_list(["ashby/valon"], ["ashby/valon", "lever/xsolla"])

    def test_P22_delete_run_without_a_terminal(self):
        root = workspace([])
        tools = Tools(Policy(root, approve=policy.ask_in_terminal))
        tools.make_run_dir("runs/r1")
        with mock.patch("sys.stdin.isatty", return_value=False), self.assertRaises(PolicyViolation):
            tools.delete_run("runs/r1")
        self.assertTrue(os.path.isdir(os.path.join(root, "runs/r1")))

    def test_P23_delete_run_when_approved(self):
        root = workspace([])
        tools = Tools(Policy(root, approve=lambda action: True))
        tools.make_run_dir("runs/r1")
        tools.delete_run("runs/r1")
        self.assertFalse(os.path.exists(os.path.join(root, "runs/r1")))

    def test_first_run_needs_no_board_list_approval(self):
        Policy(workspace([]), approve=lambda action: False).check_board_list(None, ["ashby/valon"])

    def test_adding_seen_ids_needs_no_approval(self):
        Policy(workspace([]), approve=lambda action: False).check_state_update(
            self.DROPPED, self.OLD)


class WrongVersions(unittest.TestCase):
    """GATE.md wrong versions 1 and 3: each mutant would pass a case the tests above refuse."""

    def test_wrong_version_1_prefix_path_check_is_caught(self):
        root = workspace([])
        prefix_check = lambda path, base: os.path.realpath(path).startswith(os.path.realpath(base))  # noqa: E731
        with mock.patch.object(policy, "inside", prefix_check):
            Policy(root).check_write("runs-evil/x.json")  # the mutant lets the prefix trick through
        with self.assertRaises(PolicyViolation):
            Policy(root).check_write("runs-evil/x.json")  # the real check refuses it (P12)

    def test_wrong_version_3_substring_host_check_is_caught(self):
        p = Policy(workspace([]))

        def substring_check(method, url, headers=None):
            if "greenhouse.io" not in url:
                raise PolicyViolation("off list")
        with mock.patch.object(p, "check_request", substring_check):
            p.check_request("GET", "https://boards-api.greenhouse.io.evil.example/x")  # mutant: passes
            p.check_request("GET", "http://boards-api.greenhouse.io/x")                # mutant: passes
        for url in ("https://boards-api.greenhouse.io.evil.example/x", "http://boards-api.greenhouse.io/x"):
            with self.subTest(url=url), self.assertRaises(PolicyViolation):
                p.check_request("GET", url)  # the real check refuses both (P3, P4)


if __name__ == "__main__":
    unittest.main()
