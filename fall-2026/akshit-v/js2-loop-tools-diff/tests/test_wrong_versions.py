"""GATE.md section 7: each check passes on the real code and catches the wrong version."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

from agent2 import loop, policy
from agent2.policy import PolicyViolation
from tests import wrong_versions
from tests.fakes import FIGMA, SPOTIFY, FakeClock, FakeTransport, gh, lever, no_save

_spec = importlib.util.spec_from_file_location("check_run", Path(__file__).resolve().parent.parent / "scripts" / "check_run.py")
check_run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_run)


def record_from(result, state_before, raws):
    """A run record shaped like run.py's, for the independent check."""
    return {"exit": result.exit, "budget": vars(loop.Budget()), "boards": result.boards,
            "not_attempted": result.not_attempted, "new": {k: [] for k in result.postings},
            "state_before": state_before,
            "trace": [{**e, "raw": raws.get(e.get("board"))} if e["event"] == "request" else e for e in result.trace]}


class WaFinishedWrongAnswer(unittest.TestCase):
    """CONSTRUCTED: figma had 140 jobs last run; this time it returns an empty list."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=policy.ROOT)   # check_run reads raw paths relative to ROOT
        d = Path(self.tmp.name)
        (d / "figma.json").write_bytes(gh(0).body)
        (d / "spotify.json").write_bytes(lever(1).body)
        self.raws = {FIGMA.key: (d / "figma.json").relative_to(policy.ROOT).as_posix(),
                     SPOTIFY.key: (d / "spotify.json").relative_to(policy.ROOT).as_posix()}
        self.state = {"boards": {FIGMA.key: {"seen_ids": [], "last_count": 140},
                                 SPOTIFY.key: {"seen_ids": ["lever:spotify:u0"], "last_count": 1}}}

    def tearDown(self):
        self.tmp.cleanup()

    def run_with(self, classify):
        t = FakeTransport({FIGMA.url: [gh(0)], SPOTIFY.url: [lever(1)]})
        return loop.run_loop([FIGMA, SPOTIFY], t, {k: v["last_count"] for k, v in self.state["boards"].items()},
                             loop.Budget(), no_save, clock=FakeClock(), classify=classify)

    def test_wrong_version_finishes_cleanly_and_the_independent_check_catches_it(self):
        r = self.run_with(wrong_versions.wa_classify)
        self.assertEqual(r.exit, "finished")                              # the agent's own report looks fine
        problems = check_run.check(record_from(r, self.state, self.raws))
        self.assertTrue(any("not 'no new jobs'" in p for p in problems), problems)

    def test_real_version_does_not_finish(self):
        r = self.run_with(loop.classify)
        self.assertEqual((r.exit, r.boards[FIGMA.key]["outcome"]), ("incomplete", "suspicious_empty"))
        self.assertEqual(check_run.check(record_from(r, self.state, self.raws)), [])


class WbPrefixPathCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / "out"
        self.out.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def sibling(self):
        return Path(self.tmp.name) / "out-evil" / "x.json"

    def test_real_check_refuses_sibling(self):
        with self.assertRaises(PolicyViolation):
            policy.check_write(self.sibling(), self.out)

    def test_wrong_version_lets_sibling_through(self):
        wrong_versions.wb_check_write(self.sibling(), self.out)   # no exception: the bug the real test catches


if __name__ == "__main__":
    unittest.main()
