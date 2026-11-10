"""Boundary tests B1-B17. Each test's expected outcome was predicted in BOUNDARY.md (commit 2b6071e) before
jsagent/policy.py existed. Run: python3 -m unittest tests.test_policy -v   (offline; no network)
"""

import os
import tempfile
import unittest
from pathlib import Path

from jsagent.policy import Policy, PolicyError

ROOT = Path(__file__).resolve().parent.parent


class Boundary(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.runs = base / "runs"
        self.evil = base / "runs-evil"
        self.outside = base / "elsewhere"
        for d in (self.runs, self.evil, self.outside):
            d.mkdir()
        self.p = Policy(self.runs, read_roots=[ROOT])

    def tearDown(self):
        self.tmp.cleanup()

    def refused(self, fn, *args, why=None):
        with self.assertRaises(PolicyError) as cm:
            fn(*args)
        if why:
            self.assertIn(why, str(cm.exception))
        self.assertEqual(self.p.log[-1]["decision"], "refuse")

    # --- network ---
    def test_B01_allowlisted_get_is_allowed(self):
        self.p.check_request("GET", "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs")
        self.assertEqual(self.p.log[-1]["decision"], "allow")

    def test_B02_host_off_allowlist(self):
        self.refused(self.p.check_request, "GET", "https://evil.example.com/jobs", why="not on allow-list")

    def test_B03_lookalike_host(self):
        self.refused(self.p.check_request, "GET", "https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs",
                     why="not on allow-list")

    def test_B04_plain_http(self):
        self.refused(self.p.check_request, "GET", "http://boards-api.greenhouse.io/v1/boards/x/jobs", why="https only")

    def test_B05_post_is_never_sent(self):
        self.refused(self.p.check_request, "POST", "https://api.ashbyhq.com/posting-api/job-board/notion",
                     why="GET only")

    def test_B06_real_board_not_on_my_list(self):
        self.refused(self.p.check_request, "GET", "https://api.lever.co/v0/postings/x", why="not on allow-list")

    def test_B07_credentials_in_url(self):
        self.refused(self.p.check_request, "GET", "https://me:pw@boards-api.greenhouse.io/v1/boards/x/jobs",
                     why="never logs in")

    # --- writes ---
    def test_B08_write_inside_output_folder(self):
        self.p.write_text(self.runs / "raw" / "x.json", "{}")
        self.assertTrue((self.runs / "raw" / "x.json").exists())

    def test_B09_dotdot_escape(self):
        target = self.runs / ".." / "GATE.md"
        self.refused(self.p.write_text, target, "x", why="outside output folder")
        self.assertFalse(target.exists())

    def test_B10_prefix_trick_sibling_folder(self):
        target = self.evil / "x.json"
        self.assertTrue(str(target).startswith(str(self.runs)))  # the trick: a naive prefix check would pass
        self.refused(self.p.write_text, target, "x", why="outside output folder")
        self.assertFalse(target.exists())

    def test_B11_symlink_pointing_outside(self):
        os.symlink(self.outside, self.runs / "link")
        self.refused(self.p.write_text, self.runs / "link" / "x.json", "x", why="outside output folder")
        self.assertFalse((self.outside / "x.json").exists())

    def test_B12_absolute_path_outside(self):
        self.refused(self.p.write_text, self.outside / "x.json", "x", why="outside output folder")
        self.assertFalse((self.outside / "x.json").exists())

    # --- read vs write ---
    def test_B13_read_allowed_but_write_refused_same_path(self):
        persona = ROOT / "persona" / "arya-sahni.json"
        before = persona.read_bytes()
        self.assertEqual(self.p.read_bytes(persona), before)
        self.assertEqual(self.p.log[-1]["decision"], "allow")
        self.refused(self.p.write_text, persona, "{}", why="outside output folder")
        self.assertEqual(persona.read_bytes(), before)

    def test_B14_read_outside_agent_folder(self):
        self.refused(self.p.read_bytes, Path.home() / ".ssh" / "id_rsa", why="outside every read root")

    # --- the write that needs approval ---
    def test_B15_state_write_that_only_adds_ids(self):
        path = self.runs / "state" / "b.json"
        self.p.write_state(path, ["1", "2"], {"seen_ids": ["1", "2", "3"]})
        last = [e for e in self.p.log if e["kind"] == "state-write"][-1]
        self.assertEqual(last["decision"], "allow")
        self.assertIn("adds ids only", last["reason"])

    def test_B16_state_write_removing_ids_without_approval(self):
        path = self.runs / "state" / "b.json"
        self.p.write_state(path, [], {"seen_ids": ["1", "2"]})
        before = path.read_bytes()
        self.refused(self.p.write_state, path, ["1", "2"], {"seen_ids": []}, why="needs --approve")
        self.assertEqual(path.read_bytes(), before)  # file unchanged

    def test_B17_state_write_removing_ids_with_approval(self):
        path = self.runs / "state" / "b.json"
        p = Policy(self.runs, read_roots=[ROOT], approve=True)
        p.write_state(path, [], {"seen_ids": ["1", "2"]})
        p.write_state(path, ["1", "2"], {"seen_ids": []})
        last = [e for e in p.log if e["kind"] == "state-write"][-1]
        self.assertEqual(last["decision"], "allow")
        self.assertIn("APPROVED", last["reason"])


if __name__ == "__main__":
    unittest.main()
