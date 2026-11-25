"""Boundary tests B01-B19 from BOUNDARY_TESTS.md, plus extra cases.

One test per boundary case, named test_B<nn>_... in the same order. No test
opens a network connection: check_request only inspects the request.
"""

import os
import tempfile
import unittest
from pathlib import Path

from agent import policy
from agent.policy import PolicyRefusal

GH = "https://boards-api.greenhouse.io/v1/boards/scaleai/jobs"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/openai"
HEADERS = {"User-Agent": "js2-job-search-agent/2.0"}
RAW = "out/raw/RUN1_scaleai_a1.json"
STATE = "out/state/scaleai.json"


class PolicyCase(unittest.TestCase):
    """A temporary project root with out/, data/ and a symlink escape."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._outside = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "out" / "raw").mkdir(parents=True)
        (self.root / "out" / "state").mkdir()
        (self.root / "data").mkdir()
        (self.root / "data" / "resume.example.json").write_text("{}")
        os.symlink(self._outside.name, self.root / "out" / "link")

    def tearDown(self):
        self._tmp.cleanup()
        self._outside.cleanup()

    def assertRefused(self, code, func, *args, **kwargs):
        with self.assertRaises(PolicyRefusal) as ctx:
            func(*args, **kwargs)
        self.assertEqual(ctx.exception.code, code, str(ctx.exception))
        return ctx.exception


class BoundaryTests(PolicyCase):

    def test_B01_greenhouse_get_allowed(self):
        self.assertEqual(policy.check_request("GET", GH, HEADERS), GH)

    def test_B02_ashby_get_allowed(self):
        self.assertEqual(policy.check_request("GET", ASHBY, HEADERS), ASHBY)

    def test_B03_host_off_allowlist_refused(self):
        self.assertRefused("host_not_allowed", policy.check_request,
                           "GET", "https://example.com/jobs", HEADERS)

    def test_B04_lookalike_host_refused_exact_match(self):
        self.assertRefused(
            "host_not_allowed", policy.check_request, "GET",
            "https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs",
            HEADERS)

    def test_B05_http_refused(self):
        self.assertRefused(
            "not_https", policy.check_request, "GET",
            "http://boards-api.greenhouse.io/v1/boards/scaleai/jobs", HEADERS)

    def test_B06_post_refused(self):
        self.assertRefused("method_not_allowed", policy.check_request,
                           "POST", GH, HEADERS)

    def test_B07_authorization_header_refused(self):
        self.assertRefused("credentials_not_allowed", policy.check_request,
                           "GET", GH, dict(HEADERS, Authorization="Bearer x"))

    def test_B08_redirect_off_allowlist_refused(self):
        self.assertRefused("redirect_off_allowlist", policy.check_redirect,
                           GH, "https://example.com/")

    def test_B09_write_raw_inside_out_allowed(self):
        resolved = policy.check_write(RAW, root=self.root)
        self.assertEqual(resolved, (self.root / RAW).resolve())

    def test_B10_dotdot_out_of_out_refused(self):
        self.assertRefused("path_outside_write_area", policy.check_write,
                           "out/../data/resume.example.json", root=self.root)

    def test_B11_prefix_trick_out_evil_refused(self):
        self.assertRefused("path_outside_write_area", policy.check_write,
                           "out-evil/x.json", root=self.root)

    def test_B12_symlink_out_of_project_refused(self):
        self.assertRefused("path_outside_write_area", policy.check_write,
                           "out/link/x.json", root=self.root)

    def test_B13_read_data_allowed(self):
        resolved = policy.check_read("data/resume.example.json",
                                     root=self.root)
        self.assertEqual(resolved,
                         (self.root / "data/resume.example.json").resolve())

    def test_B14_write_data_refused(self):
        self.assertRefused("path_outside_write_area", policy.check_write,
                           "data/resume.example.json", root=self.root)

    def test_B15_read_etc_passwd_refused(self):
        self.assertRefused("path_outside_read_area", policy.check_read,
                           "/etc/passwd", root=self.root)

    def test_B16_existing_raw_never_overwritten(self):
        (self.root / RAW).write_bytes(b"evidence")
        self.assertRefused("would_overwrite", policy.check_write, RAW,
                           root=self.root)
        self.assertRefused("would_overwrite", policy.write_new, RAW, b"new",
                           root=self.root)
        self.assertEqual((self.root / RAW).read_bytes(), b"evidence")

    def test_B17_reset_with_yes_allowed(self):
        (self.root / STATE).write_text('{"seen_ids": []}')
        prompts = []
        policy.request_state_reset(
            STATE, approver=lambda p: prompts.append(p) or "yes",
            root=self.root)
        self.assertFalse((self.root / STATE).exists())
        self.assertEqual(len(prompts), 1)

    def test_B18_reset_with_no_refused(self):
        (self.root / STATE).write_text('{"seen_ids": []}')
        self.assertRefused("approval_denied", policy.request_state_reset,
                           STATE, approver=lambda p: "no", root=self.root)
        self.assertTrue((self.root / STATE).exists())

    def test_B19_reset_with_no_one_to_answer_refused(self):
        (self.root / STATE).write_text('{"seen_ids": []}')
        self.assertRefused("approval_denied", policy.request_state_reset,
                           STATE, root=self.root)

        def no_stdin(prompt):
            raise EOFError

        self.assertRefused("approval_denied", policy.request_state_reset,
                           STATE, approver=no_stdin, root=self.root)
        self.assertRefused("approval_denied", policy.request_state_reset,
                           STATE, approver=lambda p: None, root=self.root)
        self.assertTrue((self.root / STATE).exists())


class ExtraPolicyTests(PolicyCase):
    """Cases beyond B01-B19 that the wrong versions in GATE section 6 need."""

    def test_extra_host_suffix_trick_refused(self):
        # B04 catches a "contains" check but not an "ends with" check:
        # these hosts end with an allowed host and must still be refused.
        for url in ("https://evilboards-api.greenhouse.io/v1/boards/x/jobs",
                    "https://x.api.ashbyhq.com/posting-api/job-board/openai"):
            self.assertRefused("host_not_allowed", policy.check_request,
                               "GET", url, HEADERS)

    def test_extra_other_host_tricks_refused(self):
        for url in ("https://boards-api.greenhouse.io.:443/v1/x",
                    "https://boards-api.greenhouse.io:8443/v1/x",
                    "https://evil.com/boards-api.greenhouse.io"):
            self.assertRefused("host_not_allowed", policy.check_request,
                               "GET", url, HEADERS)

    def test_extra_uppercase_host_allowed(self):
        policy.check_request("GET", "https://BOARDS-API.greenhouse.io/v1/x",
                             HEADERS)

    def test_extra_credentials_in_url_and_cookie_refused(self):
        self.assertRefused("credentials_not_allowed", policy.check_request,
                           "GET", "https://u:p@boards-api.greenhouse.io/v1/x",
                           HEADERS)
        self.assertRefused("credentials_not_allowed", policy.check_request,
                           "GET", GH, {"cookie": "a=b"})

    def test_extra_lowercase_get_and_other_methods_refused(self):
        for method in ("get", "PUT", "DELETE", "HEAD"):
            self.assertRefused("method_not_allowed", policy.check_request,
                               method, GH, HEADERS)

    def test_extra_redirect_rules(self):
        self.assertEqual(policy.check_redirect(GH, "/v1/boards/other/jobs"),
                         "https://boards-api.greenhouse.io/v1/boards/other/"
                         "jobs")
        self.assertRefused("not_https", policy.check_redirect, GH,
                           "http://boards-api.greenhouse.io/v1/x")

    def test_extra_symlink_inside_raw_refused(self):
        os.symlink(self._outside.name, self.root / "out" / "raw" / "esc")
        self.assertRefused("path_outside_write_area", policy.check_write,
                           "out/raw/esc/x.json", root=self.root)

    def test_extra_symlinked_file_pointing_outside_refused(self):
        target = Path(self._outside.name) / "victim.json"
        os.symlink(target, self.root / "out" / "raw" / "dangling.json")
        self.assertRefused("path_outside_write_area", policy.check_write,
                           "out/raw/dangling.json", root=self.root)

    def test_extra_out_itself_and_outside_read_refused(self):
        self.assertRefused("path_outside_write_area", policy.check_write,
                           "out", root=self.root)
        self.assertRefused("path_outside_read_area", policy.check_read,
                           "out-evil/x.json", root=self.root)
        self.assertRefused("path_outside_read_area", policy.check_read,
                           "out/link/x.json", root=self.root)

    def test_extra_replace_only_for_state_files(self):
        (self.root / STATE).write_text("{}")
        policy.check_write(STATE, root=self.root, replace=True)
        (self.root / RAW).write_bytes(b"x")
        self.assertRefused("would_overwrite", policy.check_write, RAW,
                           root=self.root, replace=True)

    def test_extra_reset_outside_state_dir_refused(self):
        (self.root / RAW).write_bytes(b"x")
        self.assertRefused("path_outside_write_area",
                           policy.request_state_reset, RAW,
                           approver=lambda p: "yes", root=self.root)
        self.assertTrue((self.root / RAW).exists())

    def test_extra_only_exact_yes_approves(self):
        (self.root / STATE).write_text("{}")
        for answer in ("y", "sure", "YES please", 1, ""):
            self.assertRefused("approval_denied", policy.request_state_reset,
                               STATE, approver=lambda p, a=answer: a,
                               root=self.root)
        policy.request_state_reset(STATE, approver=lambda p: " Yes ",
                                   root=self.root)


if __name__ == "__main__":
    unittest.main()
