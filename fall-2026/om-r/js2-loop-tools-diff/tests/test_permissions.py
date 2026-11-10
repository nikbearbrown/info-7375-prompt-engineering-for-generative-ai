"""Boundary tests for agent/permissions.py (GATE.md "Permission policy").

One test method per boundary. Offline: URL checks are pure, the redirect
check calls the redirect handler directly, and every write goes into a fresh
temporary project root.
"""
import os
import shutil
import tempfile
import unittest
import urllib.request
from pathlib import Path

from agent import fetch
from agent.permissions import (HostNotAllowed, NewBoardNotApproved, PermissionDenied,
                               WriteOutsideAllowedDirs, WritePolicy, check_url)

GREENHOUSE = "https://boards-api.greenhouse.io/v1/boards/gitlab/jobs?content=true"
LEVER = "https://api.lever.co/v0/postings/palantir?mode=json&limit=100&skip=0"


class HostAllowList(unittest.TestCase):
    def test_valid_greenhouse_url_is_allowed(self):
        self.assertEqual(check_url(GREENHOUSE), GREENHOUSE)

    def test_valid_lever_url_is_allowed(self):
        self.assertEqual(check_url(LEVER), LEVER)

    def test_explicit_port_443_is_allowed(self):
        check_url("https://api.lever.co:443/v0/postings/palantir")

    def test_plain_http_to_allowed_host_is_refused(self):
        with self.assertRaises(HostNotAllowed):
            check_url("http://api.lever.co/v0/postings/palantir")

    def test_non_allow_listed_host_is_refused(self):
        with self.assertRaises(HostNotAllowed):
            check_url("https://example.com/jobs")

    def test_userinfo_trick_greenhouse_at_evil_is_refused(self):
        with self.assertRaises(HostNotAllowed):
            check_url("https://boards-api.greenhouse.io@evil.com/v1/boards/gitlab/jobs")

    def test_non_443_port_is_refused(self):
        with self.assertRaises(HostNotAllowed):
            check_url("https://api.lever.co:8443/v0/postings/palantir")

    def test_look_alike_subdomain_is_refused(self):
        with self.assertRaises(HostNotAllowed):
            check_url("https://evil.api.lever.co/v0/postings/palantir")

    def test_allowed_host_as_prefix_of_other_domain_is_refused(self):
        with self.assertRaises(HostNotAllowed):
            check_url("https://api.lever.co.evil.com/v0/postings/palantir")

    def test_api_anthropic_com_is_refused_until_judgment_code_exists(self):
        with self.assertRaises(HostNotAllowed):
            check_url("https://api.anthropic.com/v1/messages")

    def test_fetch_refuses_disallowed_host_before_any_network_call(self):
        with self.assertRaises(HostNotAllowed):
            fetch.fetch("https://example.com/jobs")


class Redirects(unittest.TestCase):
    def setUp(self):
        self.handler = fetch._AllowListRedirects()
        self.req = urllib.request.Request(GREENHOUSE)

    def _redirect(self, newurl):
        return self.handler.redirect_request(self.req, None, 302, "Found", {}, newurl)

    def test_redirect_to_non_allow_listed_host_is_refused(self):
        with self.assertRaises(HostNotAllowed):
            self._redirect("https://evil.com/v1/boards/gitlab/jobs")

    def test_redirect_downgrade_to_http_is_refused(self):
        with self.assertRaises(HostNotAllowed):
            self._redirect("http://boards-api.greenhouse.io/v1/boards/gitlab/jobs")

    def test_redirect_within_allow_list_is_followed(self):
        new = self._redirect("https://boards-api.greenhouse.io/v1/boards/gitlab/jobs?page=2")
        self.assertEqual(new.full_url, "https://boards-api.greenhouse.io/v1/boards/gitlab/jobs?page=2")


class WriteContainment(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="js2_perm_root_"))
        self.outside = Path(tempfile.mkdtemp(prefix="js2_perm_outside_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.addCleanup(shutil.rmtree, self.outside, ignore_errors=True)
        for d in ("evidence", "state", "logs"):
            (self.root / d).mkdir()
        self.policy = WritePolicy(self.root, approved_new_boards={"gitlab"})

    def assertNothingOutside(self):
        self.assertEqual(os.listdir(self.outside), [])

    def test_write_inside_evidence_is_allowed(self):
        real = self.policy.write_bytes(self.root / "evidence" / "gitlab_x.json", b"{}")
        self.assertEqual(real.read_bytes(), b"{}")

    def test_write_inside_logs_is_allowed(self):
        self.policy.write_bytes(self.root / "logs" / "run_x.json", b"{}")

    def test_approved_new_board_state_write_is_allowed(self):
        real = self.policy.write_bytes(self.root / "state" / "gitlab_seen.json", b"{}")
        self.assertEqual(real.name, "gitlab_seen.json")

    def test_dot_dot_traversal_out_of_logs_is_refused(self):
        with self.assertRaises(WriteOutsideAllowedDirs):
            self.policy.write_bytes(self.root / "logs" / ".." / "README.md", b"x")
        self.assertFalse((self.root / "README.md").exists())

    def test_sibling_prefix_state_evil_is_refused(self):
        (self.root / "state_evil").mkdir()
        with self.assertRaises(WriteOutsideAllowedDirs):
            self.policy.write_bytes(self.root / "state_evil" / "gitlab_seen.json", b"{}")

    def test_sibling_prefix_evidence_evil_and_logs2_are_refused(self):
        # Unlike state_evil/, no state-file rule applies here: only the
        # path-component containment check stands between these and a write.
        for sibling in ("evidence_evil", "logs2"):
            with self.subTest(sibling=sibling):
                (self.root / sibling).mkdir()
                with self.assertRaises(WriteOutsideAllowedDirs):
                    self.policy.write_bytes(self.root / sibling / "x.json", b"{}")
                self.assertEqual(os.listdir(self.root / sibling), [])

    def test_symlink_inside_logs_pointing_outside_is_refused(self):
        os.symlink(self.outside, self.root / "logs" / "escape")
        with self.assertRaises(WriteOutsideAllowedDirs):
            self.policy.write_bytes(self.root / "logs" / "escape" / "pwn.txt", b"x")
        self.assertNothingOutside()

    def test_state_dir_replaced_by_symlink_outside_root_is_refused(self):
        (self.root / "state").rmdir()
        os.symlink(self.outside, self.root / "state")
        with self.assertRaises(WriteOutsideAllowedDirs):
            self.policy.write_bytes(self.root / "state" / "gitlab_seen.json", b"{}")
        self.assertNothingOutside()

    def test_non_state_file_in_state_dir_is_refused(self):
        with self.assertRaises(WriteOutsideAllowedDirs):
            self.policy.write_bytes(self.root / "state" / "notes.txt", b"x")

    def test_state_file_in_state_subdirectory_is_refused(self):
        with self.assertRaises(WriteOutsideAllowedDirs):
            self.policy.write_bytes(self.root / "state" / "sub" / "gitlab_seen.json", b"{}")

    def test_writing_the_allowed_dir_itself_is_refused(self):
        with self.assertRaises(WriteOutsideAllowedDirs):
            self.policy.write_bytes(self.root / "evidence", b"x")

    def test_absolute_path_outside_root_is_refused(self):
        with self.assertRaises(WriteOutsideAllowedDirs):
            self.policy.write_bytes(self.outside / "x.json", b"x")
        self.assertNothingOutside()

    def test_write_to_project_root_is_refused(self):
        with self.assertRaises(WriteOutsideAllowedDirs):
            self.policy.write_bytes(self.root / "GATE.md", b"x")

    def test_missing_allowed_dirs_are_created_on_first_write(self):
        fresh = Path(tempfile.mkdtemp(prefix="js2_perm_fresh_"))
        self.addCleanup(shutil.rmtree, fresh, ignore_errors=True)
        WritePolicy(fresh).write_bytes(fresh / "logs" / "run_x.json", b"{}")
        self.assertTrue((fresh / "logs" / "run_x.json").is_file())


class NewBoardApproval(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="js2_perm_root_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def test_unapproved_new_board_state_creation_is_refused(self):
        policy = WritePolicy(self.root, approved_new_boards={"gitlab"})
        with self.assertRaises(NewBoardNotApproved):
            policy.write_bytes(self.root / "state" / "stripe_seen.json", b"{}")
        self.assertFalse((self.root / "state" / "stripe_seen.json").exists())

    def test_existing_board_state_update_needs_no_approval(self):
        WritePolicy(self.root, approved_new_boards={"stripe"}).write_bytes(
            self.root / "state" / "stripe_seen.json", b"{}")
        WritePolicy(self.root).write_bytes(self.root / "state" / "stripe_seen.json", b'{"v": 2}')
        self.assertEqual((self.root / "state" / "stripe_seen.json").read_bytes(), b'{"v": 2}')

    def test_all_refusals_are_permission_errors(self):
        for exc in (HostNotAllowed, WriteOutsideAllowedDirs, NewBoardNotApproved):
            self.assertTrue(issubclass(exc, PermissionDenied))
            self.assertTrue(issubclass(exc, PermissionError))


if __name__ == "__main__":
    unittest.main()
