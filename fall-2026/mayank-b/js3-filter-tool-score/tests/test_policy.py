"""Permission boundary tests. Each name is a row in BOUNDARY-TESTS.md (predictions committed first, CP2)."""
import os
import tempfile
import unittest
from pathlib import Path
import urllib.request

from helpers import RUN_ID, temp_root
from jsa import net, policy
from jsa.policy import PolicyError, authorize, check_url


class Hosts(unittest.TestCase):
    def refused(self, url, reason, method="GET"):
        with self.assertRaises(PolicyError) as cm:
            check_url(url, method)
        self.assertEqual(cm.exception.reason, reason)

    def test_B1_host_off_allowlist(self):
        self.refused("https://example.com/jobs", "host-not-allowed")

    def test_B2_allowed_host_as_substring(self):
        self.refused("https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs", "host-not-allowed")

    def test_B3_plain_http(self):
        self.refused("http://boards-api.greenhouse.io/v1/boards/anthropic/jobs", "scheme-not-https")

    def test_B4_allowed_https_get(self):
        self.assertEqual(check_url("https://api.ashbyhq.com/posting-api/job-board/notion"),
                         "https://api.ashbyhq.com/posting-api/job-board/notion")

    def test_B5_non_get(self):
        self.refused("https://boards-api.greenhouse.io/v1/boards/anthropic/jobs", "method-not-allowed", "POST")

    def test_B6_redirect_refused_not_followed(self):
        handler = net._NoRedirect()
        req = urllib.request.Request("https://boards-api.greenhouse.io/v1/boards/x/jobs")
        with self.assertRaises(PolicyError) as cm:
            handler.redirect_request(req, None, 301, "Moved", {}, "https://evil.example/")
        self.assertEqual(cm.exception.reason, "redirect-refused")

    def test_userinfo_and_port_tricks(self):
        self.refused("https://boards-api.greenhouse.io@evil.com/x", "host-not-allowed")
        self.refused("https://boards-api.greenhouse.io:8443/x", "host-not-allowed")


class Paths(unittest.TestCase):
    def setUp(self):
        self.root = temp_root()
        (self.root / "runs" / RUN_ID).mkdir()

    def refused(self, target, mode, reason, **kw):
        with self.assertRaises(PolicyError) as cm:
            authorize(self.root, target, mode, run_id=RUN_ID, **kw)
        self.assertEqual(cm.exception.reason, reason)

    def test_B7_dotdot_escape_on_write(self):
        self.refused(f"runs/{RUN_ID}/../../state/seen-ids.json", "write", "approval-required")
        self.refused(f"runs/{RUN_ID}/../../config/x.json", "write", "outside-write-root")

    def test_B8_symlink_escape_on_write(self):
        # Review packet (GATE §8): written 2026-11-10 BEFORE the patch, to reproduce JS1's safeWrite defect.
        outside = Path(tempfile.mkdtemp(prefix="js2-outside-"))
        os.symlink(outside, self.root / "runs" / RUN_ID / "link")
        self.refused(f"runs/{RUN_ID}/link/x.json", "write", "outside-write-root")
        self.assertFalse((outside / "x.json").exists())

    def test_B8b_returned_path_is_the_resolved_one(self):
        # Chapter 5's third gap: success tests must check the path the caller will actually use.
        real = self.root / "runs" / RUN_ID / "real"
        real.mkdir()
        os.symlink(real, self.root / "runs" / RUN_ID / "alias")
        p = authorize(self.root, f"runs/{RUN_ID}/alias/f.json", "write", run_id=RUN_ID)
        self.assertEqual(p, (real / "f.json").resolve())

    def test_B9_prefix_trick_sibling(self):
        (self.root / "runs-evil").mkdir()
        self.refused("runs-evil/x.json", "write", "outside-write-root")
        self.refused(f"runs/{RUN_ID}-evil/x.json", "write", "outside-write-root")

    def test_B10_read_inside_read_root(self):
        (self.root / "config/boards.json").write_text("{}")
        self.assertTrue(authorize(self.root, "config/boards.json", "read").samefile(self.root / "config/boards.json"))

    def test_B11_read_outside_read_roots(self):
        self.refused("../js1-contract-and-watch/.env", "read", "outside-read-roots")
        self.refused("src/jsa/policy.py", "read", "outside-read-roots")

    def test_B12_readable_but_not_writable(self):
        self.refused("config/boards.json", "write", "outside-write-root")

    def test_B13_approval_needed_none_given(self):
        self.refused("state/seen-ids.json", "write", "approval-required")

    def test_B14_truthy_approval(self):
        for v in ("yes", True, 1, "true"):
            with self.subTest(approval=v):
                self.refused("state/seen-ids.json", "write", "approval-invalid", approval=v)

    def test_B15_approval_for_other_run(self):
        self.refused("state/seen-ids.json", "write", "approval-invalid", approval="2026-11-09T00-00-00Z")

    def test_B16_exact_approval(self):
        p = authorize(self.root, "state/seen-ids.json", "write", run_id=RUN_ID, approval=RUN_ID)
        self.assertEqual(p.name, "seen-ids.json")

    def test_free_write_inside_run_folder(self):
        p = policy.write_text(self.root, f"runs/{RUN_ID}/trace.jsonl", "x", run_id=RUN_ID)
        self.assertTrue(p.exists())


if __name__ == "__main__":
    unittest.main()
