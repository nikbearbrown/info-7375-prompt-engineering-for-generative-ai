"""The loop: exits, budgets, repeat rule, error policy, state (GATE.md sections 1-4, 8). Offline."""
import gzip
import hashlib
import os
import unittest

from jsagent.loop import Loop, empty_state
from tests.helpers import (AS, EMPTY, GARBAGE, GH, NOT_FOUND, SERVER, TIMEOUT, FakeClock, by_board, ok, run)
from tests.wrong_versions import WV1EmptyIsSuccess, WV2SilentSkip

THREE = [("greenhouse", "a"), ("greenhouse", "b"), ("ashby", "c")]


def table(**over):
    t = {GH.format("a"): ok((1, "ML Engineer")), GH.format("b"): ok((2, "Designer")),
         AS.format("c"): ok(("u-3", "Research Engineer"))}
    t.update({k.replace("_", "/"): v for k, v in over.items()})
    return t


def state_after_baseline():
    _, s, _, _ = run(Loop, THREE, table())
    return s


# --- checks shared by the real loop and the wrong versions -----------------------------------
def check_empty_board_is_not_finished(cls):
    """Wrong version 1: an empty board must not end 'finished, 0 new'. Returns problems found."""
    s = state_after_baseline()
    t = table()
    t[GH.format("b")] = EMPTY
    r, new_s, _, _ = run(cls, THREE, t, state=s)
    probs = []
    if r["status"] == "finished":
        probs.append("empty board reported as finished")
    if by_board(r)["greenhouse:b"]["result"] != "suspicious_empty":
        probs.append("empty board not flagged suspicious")
    return probs


def check_failed_board_is_not_finished(cls):
    """Wrong version 2: a 404 or a timeout (after its retry) must not end 'finished'."""
    probs = []
    for bad in (NOT_FOUND, TIMEOUT):
        t = table()
        t[GH.format("b")] = bad
        r, _, _, _ = run(cls, THREE, t)
        if r["status"] == "finished":
            probs.append(f"{bad.status or bad.error} board reported as finished")
    return probs


class TestWrongVersionsAreCaught(unittest.TestCase):
    def test_wv1_empty_board(self):
        self.assertEqual(check_empty_board_is_not_finished(Loop), [])
        self.assertNotEqual(check_empty_board_is_not_finished(WV1EmptyIsSuccess), [])

    def test_wv2_failed_board(self):
        self.assertEqual(check_failed_board_is_not_finished(Loop), [])
        self.assertNotEqual(check_failed_board_is_not_finished(WV2SilentSkip), [])


class TestExits(unittest.TestCase):
    def test_all_ok_first_run_is_finished_baseline_nothing_new(self):
        r, s, fetch, _ = run(Loop, THREE, table())
        self.assertEqual(r["status"], "finished")
        self.assertEqual(r["total_new"], 0)
        self.assertTrue(all(b["baseline"] for b in r["boards"]))
        self.assertEqual(len(fetch.calls), 3)
        self.assertEqual(set(s["boards"]), {"greenhouse:a", "greenhouse:b", "ashby:c"})

    def test_second_run_reports_only_unseen(self):
        s = state_after_baseline()
        t = table()
        t[GH.format("a")] = ok((1, "ML Engineer"), (9, "Data Scientist"))
        r, _, _, _ = run(Loop, THREE, t, state=s)
        self.assertEqual(r["status"], "finished")
        self.assertEqual([n["id"] for n in by_board(r)["greenhouse:a"]["new"]], ["9"])
        self.assertEqual(r["total_new"], 1)

    def test_nothing_is_new_twice(self):
        s = state_after_baseline()
        t = table()
        t[GH.format("a")] = ok((1, "ML Engineer"), (9, "Data Scientist"))
        _, s2, _, _ = run(Loop, THREE, t, state=s)
        r3, _, _, _ = run(Loop, THREE, t, state=s2)
        self.assertEqual(r3["total_new"], 0)

    def test_404_not_retried_board_failed_no_counts_run_incomplete(self):
        t = table()
        t[GH.format("b")] = NOT_FOUND
        r, _, fetch, _ = run(Loop, THREE, t)
        b = by_board(r)["greenhouse:b"]
        self.assertEqual(r["status"], "incomplete")
        self.assertEqual(fetch.calls.count(GH.format("b")), 1)
        self.assertEqual((b["result"], b["count_seen"], b["count_new"]), ("failed", None, None))
        self.assertIn("404", b["reason"])

    def test_timeout_then_success_is_retried_once(self):
        t = table()
        t[GH.format("b")] = [TIMEOUT, ok((2, "Designer"))]
        r, _, fetch, _ = run(Loop, THREE, t)
        self.assertEqual(r["status"], "finished")
        self.assertEqual(fetch.calls.count(GH.format("b")), 2)
        self.assertEqual(by_board(r)["greenhouse:b"]["attempts"], 2)

    def test_timeout_twice_fails_after_one_retry(self):
        t = table()
        t[GH.format("b")] = TIMEOUT
        r, _, fetch, _ = run(Loop, THREE, t)
        self.assertEqual(fetch.calls.count(GH.format("b")), 2)
        self.assertEqual(r["status"], "incomplete")

    def test_5xx_retried_once(self):
        t = table()
        t[GH.format("b")] = SERVER
        r, _, fetch, _ = run(Loop, THREE, t)
        self.assertEqual(fetch.calls.count(GH.format("b")), 2)
        self.assertEqual(by_board(r)["greenhouse:b"]["result"], "failed")

    def test_bad_data_not_retried_and_no_value_invented(self):
        t = table()
        t[GH.format("b")] = GARBAGE
        r, _, fetch, _ = run(Loop, THREE, t)
        b = by_board(r)["greenhouse:b"]
        self.assertEqual(fetch.calls.count(GH.format("b")), 1)
        self.assertEqual((b["result"], b["count_seen"]), ("failed", None))
        self.assertIn("bad data", b["reason"])

    def test_failed_and_empty_boards_keep_their_history(self):
        s = state_after_baseline()
        t = table()
        t[GH.format("a")] = NOT_FOUND
        t[GH.format("b")] = EMPTY
        _, s2, _, _ = run(Loop, THREE, t, state=s)
        self.assertEqual(s2["seen"], s["seen"])
        self.assertEqual(s2["boards"]["greenhouse:a"], s["boards"]["greenhouse:a"])

    def test_raw_saved_before_parse_even_for_bad_data(self):
        t = table()
        t[GH.format("b")] = GARBAGE
        r, _, _, loop = run(Loop, THREE, t)
        resp = [e for e in loop.trace if e["event"] == "response" and e["url"] == GH.format("b")][0]
        with open(os.path.join(loop.out_dir, resp["raw"]), "rb") as f:
            body = gzip.decompress(f.read())
        self.assertEqual(body, GARBAGE.body)
        self.assertEqual(resp["sha256"], hashlib.sha256(GARBAGE.body).hexdigest())


class TestBudgetsAndRepeats(unittest.TestCase):
    def test_request_budget_stops_with_budget_exhausted(self):
        r, _, fetch, _ = run(Loop, THREE, table(), budgets={"max_requests": 2})
        self.assertEqual(r["status"], "budget-exhausted")
        self.assertEqual(len(fetch.calls), 2)
        self.assertEqual(by_board(r)["ashby:c"]["result"], "not_tried")

    def test_retry_counts_against_request_budget(self):
        t = table()
        t[GH.format("a")] = TIMEOUT
        r, _, fetch, _ = run(Loop, THREE, t, budgets={"max_requests": 2})
        self.assertEqual(len(fetch.calls), 2)  # a, a-retry; b never tried
        self.assertEqual(r["status"], "budget-exhausted")
        self.assertEqual(by_board(r)["greenhouse:b"]["result"], "not_tried")

    def test_seconds_budget(self):
        r, _, fetch, _ = run(Loop, THREE, table(), budgets={"max_seconds": 60}, clock=FakeClock(step=25))
        self.assertEqual(r["status"], "budget-exhausted")
        self.assertLess(len(fetch.calls), 3)

    def test_board_budget(self):
        six = [("greenhouse", f"g{i}") for i in range(6)]
        t = {GH.format(f"g{i}"): ok((i, "x")) for i in range(6)}
        r, _, fetch, _ = run(Loop, six, t)
        self.assertEqual(r["status"], "budget-exhausted")
        self.assertEqual(len(fetch.calls), 5)
        self.assertEqual(by_board(r)["greenhouse:g5"]["result"], "not_tried")

    def test_same_board_twice_is_repeat_skipped_no_budget(self):
        r, _, fetch, loop = run(Loop, THREE + [("greenhouse", "a")], table())
        self.assertEqual(len(fetch.calls), 3)
        self.assertEqual(r["requests_used"], 3)
        self.assertEqual(r["boards"][-1]["result"], "repeat_skipped")
        self.assertEqual(r["status"], "finished")
        self.assertTrue(any(e["event"] == "repeat_skipped" for e in loop.trace))

    def test_most_serious_status_wins(self):
        t = table()
        t[GH.format("a")] = NOT_FOUND
        r, _, _, _ = run(Loop, THREE, t, budgets={"max_requests": 2})
        self.assertEqual(r["status"], "budget-exhausted")  # incomplete AND budget -> budget wins

    def test_off_list_url_is_refused_run_is_error_and_writes_no_state(self):
        from jsagent import providers
        orig = providers.PROVIDERS["ashby"]
        providers.PROVIDERS["ashby"] = providers.Provider(lambda b: "https://api.lever.co/v0/postings/x", orig.parse)
        try:
            r, s, fetch, _ = run(Loop, THREE, table())
        finally:
            providers.PROVIDERS["ashby"] = orig
        self.assertEqual(r["status"], "error")
        self.assertIsNone(s)
        self.assertNotIn("https://api.lever.co/v0/postings/x", fetch.calls)


if __name__ == "__main__":
    unittest.main()
