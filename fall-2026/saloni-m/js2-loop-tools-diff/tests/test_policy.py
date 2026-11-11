"""Permission boundary tests (GATE.md section 5). Case ids match BOUNDARY-TESTS.md.

Each case names the expected outcome from GATE.md. Saloni's own predictions were recorded in
BOUNDARY-TESTS.md and committed before these tests were first run.
"""
import os
import tempfile
import unittest
import urllib.request

from jsagent.fetch import _PolicyRedirect
from jsagent.policy import ALLOW, DENY, NEEDS_APPROVAL, Policy, PolicyError

HOSTS = ["boards-api.greenhouse.io", "api.ashbyhq.com"]
GH = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs"


class Boundary(unittest.TestCase):
    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="js2policy-"))
        self.out = os.path.join(self.root, "out")
        os.makedirs(os.path.join(self.out, "state"))
        self.state = os.path.join(self.out, "state", "seen_ids.json")
        self.outside = os.path.realpath(tempfile.mkdtemp(prefix="js2outside-"))
        self.p = Policy(self.root, self.out, HOSTS, approval_files=[self.state])

    def req(self, url, method="GET"):
        return self.p.check_request(method, url).outcome

    # --- network --------------------------------------------------------------------------
    def test_B01_allowed_greenhouse_get(self):
        self.assertEqual(self.req(GH), ALLOW)

    def test_B02_allowed_ashby_get(self):
        self.assertEqual(self.req("https://api.ashbyhq.com/posting-api/job-board/openai"), ALLOW)

    def test_B03_host_off_the_allow_list(self):
        self.assertEqual(self.req("https://api.lever.co/v0/postings/netflix"), DENY)

    def test_B04_lookalike_host_suffix_trick(self):
        self.assertEqual(self.req("https://boards-api.greenhouse.io.evil.example/v1/boards/x/jobs"), DENY)

    def test_B05_lookalike_host_prefix_trick(self):
        self.assertEqual(self.req("https://evilboards-api.greenhouse.io/v1/boards/x/jobs"), DENY)

    def test_B06_plain_http(self):
        self.assertEqual(self.req("http://boards-api.greenhouse.io/v1/boards/anthropic/jobs"), DENY)

    def test_B07_post_to_allowed_host_is_an_application(self):
        self.assertEqual(self.req("https://boards-api.greenhouse.io/v1/boards/anthropic/jobs/1", "POST"), DENY)

    def test_B08_credentials_in_url_is_a_login(self):
        self.assertEqual(self.req("https://me:pw@boards-api.greenhouse.io/v1/boards/anthropic/jobs"), DENY)

    def test_B09_allowed_host_hidden_in_query_string(self):
        self.assertEqual(self.req("https://evil.example/?next=https://boards-api.greenhouse.io/"), DENY)

    def test_B10_redirect_to_off_list_host_is_refused(self):
        h = _PolicyRedirect(self.p)
        req = urllib.request.Request(GH)
        with self.assertRaises(PolicyError):
            h.redirect_request(req, None, 302, "Found", {}, "https://evil.example/jobs")

    # --- files: write ---------------------------------------------------------------------
    def w(self, path, approved=False):
        return self.p.check_write(path, approved).outcome

    def test_B11_write_inside_out(self):
        self.assertEqual(self.w(os.path.join(self.out, "runs", "r1", "trace.jsonl")), ALLOW)

    def test_B12_dotdot_escape(self):
        self.assertEqual(self.w(os.path.join(self.out, "..", "GATE.md")), DENY)

    def test_B13_sibling_prefix_trick_out_evil(self):
        os.makedirs(os.path.join(self.root, "out-evil"))
        self.assertEqual(self.w(os.path.join(self.root, "out-evil", "x.json")), DENY)

    def test_B14_symlink_inside_out_pointing_outside(self):
        link = os.path.join(self.out, "link")
        os.symlink(self.outside, link)
        self.assertEqual(self.w(os.path.join(link, "x.json")), DENY)
        with self.assertRaises(PolicyError):
            self.p.write_bytes(os.path.join(link, "x.json"), b"x")
        self.assertEqual(os.listdir(self.outside), [])

    def test_B15_absolute_path_outside(self):
        self.assertEqual(self.w("/etc/js2-should-never-exist"), DENY)

    # --- files: read vs write -------------------------------------------------------------
    def test_B16_read_of_project_file_allowed_but_write_denied(self):
        gate = os.path.join(self.root, "GATE.md")
        self.assertEqual(self.p.check_read(gate).outcome, ALLOW)
        self.assertEqual(self.w(gate), DENY)

    def test_B17_read_outside_project_denied(self):
        self.assertEqual(self.p.check_read(os.path.expanduser("~/.ssh/id_rsa")).outcome, DENY)

    # --- files: approval ------------------------------------------------------------------
    def test_B18_first_write_of_history_allowed(self):
        self.assertEqual(self.w(self.state), ALLOW)

    def test_B19_overwrite_history_without_approval(self):
        with open(self.state, "w") as f:
            f.write("{}")
        self.assertEqual(self.w(self.state), NEEDS_APPROVAL)
        with self.assertRaises(PolicyError):
            self.p.write_bytes(self.state, b"overwritten")
        with open(self.state) as f:
            self.assertEqual(f.read(), "{}")

    def test_B20_overwrite_history_with_approval(self):
        with open(self.state, "w") as f:
            f.write("{}")
        self.assertEqual(self.w(self.state, approved=True), ALLOW)

    def test_B21_symlink_to_history_file_still_needs_approval(self):
        with open(self.state, "w") as f:
            f.write("{}")
        alias = os.path.join(self.out, "alias.json")
        os.symlink(self.state, alias)
        self.assertEqual(self.w(alias), NEEDS_APPROVAL)


if __name__ == "__main__":
    unittest.main()
