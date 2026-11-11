"""The loop (GATE.md sections 1-4 and 6). Every expectation comes from GATE.md; the section is named in each test."""
import os, importlib, unittest
from tests.fakes import gh, lever, NOT_FOUND, BLANK, TIMEOUT, Clock, ScriptedFetch
from watcher.loop import Budget

# Run the same tests against a wrong version:  WATCHER_LOOP=wrong_versions.empty_as_zero python3 -m unittest tests.test_loop
loop = importlib.import_module(os.environ.get("WATCHER_LOOP", "watcher.loop"))

K, D, P, BAD = "greenhouse:klaviyo", "greenhouse:datadog", "lever:palantir", "greenhouse:no-such-board-7375"
B = lambda k: {"ats": k.split(":")[0], "slug": k.split(":")[1]}

def run(boards, script, seen=None, budget=None, cost=1.0):
    c = Clock(); f = ScriptedFetch(script, clock=c, cost=cost)
    return loop.run([B(k) for k in boards], f, budget=budget or Budget(), clock=c, seen=seen), f

def status(r, k): return next(b for b in r["boards"] if b["board"] == k)

class Exits(unittest.TestCase):                       # GATE 1
    def test_finished_reports_boards_and_new_count_even_zero(self):
        r, _ = run([K, P], {K: [gh(1, 2)], P: [lever(9)]}, seen={K: {"1", "2"}, P: {"9"}})
        self.assertEqual(r["exit"], "finished")
        self.assertEqual(r["boards_checked"], 2); self.assertEqual(r["new_count"], 0)
    def test_incomplete_lists_failed_boards_and_why(self):
        r, _ = run([K, BAD], {K: [gh(1)], BAD: [NOT_FOUND]})
        self.assertEqual(r["exit"], "incomplete")
        self.assertEqual(status(r, BAD)["status"], "failed"); self.assertIn("404", status(r, BAD)["error"])
    def test_budget_exhausted_says_which_limit_and_unfinished_boards(self):
        r, _ = run([K, D, P], {K: [gh(1)], D: [gh(2)], P: [lever(3)]}, budget=Budget(requests=2))
        self.assertEqual(r["exit"], "budget-exhausted"); self.assertEqual(r["limit_hit"], "requests")
        self.assertEqual(status(r, P)["status"], "not-reached")
    def test_error_when_no_board_succeeds(self):
        r, _ = run([BAD], {BAD: [NOT_FOUND]})
        self.assertEqual(r["exit"], "error")
    def test_error_when_run_cannot_start(self):
        r, _ = run([], {})
        self.assertEqual(r["exit"], "error")

class Budgets(unittest.TestCase):                     # GATE 2
    def test_defaults_are_my_numbers(self):
        b = Budget(); self.assertEqual((b.boards, b.requests, b.seconds), (5, 15, 60))
    def test_retries_count_toward_requests(self):
        r, f = run([K], {K: [TIMEOUT, gh(1)]})
        self.assertEqual(r["used"]["requests"], 2); self.assertEqual(len(f.calls), 2)
    def test_more_than_five_distinct_boards_is_budget_exhausted(self):
        ks = [f"greenhouse:b{i}" for i in range(6)]
        r, f = run(ks, {k: [gh(i)] for i, k in enumerate(ks)})
        self.assertEqual(len(f.calls), 5); self.assertEqual(r["exit"], "budget-exhausted"); self.assertEqual(r["limit_hit"], "boards")
    def test_seconds_limit_stops_the_loop(self):
        r, f = run([K, D, P], {K: [gh(1)], D: [gh(2)], P: [lever(3)]}, cost=31.0)
        self.assertEqual(r["exit"], "budget-exhausted"); self.assertEqual(r["limit_hit"], "seconds")
        self.assertEqual(len(f.calls), 2)

class Repeat(unittest.TestCase):                      # GATE 3
    def test_duplicate_board_is_skipped_and_noted(self):
        r, f = run([K, K], {K: [gh(1)]})
        self.assertEqual(f.calls, [K])
        self.assertTrue(any("duplicate" in n for n in r["notes"]))
        self.assertEqual(r["exit"], "finished")

class Errors(unittest.TestCase):                      # GATE 4
    def test_bad_name_reported_no_retry_move_on(self):
        r, f = run([BAD, K], {BAD: [NOT_FOUND], K: [gh(1)]})
        self.assertEqual(f.calls, [BAD, K])           # one try for the bad name, then the next board
    def test_timeout_retried_once_then_success(self):
        r, f = run([K], {K: [TIMEOUT, gh(1)]})
        self.assertEqual(status(r, K)["status"], "ok"); self.assertEqual(f.calls, [K, K])
    def test_blank_body_retried_once(self):
        r, f = run([K], {K: [BLANK, gh(1)]})
        self.assertEqual(status(r, K)["status"], "ok"); self.assertEqual(len(f.calls), 2)
    def test_two_timeouts_fail_then_next_board(self):
        r, f = run([K, P], {K: [TIMEOUT, TIMEOUT], P: [lever(3)]})
        self.assertEqual(f.calls, [K, K, P]); self.assertEqual(status(r, K)["status"], "failed")
    def test_failed_board_has_no_invented_values(self):
        r, _ = run([BAD, K], {BAD: [NOT_FOUND], K: [gh(1)]})
        self.assertIsNone(status(r, BAD)["jobs"]); self.assertIsNone(status(r, BAD)["new"])
    def test_every_attempt_is_observed(self):
        r, _ = run([K], {K: [TIMEOUT, gh(1)]})
        self.assertEqual([o["outcome"] for o in r["observations"]], ["timeout", "ok"])

class WrongVersions(unittest.TestCase):               # GATE 6
    def test_wrong1_empty_list_is_success_but_failure_is_not_zero(self):
        r, _ = run([K, D], {K: [gh()], D: [TIMEOUT, TIMEOUT]})
        self.assertEqual(status(r, K)["status"], "ok"); self.assertEqual(status(r, K)["jobs"], 0)
        self.assertEqual(status(r, D)["status"], "failed"); self.assertIsNone(status(r, D)["jobs"])
        self.assertEqual(r["exit"], "incomplete")
    def test_wrong2_timeout_on_last_allowed_request_gets_no_retry(self):
        # GATE 6.2, scaled down: the request limit is 3 and request 3 times out while no budget is left for its retry.
        r, f = run([K, D, P], {K: [gh(1)], D: [gh(2)], P: [TIMEOUT, lever(3)]}, budget=Budget(requests=3))
        self.assertEqual(len(f.calls), 3)                           # no 4th request
        self.assertEqual(r["exit"], "budget-exhausted"); self.assertEqual(r["limit_hit"], "requests")
        self.assertEqual(status(r, P)["status"], "failed"); self.assertIn("timeout", status(r, P)["error"])
    def test_wrong2_timeout_while_another_board_waits(self):
        # GATE 6.2 as written, at limit 7: request 7 is a first try that times out, and board b is still waiting.
        ks = [K, D, P, "greenhouse:a", "greenhouse:b"]
        script = {K: [TIMEOUT, TIMEOUT], D: [TIMEOUT, TIMEOUT], P: [TIMEOUT, TIMEOUT],
                  "greenhouse:a": [TIMEOUT, TIMEOUT], "greenhouse:b": [gh(1)]}
        r, f = run(ks, script, budget=Budget(requests=7))
        self.assertEqual(len(f.calls), 7)                           # the retry would be request 8: not made
        self.assertEqual(r["exit"], "budget-exhausted")
        self.assertEqual(status(r, "greenhouse:a")["status"], "failed"); self.assertIn("timeout", status(r, "greenhouse:a")["error"])
        self.assertEqual(status(r, "greenhouse:b")["status"], "not-reached")
    def test_at_my_default_numbers_requests_cannot_exceed_ten(self):
        # Finding while writing tests: 5 boards x (1 try + 1 retry) = 10 < 15, so the 15-request limit is never the binding one.
        ks = [K, D, P, "greenhouse:a", "greenhouse:b"]
        r, f = run(ks, {k: [TIMEOUT, TIMEOUT] for k in ks})
        self.assertEqual(len(f.calls), 10); self.assertEqual(r["exit"], "error")

class Watch(unittest.TestCase):                       # carried over from JS1: new since last run, by id
    def test_first_sight_of_a_board_is_a_baseline(self):
        r, _ = run([K], {K: [gh(1, 2)]})
        self.assertEqual(status(r, K)["new"], []); self.assertTrue(status(r, K)["baseline"])
    def test_new_ids_only(self):
        r, _ = run([K], {K: [gh(1, 2, 3)]}, seen={K: {"1", "2"}})
        self.assertEqual([j["id"] for j in status(r, K)["new"]], ["3"])

if __name__ == "__main__": unittest.main()
