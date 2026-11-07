import json
import os
import unittest
from unittest import mock

from js2 import fetch, loop
from tests.helpers import FakeResponse, SandboxTestCase, greenhouse_body, http_error, lever_body

URLOPEN = "js2.fetch.urllib.request.urlopen"


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def ok(ats, *ids):
    body = greenhouse_body(*ids) if ats == "greenhouse" else lever_body(*ids)
    return {"ats": ats, "status_code": 200, "data": json.loads(body), "raw_path": None,
            "raw_write_decision": True}


class ScriptedFetcher:
    """Returns or raises the next scripted outcome for each token."""

    def __init__(self, ats, script):
        self.ats = ats
        self.script = {k: list(v) for k, v in script.items()}
        self.calls = []

    def __call__(self, token, timeout):
        self.calls.append(token)
        outcome = self.script[token].pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def gh_error(token, status, retriable, kind="http"):
    return fetch.BoardFetchError("greenhouse:" + token, status, retriable, kind, "%s failed" % token)


def boards(*tokens):
    return [{"name": t, "ats": "greenhouse", "token": t} for t in tokens]


class LoopEndToEndTest(SandboxTestCase):
    """The real BOARDS list through the real fetch layer, network mocked."""

    def urlopen(self, req, timeout):
        url = req.full_url
        if "invalid-board-xyz" in url:
            raise http_error(url, 404)
        if "api.lever.co" in url:
            return FakeResponse(lever_body("s1", "s2"))
        return FakeResponse(greenhouse_body(1, 2, 3))

    def test_deliberate_invalid_board_gives_incomplete(self):
        with mock.patch(URLOPEN, side_effect=self.urlopen) as urlopen:
            trace = loop.run()
        self.assertEqual(trace["status"], "incomplete")
        self.assertEqual(trace["boards_checked"], 4)
        self.assertEqual(trace["boards_succeeded"], 3)
        self.assertEqual(trace["boards_failed"], 1)
        self.assertEqual(urlopen.call_count, 4)
        bad = trace["boards"][3]
        self.assertEqual((bad["board"], bad["outcome"], bad["status_code"]), ("invalid-board-xyz", "failed", 404))

        self.assertTrue(trace["trace_path"].startswith(os.path.join(self.output, "traces") + os.sep))
        with open(trace["trace_path"]) as f:
            saved = json.load(f)
        self.assertEqual(saved["status"], "incomplete")
        self.assertEqual(len(os.listdir(os.path.join(self.output, "raw"))), 3)

    def test_budget_constants_match_gate(self):
        self.assertEqual((loop.MAX_BOARDS, loop.MAX_REQUESTS, loop.MAX_SECONDS), (4, 8, 90))
        self.assertEqual([(b["ats"], b["token"]) for b in loop.BOARDS], [
            ("greenhouse", "databricks"), ("greenhouse", "stripe"),
            ("lever", "spotify"), ("greenhouse", "invalid-board-xyz")])


class LoopTest(SandboxTestCase):
    def run_loop(self, script, board_list, clock=None):
        gh = ScriptedFetcher("greenhouse", script)
        trace = loop.run(boards=board_list, fetchers={"greenhouse": gh}, clock=clock or FakeClock(),
                         write_trace=False)
        return trace, gh

    def test_empty_response_board_gives_incomplete(self):
        for empty in ({}, {"jobs": []}, []):
            result = ok("greenhouse", 1)
            result["data"] = empty
            trace, _ = self.run_loop({"a": [ok("greenhouse", 1)], "b": [result]}, boards("a", "b"))
            self.assertEqual(trace["status"], "incomplete", empty)
            self.assertEqual(trace["boards"][1]["kind"], "invalid")
            self.assertEqual(trace["attempts"][-1]["outcome"], "invalid")

    def test_all_boards_ok_gives_finished(self):
        trace, _ = self.run_loop({"a": [ok("greenhouse", 1)], "b": [ok("greenhouse", 2, 3)]}, boards("a", "b"))
        self.assertEqual(trace["status"], "finished")
        self.assertEqual(trace["boards"][1]["posting_ids"], ["2", "3"])

    def test_time_budget_exhausted_before_last_board(self):
        clock = FakeClock()

        def slow(token, timeout):
            clock.now += 50
            return ok("greenhouse", 1)

        trace = loop.run(boards=boards("a", "b", "c"), fetchers={"greenhouse": slow}, clock=clock,
                         write_trace=False)
        self.assertEqual(trace["status"], "budget-exhausted")
        self.assertIn("time limit", trace["stop_reason"])
        self.assertEqual(trace["requests_used"], 2)
        self.assertEqual(trace["boards"][2]["outcome"], "not_checked")

    def test_board_budget_exhausted_before_fifth_board(self):
        tokens = ["a", "b", "c", "d", "e"]
        trace, gh = self.run_loop({t: [ok("greenhouse", 1)] for t in tokens}, boards(*tokens))
        self.assertEqual(trace["status"], "budget-exhausted")
        self.assertEqual(gh.calls, ["a", "b", "c", "d"])
        self.assertEqual(trace["boards"][4]["outcome"], "not_checked")

    def test_repeat_rule_reuses_without_second_fetch(self):
        trace, gh = self.run_loop({"a": [ok("greenhouse", 7)]}, boards("a", "a"))
        self.assertEqual(gh.calls, ["a"])
        self.assertEqual(trace["requests_used"], 1)
        self.assertTrue(trace["boards"][1]["reused"])
        self.assertEqual(trace["boards"][1]["posting_ids"], ["7"])
        self.assertEqual(trace["attempts"][1]["outcome"], "reused")
        self.assertEqual(trace["status"], "finished")

    def test_retry_once_on_retriable_error_and_log_it(self):
        trace, gh = self.run_loop({"a": [gh_error("a", 503, True), ok("greenhouse", 1)]}, boards("a"))
        self.assertEqual(gh.calls, ["a", "a"])
        self.assertEqual(trace["requests_used"], 2)
        first, second = trace["attempts"]
        self.assertEqual((first["attempt"], first["outcome"], first["status_code"]), (1, "failed", 503))
        self.assertEqual((second["attempt"], second["outcome"]), (2, "fetched"))
        self.assertIn("retry", second["reason"])
        self.assertEqual(trace["status"], "finished")

    def test_two_failures_stop_retrying(self):
        script = {"a": [gh_error("a", None, True, "timeout"), gh_error("a", 502, True), ok("greenhouse", 1)],
                  "b": [ok("greenhouse", 2)]}
        trace, gh = self.run_loop(script, boards("a", "b"))
        self.assertEqual(gh.calls, ["a", "a", "b"])
        self.assertEqual(trace["boards"][0]["outcome"], "failed")
        self.assertEqual(trace["boards"][1]["outcome"], "ok")
        self.assertEqual(trace["status"], "incomplete")

    def test_no_retry_on_permanent_error(self):
        trace, gh = self.run_loop({"a": [gh_error("a", 404, False), ok("greenhouse", 1)]}, boards("a"))
        self.assertEqual(gh.calls, ["a"])
        self.assertEqual(trace["status"], "incomplete")

    def test_unexpected_exception_gives_error(self):
        trace, _ = self.run_loop({"a": [RuntimeError("boom")]}, boards("a"))
        self.assertEqual(trace["status"], "error")
        self.assertIn("boom", trace["stop_reason"])

    def test_permanent_failure_not_retried_on_second_appearance(self):
        """REVIEW PACKET: a permanently-failed board appearing twice in the
        BOARDS list should not be fetched a second time. Currently it is."""
        boards = [
            {"ats": "greenhouse", "token": "bad", "name": "Bad Board"},
            {"ats": "greenhouse", "token": "bad", "name": "Bad Board"},
        ]
        fetch_count = {"n": 0}
        def counting_fetch(token, timeout):
            fetch_count["n"] += 1
            raise fetch.BoardFetchError("bad", 404, False, "http", "HTTP 404")
        result = loop.run(
            boards=boards,
            fetchers={"greenhouse": counting_fetch},
            output_dir=self.output,
            write_trace=False,
        )
        self.assertEqual(fetch_count["n"], 1,
            "permanent failure fetched twice — repeat rule does not cache failures")


if __name__ == "__main__":
    unittest.main()
