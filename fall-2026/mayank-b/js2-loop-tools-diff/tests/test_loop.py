"""Loop tests: exits, budgets, repeat rule, error policy, W5/W6/W7/W9. Scripted fetch, no network."""
import json
import unittest

from helpers import BUDGET, PERSONA, RUN_ID, TIMEOUT, Clock, ScriptedFetch, ashby, gh, plan, temp_root
from jsa import loop


def go(p, script, seen=None, budget=None, clock=None):
    root = temp_root()
    f = ScriptedFetch(script)
    s = loop.run(str(root), RUN_ID, p, budget or BUDGET, PERSONA, seen or {}, fetch=f, clock=clock or Clock())
    return s, f, root


def by_board(s):
    return {r["board"]: r for r in s["results"]}


class Exits(unittest.TestCase):
    def test_finished_all_ok(self):
        s, _, _ = go(plan(("greenhouse", "anthropic"), ("ashby", "notion")), {"anthropic": [(200, gh(1, 2))], "notion": [(200, ashby(1))]})
        self.assertEqual(s["exit"], "finished")
        self.assertEqual(s["needs_mayank"], [])

    def test_one_board_fails_run_still_finished_and_flagged(self):  # decision 1a
        s, _, _ = go(plan(("greenhouse", "anthropic"), ("greenhouse", "nope")), {"anthropic": [(200, gh(1))], "nope": [(404, b'{"error":"not found"}')]})
        self.assertEqual(s["exit"], "finished")
        self.assertEqual(s["needs_mayank"], ["greenhouse/nope"])

    def test_W5_failure_is_error_not_zero(self):
        s, _, _ = go(plan(("greenhouse", "nope"),), {"nope": [(404, b"{}")]})
        r = by_board(s)["greenhouse/nope"]
        self.assertEqual(r["result"], "error")
        self.assertIsNone(r["postings"])
        self.assertNotIn("new", r)

    def test_W6_budget_exhausted_is_not_finished(self):
        b = dict(BUDGET, max_requests=2)
        s, f, _ = go(plan(("greenhouse", "a"), ("greenhouse", "b"), ("greenhouse", "c")), {"/a/": [(200, gh(1))], "/b/": [(200, gh(2))], "/c/": [(200, gh(3))]}, budget=b)
        self.assertEqual(s["exit"], "budget-exhausted")
        self.assertEqual(s["budget_hit"], "max_requests")
        self.assertEqual(len(f.calls), 2)  # the 3rd request is never sent
        self.assertEqual(s["never_attempted"], ["greenhouse/c"])

    def test_board_cap(self):
        b = dict(BUDGET, max_boards=1)
        s, f, _ = go(plan(("greenhouse", "a"), ("ashby", "b")), {"/a/": [(200, gh(1))], "/b": [(200, ashby(1))]}, budget=b)
        self.assertEqual((s["exit"], s["budget_hit"], len(f.calls)), ("budget-exhausted", "max_boards", 1))

    def test_seconds_cap_checked_before_request(self):
        b = dict(BUDGET, max_seconds=5)
        s, f, _ = go(plan(("greenhouse", "a"), ("greenhouse", "b")), {"/a/": [(200, gh(1))], "/b/": [(200, gh(2))]}, budget=b, clock=Clock(step=3))
        self.assertEqual((s["exit"], s["budget_hit"]), ("budget-exhausted", "max_seconds"))
        self.assertEqual(len(f.calls), 1)


class Repeat(unittest.TestCase):
    def test_W7_same_board_other_case_and_encoding_is_skipped(self):
        s, f, _ = go(plan(("ashby", "notion"), ("ashby", "Notion"), ("ashby", "Jasper%20AI"), ("ashby", "jasper ai")),
                     {"notion": [(200, ashby(1))], "Jasper%20AI": [(200, ashby(2))]})
        self.assertEqual(len(f.calls), 2)
        self.assertEqual([k["same_as"] for k in s["skipped"]], ["ashby/notion", "ashby/jasper ai"])
        self.assertEqual(s["exit"], "incomplete")
        self.assertEqual(s["requests"], 2)


class ErrorPolicy(unittest.TestCase):
    def test_404_never_retried(self):
        _, f, _ = go(plan(("greenhouse", "nope"),), {"nope": [(404, b"{}")]})
        self.assertEqual(len(f.calls), 1)

    def test_malformed_never_retried(self):
        s, f, _ = go(plan(("greenhouse", "x"),), {"/x/": [(200, b"<html>not json</html>")]})
        self.assertEqual((len(f.calls), by_board(s)["greenhouse/x"]["error_kind"]), (1, "malformed"))

    def test_5xx_retried_once_then_ok(self):
        s, f, _ = go(plan(("greenhouse", "x"),), {"/x/": [(503, b""), (200, gh(1))]})
        self.assertEqual((len(f.calls), by_board(s)["greenhouse/x"]["result"]), (2, "ok"))

    def test_timeout_retried_once_then_error(self):
        s, f, _ = go(plan(("greenhouse", "x"),), {"/x/": [TIMEOUT("slow"), TIMEOUT("slow")]})
        self.assertEqual((len(f.calls), by_board(s)["greenhouse/x"]["error_kind"]), (2, "timeout"))

    def test_retry_counts_against_request_budget(self):
        b = dict(BUDGET, max_requests=1)
        s, f, _ = go(plan(("greenhouse", "x"),), {"/x/": [(503, b""), (200, gh(1))]}, budget=b)
        self.assertEqual(len(f.calls), 1)
        self.assertEqual(by_board(s)["greenhouse/x"]["result"], "error")


class State(unittest.TestCase):
    def test_W9_failed_board_keeps_its_seen_ids(self):
        seen = {"greenhouse/x": ["1", "2"], "greenhouse/y": ["9"]}
        s, _, root = go(plan(("greenhouse", "x"), ("greenhouse", "y")), {"/x/": [(404, b"{}")], "/y/": [(200, gh(9, 10))]}, seen=seen)
        proposed = json.loads((root / "runs" / RUN_ID / "proposed-seen-ids.json").read_text())
        self.assertEqual(proposed["greenhouse/x"], ["1", "2"])
        self.assertEqual(proposed["greenhouse/y"], ["10", "9"])

    def test_baseline_reports_nothing_new_then_new_ids_are_new(self):
        s, _, _ = go(plan(("greenhouse", "x"),), {"/x/": [(200, gh(1, 2))]})
        self.assertTrue(by_board(s)["greenhouse/x"]["baseline"])
        self.assertEqual(by_board(s)["greenhouse/x"]["new"], [])
        s2, _, _ = go(plan(("greenhouse", "x"),), {"/x/": [(200, gh(1, 2, 3))]}, seen={"greenhouse/x": ["1", "2"]})
        self.assertEqual([j["id"] for j in by_board(s2)["greenhouse/x"]["new"]], ["3"])

    def test_raw_response_saved_byte_for_byte_with_hash(self):
        body = gh(1)
        s, _, root = go(plan(("greenhouse", "x"),), {"/x/": [(200, body)]})
        obs = by_board(s)["greenhouse/x"]["attempts"][0]
        self.assertEqual((root / "runs" / RUN_ID / obs["raw"]).read_bytes(), body)
        import hashlib
        self.assertEqual(obs["sha256"], hashlib.sha256(body).hexdigest())


class RunErrors(unittest.TestCase):
    def test_invalid_plan_entry_stops_run(self):
        with self.assertRaises(loop.RunError):
            go([{"ats": "lever", "slug": "x"}], {})

    def test_real_persona_refused(self):
        p = json.loads(json.dumps(PERSONA))
        p["personal"]["email"] = "someone@gmail.com"
        with self.assertRaises(loop.RunError):
            loop.run(str(temp_root()), RUN_ID, plan(("greenhouse", "x")), BUDGET, p, {}, fetch=ScriptedFetch({}))


if __name__ == "__main__":
    unittest.main()
