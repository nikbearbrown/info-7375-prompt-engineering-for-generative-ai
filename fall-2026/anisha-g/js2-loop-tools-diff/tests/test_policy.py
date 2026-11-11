"""Boundary tests for the permission policy (GATE.md section 5).
Each test is one row of PREDICTIONS.md; the expected result is my prediction, written before this file existed."""
import os, tempfile, unittest
from pathlib import Path
from watcher.policy import Policy, Blocked, NeedsApproval
from watcher.fetch import PolicyRedirectHandler

GH = "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs"

class Network(unittest.TestCase):
    def setUp(self): self.p = Policy(base_dir=tempfile.mkdtemp())
    def test_01_greenhouse_get_allowed(self):
        self.p.check_request("GET", GH)                      # no exception = allowed
    def test_02_lever_get_allowed(self):
        self.p.check_request("GET", "https://api.lever.co/v0/postings/palantir?mode=json")
    def test_03_ashby_blocked(self):
        with self.assertRaises(Blocked): self.p.check_request("GET", "https://api.ashbyhq.com/posting-api/job-board/acme")
    def test_04_lookalike_host_blocked(self):
        with self.assertRaises(Blocked): self.p.check_request("GET", "https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs")
    def test_05_userinfo_trick_blocked(self):
        with self.assertRaises(Blocked): self.p.check_request("GET", "https://boards-api.greenhouse.io@evil.com/v1/boards/x/jobs")
    def test_06_post_blocked(self):
        with self.assertRaises(Blocked): self.p.check_request("POST", GH)
    def test_07_plain_http_blocked(self):
        with self.assertRaises(Blocked): self.p.check_request("GET", GH.replace("https://", "http://"))
    def test_08_redirect_off_allowlist_blocked(self):
        import urllib.request
        h = PolicyRedirectHandler(self.p)
        req = urllib.request.Request(GH)
        with self.assertRaises(Blocked) as e:
            h.redirect_request(req, None, 302, "Found", {}, "https://evil.com/")
        self.assertIn("evil.com", str(e.exception))           # the report names the blocked host
    # never-list (GATE 5b): an apply/login path on an allowed host is still refused
    def test_never_apply_path_blocked_even_with_get(self):
        with self.assertRaises(Blocked): self.p.check_request("GET", "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs/1/applications")

class Files(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp()); self.p = Policy(base_dir=self.base)
        (self.base / "reports/job-watch").mkdir(parents=True)
    def test_09_new_report_allowed(self):
        self.p.check_write(self.base / "reports/job-watch/run-1.json")
    def test_10_dotdot_escape_blocked(self):
        with self.assertRaises(Blocked): self.p.check_write(self.base / "reports/job-watch/../../agent.py")
    def test_11_prefix_trick_blocked(self):
        (self.base / "reports/job-watch-evil").mkdir()
        with self.assertRaises(Blocked): self.p.check_write(self.base / "reports/job-watch-evil/x.json")
    def test_12_symlink_escape_blocked(self):
        outside = Path(tempfile.mkdtemp())
        os.symlink(outside, self.base / "reports/job-watch/link")
        with self.assertRaises(Blocked): self.p.check_write(self.base / "reports/job-watch/link/x.json")
    def test_13_absolute_path_blocked(self):
        with self.assertRaises(Blocked): self.p.check_write(Path("/etc/x.json"))
    def test_14_overwrite_needs_approval(self):
        f = self.base / "reports/job-watch/run-1.json"; f.write_text("{}")
        with self.assertRaises(NeedsApproval): self.p.check_write(f)
    def test_15_overwrite_with_approval_allowed(self):
        f = self.base / "reports/job-watch/run-1.json"; f.write_text("{}")
        self.p.check_write(f, approved=True)
    def test_16_read_report_allowed(self):
        f = self.base / "reports/job-watch/run-1.json"; f.write_text("{}")
        self.p.check_read(f)
    def test_17_delete_blocked(self):
        f = self.base / "reports/job-watch/run-1.json"; f.write_text("{}")
        with self.assertRaises(Blocked): self.p.check_delete(f)
        self.assertTrue(f.exists())
    def test_approval_does_not_open_outside_folder(self):
        # approval is only for overwrites INSIDE the folder; it never unlocks an escape
        with self.assertRaises(Blocked): self.p.check_write(self.base / "reports/job-watch/../../agent.py", approved=True)

if __name__ == "__main__": unittest.main()
