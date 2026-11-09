"""The loop against GATE.md: exits, budgets, repeat rule, error policy, and wrong versions 2 and 4."""
import json
import os
import unittest
from unittest import mock

from helpers import (ASHBY, GH, LEVER, Clock, TransientError, ashby_body, board, gh_body, lever_body, make,
                     read_state, stamp)

import loop
from loop import Run

THREE = [board("greenhouse", "abacusinsights"), board("ashby", "valon"), board("lever", "xsolla")]
NOT_FOUND = (404, b"Not Found")


def ok_script(gh=(1, 2), ashby=("a", "b"), lever=("x",)):
    return {GH.format("abacusinsights"): [(200, gh_body(*gh))], ASHBY.format("valon"): [(200, ashby_body(*ashby))],
            LEVER.format("xsolla"): [(200, lever_body(*lever))]}


def go(tools, sleep=None, clock=None, budgets=None, config="config/boards.json"):
    sleeps = []
    run_dir, s = loop.run(tools, config_path=config, now=stamp(), budgets=budgets,
                          clock=clock or Clock(), sleep=sleep or sleeps.append)
    s["_sleeps"] = sleeps
    return run_dir, s


class ThreeBoardsTwoSystems(unittest.TestCase):
    def test_all_three_boards_succeed_and_the_run_finishes(self):
        root, tools = make(THREE, ok_script())
        run_dir, s = go(tools)
        self.assertEqual(s["exit"], "finished")
        self.assertEqual(s["requests"], 3)
        self.assertEqual({r["status"] for r in s["results"].values()}, {"ok"})
        self.assertTrue(all(r["baseline"] and r["new"] == [] for r in s["results"].values()))
        self.assertEqual(read_state(root)["boards"]["ashby/valon"]["seen"], ["a", "b"])
        for name in ("trace.jsonl", "run.json", "report.md", "raw/lever_xsolla.json"):
            self.assertTrue(os.path.exists(os.path.join(root, run_dir, name)), name)

    def test_second_run_reports_new_and_closed_postings(self):
        root, tools = make(THREE, ok_script())
        go(tools)
        tools.script = ok_script(gh=(2, 3), ashby=("a", "b"), lever=("x",))
        _, s = go(tools)
        gh = s["results"]["greenhouse/abacusinsights"]
        self.assertEqual([p["id"] for p in gh["new"]], ["3"])
        self.assertEqual(gh["closed"], ["1"])
        self.assertEqual(read_state(root)["boards"]["greenhouse/abacusinsights"]["seen"], ["1", "2", "3"])

    def test_a_posting_that_closes_and_returns_is_not_new(self):
        root, tools = make(THREE, ok_script(gh=(1, 2)))
        go(tools)
        tools.script = ok_script(gh=(2,))
        go(tools)
        tools.script = ok_script(gh=(1, 2))
        _, s = go(tools)
        self.assertEqual(s["results"]["greenhouse/abacusinsights"]["new"], [])


class ErrorPolicy(unittest.TestCase):
    """The deliberate failure, timeouts, 5xx, and nothing invented."""

    def test_deliberate_404_with_plain_text_body_is_a_failed_board_not_a_crash(self):
        boards = THREE + [board("ashby", "valonn")]
        script = ok_script()
        script[ASHBY.format("valonn")] = [NOT_FOUND]
        root, tools = make(boards, script)
        run_dir, s = go(tools)
        self.assertEqual(s["exit"], "incomplete")
        self.assertEqual(s["results"]["ashby/valonn"]["status"], "failed")
        self.assertIn("HTTP 404", s["results"]["ashby/valonn"]["reason"])
        self.assertEqual(s["requests"], 4)  # no retry of a 404
        self.assertEqual(s["_sleeps"], [])
        self.assertNotIn("ashby/valonn", read_state(root)["boards"])  # no value invented
        with open(os.path.join(root, run_dir, "raw/ashby_valonn.http404.txt"), "rb") as f:
            self.assertEqual(f.read(), b"Not Found")

    def test_a_failed_board_keeps_its_previous_state(self):
        root, tools = make(THREE, ok_script())
        go(tools)
        before = read_state(root)["boards"]["ashby/valon"]
        tools.script = ok_script()
        tools.script[ASHBY.format("valon")] = [(500, b"oops"), (503, b"oops")]
        _, s = go(tools)
        self.assertEqual(s["exit"], "incomplete")
        self.assertEqual(read_state(root)["boards"]["ashby/valon"], before)

    def test_timeout_is_retried_once_after_two_seconds(self):
        script = ok_script()
        script[ASHBY.format("valon")] = [TransientError("timeout"), (200, ashby_body("a"))]
        _, tools = make(THREE, script)
        _, s = go(tools)
        self.assertEqual(s["exit"], "finished")
        self.assertEqual(s["requests"], 4)
        self.assertEqual(s["_sleeps"], [2])

    def test_second_timeout_fails_the_board_after_one_retry(self):
        script = ok_script()
        script[ASHBY.format("valon")] = [TransientError("timeout"), TransientError("timeout")]
        _, tools = make(THREE, script)
        _, s = go(tools)
        self.assertEqual(s["exit"], "incomplete")
        self.assertIn("after one retry", s["results"]["ashby/valon"]["reason"])
        self.assertEqual(s["requests"], 4)

    def test_other_4xx_is_not_retried(self):
        script = ok_script()
        script[LEVER.format("xsolla")] = [(403, b"Forbidden")]
        _, tools = make(THREE, script)
        _, s = go(tools)
        self.assertEqual(s["results"]["lever/xsolla"]["status"], "failed")
        self.assertEqual(s["requests"], 3)

    def test_unparseable_200_is_a_failed_board(self):
        script = ok_script()
        script[GH.format("abacusinsights")] = [(200, b"<html>maintenance</html>")]
        root, tools = make(THREE, script)
        _, s = go(tools)
        self.assertEqual(s["exit"], "incomplete")
        self.assertIn("unparseable", s["results"]["greenhouse/abacusinsights"]["reason"])


class Budgets(unittest.TestCase):
    def test_request_budget_counts_retries(self):
        script = ok_script()
        script[GH.format("abacusinsights")] = [TransientError("t"), TransientError("t")]
        script[ASHBY.format("valon")] = [TransientError("t"), (200, ashby_body("a"))]
        _, tools = make(THREE, script)
        _, s = go(tools, budgets={"requests": 3})
        self.assertEqual(s["exit"], "budget-exhausted")
        self.assertEqual(s["requests"], 3)
        self.assertIn("lever/xsolla", s["unvisited"])

    def test_board_budget(self):
        boards = [board("ashby", f"b{i}") for i in range(6)]
        script = {ASHBY.format(f"b{i}"): [(200, ashby_body(i))] for i in range(6)}
        _, tools = make(boards, script)
        _, s = go(tools)
        self.assertEqual(s["exit"], "budget-exhausted")
        self.assertEqual(s["boards_started"], 5)
        self.assertEqual(s["unvisited"], ["ashby/b5"])

    def test_time_budget(self):
        _, tools = make(THREE, ok_script())
        _, s = go(tools, clock=Clock(step=25))
        self.assertEqual(s["exit"], "budget-exhausted")
        self.assertIn("seconds", s["reason"])

    def test_budget_exhausted_still_saves_the_boards_that_succeeded(self):
        root, tools = make(THREE, ok_script())
        _, s = go(tools, budgets={"requests": 2})
        self.assertEqual(s["exit"], "budget-exhausted")
        self.assertIn("ashby/valon", read_state(root)["boards"])


class RepeatRule(unittest.TestCase):
    def test_a_repeated_board_is_refused_logged_and_the_run_goes_on(self):
        boards = THREE + [board("ashby", "valon")]
        root, tools = make(boards, ok_script())
        run_dir, s = go(tools)
        self.assertEqual(s["requests"], 3)
        with open(os.path.join(root, run_dir, "trace.jsonl")) as f:
            events = [json.loads(line)["event"] for line in f]
        self.assertIn("repeat refused", events)
        self.assertEqual(s["exit"], "finished")


class ErrorExit(unittest.TestCase):
    def test_policy_violation_mid_run_stops_with_error_and_writes_no_state(self):
        _, tools = make(THREE, ok_script())
        real = tools.policy.check_request

        def refuse_lever(method, url, headers=None):
            if "lever" in url:
                raise loop.PolicyViolation("refused for the test")
            return real(method, url, headers)
        tools.policy.check_request = refuse_lever
        root = tools.policy.root
        _, s = go(tools)
        self.assertEqual(s["exit"], "error")
        self.assertFalse(os.path.exists(os.path.join(root, "state/seen.json")))

    def test_bad_board_token_is_an_error_before_any_request(self):
        _, tools = make([board("greenhouse", "abacus/../x")], {})
        _, s = go(tools)
        self.assertEqual(s["exit"], "error")
        self.assertEqual(tools.sent, [])

    def test_board_list_change_without_approval_is_an_error(self):
        root, tools = make(THREE, ok_script())
        go(tools)
        state_before = read_state(root)
        with open(os.path.join(root, "config/boards.json"), "w") as f:
            json.dump({"boards": THREE[:2]}, f)
        tools.script = ok_script()
        _, s = go(tools)
        self.assertEqual(s["exit"], "error")
        self.assertEqual(read_state(root), state_before)
        self.assertEqual(tools.policy.decisions[-1]["approved"], False)

    def test_interrupt_is_incomplete_and_keeps_finished_boards(self):
        script = ok_script()
        script[ASHBY.format("valon")] = [KeyboardInterrupt()]
        root, tools = make(THREE, script)
        _, s = go(tools)
        self.assertEqual(s["exit"], "incomplete")
        self.assertIn("ashby/valon", s["unvisited"])
        self.assertIn("greenhouse/abacusinsights", read_state(root)["boards"])


class WrongVersions(unittest.TestCase):
    """GATE.md wrong versions 2 and 4, run as mutants: each one turns a test above green-but-wrong."""

    def test_wrong_version_2_failed_board_read_as_no_new_jobs_is_caught(self):
        boards = THREE + [board("ashby", "valonn")]

        def script():
            s = ok_script()
            s[ASHBY.format("valonn")] = [NOT_FOUND]
            return s
        real = Run.fetch_board

        def as_empty(self, b, raw_dir):
            postings, reason = real(self, b, raw_dir)
            return (postings if postings is not None else []), None
        _, tools = make(boards, script())
        with mock.patch.object(Run, "fetch_board", as_empty):
            _, mutant = go(tools)
        self.assertEqual(mutant["exit"], "finished")  # the mutant reports a clean run
        _, tools = make(boards, script())
        _, real_run = go(tools)
        self.assertEqual(real_run["exit"], "incomplete")  # the real loop does not

    def test_wrong_version_4_uncounted_retries_are_caught(self):
        def script():
            s = ok_script()
            for url in s:
                s[url] = [TransientError("t")] + s[url]
            return s

        def count_first_attempts_only(self):
            if self.requests + 1 > self.budgets["requests"]:
                raise loop.BudgetExhausted("requests")
        original_get = Run.get

        def get_without_counting_retries(self, url, retry=False):
            if retry:
                key = ("GET", url)
                self.sent.add(key)
                return self.tools.http_get(url, timeout=1)
            return original_get(self, url, retry)
        _, tools = make(THREE, script())
        with mock.patch.object(Run, "get", get_without_counting_retries):
            _, mutant = go(tools, budgets={"requests": 4})
        self.assertEqual(mutant["exit"], "finished")  # 6 requests sent under a budget of 4
        self.assertEqual(len(tools.sent), 6)
        _, tools = make(THREE, script())
        _, real_run = go(tools, budgets={"requests": 4})
        self.assertEqual(real_run["exit"], "budget-exhausted")
        self.assertLessEqual(len(tools.sent), 4)


if __name__ == "__main__":
    unittest.main()
