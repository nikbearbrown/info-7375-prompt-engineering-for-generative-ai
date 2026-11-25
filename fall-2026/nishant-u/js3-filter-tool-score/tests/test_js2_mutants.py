"""Each GATE.md wrong version is caught; the real code passes the same check."""
import tempfile
import unittest
from pathlib import Path

from tests import helpers, js2_helpers as h, js2_mutants as m


class WrongVersions(helpers.ContractTest):
    modules = ("agent2.policy", "agent2.loop")

    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name).resolve()
        (self.parent / "out").mkdir()
        (self.parent / "out-evil").mkdir()

    def accepts(self, policy_class, *args, **kwargs):
        try:
            policy_class(self.parent / "out").authorize(*args, **kwargs)
            return True
        except self.policy.PolicyRefused:
            return False

    def run_with(self, loop_class, boards, responses, budgets=None, out="out"):
        clock = h.FakeClock()
        client = h.FakeClient(responses, clock=clock)
        report = loop_class(boards, policy=self.policy.Policy(self.parent / out), client=client,
                            clock=clock, sleep=clock.sleep, budgets=budgets).run()
        return report, client

    def test_1_string_prefix_containment_is_caught(self):
        target = str(self.parent / "out-evil" / "x.txt")
        self.assertFalse(self.accepts(self.policy.Policy, "write_run_file", target))
        self.assertTrue(self.accepts(m.prefix_policy(), "write_run_file", target))

    def test_2_uncounted_retries_are_caught(self):
        failing = {b["url"]: [(500, b"err")] for b in self.loop.PROFILES["full"]}
        for cls, ok in ((self.loop.Loop, True), (m.uncounted_retry_loop(), False)):
            with self.subTest(cls=cls.__name__):
                report, client = self.run_with(cls, self.loop.PROFILES["full"], failing, budgets={"requests": 3})
                within = len(client.calls) <= 3 and report["used"]["requests"] == len(client.calls)
                self.assertEqual(within, ok)

    def test_3_finished_despite_failure_is_caught(self):
        real, _ = self.run_with(self.loop.Loop, self.loop.PROFILES["full"], h.ok_responses())
        wrong, _ = self.run_with(m.finished_despite_failure_loop(), self.loop.PROFILES["full"],
                                 h.ok_responses(), out="out2")
        self.assertEqual(real["exit"], "incomplete")
        self.assertEqual(wrong["exit"], "finished")

    def test_4_truthy_approval_is_caught(self):
        for value in ("yes", 1):
            with self.subTest(approved=value):
                self.assertFalse(self.accepts(self.policy.Policy, "reset_state", "state/seen_ids.json", approved=value))
                self.assertTrue(self.accepts(m.truthy_approval_policy(), "reset_state", "state/seen_ids.json",
                                             approved=value))

    def test_5_invented_value_is_caught(self):
        def bad_board(report):
            return next(b for b in report["boards"] if b["board"] == "no-such-board-js2-test")
        real, _ = self.run_with(self.loop.Loop, self.loop.PROFILES["full"], h.ok_responses())
        wrong, _ = self.run_with(m.invented_value_loop(), self.loop.PROFILES["full"], h.ok_responses(), out="out2")
        self.assertIsNone(bad_board(real)["new_ids"])
        self.assertEqual(bad_board(wrong)["new_ids"], [])

    def test_6_replacing_update_state_is_caught(self):
        def after(policy_class):
            p = policy_class(self.parent / "out" / policy_class.__name__)
            p.update_state("state/seen_ids.json", ["greenhouse:faire:1"])
            p.update_state("state/seen_ids.json", ["greenhouse:faire:2"])
            return p.read_state("state/seen_ids.json")["seen_ids"]
        self.assertEqual(after(self.policy.Policy), ["greenhouse:faire:1", "greenhouse:faire:2"])
        self.assertEqual(after(m.replacing_update_policy()), ["greenhouse:faire:2"])


if __name__ == "__main__":
    unittest.main()
