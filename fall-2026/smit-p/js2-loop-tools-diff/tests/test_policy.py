"""Boundary tests for agent/policy.py. Case ids P1..P25 match the prediction table in POLICY.md."""

import os
import tempfile
import unittest

from agent import policy
from agent.policy import ALLOW, DENY, NEEDS_APPROVAL

GH = "https://boards-api.greenhouse.io/v1/boards/figma/jobs"


class RequestBoundary(unittest.TestCase):
    def check(self, url, method="GET", headers=None):
        return policy.check_request(method, url, headers)

    def test_P01_allowed_host(self):
        self.assertEqual(self.check(GH).result, ALLOW)

    def test_P02_host_off_list(self):
        d = self.check("https://evil.example.com/jobs")
        self.assertEqual((d.result, "host" in d.reason), (DENY, True))

    def test_P03_lookalike_prefix_host(self):
        d = self.check("https://boards-api.greenhouse.io.evil.com/v1/boards/figma/jobs")
        self.assertEqual((d.result, "host" in d.reason), (DENY, True))

    def test_P04_suffix_trick_host(self):
        d = self.check("https://evilgreenhouse.io/v1/boards/figma/jobs")
        self.assertEqual((d.result, "host" in d.reason), (DENY, True))

    def test_P05_plain_http(self):
        d = self.check(GH.replace("https", "http"))
        self.assertEqual((d.result, "scheme" in d.reason), (DENY, True))

    def test_P06_credentials_in_url(self):
        d = self.check("https://user:pw@api.lever.co/v0/postings/spotify")
        self.assertEqual((d.result, "credentials" in d.reason), (DENY, True))

    def test_P07_nondefault_port(self):
        d = self.check("https://api.lever.co:8443/v0/postings/spotify")
        self.assertEqual((d.result, "port" in d.reason), (DENY, True))

    def test_P08_post_apply(self):
        d = self.check("https://api.lever.co/v0/postings/spotify/abc/apply", method="POST")
        self.assertEqual((d.result, "method" in d.reason), (DENY, True))

    def test_P09_get_apply_path(self):
        d = self.check("https://api.lever.co/v0/postings/spotify/abc/apply")
        self.assertEqual((d.result, "apply" in d.reason), (DENY, True))

    def test_P10_ip_literal(self):
        d = self.check("https://127.0.0.1/")
        self.assertEqual((d.result, "host" in d.reason), (DENY, True))

    def test_P11_uppercase_host_normalized(self):
        self.assertEqual(self.check("https://API.LEVER.CO/v0/postings/spotify").result, ALLOW)

    def test_P12_authorization_header(self):
        d = self.check(GH, headers={"Authorization": "Bearer x"})
        self.assertEqual((d.result, "credential" in d.reason), (DENY, True))


class PathBoundary(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.outside = tempfile.TemporaryDirectory()
        self.base = self.tmp.name
        for d in ("jobs/state", "config", "fixtures", "jobs-evil"):
            os.makedirs(os.path.join(self.base, d))
        os.symlink(self.outside.name, os.path.join(self.base, "jobs", "escape"))

    def tearDown(self):
        self.tmp.cleanup()
        self.outside.cleanup()

    def test_P13_write_inside_jobs(self):
        self.assertEqual(policy.check_write(self.base, "jobs/state/figma.state.json").result, ALLOW)

    def test_P14_dotdot_escape(self):
        self.assertEqual(policy.check_write(self.base, "jobs/../GATE.md").result, DENY)

    def test_P15_prefix_trick_sibling(self):
        self.assertEqual(policy.check_write(self.base, "jobs-evil/x.json").result, DENY)

    def test_P16_symlink_escape(self):
        self.assertEqual(policy.check_write(self.base, "jobs/escape/x.json").result, DENY)
        with self.assertRaises(policy.PolicyDenied):
            policy.guarded_write(self.base, "jobs/escape/x.json", "{}")
        self.assertEqual(os.listdir(self.outside.name), [])  # nothing landed outside

    def test_P17_absolute_outside(self):
        self.assertEqual(policy.check_write(self.base, "/tmp/x.json").result, DENY)

    def test_P18_read_config(self):
        self.assertEqual(policy.check_read(self.base, "config/boards.json").result, ALLOW)

    def test_P19_config_write_needs_approval(self):
        self.assertEqual(policy.check_write(self.base, "config/boards.json").result, NEEDS_APPROVAL)
        with self.assertRaises(policy.PolicyDenied):
            policy.guarded_write(self.base, "config/boards.json", "[]")
        self.assertFalse(os.path.exists(os.path.join(self.base, "config/boards.json")))

    def test_P20_config_write_with_approval(self):
        d = policy.check_write(self.base, "config/budgets.json", approved=True)
        self.assertEqual(d.result, ALLOW)

    def test_P21_read_outside(self):
        self.assertEqual(policy.check_read(self.base, "/etc/passwd").result, DENY)

    def test_P22_read_own_docs_denied(self):
        self.assertEqual(policy.check_read(self.base, "GATE.md").result, DENY)

    def test_P23_baseline_delete_needs_approval(self):
        path = "jobs/state/figma.state.json"
        self.assertEqual(policy.check_delete(self.base, path).result, NEEDS_APPROVAL)
        self.assertEqual(policy.check_delete(self.base, path, approved=True).result, ALLOW)

    def test_P24_forbidden_actions(self):
        for name in ("apply", "email", "message", "login", "Apply"):
            self.assertEqual(policy.check_action(name).result, DENY, name)

    def test_P25_nul_byte(self):
        d = policy.check_write(self.base, "jobs/runs/x.json\0.sh")
        self.assertEqual((d.result, d.reason), (DENY, "invalid path"))

    def test_write_inside_jobs_not_fooled_by_trailing_slash_root(self):
        # The write root itself is allowed as a parent, but a file named "jobs" beside it is not.
        self.assertEqual(policy.check_write(self.base, "jobsx").result, DENY)


if __name__ == "__main__":
    unittest.main()
