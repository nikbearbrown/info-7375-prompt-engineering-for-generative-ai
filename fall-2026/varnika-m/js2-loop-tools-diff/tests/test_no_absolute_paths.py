"""Privacy: what a run writes names files relative to this folder, never by the absolute path.

The absolute path starts with the home folder, which includes my username. Written before the change.
"""

import unittest

from tests.helpers import MISSING, THREE, FakeClock, FakeNet, GH, make_root, run_loop, status
from tests.test_loop import three_ok


class NoAbsolutePathsInWhatARunWrites(unittest.TestCase):
    def test_trace_record_and_report_use_relative_paths(self):
        root, clock = make_root(self, THREE + [MISSING]), FakeClock()
        script = three_ok()
        script[GH % MISSING["board"]] = [status(404, b"{}")]
        record = run_loop(root, FakeNet(clock, script), clock)
        for name in ("trace", "record", "report"):
            text = (root / record["files"][name]).read_text(encoding="utf-8")
            self.assertNotIn(str(root), text, "%s contains the absolute folder path" % name)

    def test_a_refused_state_reset_names_the_file_relatively(self):
        from agent.policy import Policy
        root, clock = make_root(self, THREE), FakeClock()
        decision = Policy(root).check_write(root / "jobs" / "state" / "x.json", kind="state", board="a/b",
                                            drops_ids=True)
        self.assertEqual(decision.target, "jobs/state/x.json")
        outside = Policy(root).check_read(root.parent / "elsewhere" / "secret.txt")
        self.assertNotIn(str(root.parent), outside.target)


if __name__ == "__main__":
    unittest.main()
