"""Boundary tests for the permission policy (GATE.md section 5).

The expected outcomes come from GATE.md, not from my predictions. BOUNDARY-PREDICTIONS.md (commit b5381cf)
holds what I predicted before these tests existed; cases 12 and 14 are where the two differ.
"""

import os
import tempfile
import unittest
from pathlib import Path

from jsagent2.policy import Policy

GH = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"

# (case #, kind, target, expected) — kind: GET/POST = network, read, write, write-approved
CASES = [
    (1, "GET", GH, "allow"),
    (2, "GET", "https://api.ashbyhq.com/posting-api/job-board/notion", "allow"),
    (3, "GET", "https://www.linkedin.com/jobs/", "refuse"),
    (4, "GET", "https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs", "refuse"),
    (5, "GET", "http://boards-api.greenhouse.io/v1/boards/stripe/jobs", "refuse"),
    (6, "POST", "https://boards-api.greenhouse.io/v1/boards/stripe/jobs/123", "refuse"),
    (7, "write", "out/reports/run.md", "allow"),
    (8, "write", "out/../GATE.md", "refuse"),
    (9, "write", "out-evil/run.md", "refuse"),
    (10, "write", "out/link/x.json", "refuse"),
    (11, "read", "config/boards.json", "allow"),
    (12, "write", "config/boards.json", "refuse"),
    (13, "read", "~/.ssh/id_rsa", "refuse"),
    (14, "write", "out/state/seen.json", "hold"),
    (15, "write-approved", "out/state/seen.json", "allow"),
    (16, "write", "/tmp/x.json", "refuse"),
]


def make_root():
    """A throwaway project folder with config/, out/, out-evil/ and out/link -> a folder outside the root."""
    tmp = Path(tempfile.mkdtemp())
    root = tmp / "proj"
    (root / "config").mkdir(parents=True)
    (root / "config" / "boards.json").write_text("{}")
    (root / "out" / "state").mkdir(parents=True)
    (root / "out" / "state" / "seen.json").write_text("{}")
    (root / "out-evil").mkdir()
    outside = tmp / "outside"
    outside.mkdir()
    os.symlink(outside, root / "out" / "link")
    return root


def decide(policy_cls, root, kind, target):
    if kind in ("GET", "POST"):
        return policy_cls(root).check_request(kind, target).verdict
    if kind == "read":
        return policy_cls(root).check_read(target).verdict
    if kind == "write":
        return policy_cls(root).check_write(target).verdict
    if kind == "write-approved":
        return policy_cls(root, approve_state_write=True).check_write(target).verdict
    raise ValueError(kind)


def failing_cases(policy_cls):
    """Run all 16 cases against a policy class; return the ones it gets wrong (used for wrong versions too)."""
    root = make_root()
    wrong = []
    for num, kind, target, expected in CASES:
        got = decide(policy_cls, root, kind, target)
        if got != expected:
            wrong.append((num, expected, got))
    return wrong


class BoundaryCases(unittest.TestCase):
    def test_all_16_cases(self):
        root = make_root()
        for num, kind, target, expected in CASES:
            with self.subTest(case=num, kind=kind, target=target):
                self.assertEqual(decide(Policy, root, kind, target), expected)

    def test_refusal_has_a_reason(self):
        d = Policy(make_root()).check_request("GET", "https://www.linkedin.com/jobs/")
        self.assertEqual(d.verdict, "refuse")
        self.assertIn("www.linkedin.com", d.reason)


class ExtraPolicy(unittest.TestCase):
    def test_credentials_in_url_refused(self):
        self.assertEqual(Policy(make_root()).check_request("GET", "https://u:p@boards-api.greenhouse.io/v1/boards/x/jobs").verdict, "refuse")

    def test_delete_needs_approval(self):
        self.assertEqual(Policy(make_root()).check_delete("out/reports/run.md").verdict, "hold")

    def test_write_outside_with_approval_flag_still_refused(self):
        # approval covers the state file only; it never widens the folder
        self.assertEqual(Policy(make_root(), approve_state_write=True).check_write("config/boards.json").verdict, "refuse")

    def test_symlinked_file_inside_out_refused(self):
        root = make_root()
        os.symlink(root / "config" / "boards.json", root / "out" / "sneaky.json")
        self.assertEqual(Policy(root).check_write("out/sneaky.json").verdict, "refuse")

    def test_read_outside_via_dotdot_refused(self):
        self.assertEqual(Policy(make_root()).check_read("config/../../outside/secret").verdict, "refuse")


if __name__ == "__main__":
    unittest.main()
