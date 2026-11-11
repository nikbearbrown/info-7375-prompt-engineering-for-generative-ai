"""Boundary cases from GATE.md ("Boundary cases — predicted before running"), one test per row.
Written from the gate before jobwatch2/policy.py existed. Each test's docstring is the gate's prediction.
"""
import os
import pathlib
import tempfile
import unittest

from jobwatch2.policy import Policy

GH = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
LEVER_ID = "6ed76ce8-4156-4b60-b120-403538bd66cd"


class Boundary(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.outside = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name) / "js2"
        (self.root / "runs" / "state").mkdir(parents=True)
        (self.root / "personas").mkdir()
        (self.root / "personas" / "maya-sehgal.resume.json").write_text("{}")
        (self.root.parent / "runs-evil").mkdir()
        os.symlink(self.outside.name, self.root / "runs" / "link")
        self.p = Policy(self.root)

    def tearDown(self):
        self.tmp.cleanup()
        self.outside.cleanup()

    def assertAllowed(self, d):
        self.assertTrue(d.allowed, d.reason)

    def assertDenied(self, d, why):
        self.assertFalse(d.allowed)
        self.assertIn(why, d.reason)

    def test_01_allowed_board_get(self):
        """allow"""
        self.assertAllowed(self.p.request("GET", GH))

    def test_02_host_off_allow_list(self):
        """deny: host not allowed"""
        self.assertDenied(self.p.request("GET", "https://example.com/jobs"), "host")

    def test_03_http_scheme(self):
        """deny: scheme not https"""
        self.assertDenied(self.p.request("GET", GH.replace("https:", "http:")), "scheme")

    def test_04_host_suffix_trick(self):
        """deny: host not allowed (suffix trick)"""
        self.assertDenied(self.p.request("GET", "https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs"),
                          "host")

    def test_05_post_apply(self):
        """deny: method not GET (never apply)"""
        self.assertDenied(self.p.request("POST", f"https://api.lever.co/v0/postings/palantir/{LEVER_ID}/apply"),
                          "method")

    def test_06_get_apply_path(self):
        """deny: path not a board listing"""
        self.assertDenied(self.p.request("GET", f"https://api.lever.co/v0/postings/palantir/{LEVER_ID}/apply"),
                          "path")

    def test_07_credential_headers(self):
        """deny: credential header (never log in)"""
        for h in ({"Authorization": "Bearer x"}, {"Cookie": "s=1"}, {"authorization": "x"}):
            with self.subTest(h=h):
                self.assertDenied(self.p.request("GET", GH, headers=h), "credential")

    def test_08_write_state_inside_runs(self):
        """allow"""
        self.assertAllowed(self.p.write("runs/state/greenhouse__stripe.json"))

    def test_09_write_dotdot_escape(self):
        """deny: escapes runs/"""
        self.assertDenied(self.p.write("runs/../GATE.md"), "outside runs")

    def test_10_write_prefix_trick(self):
        """deny: outside runs/ (runs-evil beside runs)"""
        self.assertDenied(self.p.write("../runs-evil/x.json"), "outside runs")
        self.assertDenied(self.p.write(str(self.root.parent / "runs-evil" / "x.json")), "outside runs")

    def test_11_write_through_symlink(self):
        """deny: resolved path outside runs/"""
        self.assertDenied(self.p.write("runs/link/x.json"), "outside runs")

    def test_12_write_absolute_elsewhere(self):
        """deny: outside runs/"""
        self.assertDenied(self.p.write("/tmp/x.json"), "outside runs")

    def test_13_read_persona(self):
        """allow (read)"""
        self.assertAllowed(self.p.read("personas/maya-sehgal.resume.json"))

    def test_14_write_persona(self):
        """deny: read allowed, write not"""
        self.assertDenied(self.p.write("personas/maya-sehgal.resume.json"), "outside runs")

    def test_15_read_outside_folder(self):
        """deny: outside the assignment folder"""
        self.assertDenied(self.p.read(os.path.expanduser("~/.ssh/id_rsa")), "outside")
        self.assertDenied(self.p.read("../../../../etc/passwd"), "outside")

    def test_16_reset_without_approval(self):
        """deny: needs-approval"""
        self.assertDenied(self.p.reset("greenhouse/stripe"), "needs-approval")

    def test_17_reset_with_approval(self):
        """allow"""
        self.assertAllowed(Policy(self.root, approvals=["greenhouse/stripe"]).reset("greenhouse/stripe"))

    def test_18_reset_other_board(self):
        """deny: approval is for a different board"""
        self.assertDenied(Policy(self.root, approvals=["greenhouse/stripe"]).reset("ashby/openai"), "needs-approval")

    def test_19_repeat_blocked(self):
        """second one: deny, repeat-blocked"""
        self.assertAllowed(self.p.request("GET", GH))
        self.p.record_request("GET", GH)
        self.assertDenied(self.p.request("GET", GH), "repeat-blocked")


class OtherPolicyEdges(unittest.TestCase):
    """Extra cases not in the gate table; predictions written alongside."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "runs").mkdir()
        self.p = Policy(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_each_ats_listing_allowed_and_nothing_else(self):
        ok = ["https://api.ashbyhq.com/posting-api/job-board/openai",
              "https://api.lever.co/v0/postings/palantir?mode=json",
              "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"]
        bad = ["https://api.lever.co/v0/postings/palantir",           # no mode=json
               "https://api.ashbyhq.com/posting-api/job-board/Open_AI",  # bad slug
               "https://boards-api.greenhouse.io/v1/boards/stripe/jobs/123",  # single job, not listing
               "https://boards-api.greenhouse.io:8443/v1/boards/stripe/jobs"]  # port
        for u in ok:
            with self.subTest(u=u):
                self.assertTrue(self.p.request("GET", u).allowed, u)
        for u in bad:
            with self.subTest(u=u):
                self.assertFalse(self.p.request("GET", u).allowed, u)

    def test_sanctioned_retry_is_the_only_repeat(self):
        u = "https://api.ashbyhq.com/posting-api/job-board/openai"
        self.p.record_request("GET", u)
        self.assertTrue(self.p.request("GET", u, retry=True).allowed)
        self.p.record_request("GET", u)
        self.assertFalse(self.p.request("GET", u, retry=True).allowed)  # no second retry

    def test_write_runs_dir_itself_and_sibling_name_runs2(self):
        self.assertTrue(self.p.write("runs/x.json").allowed)
        self.assertFalse(self.p.write("runs2/x.json").allowed)


if __name__ == "__main__":
    unittest.main()
