"""Loop tests for GATE.md sections 1-4. Offline: every request goes to a
FakeTransport, and every response body is CONSTRUCTED.
"""

import json
import tempfile
import unittest
from pathlib import Path

import js2_harness as h
from agent import loop, policy, transport


class LoopCase(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def root(self, **kwargs):
        return h.make_root(self.tmp / "proj", **kwargs)

    def only_trace_written(self, root, run_id="RUN1"):
        files = sorted(str(p.relative_to(root / "out"))
                       for p in (root / "out").rglob("*") if p.is_file())
        self.assertEqual(files, [f"runs/{run_id}/trace.jsonl"])


class ExitTests(LoopCase):

    def four_ok(self):
        script = h.default_script()
        script[h.NO_SUCH] = [h.ok(h.gh_body([99]))]
        return script

    def test_finished_exit_0_with_own_report_note(self):
        root = self.root()
        fake = h.FakeTransport(self.four_ok())
        exit_name, _ = h.run(root, fake)
        self.assertEqual(exit_name, loop.FINISHED)
        s = h.summary(root)
        self.assertEqual(s["exit_code"], 0)
        self.assertEqual(s["boards_succeeded"],
                         [b["name"] for b in h.BOARDS])
        self.assertIn("not an independent check", h.report(root))
        self.assertEqual(len(fake.calls), 4)

    def test_second_run_reports_only_new_ids(self):
        root = self.root()
        h.run(root, h.FakeTransport(self.four_ok()), run_id="RUN1")
        script = self.four_ok()
        script[h.SCALE] = [h.ok(h.gh_body([1, 2, 3, 4]))]
        script[h.OPENAI] = [h.ok(h.ashby_body(["a-1", "a-2", "a-3"]))]
        exit_name, _ = h.run(root, h.FakeTransport(script), run_id="RUN2")
        self.assertEqual(exit_name, loop.FINISHED)
        s = h.summary(root, "RUN2")
        self.assertEqual(h.board(s, "scaleai")["new_ids"], ["4"])
        self.assertEqual(h.board(s, "openai")["new_ids"], ["a-3"])
        self.assertEqual(h.board(s, "databricks")["new"], 0)
        first = h.summary(root, "RUN1")
        self.assertTrue(h.board(first, "scaleai")["baseline"])
        self.assertEqual(h.board(first, "scaleai")["new"], 0)

    def test_incomplete_exit_1_when_a_board_fails(self):
        root = self.root()
        exit_name, _ = h.run(root, h.FakeTransport(h.default_script()))
        self.assertEqual(exit_name, loop.INCOMPLETE)
        s = h.summary(root)
        self.assertEqual(s["exit_code"], 1)
        self.assertEqual(s["boards_failed"], ["rithika-js2-no-such-board"])
        self.assertEqual(s["boards_succeeded"],
                         ["scaleai", "databricks", "openai"])
        failed = h.board(s, "rithika-js2-no-such-board")
        self.assertEqual(failed["http_status"], 404)
        self.assertEqual(failed["reason"], "http_404")
        report = h.report(root)
        self.assertTrue(report.split("## Needs your attention")[0]
                        .count("\n") <= 3, "attention section must be first")
        attention = report.split("## Needs your attention")[1] \
            .split("## Result")[0]
        self.assertIn("rithika-js2-no-such-board", attention)
        self.assertIn("unknown", attention)

    def test_budget_exhausted_exit_2(self):
        root = self.root(budgets=dict(h.BUDGETS, max_requests=2))
        exit_name, _ = h.run(root, h.FakeTransport(h.default_script()))
        self.assertEqual(exit_name, loop.BUDGET_EXHAUSTED)
        s = h.summary(root)
        self.assertEqual(s["exit_code"], 2)
        self.assertEqual(s["budget_limit_hit"], "max_requests")
        self.assertEqual(s["boards_succeeded"], ["scaleai", "databricks"])
        self.assertEqual(s["boards_not_tried"],
                         ["openai", "rithika-js2-no-such-board"])
        self.assertIn("max_requests", h.report(root))

    def test_error_exit_3_invalid_resume_writes_only_trace(self):
        root = self.root(resume_text=json.dumps({
            "personal": {"name": "X", "email": "x@gmail.com",
                         "phone": "555"}, "skills": {"languages": []}}))
        fake = h.FakeTransport(h.default_script())
        exit_name, runner = h.run(root, fake)
        self.assertEqual(exit_name, loop.ERROR)
        self.assertIn("resume_invalid", runner.error)
        self.assertEqual(fake.calls, [])
        self.only_trace_written(root)
        end = h.trace(root)[-1]
        self.assertEqual((end["kind"], end["exit"], end["exit_code"]),
                         ("run_end", "error", 3))

    def test_error_unreadable_state(self):
        root = self.root()
        path = h.state_path(root, "scaleai")
        path.parent.mkdir(parents=True)
        path.write_text("{not json")
        fake = h.FakeTransport(h.default_script())
        exit_name, runner = h.run(root, fake)
        self.assertEqual(exit_name, loop.ERROR)
        self.assertIn("state_unreadable", runner.error)
        self.assertEqual(fake.calls, [])
        self.assertEqual(path.read_text(), "{not json")

    def test_error_same_board_twice_in_config(self):
        root = self.root(boards=[h.BOARDS[0], h.BOARDS[1], dict(h.BOARDS[0])])
        fake = h.FakeTransport(h.default_script())
        exit_name, runner = h.run(root, fake)
        self.assertEqual(exit_name, loop.ERROR)
        self.assertIn("config_duplicate_board", runner.error)
        self.assertEqual(fake.calls, [])

    def test_error_same_url_under_two_names(self):
        root = self.root(boards=[h.BOARDS[0], dict(h.BOARDS[0], name="x")])
        exit_name, runner = h.run(root, h.FakeTransport(h.default_script()))
        self.assertEqual(exit_name, loop.ERROR)
        self.assertIn("config_duplicate_board", runner.error)

    def test_error_off_allowlist_board_in_config(self):
        root = self.root(boards=[{"name": "evil", "ats": "greenhouse",
                                  "url": "https://example.com/jobs"}])
        fake = h.FakeTransport({})
        exit_name, runner = h.run(root, fake)
        self.assertEqual(exit_name, loop.ERROR)
        self.assertIn("host_not_allowed", runner.error)
        self.assertEqual(fake.calls, [])

    def test_error_redirect_off_allowlist_stops_run(self):
        root = self.root()
        h.write_state(root, "scaleai", [1])
        before = h.state_path(root, "scaleai").read_bytes()
        script = h.default_script()
        script[h.DATABRICKS] = [h.status(302, b"",
                                         {"location": "https://example.com/"})]
        fake = h.FakeTransport(script)
        exit_name, runner = h.run(root, fake)
        self.assertEqual(exit_name, loop.ERROR)
        self.assertIn("redirect_off_allowlist", runner.error)
        self.assertEqual(len(fake.calls), 2)  # never followed, never retried
        self.assertEqual(h.state_path(root, "scaleai").read_bytes(), before)
        self.assertFalse((root / "out" / "raw").exists())

    def test_exit_codes_match_gate(self):
        self.assertEqual(loop.EXIT_CODES, {"finished": 0, "incomplete": 1,
                                           "budget_exhausted": 2, "error": 3})


class BudgetTests(LoopCase):

    def test_max_boards_fifth_board_refused_at_startup(self):
        fifth = {"name": "extra", "ats": "greenhouse",
                 "url": "https://boards-api.greenhouse.io/v1/boards/extra/"
                        "jobs"}
        root = self.root(boards=h.BOARDS + [fifth])
        fake = h.FakeTransport(h.default_script())
        exit_name, runner = h.run(root, fake)
        self.assertEqual(exit_name, loop.ERROR)
        self.assertIn("config_too_many_boards", runner.error)
        self.assertEqual(fake.calls, [])
        self.only_trace_written(root)

    def test_max_requests_checked_before_the_request(self):
        root = self.root(budgets=dict(h.BUDGETS, max_requests=3))
        fake = h.FakeTransport(h.default_script())
        exit_name, _ = h.run(root, fake)
        self.assertEqual(exit_name, loop.BUDGET_EXHAUSTED)
        self.assertEqual(len(fake.calls), 3)  # the 4th is never sent
        s = h.summary(root)
        self.assertEqual(s["usage"]["requests"], 3)
        self.assertEqual(s["boards_not_tried"], ["rithika-js2-no-such-board"])
        stop = [t for t in h.trace(root) if t["kind"] == "decision"
                and t.get("reason") == "budget_exhausted"]
        self.assertEqual(stop[0]["limit"], "max_requests")
        self.assertEqual(stop[0]["requests_sent"], 3)

    def test_max_requests_blocks_a_retry(self):
        root = self.root(boards=h.BOARDS[:1],
                         budgets=dict(h.BUDGETS, max_requests=1))
        script = {h.SCALE: [transport.TransportTimeout("t"),
                            h.ok(h.gh_body([1]))]}
        fake = h.FakeTransport(script)
        exit_name, _ = h.run(root, fake)
        self.assertEqual(exit_name, loop.BUDGET_EXHAUSTED)
        self.assertEqual(len(fake.calls), 1)
        b = h.board(h.summary(root), "scaleai")
        self.assertEqual(b["status"], "failed")
        self.assertIsNone(b["new"])
        self.assertFalse(h.state_path(root, "scaleai").exists())

    def test_max_run_seconds_checked_before_the_request(self):
        root = self.root()
        clock = h.FakeClock()
        script = h.default_script()
        script[h.NO_SUCH] = [h.ok(h.gh_body([5]))]
        fake = h.FakeTransport(script, clock=clock, seconds_per_call=30)
        exit_name, _ = h.run(root, fake, clock=clock)
        # t=0, 30, 60 each leave room for a 20 s request inside 90 s;
        # at t=90 a 4th request could not finish in time, so it is not sent.
        self.assertEqual(exit_name, loop.BUDGET_EXHAUSTED)
        self.assertEqual(len(fake.calls), 3)
        s = h.summary(root)
        self.assertEqual(s["budget_limit_hit"], "max_run_seconds")
        self.assertEqual(s["boards_not_tried"], ["rithika-js2-no-such-board"])

    def test_max_request_seconds_is_the_transport_timeout(self):
        root = self.root()
        fake = h.FakeTransport(h.default_script())
        h.run(root, fake)
        self.assertEqual({c["timeout"] for c in fake.calls}, {20})

    def test_no_claude_calls(self):
        root = self.root()
        h.run(root, h.FakeTransport(h.default_script()))
        s = h.summary(root)
        self.assertEqual(s["usage"]["claude_calls"], 0)
        self.assertEqual(s["budgets"]["max_claude_calls"], 0)

    def test_requests_are_get_without_credentials(self):
        root = self.root()
        fake = h.FakeTransport(h.default_script())
        h.run(root, fake)
        for call in fake.calls:
            self.assertEqual(call["method"], "GET")
            self.assertFalse({k.lower() for k in call["headers"]}
                             & {"authorization", "cookie"})


class ErrorPolicyTests(LoopCase):

    def one_board(self, items, name=0):
        board = h.BOARDS[name]
        root = self.root(boards=[board])
        fake = h.FakeTransport({board["url"]: items})
        clock = h.FakeClock()
        exit_name, runner = h.run(root, fake, clock=clock)
        return root, fake, clock, exit_name

    def test_404_not_retried(self):
        root, fake, clock, exit_name = self.one_board(
            [h.status(404, h.NOT_FOUND)], name=3)
        self.assertEqual(exit_name, loop.INCOMPLETE)
        self.assertEqual(fake.count(h.NO_SUCH), 1)
        self.assertEqual(clock.sleeps, [])
        raw = root / "out" / "raw" / "RUN1_rithika-js2-no-such-board_a1.json"
        self.assertEqual(raw.read_bytes(), h.NOT_FOUND)

    def test_other_4xx_not_retried(self):
        _, fake, _, exit_name = self.one_board([h.status(403, b"no")])
        self.assertEqual(exit_name, loop.INCOMPLETE)
        self.assertEqual(len(fake.calls), 1)

    def test_429_not_retried_and_rate_limited(self):
        root, fake, _, exit_name = self.one_board([h.status(429, b"slow")])
        self.assertEqual(exit_name, loop.INCOMPLETE)
        self.assertEqual(len(fake.calls), 1)
        self.assertEqual(h.board(h.summary(root), "scaleai")["reason"],
                         "rate_limited")
        self.assertIn("rate limited", h.report(root))

    def test_timeout_retried_once_after_2_seconds(self):
        root, fake, clock, exit_name = self.one_board(
            [transport.TransportTimeout("t"), h.ok(h.gh_body([1, 2]))])
        self.assertEqual(exit_name, loop.FINISHED)
        self.assertEqual(len(fake.calls), 2)
        self.assertEqual(clock.sleeps, [2])
        actions = [t["attempt"] for t in h.trace(root)
                   if t["kind"] == "action"]
        self.assertEqual(actions, ["attempt 1 of 2", "attempt 2 of 2"])
        self.assertFalse([t for t in h.trace(root)
                          if t["kind"] == "repeat_blocked"])

    def test_connection_error_retried_once(self):
        _, fake, _, exit_name = self.one_board(
            [transport.TransportConnectionError("c"), h.ok(h.gh_body([1]))])
        self.assertEqual(exit_name, loop.FINISHED)
        self.assertEqual(len(fake.calls), 2)

    def test_5xx_twice_fails_after_two_attempts(self):
        root, fake, clock, exit_name = self.one_board(
            [h.status(503, b"busy"), h.status(502, b"bad")])
        self.assertEqual(exit_name, loop.INCOMPLETE)
        self.assertEqual(len(fake.calls), 2)
        self.assertEqual(clock.sleeps, [2])
        b = h.board(h.summary(root), "scaleai")
        self.assertEqual((b["reason"], b["attempts"]), ("http_502", 2))
        self.assertEqual(len(b["raw_files"]), 2)

    def test_malformed_json_not_retried(self):
        root, fake, _, exit_name = self.one_board([h.ok(b"<html>oops")])
        self.assertEqual(exit_name, loop.INCOMPLETE)
        self.assertEqual(len(fake.calls), 1)
        b = h.board(h.summary(root), "scaleai")
        self.assertEqual(b["reason"], "malformed_response")
        self.assertEqual((root / b["raw_files"][0]).read_bytes(),
                         b"<html>oops")

    def test_missing_jobs_field_is_malformed(self):
        root, fake, _, exit_name = self.one_board(
            [h.ok(b'{"meta": {"total": 0}}')])
        self.assertEqual(exit_name, loop.INCOMPLETE)
        self.assertEqual(len(fake.calls), 1)
        self.assertEqual(h.board(h.summary(root), "scaleai")["reason"],
                         "malformed_response")

    def test_failed_board_new_is_unknown_never_zero(self):
        root, _, _, _ = self.one_board([h.status(404, h.NOT_FOUND)], name=3)
        b = h.board(h.summary(root), "rithika-js2-no-such-board")
        self.assertIsNone(b["new"])
        self.assertIsNone(b["new_ids"])
        self.assertIsNone(b["postings_seen"])
        self.assertIn("| unknown |", h.report(root))

    def test_failed_board_state_file_untouched(self):
        root = self.root()
        path = h.write_state(root, "rithika-js2-no-such-board", [7, 8])
        before = path.read_bytes()
        h.run(root, h.FakeTransport(h.default_script()))
        self.assertEqual(path.read_bytes(), before)
        b = h.board(h.summary(root), "rithika-js2-no-such-board")
        self.assertFalse(b["state_updated"])
        # ...and a succeeded board's state was updated.
        self.assertTrue(h.state_path(root, "scaleai").exists())

    def test_failed_board_without_state_creates_none(self):
        root = self.root()
        h.run(root, h.FakeTransport(h.default_script()))
        self.assertFalse(h.state_path(root,
                                      "rithika-js2-no-such-board").exists())

    def test_raw_saved_unchanged_with_run_board_attempt_name(self):
        root = self.root()
        body = h.gh_body([1, 2, 3])
        script = h.default_script()
        script[h.SCALE] = [h.ok(body)]
        h.run(root, h.FakeTransport(script), run_id="R9")
        self.assertEqual(
            (root / "out" / "raw" / "R9_scaleai_a1.json").read_bytes(), body)

    def test_existing_run_dir_is_never_overwritten(self):
        root = self.root()
        h.run(root, h.FakeTransport(h.default_script()), run_id="SAME")
        trace_before = (root / "out/runs/SAME/trace.jsonl").read_bytes()
        exit_name, runner = h.run(root, h.FakeTransport(h.default_script()),
                                  run_id="SAME")
        self.assertEqual(exit_name, loop.ERROR)
        self.assertIn("would_overwrite", runner.error)
        self.assertEqual((root / "out/runs/SAME/trace.jsonl").read_bytes(),
                         trace_before)


class RepeatRuleTests(LoopCase):

    def test_retry_is_allowed_but_traced_as_attempt_2_of_2(self):
        root = self.root(boards=[h.BOARDS[0]])
        fake = h.FakeTransport({h.SCALE: [h.status(500, b"x"),
                                          h.ok(h.gh_body([1]))]})
        exit_name, _ = h.run(root, fake)
        self.assertEqual(exit_name, loop.FINISHED)
        decisions = [t for t in h.trace(root) if t["kind"] == "decision"
                     and t.get("do") == "fetch"]
        self.assertEqual([d["attempt"] for d in decisions],
                         ["attempt 1 of 2", "attempt 2 of 2"])

    def test_accidental_repeat_is_blocked_not_sent(self):
        # A redirect back to the same URL would repeat the same action.
        root = self.root(boards=[h.BOARDS[0]])
        fake = h.FakeTransport({h.SCALE: [h.status(
            301, b"", {"location": h.SCALE})]})
        exit_name, _ = h.run(root, fake)
        self.assertEqual(exit_name, loop.INCOMPLETE)
        self.assertEqual(len(fake.calls), 1)
        b = h.board(h.summary(root), "scaleai")
        self.assertEqual(b["reason"], "repeat_blocked")
        self.assertIsNone(b["new"])
        self.assertTrue([t for t in h.trace(root)
                         if t["kind"] == "repeat_blocked"])

    def test_redirect_into_another_boards_url_is_a_repeat(self):
        root = self.root(boards=h.BOARDS[:2])
        fake = h.FakeTransport({
            h.SCALE: [h.ok(h.gh_body([1]))],
            h.DATABRICKS: [h.status(302, b"", {"location": h.SCALE})]})
        exit_name, _ = h.run(root, fake)
        self.assertEqual(exit_name, loop.INCOMPLETE)
        self.assertEqual(fake.count(h.SCALE), 1)
        self.assertEqual(h.board(h.summary(root), "databricks")["reason"],
                         "repeat_blocked")

    def test_allowed_redirect_is_followed_and_saved(self):
        target = "https://boards-api.greenhouse.io/v1/boards/scaleai2/jobs"
        body = h.gh_body([5])
        root = self.root(boards=[h.BOARDS[0]])
        fake = h.FakeTransport({
            h.SCALE: [h.status(301, b"moved", {"location": target})],
            target: [h.ok(body)]})
        exit_name, _ = h.run(root, fake)
        self.assertEqual(exit_name, loop.FINISHED)
        self.assertEqual((root / "out/raw/RUN1_scaleai_a1_r1.json")
                         .read_bytes(), body)

    def test_retry_after_4xx_is_never_a_second_attempt(self):
        root = self.root(boards=[h.BOARDS[3]])
        fake = h.FakeTransport({h.NO_SUCH: [h.status(404, h.NOT_FOUND),
                                            h.ok(h.gh_body([1]))]})
        h.run(root, fake)
        self.assertFalse([t for t in h.trace(root)
                          if t["kind"] == "retry_scheduled"])

    def test_duplicate_posting_ids_counted_once(self):
        root = self.root(boards=[h.BOARDS[0], h.BOARDS[2]])
        h.write_state(root, "scaleai", [1])
        h.write_state(root, "openai", ["a-1"])
        fake = h.FakeTransport({
            h.SCALE: [h.ok(h.gh_body([1, 2, 2, 3, 3, 3]))],
            h.OPENAI: [h.ok(h.ashby_body(["a-1", "a-2", "a-2"]))]})
        exit_name, _ = h.run(root, fake)
        self.assertEqual(exit_name, loop.FINISHED)
        s = h.summary(root)
        gh = h.board(s, "scaleai")
        self.assertEqual(gh["postings_seen"], 3)
        self.assertEqual(gh["new"], 2)
        self.assertEqual(gh["new_ids"], ["2", "3"])
        self.assertEqual(gh["duplicates"], ["2", "3", "3"])
        self.assertEqual(h.board(s, "openai")["new_ids"], ["a-2"])
        dups = [t for t in h.trace(root) if t["kind"] == "duplicate_posting"]
        self.assertEqual(len(dups), 4)
        saved = json.loads(h.state_path(root, "scaleai").read_text())
        self.assertEqual(saved["seen_ids"], ["1", "2", "3"])


class TraceAndReplayTests(LoopCase):

    def test_trace_has_every_loop_step(self):
        root = self.root()
        h.run(root, h.FakeTransport(h.default_script()))
        kinds = [t["kind"] for t in h.trace(root)]
        for kind in ("run_start", "observation", "decision", "action",
                     "result", "board_ok", "board_failed", "run_end"):
            self.assertIn(kind, kinds)
        self.assertEqual(kinds.count("action"), 4)
        self.assertEqual(kinds.count("result"), 4)

    def test_state_before_kept_for_independent_check(self):
        root = self.root()
        path = h.write_state(root, "scaleai", [1])
        before = path.read_bytes()
        h.run(root, h.FakeTransport(h.default_script()))
        self.assertEqual((root / "out/runs/RUN1/state_before/scaleai.json")
                         .read_bytes(), before)
        self.assertNotEqual(path.read_bytes(), before)

    def test_replay_dir_is_seeded_everywhere(self):
        root = self.root(boards=[h.BOARDS[0], h.BOARDS[2]])
        replay = root / "data" / "replay"
        replay.mkdir()
        (replay / "scaleai.json").write_bytes(h.gh_body([1, 2]))
        (replay / "openai.json").write_bytes(h.ashby_body(["a"]))
        exit_name, runner = h.run(root, replay_dir=Path("data/replay"),
                                  run_id="R-SEEDED")
        self.assertEqual(exit_name, loop.FINISHED)
        self.assertEqual(runner.mode, "SEEDED")
        self.assertEqual({t["mode"] for t in h.trace(root, "R-SEEDED")},
                         {"SEEDED"})
        self.assertEqual(h.summary(root, "R-SEEDED")["mode"], "SEEDED")
        self.assertIn("SEEDED", h.report(root, "R-SEEDED").splitlines()[0])
        # A SEEDED run never touches the LIVE state.
        self.assertTrue(h.state_path(root, "scaleai", seeded=True).exists())
        self.assertFalse(h.state_path(root, "scaleai").exists())

    def test_replay_of_a_previous_run_reproduces_it(self):
        root = self.root()
        script = h.default_script()
        script[h.DATABRICKS] = [transport.TransportTimeout("t"),
                                h.ok(h.gh_body([10]))]
        h.run(root, h.FakeTransport(script), run_id="LIVE1")
        live = h.summary(root, "LIVE1")
        clock = h.FakeClock()
        exit_name, _ = h.run(root, replay_dir=Path("out/runs/LIVE1"),
                             run_id="REPLAY1", clock=clock)
        replayed = h.summary(root, "REPLAY1")
        self.assertEqual(exit_name, live["exit"])
        self.assertEqual(clock.sleeps, [2])
        for name in ("scaleai", "databricks", "openai",
                     "rithika-js2-no-such-board"):
            a, b = h.board(live, name), h.board(replayed, name)
            for key in ("status", "http_status", "reason", "postings_seen",
                        "attempts"):
                self.assertEqual(a[key], b[key], (name, key))

    def test_replay_dir_outside_read_area_is_an_error(self):
        root = self.root()
        outside = self.tmp / "elsewhere"
        outside.mkdir()
        exit_name, runner = h.run(root, replay_dir=outside)
        self.assertEqual(exit_name, loop.ERROR)
        self.assertIn("path_outside_read_area", runner.error)

    def test_replay_missing_file_fails_board_without_retry(self):
        root = self.root(boards=[h.BOARDS[0]])
        (root / "data" / "replay").mkdir()
        clock = h.FakeClock()
        exit_name, _ = h.run(root, replay_dir=Path("data/replay"),
                             clock=clock)
        self.assertEqual(exit_name, loop.INCOMPLETE)
        self.assertEqual(clock.sleeps, [])
        self.assertEqual(h.board(h.summary(root), "scaleai")["reason"],
                         "replay_missing")


class CliAndTransportTests(LoopCase):

    def test_cli_replay_returns_exit_code_and_labels_seeded(self):
        import contextlib
        import io
        root = self.root(boards=[h.BOARDS[0]])
        (root / "data" / "replay").mkdir()
        (root / "data" / "replay" / "scaleai.json").write_bytes(
            h.gh_body([1]))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = loop.main(["--replay", "data/replay"], root=root,
                             run_id="CLI1")
        self.assertEqual(code, 0)
        self.assertIn("[SEEDED] exit: finished (0)", out.getvalue())

    def test_real_transport_refuses_before_opening(self):
        real = transport.UrllibTransport()

        class NoNetwork:
            def open(self, *args, **kwargs):
                raise AssertionError("network call attempted")

        real._opener = NoNetwork()
        with self.assertRaises(policy.PolicyRefusal):
            real("GET", "https://example.com/", {}, 20)
        with self.assertRaises(policy.PolicyRefusal):
            real("POST", h.SCALE, {}, 20)


class AdapterTests(unittest.TestCase):

    def test_greenhouse_and_ashby_shapes(self):
        from agent import adapters
        gh = adapters.parse_greenhouse(h.gh_body([7]))
        self.assertEqual(gh[0]["id"], "7")
        self.assertEqual(gh[0]["location"], "Remote")
        self.assertEqual(set(gh[0]), {"id", "title", "location", "content",
                                      "url"})
        ab = adapters.parse_ashby(h.ashby_body(["u-1"]))
        self.assertEqual((ab[0]["id"], ab[0]["location"], ab[0]["content"]),
                         ("u-1", "SF", "<p>x</p>"))

    def test_malformed_cases(self):
        from agent import adapters
        for body in (b"not json", b"[]", b'{"jobs": null}', b'{"x": 1}',
                     b'{"jobs": [{"title": "no id"}]}',
                     b'{"jobs": [{"id": true}]}', b"\xff\xfe"):
            for parse in (adapters.parse_greenhouse, adapters.parse_ashby):
                with self.assertRaises(adapters.MalformedResponse) as ctx:
                    parse(body)
                self.assertEqual(ctx.exception.code, "malformed_response")


class BoardsOptionTests(LoopCase):
    """--boards FILE: same checks as config/boards.json, before any request."""

    def run_main(self, root, argv, fake):
        import contextlib
        import io
        clock = h.FakeClock()
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            return loop.main(argv, root=root, transport=fake, clock=clock,
                             sleep=clock.sleep, run_id="B1")

    def write_boards(self, root, name, boards):
        path = root / "config" / name
        path.write_text(json.dumps({"boards": boards}))
        return f"config/{name}"

    def test_no_option_uses_config_boards_json(self):
        root = self.root()
        fake = h.FakeTransport(h.default_script())
        code = self.run_main(root, [], fake)
        self.assertEqual(code, 1)  # the deliberate 404 board
        s = h.summary(root, "B1")
        self.assertEqual(s["boards_file"], "config/boards.json")
        self.assertEqual([b["name"] for b in s["boards"]],
                         [b["name"] for b in h.BOARDS])
        self.assertEqual(len(fake.calls), 4)
        startup = [t for t in h.trace(root, "B1") if t["kind"] == "startup"]
        self.assertEqual(startup[0]["boards_file"], "config/boards.json")
        self.assertIn("Boards file: `config/boards.json`",
                      h.report(root, "B1"))

    def test_boards_demo_3_runs_only_those_boards(self):
        root = self.root()
        real = h.ROOT / "config" / "boards_demo_3.json"
        (root / "config" / "boards_demo_3.json").write_bytes(
            real.read_bytes())
        fake = h.FakeTransport(h.default_script())
        code = self.run_main(root, ["--boards", "config/boards_demo_3.json"],
                             fake)
        self.assertEqual(code, 0)
        s = h.summary(root, "B1")
        self.assertEqual([b["name"] for b in s["boards"]],
                         ["scaleai", "databricks", "openai"])
        self.assertEqual([c["url"] for c in fake.calls],
                         [h.SCALE, h.DATABRICKS, h.OPENAI])
        self.assertEqual(s["boards_file"], "config/boards_demo_3.json")
        startup = [t for t in h.trace(root, "B1") if t["kind"] == "startup"]
        self.assertEqual(startup[0]["boards_file"],
                         "config/boards_demo_3.json")
        self.assertIn("Boards file: `config/boards_demo_3.json`",
                      h.report(root, "B1"))

    def test_boards_demo_3_is_an_exact_subset_of_boards_json(self):
        full = json.loads((h.ROOT / "config" / "boards.json").read_text())
        demo = json.loads((h.ROOT / "config" / "boards_demo_3.json")
                          .read_text())
        wanted = ("scaleai", "databricks", "openai")
        self.assertEqual(demo["boards"],
                         [b for b in full["boards"] if b["name"] in wanted])

    def test_boards_file_outside_readable_folders_exits_3(self):
        root = self.root()
        outside = self.tmp / "elsewhere.json"
        outside.write_text(json.dumps({"boards": h.BOARDS[:1]}))
        fake = h.FakeTransport(h.default_script())
        code = self.run_main(root, ["--boards", str(outside)], fake)
        self.assertEqual(code, 3)
        self.assertEqual(fake.calls, [])
        self.only_trace_written(root, "B1")
        end = h.trace(root, "B1")[-1]
        self.assertIn("path_outside_read_area", end["reason"])

    def test_boards_file_with_duplicate_board_exits_3(self):
        root = self.root()
        rel = self.write_boards(root, "dup.json",
                                [h.BOARDS[0], h.BOARDS[2], h.BOARDS[0]])
        fake = h.FakeTransport(h.default_script())
        code = self.run_main(root, ["--boards", rel], fake)
        self.assertEqual(code, 3)
        self.assertEqual(fake.calls, [])
        self.only_trace_written(root, "B1")
        self.assertIn("config_duplicate_board",
                      h.trace(root, "B1")[-1]["reason"])

    def test_boards_file_with_host_off_allowlist_exits_3(self):
        root = self.root()
        rel = self.write_boards(root, "evil.json", [
            h.BOARDS[0],
            {"name": "evil", "ats": "greenhouse",
             "url": "https://boards-api.greenhouse.io.evil.com/v1/x"}])
        fake = h.FakeTransport(h.default_script())
        code = self.run_main(root, ["--boards", rel], fake)
        self.assertEqual(code, 3)
        self.assertEqual(fake.calls, [])
        self.only_trace_written(root, "B1")
        self.assertIn("host_not_allowed", h.trace(root, "B1")[-1]["reason"])

    def test_boards_file_over_max_boards_exits_3(self):
        root = self.root(budgets=dict(h.BUDGETS, max_boards=2))
        rel = self.write_boards(root, "three.json", h.BOARDS[:3])
        fake = h.FakeTransport(h.default_script())
        code = self.run_main(root, ["--boards", rel], fake)
        self.assertEqual(code, 3)
        self.assertEqual(fake.calls, [])
        self.assertIn("config_too_many_boards",
                      h.trace(root, "B1")[-1]["reason"])

if __name__ == "__main__":
    unittest.main()
