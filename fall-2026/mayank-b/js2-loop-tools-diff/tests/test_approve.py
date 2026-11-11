"""The one approval-needed write (GATE §4 4b-C, §6 6c)."""
import json
import unittest

from helpers import RUN_ID, temp_root
from jsa import cli


def setup(root, proposed, current, needs=(), suspects=()):
    rd = root / "runs" / RUN_ID
    rd.mkdir(parents=True, exist_ok=True)
    (rd / "proposed-seen-ids.json").write_text(json.dumps(proposed))
    (rd / "report.json").write_text(json.dumps({"needs_mayank": list(needs)}))
    boards = {b: {"verdict": "suspect" if b in suspects else "ok"} for b in proposed}
    (rd / "check.json").write_text(json.dumps({"boards": boards}))
    (root / "state/seen-ids.json").write_text(json.dumps(current))


class Approve(unittest.TestCase):
    def setUp(self):
        self.root = temp_root()
        self._old, cli.ROOT = cli.ROOT, self.root

    def tearDown(self):
        cli.ROOT = self._old

    def state(self):
        return json.loads((self.root / "state/seen-ids.json").read_text())

    def test_refused_before_checker_ran(self):
        (self.root / "runs" / RUN_ID).mkdir(parents=True)
        self.assertEqual(cli.main(["approve", RUN_ID, "--approve-state", RUN_ID]), 2)

    def test_truthy_approval_writes_nothing(self):
        setup(self.root, {"greenhouse/a": ["1", "2"]}, {"greenhouse/a": ["1"]})
        self.assertEqual(cli.main(["approve", RUN_ID, "--approve-state", "yes"]), 2)
        self.assertEqual(self.state(), {"greenhouse/a": ["1"]})

    def test_exact_approval_applies(self):
        setup(self.root, {"greenhouse/a": ["1", "2"]}, {"greenhouse/a": ["1"]})
        self.assertEqual(cli.main(["approve", RUN_ID, "--approve-state", RUN_ID]), 0)
        self.assertEqual(self.state(), {"greenhouse/a": ["1", "2"]})

    def test_suspect_board_held_until_acked(self):
        setup(self.root, {"greenhouse/hubspot": [], "greenhouse/a": ["1", "2"]}, {"greenhouse/hubspot": ["7"], "greenhouse/a": ["1"]}, suspects=["greenhouse/hubspot"])
        self.assertEqual(cli.main(["approve", RUN_ID, "--approve-state", RUN_ID]), 3)
        self.assertEqual(self.state()["greenhouse/hubspot"], ["7"])
        self.assertEqual(self.state()["greenhouse/a"], ["1", "2"])
        self.assertEqual(cli.main(["approve", RUN_ID, "--approve-state", RUN_ID, "--ack", "greenhouse/hubspot"]), 0)
        self.assertEqual(self.state()["greenhouse/hubspot"], [])

    def test_W9_error_board_state_survives_approve(self):
        setup(self.root, {"greenhouse/x": ["1", "2"]}, {"greenhouse/x": ["1", "2"]}, needs=["greenhouse/x"])
        cli.main(["approve", RUN_ID, "--approve-state", RUN_ID])
        self.assertEqual(self.state()["greenhouse/x"], ["1", "2"])


if __name__ == "__main__":
    unittest.main()
