"""Boundary tests for the permission policy. Each case's expected outcome is written in
POLICY_TESTS.md, committed before these tests were first run.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

from agent2 import policy
from agent2.fetch import AllowListRedirects
from agent2.policy import NeedsApproval, PolicyViolation


def make_link(link: Path, target: Path) -> None:
    """A directory link inside out/ that points outside it: a symlink on POSIX, a junction
    on Windows (a junction needs no admin rights; resolve() follows both)."""
    if sys.platform == "win32":
        import _winapi
        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


class Boundaries(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.root = base / "project"
        self.out = self.root / "out"
        self.out.mkdir(parents=True)
        (self.root / "out-evil").mkdir()
        (self.root / "GATE.md").write_text("x")
        self.outside = base / "elsewhere"
        self.outside.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    # --- requests ---
    def test_B01_host_off_allow_list(self):
        with self.assertRaises(PolicyViolation):
            policy.check_request("GET", "https://evil.example.com/jobs")

    def test_B02_lookalike_host_suffix(self):
        with self.assertRaises(PolicyViolation):
            policy.check_request("GET", "https://boards-api.greenhouse.io.evil.example/v1/boards/figma/jobs")

    def test_B03_http_not_https(self):
        with self.assertRaises(PolicyViolation):
            policy.check_request("GET", "http://api.lever.co/v0/postings/spotify")

    def test_B04_post_to_allowed_host(self):
        with self.assertRaises(PolicyViolation):
            policy.check_request("POST", "https://api.lever.co/v0/postings/spotify/apply")

    def test_B05_get_allowed_host(self):
        policy.check_request("GET", "https://api.ashbyhq.com/posting-api/job-board/snowflake")

    def test_B06_redirect_off_allow_list(self):
        with self.assertRaises(PolicyViolation):
            AllowListRedirects().redirect_request(None, None, 302, "Found", {}, "https://evil.example.com/")

    # --- writes ---
    def test_B07_write_inside_out(self):
        p = policy.check_write(self.out / "state" / "seen_ids.json", self.out)
        self.assertTrue(p.is_relative_to(self.out.resolve()))

    def test_B08_dotdot_escape(self):
        with self.assertRaises(PolicyViolation):
            policy.check_write(self.out / ".." / "GATE.md", self.out)

    def test_B09_prefix_trick_sibling_folder(self):
        with self.assertRaises(PolicyViolation):
            policy.check_write(self.root / "out-evil" / "x.json", self.out)

    def test_B10_link_inside_out_pointing_outside(self):
        link = self.out / "escape"
        make_link(link, self.outside)
        with self.assertRaises(PolicyViolation):
            policy.check_write(link / "x.json", self.out)

    def test_B11_absolute_path_outside(self):
        with self.assertRaises(PolicyViolation):
            policy.check_write(self.outside / "x.json", self.out)

    # --- read versus write on the same file ---
    def test_B12_read_allowed_write_refused_same_file(self):
        target = self.root / "GATE.md"
        policy.check_read(target, self.root)
        with self.assertRaises(PolicyViolation):
            policy.check_write(target, self.out)

    def test_B13_read_outside_project(self):
        with self.assertRaises(PolicyViolation):
            policy.check_read(self.outside / "anything.txt", self.root)

    # --- a write that needs my approval ---
    def test_B14_reset_state_without_approval(self):
        state = self.out / "state" / "seen_ids.json"
        state.parent.mkdir()
        state.write_text("{}")
        with self.assertRaises(NeedsApproval):
            policy.reset_state(state, approvals=frozenset(), out_dir=self.out)
        self.assertTrue(state.exists())

    def test_B15_reset_state_with_approval(self):
        state = self.out / "state" / "seen_ids.json"
        state.parent.mkdir()
        state.write_text("{}")
        policy.reset_state(state, approvals=frozenset({"reset-state"}), out_dir=self.out)
        self.assertFalse(state.exists())


if __name__ == "__main__":
    unittest.main()
