"""GATE.md's three wrong versions. Each check passes on the real loop and must fail on its wrong version.

The boards and answers are CONSTRUCTED; no network is used.
"""
import unittest

from agent import check, wrong_versions
from tests.fakes import BUDGETS, LEVER_404, FakeNet, Project, greenhouse, lever, url

GOOD = {"name": "acme", "system": "greenhouse"}
BAD = {"name": "no-such-board", "system": "lever"}


def requests_to_failing_board_ok(net):
    """GATE.md: a wrong board name is asked for once, never again."""
    return net.calls.count(url("lever", "no-such-board")) == 1


def within_limits(net, result, budgets, hosts):
    """GATE.md: never more requests than the budget, never a host off the allow-list."""
    return len(net.calls) <= budgets["max_requests"] and all(u.split("/")[2] in hosts for u in net.calls)


class WrongVersionTests(unittest.TestCase):
    def setUp(self):
        self.p = Project(self)

    def nets(self):
        return FakeNet({url("greenhouse", "acme"): [(200, greenhouse(1))], url("lever", "no-such-board"): [(404, LEVER_404)],
                        url("lever", "beta"): [(200, lever("a"))]})

    def test_catches_wrong_version_1_retries_a_failing_board(self):
        net = self.nets()
        self.p.run([GOOD, BAD], net)
        self.assertTrue(requests_to_failing_board_ok(net), "the real loop passes")
        net = self.nets()
        self.p.run([GOOD, BAD], net, hooks=wrong_versions.RETRIES_FOREVER)
        self.assertFalse(requests_to_failing_board_ok(net), "wrong version 1 is caught")

    def test_catches_wrong_version_2_over_budget_and_off_list_host(self):
        from agent.policy import Policy
        budgets = BUDGETS | {"max_requests": 2}
        boards = [GOOD, {"name": "beta", "system": "lever"}, BAD]
        hosts = ["boards-api.greenhouse.io"]
        self.p.policy = Policy(root=self.p.root, hosts=hosts)
        net = self.nets()
        result, _, _ = self.p.run(boards, net, budgets=budgets)
        self.assertTrue(within_limits(net, result, budgets, hosts), "the real loop passes")
        net = self.nets()
        result, _, _ = self.p.run(boards, net, budgets=budgets, hooks=wrong_versions.NO_LIMITS)
        self.assertFalse(within_limits(net, result, budgets, hosts), "wrong version 2 is caught")

    def test_catches_wrong_version_3_failed_board_reported_as_empty(self):
        result, _, run_dir = self.p.run([GOOD, BAD], self.nets())
        self.assertEqual(result.status, "incomplete")
        self.assertEqual(check.check(run_dir, self.p.root)[0], [], "the independent check passes the real loop")
        result, _, run_dir = self.p.run([GOOD, BAD], self.nets(), hooks=wrong_versions.FAILED_AS_EMPTY, tag="-WRONG-V3")
        self.assertEqual(result.status, "finished", "wrong version 3 ends cleanly ...")
        problems, _ = check.check(run_dir, self.p.root)
        self.assertTrue(any("not a job list" in p for p in problems), "... and the independent check catches it")


if __name__ == "__main__":
    unittest.main()
