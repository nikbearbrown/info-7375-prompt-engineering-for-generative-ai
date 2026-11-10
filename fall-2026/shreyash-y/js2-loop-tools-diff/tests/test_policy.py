"""BOUNDARY-TESTS.md rows 1-20, one test each. Predictions were committed before policy.py existed."""
import os
import pathlib
import tempfile
import unittest

from jsagent import policy


class Requests(unittest.TestCase):
    def refused(self, method, url, kind):
        with self.assertRaises(policy.PolicyViolation) as cm:
            policy.check_request(method, url)
        self.assertEqual(cm.exception.kind, kind, url)

    def test_01_host_off_list(self):
        self.refused("GET", "https://evil.example.com/v1/boards/oscar/jobs", "host")

    def test_02_lookalike_host(self):
        self.refused("GET", "https://boards-api.greenhouse.io.evil.com/v1/boards/oscar/jobs", "host")

    def test_03_plain_http(self):
        self.refused("GET", "http://api.lever.co/v0/postings/palantir", "scheme")

    def test_04_userinfo_trick(self):
        self.refused("GET", "https://api.lever.co@evil.example.com/v0/postings/x", "host")

    def test_05_allowed_host_wrong_path(self):
        self.refused("GET", "https://boards-api.greenhouse.io/v1/boards/oscar/jobs/123/applications", "path")

    def test_06_write_method(self):
        self.refused("POST", "https://api.ashbyhq.com/posting-api/job-board/linear", "method")

    def test_07_redirect_off_list(self):
        with self.assertRaises(policy.PolicyViolation) as cm:
            policy.check_redirect("https://api.ashbyhq.com/posting-api/job-board/linear", "https://evil.example.com/")
        self.assertEqual(cm.exception.kind, "host")

    def test_08_allowed(self):
        policy.check_request("GET", "https://api.ashbyhq.com/posting-api/job-board/linear")
        policy.check_request("GET", "https://boards-api.greenhouse.io/v1/boards/oscar/jobs?content=true")
        policy.check_request("GET", "https://api.lever.co/v0/postings/palantir?mode=json")


class Files(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = pathlib.Path(self.tmp.name).resolve()
        self.project = base / "proj"
        self.runs = self.project / "runs"
        (self.runs / "state").mkdir(parents=True)
        (self.runs / "old" / "raw").mkdir(parents=True)
        (self.project / "GATE.md").write_text("gate")
        (self.runs / "state" / "state-old.json").write_text("{}")
        (self.runs / "old" / "raw" / "x.json").write_text("{}")
        self.outside = base / "outside"
        self.outside.mkdir()
        os.symlink(self.outside, self.runs / "link")
        self.files = policy.Files(self.project, self.runs)

    def tearDown(self):
        self.tmp.cleanup()

    def refused(self, fn, kind):
        with self.assertRaises(policy.PolicyViolation) as cm:
            fn()
        self.assertEqual(cm.exception.kind, kind)

    def test_09_dotdot_escape(self):
        self.refused(lambda: self.files.write(self.runs / ".." / "GATE.md", b"x"), "outside-runs")
        self.assertEqual((self.project / "GATE.md").read_text(), "gate")

    def test_10_prefix_trick(self):
        self.refused(lambda: self.files.write(self.project / "runs-evil" / "x.json", b"x"), "outside-runs")
        self.assertFalse((self.project / "runs-evil").exists())

    def test_11_symlink_out(self):
        self.refused(lambda: self.files.write(self.runs / "link" / "x.json", b"x"), "outside-runs")
        self.assertEqual(list(self.outside.iterdir()), [])

    def test_12_absolute_path(self):
        self.refused(lambda: self.files.write(pathlib.Path(self.tmp.name) / "x.json", b"x"), "outside-runs")

    def test_13_budgets_file(self):
        self.refused(lambda: self.files.write(self.project / "budgets.json", b"{}"), "outside-runs")

    def test_14_new_evidence_allowed(self):
        p = self.runs / "r1" / "raw" / "x.json"
        self.files.write(p, b"{}")
        self.assertEqual(p.read_bytes(), b"{}")

    def test_15_overwrite_state_needs_approval(self):
        with self.assertRaises(policy.NeedsApproval):
            self.files.write(self.runs / "state" / "state-old.json", b'{"new": 1}')
        self.assertEqual((self.runs / "state" / "state-old.json").read_text(), "{}")

    def test_16_overwrite_with_approval(self):
        policy.Files(self.project, self.runs, approve=True).write(self.runs / "state" / "state-old.json", b'{"new": 1}')
        self.assertEqual((self.runs / "state" / "state-old.json").read_text(), '{"new": 1}')

    def test_17_delete_evidence_needs_approval(self):
        with self.assertRaises(policy.NeedsApproval):
            self.files.delete(self.runs / "old" / "raw" / "x.json")
        self.assertTrue((self.runs / "old" / "raw" / "x.json").exists())

    def test_18_append_own_trace(self):
        p = self.runs / "r1" / "trace.jsonl"
        self.files.write(p, b"a\n")
        self.files.append(p, b"b\n")
        self.assertEqual(p.read_bytes(), b"a\nb\n")
        with self.assertRaises(policy.NeedsApproval):
            policy.Files(self.project, self.runs).append(p, b"c\n")  # a later run did not create it

    def test_19_read_inside(self):
        self.assertEqual(self.files.read(self.project / "GATE.md"), b"gate")

    def test_20_read_outside(self):
        self.refused(lambda: self.files.read(pathlib.Path.home() / ".ssh" / "config"), "read-outside")


if __name__ == "__main__":
    unittest.main()
