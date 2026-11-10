"""The loop: exits, budgets, the repeat rule and the error policy (GATE.md sections 1-4)."""

import gzip
import hashlib
import json
import unittest

from agent.tools import FetchError
from tests.helpers import (ANTHROPIC, ASHBY, GH, LEVER, LINEAR, MISSING, PALANTIR, THREE, FakeClock, FakeNet,
                           ashby_body, ashby_job, board, gh_body, gh_job, lever_body, lever_job, make_root, ok,
                           run_loop, status)

NOT_FOUND = status(404, b'{"status":404,"error":"Job not found"}')


def three_ok(gh_ids=(1, 2), lever_ids=("a", "b"), ashby_ids=("x",)):
    return {GH % "anthropic": [ok(gh_body(*[gh_job(i) for i in gh_ids]))],
            LEVER % "palantir": [ok(lever_body(*[lever_job(i) for i in lever_ids]))],
            ASHBY % "linear": [ok(ashby_body(*[ashby_job(i) for i in ashby_ids]))]}


class Exits(unittest.TestCase):
    def test_three_good_boards_finish(self):
        root, clock = make_root(self, THREE), FakeClock()
        record = run_loop(root, FakeNet(clock, three_ok()), clock)
        self.assertEqual(record["exit"], "finished")
        self.assertEqual(record["exit_code"], 0)
        self.assertEqual([b["status"] for b in record["boards"]], ["ok", "ok", "ok"])

    def test_deliberate_failure_makes_the_run_incomplete_not_finished(self):
        root, clock = make_root(self, THREE + [MISSING]), FakeClock()
        script = three_ok()
        script[GH % MISSING["board"]] = [NOT_FOUND]
        record = run_loop(root, FakeNet(clock, script), clock)
        self.assertEqual(record["exit"], "incomplete")
        self.assertEqual(record["exit_code"], 2)
        missing = board(record, "greenhouse/" + MISSING["board"])
        self.assertEqual((missing["status"], missing["reason"], missing["http_status"]),
                         ("failed", "not_found", 404))

    def test_exit_codes(self):
        from agent.loop import EXIT_CODES
        self.assertEqual(EXIT_CODES, {"finished": 0, "error": 1, "incomplete": 2, "budget_exhausted": 3})

    def test_every_run_writes_a_record_a_report_and_a_trace_ending_in_the_exit(self):
        root, clock = make_root(self, THREE), FakeClock()
        record = run_loop(root, FakeNet(clock, three_ok()), clock)
        for name in ("record", "report", "trace"):
            self.assertTrue((root / record["files"][name]).is_file(), name)
        lines = [json.loads(line) for line in (root / record["files"]["trace"]).read_text().splitlines()]
        self.assertEqual(lines[-1]["action"], "exit")
        self.assertEqual(lines[-1]["exit"], "finished")
        fetches = [line for line in lines if line["action"] == "fetch"]
        self.assertEqual(len(fetches), 3)
        for line in fetches:
            self.assertIn("requests_left", line["budget"])
            self.assertIn("seconds_left", line["budget"])


class FailedBoardsInventNothing(unittest.TestCase):
    """W6: a failed board is never 0 postings, and its state is not touched."""

    def test_not_found_has_null_counts_and_no_state(self):
        root, clock = make_root(self, [MISSING]), FakeClock()
        record = run_loop(root, FakeNet(clock, {GH % MISSING["board"]: [NOT_FOUND]}), clock)
        missing = record["boards"][0]
        self.assertIsNone(missing["counts"])
        self.assertNotIn("new_postings", missing)
        self.assertFalse((root / "jobs" / "state" / ("greenhouse-%s.json" % MISSING["board"])).exists())

    def test_failure_after_a_good_run_leaves_state_byte_for_byte_unchanged(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1)))]}), clock, run_id="run-1")
        state = root / "jobs" / "state" / "greenhouse-anthropic.json"
        before = state.read_bytes()
        record = run_loop(root, FakeNet(clock, {GH % "anthropic": [NOT_FOUND]}), clock, run_id="run-2")
        self.assertEqual(record["exit"], "incomplete")
        self.assertIsNone(record["boards"][0]["counts"])
        self.assertEqual(state.read_bytes(), before)

    def test_empty_board_is_suspect_not_no_new_jobs(self):
        """W5: a 200 with zero postings is not proof that there are no jobs."""
        root, clock = make_root(self, [LINEAR]), FakeClock()
        run_loop(root, FakeNet(clock, {ASHBY % "linear": [ok(ashby_body(ashby_job("x")))]}), clock, run_id="run-1")
        state = root / "jobs" / "state" / "ashby-linear.json"
        before = state.read_bytes()
        record = run_loop(root, FakeNet(clock, {ASHBY % "linear": [ok(ashby_body())]}), clock, run_id="run-2")
        linear = record["boards"][0]
        self.assertEqual((linear["status"], linear["reason"]), ("suspect", "empty"))
        self.assertIsNone(linear["counts"])
        self.assertEqual(record["exit"], "incomplete")
        self.assertEqual(state.read_bytes(), before)

    def test_body_that_is_not_a_board_is_bad_shape(self):
        root, clock = make_root(self, [ANTHROPIC, PALANTIR]), FakeClock()
        net = FakeNet(clock, {GH % "anthropic": [ok(b"<html>maintenance</html>")],
                              LEVER % "palantir": [ok(b'{"ok": true}')]})
        record = run_loop(root, net, clock)
        self.assertEqual([(b["status"], b["reason"]) for b in record["boards"]],
                         [("failed", "bad_shape"), ("failed", "bad_shape")])
        self.assertEqual(len(net.calls), 2)

    def test_forbidden_is_not_retried(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        net = FakeNet(clock, {GH % "anthropic": [status(403)]})
        record = run_loop(root, net, clock)
        self.assertEqual((record["boards"][0]["status"], record["boards"][0]["reason"]), ("failed", "forbidden"))
        self.assertEqual(len(net.calls), 1)

    def test_too_large_is_a_failure(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        net = FakeNet(clock, {GH % "anthropic": [FetchError("too_large", "over 20000000 bytes")]})
        record = run_loop(root, net, clock)
        self.assertEqual(record["boards"][0]["reason"], "too_large")
        self.assertEqual(len(net.calls), 1)


class Retries(unittest.TestCase):
    """W8: retry only transient failures, at most twice."""

    def test_not_found_is_requested_exactly_once(self):
        root, clock = make_root(self, [MISSING]), FakeClock()
        net = FakeNet(clock, {GH % MISSING["board"]: [NOT_FOUND, NOT_FOUND, NOT_FOUND]})
        run_loop(root, net, clock)
        self.assertEqual(len(net.calls), 1)
        self.assertEqual(clock.sleeps, [])

    def test_service_unavailable_is_tried_three_times_then_fails(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        net = FakeNet(clock, {GH % "anthropic": [status(503)] * 4})
        record = run_loop(root, net, clock)
        self.assertEqual(len(net.calls), 3)
        self.assertEqual(clock.sleeps, [2, 4])
        self.assertEqual((record["boards"][0]["status"], record["boards"][0]["reason"]), ("failed", "transient"))

    def test_one_transient_failure_then_success(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        net = FakeNet(clock, {GH % "anthropic": [FetchError("timeout", "timed out"), ok(gh_body(gh_job(1)))]})
        record = run_loop(root, net, clock)
        self.assertEqual(record["boards"][0]["status"], "ok")
        self.assertEqual(record["boards"][0]["requests"], 2)
        self.assertEqual(record["exit"], "finished")

    def test_long_retry_after_is_not_retried(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        net = FakeNet(clock, {GH % "anthropic": [status(429, headers={"retry-after": "60"})]})
        record = run_loop(root, net, clock)
        self.assertEqual(len(net.calls), 1)
        self.assertEqual(record["boards"][0]["reason"], "transient")


class Budgets(unittest.TestCase):
    def test_request_budget_runs_out_before_every_board(self):
        """W7: a stop that is not a success says so."""
        root, clock = make_root(self, THREE), FakeClock()
        net = FakeNet(clock, three_ok())
        record = run_loop(root, net, clock, limits={"requests": 2})
        self.assertEqual(record["exit"], "budget_exhausted")
        self.assertEqual(record["exit_code"], 3)
        self.assertEqual(record["exit_reason"], "requests")
        self.assertEqual(record["not_attempted"], ["ashby/linear"])
        self.assertEqual(len(net.calls), 2)

    def test_seconds_budget_runs_out_before_a_board(self):
        root, clock = make_root(self, THREE), FakeClock()
        script = three_ok()
        script[GH % "anthropic"] = [(130, ok(gh_body(gh_job(1))))]
        net = FakeNet(clock, script)
        record = run_loop(root, net, clock)
        self.assertEqual((record["exit"], record["exit_reason"]), ("budget_exhausted", "seconds"))
        self.assertEqual(record["not_attempted"], ["lever/palantir", "ashby/linear"])

    def test_board_budget(self):
        root, clock = make_root(self, THREE), FakeClock()
        record = run_loop(root, FakeNet(clock, three_ok()), clock, limits={"boards": 1})
        self.assertEqual((record["exit"], record["exit_reason"]), ("budget_exhausted", "boards"))
        self.assertEqual(record["not_attempted"], ["lever/palantir", "ashby/linear"])

    def test_a_request_never_gets_more_seconds_than_are_left(self):
        """W12: the budget is checked before every request, not only between boards."""
        root, clock = make_root(self, [ANTHROPIC, PALANTIR]), FakeClock()
        script = three_ok()
        script[GH % "anthropic"] = [(110, ok(gh_body(gh_job(1))))]
        net = FakeNet(clock, script)
        run_loop(root, net, clock)
        self.assertEqual(net.calls[0]["timeout"], 30)
        self.assertLessEqual(net.calls[1]["timeout"], 10)

    def test_retry_that_does_not_fit_the_request_budget_is_not_made(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        net = FakeNet(clock, {GH % "anthropic": [status(503)] * 3})
        record = run_loop(root, net, clock, limits={"requests": 1})
        self.assertEqual(len(net.calls), 1)
        self.assertEqual(record["boards"][0]["reason"], "transient")

    def test_raising_a_budget_is_refused_before_the_run_starts(self):
        """W10: flags may only lower a budget."""
        from agent.loop import run
        root, clock = make_root(self, THREE), FakeClock()
        net = FakeNet(clock, three_ok())
        with self.assertRaises(ValueError):
            run(root, transport=net, clock=clock, sleep=clock.sleep, limits={"requests": 9})
        self.assertEqual(net.calls, [])
        self.assertEqual(list((root / "jobs").iterdir()), [])

    def test_the_byte_budget_is_passed_to_the_network(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        net = FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1)))]})
        run_loop(root, net, clock)
        self.assertEqual(net.calls[0]["max_bytes"], 20000000)


class RepeatRule(unittest.TestCase):
    def test_same_board_twice_is_watched_once(self):
        """W11: Greenhouse/Anthropic and greenhouse/anthropic are the same board."""
        twice = [ANTHROPIC, {"system": "Greenhouse", "board": "Anthropic", "company": "Anthropic"}]
        root, clock = make_root(self, twice), FakeClock()
        net = FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1)))]})
        record = run_loop(root, net, clock)
        self.assertEqual(len(net.calls), 1)
        self.assertEqual([b["status"] for b in record["boards"]], ["ok", "skipped_repeat"])
        self.assertEqual(record["exit"], "finished")

    def test_three_refused_repeats_stop_the_loop(self):
        from agent.loop import Loop, RepeatLimit
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        net = FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1)))]})
        loop = Loop(root, transport=net, clock=clock, sleep=clock.sleep, run_id="r")
        loop.request("greenhouse/anthropic", GH % "anthropic")
        loop.request("greenhouse/anthropic", GH % "anthropic")
        loop.request("greenhouse/anthropic", GH % "ANTHROPIC".lower())
        with self.assertRaises(RepeatLimit):
            loop.request("greenhouse/anthropic", "https://BOARDS-API.greenhouse.io/v1/boards/anthropic/jobs?content=true")
        self.assertEqual(len(net.calls), 1)


class Redirects(unittest.TestCase):
    def test_redirect_off_the_list_is_not_followed(self):
        """W9."""
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        net = FakeNet(clock, {GH % "anthropic": [status(302, headers={"location": "https://evil.example/jobs"})]})
        record = run_loop(root, net, clock)
        self.assertEqual(net.urls(), [GH % "anthropic"])
        self.assertEqual((record["boards"][0]["status"], record["boards"][0]["reason"]),
                         ("failed", "refused_redirect"))

    def test_redirect_to_an_allowed_board_is_followed_and_counted(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        moved = "https://boards-api.greenhouse.io/v1/boards/anthropic-new/jobs?content=true"
        net = FakeNet(clock, {GH % "anthropic": [status(301, headers={"location": moved})],
                              moved: [ok(gh_body(gh_job(1)))]})
        record = run_loop(root, net, clock)
        self.assertEqual(net.urls(), [GH % "anthropic", moved])
        self.assertEqual(record["boards"][0]["status"], "ok")
        self.assertEqual(record["budget"]["used"]["requests"], 2)


class Errors(unittest.TestCase):
    def test_a_real_looking_resume_stops_the_run_before_any_request(self):
        import tempfile
        from pathlib import Path
        persona = json.loads(Path(__file__).resolve().parent.parent.joinpath(
            "persona", "aarav-patel.resume.example.json").read_text(encoding="utf-8"))
        persona["personal"]["email"] = "someone@realmail.invalid"
        fake = Path(tempfile.mkdtemp()) / "p.json"
        self.addCleanup(fake.unlink)
        fake.write_text(json.dumps(persona), encoding="utf-8")
        root, clock = make_root(self, THREE, persona=fake), FakeClock()
        net = FakeNet(clock, three_ok())
        record = run_loop(root, net, clock)
        self.assertEqual(record["exit"], "error")
        self.assertEqual(net.calls, [])

    def test_unreadable_state_file_is_an_error_not_a_fresh_start(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        (root / "jobs" / "state").mkdir()
        (root / "jobs" / "state" / "greenhouse-anthropic.json").write_text("{not json", encoding="utf-8")
        record = run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1)))]}), clock)
        self.assertEqual(record["exit"], "error")
        self.assertEqual(record["exit_code"], 1)

    def test_board_name_the_policy_refuses_is_an_error(self):
        root, clock = make_root(self, [{"system": "greenhouse", "board": "../etc", "company": "x"}]), FakeClock()
        net = FakeNet(clock, {})
        record = run_loop(root, net, clock)
        self.assertEqual((record["exit"], record["exit_reason"]), ("error", "policy_refused"))
        self.assertEqual(net.calls, [])

    def test_unknown_system_is_an_error(self):
        root, clock = make_root(self, [{"system": "workday", "board": "x", "company": "x"}]), FakeClock()
        record = run_loop(root, FakeNet(clock, {}), clock)
        self.assertEqual(record["exit"], "error")


class Evidence(unittest.TestCase):
    def test_raw_responses_are_saved_byte_for_byte_including_failures(self):
        root, clock = make_root(self, [ANTHROPIC, MISSING]), FakeClock()
        body = gh_body(gh_job(1))
        net = FakeNet(clock, {GH % "anthropic": [ok(body)], GH % MISSING["board"]: [NOT_FOUND]})
        record = run_loop(root, net, clock)
        for b, expected in zip(record["boards"], (body, NOT_FOUND.body)):
            attempt = b["attempts"][0]
            saved = gzip.decompress((root / attempt["raw_file"]).read_bytes())
            self.assertEqual(saved, expected)
            self.assertEqual(attempt["raw_sha256"], hashlib.sha256(expected).hexdigest())

    def test_new_ids_are_reported_with_the_js1_rule_verdict(self):
        root, clock = make_root(self, [ANTHROPIC]), FakeClock()
        run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(gh_body(gh_job(1)))]}), clock, run_id="run-1")
        good = gh_job(2, body="2+ years. Python and AWS.")
        second = gh_body(gh_job(1, title="Renamed Software Engineer"), good)
        record = run_loop(root, FakeNet(clock, {GH % "anthropic": [ok(second)]}), clock, run_id="run-2")
        anthropic = record["boards"][0]
        self.assertEqual(anthropic["run_kind"], "watch")
        self.assertEqual([p["job_id"] for p in anthropic["new_postings"]], ["2"])
        self.assertEqual(anthropic["new_postings"][0]["rule_verdict"]["verdict"], "MATCH")
        self.assertEqual(anthropic["counts"], {"postings": 2, "new": 1, "gone": 0, "duplicate_ids": 0})

    def test_first_run_of_a_board_is_a_baseline(self):
        root, clock = make_root(self, [PALANTIR]), FakeClock()
        record = run_loop(root, FakeNet(clock, {LEVER % "palantir": [ok(lever_body(lever_job("a")))]}), clock)
        self.assertEqual(record["boards"][0]["run_kind"], "baseline")
        self.assertEqual(record["boards"][0]["new_postings"], [])
        state = json.loads((root / "jobs" / "state" / "lever-palantir.json").read_text())
        self.assertEqual(state["seen_ids"], ["a"])


if __name__ == "__main__":
    unittest.main()
