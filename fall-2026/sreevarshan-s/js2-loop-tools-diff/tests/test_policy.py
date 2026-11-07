import os
import unittest

from js2 import policy
from tests.helpers import SandboxTestCase


class AllowRequestTest(SandboxTestCase):
    def test_blocks_non_https(self):
        self.assertFalse(policy.allow_request("http://boards-api.greenhouse.io/v1/boards/stripe/jobs"))
        self.assertEqual(policy.DECISIONS[-1]["decision"], "blocked")
        self.assertIn("not https", policy.DECISIONS[-1]["reason"])

    def test_blocks_host_off_allow_list(self):
        for url in [
            "https://example.com/jobs",
            "https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs",
            "https://api.lever.co@evil.com/v0/postings/spotify",
        ]:
            self.assertFalse(policy.allow_request(url), url)
            self.assertIn("allow-list", policy.DECISIONS[-1]["reason"])

    def test_allows_https_allow_listed_hosts(self):
        self.assertTrue(policy.allow_request("https://boards-api.greenhouse.io/v1/boards/stripe/jobs"))
        self.assertTrue(policy.allow_request("https://api.lever.co/v0/postings/spotify?mode=json"))
        self.assertEqual([d["decision"] for d in policy.DECISIONS], ["allowed", "allowed"])


class AllowWriteTest(SandboxTestCase):
    def test_blocks_dot_dot(self):
        path = os.path.join(self.output, "raw", "..", "..", "escape.json")
        self.assertIs(policy.allow_write(path), False)
        self.assertEqual(policy.DECISIONS[-1]["decision"], "blocked")

    def test_blocks_sibling_prefix_folder(self):
        evil = self.output + "-evil"
        os.makedirs(evil)
        self.assertIs(policy.allow_write(os.path.join(evil, "x.json")), False)

    def test_blocks_output_folder_itself(self):
        self.assertIs(policy.allow_write(self.output), False)

    def test_blocks_symlink_pointing_outside(self):
        outside = os.path.join(self.tmp, "outside")
        os.makedirs(outside)
        link = os.path.join(self.output, "link")
        os.symlink(outside, link)
        self.assertIs(policy.allow_write(os.path.join(link, "x.json")), False)
        self.assertIn("outside", policy.DECISIONS[-1]["reason"])

    def test_blocks_file_symlink_pointing_outside(self):
        target = os.path.join(self.tmp, "victim.txt")
        open(target, "w").close()
        link = os.path.join(self.output, "state.txt")
        os.symlink(target, link)
        self.assertIs(policy.allow_write(link), False)

    def test_overwriting_existing_evidence_needs_approval(self):
        path = os.path.join(self.output, "raw", "a.json")
        os.makedirs(os.path.dirname(path))
        with open(path, "wb") as f:
            f.write(b"{}")
        self.assertEqual(policy.allow_write(path), policy.NEEDS_APPROVAL)
        self.assertEqual(policy.DECISIONS[-1]["decision"], "needs_approval")

    def test_allows_normal_new_write(self):
        path = os.path.join(self.output, "raw", "new.json")
        self.assertIs(policy.allow_write(path), True)
        self.assertEqual(policy.DECISIONS[-1]["decision"], "allowed")

    def test_allows_overwriting_non_evidence_state_file(self):
        path = os.path.join(self.output, "state.txt")
        open(path, "w").close()
        self.assertIs(policy.allow_write(path), True)

    def test_write_bytes_writes_only_when_allowed(self):
        good = os.path.join(self.output, "raw", "ok.json")
        self.assertIs(policy.write_bytes(good, b"{}"), True)
        with open(good, "rb") as f:
            self.assertEqual(f.read(), b"{}")
        self.assertEqual(policy.write_bytes(good, b"changed"), policy.NEEDS_APPROVAL)
        with open(good, "rb") as f:
            self.assertEqual(f.read(), b"{}")
        bad = os.path.join(self.tmp, "escape.json")
        self.assertIs(policy.write_bytes(bad, b"{}"), False)
        self.assertFalse(os.path.exists(bad))

    def test_every_decision_is_logged_with_reason(self):
        with self.assertLogs("js2.policy", level="INFO") as logs:
            policy.allow_request("http://example.com")
            policy.allow_write(os.path.join(self.output, "a.json"))
        self.assertEqual(len(logs.output), 2)
        for d in policy.DECISIONS:
            self.assertTrue(d["reason"])


if __name__ == "__main__":
    unittest.main()
