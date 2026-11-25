"""The 23 boundary cases of BOUNDARY-TESTS.md, one test each, in the same order.

Writes go to a temporary folder that stands in for the project, so no test touches the real runs/ or evidence/.
No test opens a network connection.
"""
import shutil
import tempfile
import unittest
import urllib.request
from pathlib import Path

from agent import tools
from agent.policy import Policy, PolicyRefused

HOSTS = ["boards-api.greenhouse.io", "api.lever.co", "api.ashbyhq.com"]


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base)
        self.root = self.base / "project"
        for d in ("runs", "evidence", "config", "agent"):
            (self.root / d).mkdir(parents=True)
        (self.root / "config" / "boards.json").write_text("[]")
        (self.root / "GATE.md").write_text("gate")
        self.policy = Policy(root=self.root, hosts=HOSTS)

    def refused_write(self, path, **kwargs):
        with self.assertRaises(PolicyRefused):
            self.policy.write_text(path, "x", **kwargs)

    def test_01_greenhouse_get_allowed(self):
        url = "https://boards-api.greenhouse.io/v1/boards/pinterest/jobs?content=true"
        self.assertEqual(self.policy.check_request("GET", url), url)

    def test_02_lever_get_allowed(self):
        url = "https://api.lever.co/v0/postings/spotify?mode=json"
        self.assertEqual(self.policy.check_request("GET", url), url)

    def test_03_host_off_allow_list_refused(self):
        opened = []
        with self.assertRaises(PolicyRefused):
            tools.http_get("https://example.com/jobs", self.policy, 5, opener=type("O", (), {"open": lambda *a, **k: opened.append(a)})())
        self.assertEqual(opened, [], "refused before any connection")

    def test_04_look_alike_host_refused(self):
        with self.assertRaises(PolicyRefused):
            self.policy.check_request("GET", "https://boards-api.greenhouse.io.evil.com/jobs")

    def test_05_plain_http_refused(self):
        with self.assertRaises(PolicyRefused):
            self.policy.check_request("GET", "http://boards-api.greenhouse.io/v1/boards/pinterest/jobs")

    def test_06_post_refused(self):
        with self.assertRaises(PolicyRefused):
            self.policy.check_request("POST", "https://api.lever.co/v0/postings/spotify?mode=json")

    def test_07_redirect_off_allow_list_refused(self):
        handler = tools._redirect_handler(self.policy)()
        request = urllib.request.Request("https://api.lever.co/v0/postings/spotify?mode=json")
        with self.assertRaises(PolicyRefused):
            handler.redirect_request(request, None, 302, "Found", {}, "https://example.com/")
        allowed = handler.redirect_request(request, None, 302, "Found", {}, "https://api.lever.co/v0/postings/x")
        self.assertEqual(allowed.full_url, "https://api.lever.co/v0/postings/x")

    def test_08_write_in_runs_allowed(self):
        path = self.policy.write_text("runs/state/seen_ids.json", "{}")
        self.assertEqual(path.read_text(), "{}")

    def test_09_write_in_evidence_allowed(self):
        self.assertTrue(self.policy.write_text("evidence/raw/x.json", "{}").exists())

    def test_10_dotdot_escape_refused(self):
        self.refused_write("runs/../GATE.md")
        self.assertEqual((self.root / "GATE.md").read_text(), "gate", "the file outside runs/ is untouched")

    def test_11_prefix_trick_refused(self):
        self.refused_write("runs-evil/x.json")
        self.assertFalse((self.root / "runs-evil").exists())

    def test_12_symlink_escape_refused(self):
        outside = self.base / "outside"
        outside.mkdir()
        (self.root / "runs" / "link").symlink_to(outside, target_is_directory=True)
        self.refused_write("runs/link/x.json")
        self.assertEqual(list(outside.iterdir()), [], "nothing was written through the symlink")

    def test_13_absolute_outside_refused(self):
        target = self.base / "x.json"
        self.refused_write(target)
        self.assertFalse(target.exists())

    def test_14_read_config_allowed(self):
        self.assertEqual(self.policy.check_read("config/boards.json").read_text(), "[]")

    def test_15_read_outside_refused(self):
        (self.base / "js1").mkdir()
        (self.base / "js1" / "README.md").write_text("other")
        with self.assertRaises(PolicyRefused):
            self.policy.check_read("../js1/README.md")

    def test_16_config_write_without_approval_refused(self):
        with self.assertRaisesRegex(PolicyRefused, "needs my approval"):
            self.policy.write_text("config/budgets.json", "{}")
        self.assertFalse((self.root / "config" / "budgets.json").exists())

    def test_17_config_write_with_approval_allowed(self):
        self.assertTrue(self.policy.write_text("config/budgets.json", "{}", approved=True).exists())

    def test_18_rule_write_without_approval_refused(self):
        with self.assertRaisesRegex(PolicyRefused, "needs my approval"):
            self.policy.write_text("agent/rule.py", "x")

    # Cases 19 to 23: my own predictions, committed before these tests (BOUNDARY-TESTS.md).
    def test_19_ashby_get_allowed(self):
        url = "https://api.ashbyhq.com/posting-api/job-board/ramp"
        self.assertEqual(self.policy.check_request("GET", url), url)

    def test_20_userinfo_trick_refused(self):
        with self.assertRaises(PolicyRefused):
            self.policy.check_request("GET", "https://api.lever.co@example.com/v0/postings/x")

    def test_21_other_port_allowed(self):
        url = "https://api.lever.co:8443/v0/postings/spotify"
        self.assertEqual(self.policy.check_request("GET", url), url)

    def test_22_dotdot_into_config_refused(self):
        with self.assertRaisesRegex(PolicyRefused, "needs my approval"):
            self.policy.write_text("evidence/raw/../../config/hosts.json", "{}")
        self.assertFalse((self.root / "config" / "hosts.json").exists())

    def test_23_capital_letters_host_allowed(self):
        url = "https://BOARDS-API.GREENHOUSE.IO/v1/boards/pinterest/jobs"
        self.assertEqual(self.policy.check_request("GET", url), url)


if __name__ == "__main__":
    unittest.main()
