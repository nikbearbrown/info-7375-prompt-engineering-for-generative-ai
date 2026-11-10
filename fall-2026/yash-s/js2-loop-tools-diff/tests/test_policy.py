"""The 15 boundary cases in BOUNDARY-TESTS.md, one test each, named by row number; plus extras.

run from the js2-loop-tools-diff folder:
  python3 -m unittest discover -s tests -v

Offline: URLs are only checked, never fetched. Files live in a temporary folder.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import agent  # noqa: E402
import policy  # noqa: E402

GH = "https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/openai?includeCompensation=true"


class Network(unittest.TestCase):
    """Rows 1-5 and 14: hosts, scheme and redirects."""

    def refused(self, method, url):
        with self.assertRaises(policy.PolicyViolation):
            policy.check_request(method, url)

    def test_01_https_greenhouse_allowed(self):
        self.assertEqual(policy.check_request("GET", GH), GH)

    def test_02_https_ashby_allowed(self):
        self.assertEqual(policy.check_request("GET", ASHBY), ASHBY)

    def test_03_host_off_the_allow_list_refused(self):
        self.refused("GET", "https://example.com/jobs")

    def test_04_look_alike_host_refused(self):
        self.refused("GET", "https://boards-api.greenhouse.io.evil.com/v1/boards/databricks/jobs")

    def test_05_plain_http_refused(self):
        self.refused("GET", "http://boards-api.greenhouse.io/v1/boards/databricks/jobs")

    def test_14_redirect_refused(self):
        with self.assertRaises(policy.PolicyViolation):
            policy.RefuseRedirects().redirect_request(None, None, 302, "Found", {}, "https://evil.example.com/")

    def test_14_http_get_installs_the_redirect_refusal(self):
        seen = {}

        def fake_build_opener(*handlers):
            seen["handlers"] = handlers
            raise RuntimeError("stop before any network")
        with mock.patch.object(agent.urllib.request, "build_opener", fake_build_opener):
            with self.assertRaises(RuntimeError):
                agent.http_get(GH, 5)
        self.assertIn(policy.RefuseRedirects, seen["handlers"])

    def test_off_list_url_refused_before_any_network(self):
        with mock.patch.object(agent.urllib.request, "build_opener", side_effect=AssertionError("network")):
            with self.assertRaises(policy.PolicyViolation):
                agent.http_get("https://example.com/", 5)

    def test_extra_user_part_trick_refused(self):
        self.refused("GET", "https://boards-api.greenhouse.io@evil.com/v1/boards/x/jobs")

    def test_extra_other_port_refused(self):
        self.refused("GET", "https://boards-api.greenhouse.io:8443/v1/boards/x/jobs")

    def test_extra_post_refused(self):
        self.refused("POST", GH)


class Files(unittest.TestCase):
    """Rows 6-13 and 15: reads, writes, escapes and approval."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.root = root
        for d in ("runs", "state", "persona", "runs-evil", "outside"):
            (root / d).mkdir()
        self.resume = root / "persona" / "resume.json"
        self.resume.write_text('{"fictional": true}')
        self.state_file = root / "state" / "greenhouse-anthropic.state.json"
        self.state_file.write_text('{"board": "anthropic", "seen_ids": [1, 2]}')
        self.pol = policy.Policy(root / "runs", root / "state", [root / "persona"])

    def refused(self, fn, *args, **kwargs):
        with self.assertRaises(policy.PolicyViolation):
            fn(*args, **kwargs)

    def test_06_write_inside_runs_allowed(self):
        target = self.pol.write_evidence(self.root / "runs" / "evidence.json", b"{}")
        self.assertEqual(target.read_bytes(), b"{}")

    def test_07_dot_dot_escape_refused(self):
        self.refused(self.pol.write_evidence, self.root / "runs" / ".." / "outside.json", b"x")
        self.assertFalse((self.root / "outside.json").exists())

    def test_08_look_alike_folder_prefix_refused(self):
        self.refused(self.pol.write_evidence, self.root / "runs-evil" / "output.json", b"x")
        self.assertFalse((self.root / "runs-evil" / "output.json").exists())

    def test_09_symlink_pointing_outside_refused(self):
        os.symlink(self.root / "outside", self.root / "runs" / "link")
        self.refused(self.pol.write_evidence, self.root / "runs" / "link" / "x.json", b"x")
        os.symlink(self.root / "outside" / "f.json", self.root / "runs" / "f.json")
        self.refused(self.pol.write_evidence, self.root / "runs" / "f.json", b"x")
        self.assertEqual(list((self.root / "outside").iterdir()), [])

    def test_10_read_the_persona_allowed(self):
        self.assertEqual(self.pol.read_bytes(self.resume), b'{"fictional": true}')

    def test_11_write_the_persona_refused(self):
        self.refused(self.pol.write_evidence, self.resume, b"changed")
        self.refused(self.pol.update_state, self.resume, {"changed": True})
        self.assertEqual(self.resume.read_bytes(), b'{"fictional": true}')

    def test_12_reset_state_without_approval_refused(self):
        self.refused(self.pol.reset_state, self.state_file)
        self.assertTrue(self.state_file.exists())

    def test_13_reset_state_with_approval_allowed(self):
        self.pol.reset_state(self.state_file, approved=True)
        self.assertFalse(self.state_file.exists())

    def test_15_absolute_path_outside_refused(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            target = Path(elsewhere).resolve() / "abs.json"
            self.refused(self.pol.write_evidence, target, b"x")
            self.assertFalse(target.exists())

    def test_extra_approval_never_allows_a_path_outside_the_state_folder(self):
        outside = self.root / "outside" / "x.state.json"
        outside.write_text("{}")
        self.refused(self.pol.reset_state, outside, approved=True)
        self.assertTrue(outside.exists())

    def test_extra_approval_must_be_exactly_true(self):
        self.refused(self.pol.reset_state, self.state_file, approved="yes")
        self.assertTrue(self.state_file.exists())

    def test_extra_evidence_is_create_only(self):
        p = self.root / "runs" / "raw.json"
        self.pol.write_evidence(p, b"first")
        with self.assertRaises(FileExistsError):
            self.pol.write_evidence(p, b"second")
        self.assertEqual(p.read_bytes(), b"first")

    def test_extra_read_outside_allowed_folders_refused(self):
        (self.root / "outside" / "secret.txt").write_text("x")
        self.refused(self.pol.read_bytes, self.root / "outside" / "secret.txt")

    def test_extra_state_only_inside_the_state_folder(self):
        self.refused(self.pol.update_state, self.root / "runs" / "x.state.json", {})

    def test_extra_run_folders_are_never_reused(self):
        a = self.pol.make_run_dir("run-x")
        b = self.pol.make_run_dir("run-x")
        self.assertNotEqual(a, b)
        self.assertTrue(b.name.endswith("-2"))


if __name__ == "__main__":
    unittest.main()
