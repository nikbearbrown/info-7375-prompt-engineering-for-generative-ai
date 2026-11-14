"""Boundary tests for agent/policy.py, one per row of BOUNDARY_TABLE.md.

Predictions were committed in 75ff81e before this file existed.
Every path test runs inside a fresh temporary folder that stands in for the
project root, so nothing outside it is ever written. Row 7 (/etc/passwd)
only asks the policy; it never attempts a write.

The "run exits error" half of each prediction is checked by the loop tests
(the loop turns PolicyViolation into exit status `error`); these tests check
that PolicyViolation is raised.
"""

import tempfile
import unittest
from pathlib import Path

from agent.policy import Policy, PolicyViolation, guarded_write


class PolicyBoundaryTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve()
        (self.root / "out").mkdir()
        (self.root / "boards.json").write_text('{"boards": []}', encoding="utf-8")
        self.policy = Policy(self.root)
        self.approved = Policy(self.root, approve=True)

    def tearDown(self):
        self._tmp.cleanup()

    def assertBlocked(self, fn, *args):
        with self.assertRaises(PolicyViolation) as ctx:
            fn(*args)
        return ctx.exception

    # --- requests -------------------------------------------------------

    def test_b01_host_not_on_allow_list(self):
        e = self.assertBlocked(self.policy.check_request, "GET", "https://api.github.com/repos")
        self.assertIn("host", e.reason)

    def test_b02_lookalike_host(self):
        e = self.assertBlocked(
            self.policy.check_request, "GET", "https://boards-api.greenhouse.io.evil.com/jobs"
        )
        self.assertIn("host", e.reason)

    def test_b03_post_to_allowed_host(self):
        e = self.assertBlocked(
            self.policy.check_request, "POST",
            "https://boards-api.greenhouse.io/v1/boards/github/jobs",
        )
        self.assertIn("method", e.reason)

    def test_b11_get_allowed_host(self):
        # Must not raise.
        self.policy.check_request("GET", "https://boards-api.greenhouse.io/v1/boards/robinhood/jobs")

    # --- writes ---------------------------------------------------------

    def test_b04_dotdot_traversal(self):
        self.assertBlocked(self.policy.check_write, "out/../secret.txt")
        self.assertBlocked(guarded_write, self.policy, "out/../secret.txt", "x")
        self.assertFalse((self.root / "secret.txt").exists())

    def test_b05_prefix_lookalike_folder(self):
        (self.root / "out-evil").mkdir()
        self.assertBlocked(self.policy.check_write, "out-evil/jobs.json")
        self.assertBlocked(guarded_write, self.policy, "out-evil/jobs.json", "x")
        self.assertFalse((self.root / "out-evil" / "jobs.json").exists())

    def test_b06_symlink_escape(self):
        link = self.root / "out" / "symlink_escape"
        link.symlink_to(self.root, target_is_directory=True)
        self.assertBlocked(self.policy.check_write, "out/symlink_escape")
        # Writing a file *through* the link must also be blocked.
        self.assertBlocked(guarded_write, self.policy, "out/symlink_escape/escaped.txt", "x")
        self.assertFalse((self.root / "escaped.txt").exists())

    def test_b07_absolute_path(self):
        # Asks the policy only; never attempts a real write to /etc.
        self.assertBlocked(self.policy.check_write, "/etc/passwd")

    def test_b08_read_boards_json(self):
        real = self.policy.check_read("boards.json")
        self.assertEqual(real, self.root / "boards.json")

    def test_b09_write_boards_json_without_approve(self):
        e = self.assertBlocked(guarded_write, self.policy, "boards.json", '{"changed": true}')
        self.assertIn("--approve", e.reason)
        self.assertEqual((self.root / "boards.json").read_text(), '{"boards": []}')

    def test_b10_write_boards_json_with_approve(self):
        guarded_write(self.approved, "boards.json", '{"changed": true}')
        self.assertEqual((self.root / "boards.json").read_text(), '{"changed": true}')

    def test_b12_write_inside_out(self):
        guarded_write(self.policy, "out/jobs.json", "[]")
        self.assertTrue((self.root / "out" / "jobs.json").exists())


if __name__ == "__main__":
    unittest.main()
