"""The loop end to end, offline (GATE.md: Exits, Budgets, Repeat rule, Error policy, the trace, and
wrong versions 1, 2 and 4). Board answers are constructed fixtures handed out by FakeNet."""

import gzip
import hashlib
import json
import os
import unittest

from job_agent import gate, loop, providers
from job_agent.errors import BrokenInput, NeedsApproval, Redirected, Refused

from .loop_helpers import (Clock, FakeNet, Workspace, answer, ashby_job, greenhouse_job, lever_job, timeout,
                           url)

OPENAI, VERKADA, PALANTIR, BAD = (("ashby", "openai"), ("greenhouse", "verkada"), ("lever", "palantir"),
                                  ("greenhouse", "no-such-board-js2-test"))
NOT_FOUND = b'{"status":404,"error":"Job not found"}'


def board_entry(summary, key):
    return next(b for b in summary["boards"] if b["key"] == key)


class LoopTest(unittest.TestCase):
    def setUp(self):
        self.ws = Workspace()
        self.addCleanup(self.ws.cleanup)

    def three_good(self, openai=None, verkada=None, palantir=None):
        return {
            url(*OPENAI): [answer(*OPENAI, openai or [ashby_job("a-1"), ashby_job("a-2")])],
            url(*VERKADA): [answer(*VERKADA, verkada or [greenhouse_job(101), greenhouse_job(102)])],
            url(*PALANTIR): [answer(*PALANTIR, palantir or [lever_job("l-1")])],
        }

    # Exits

    def test_three_boards_read_is_finished_and_each_board_gets_its_first_state(self):
        self.ws.boards(OPENAI, VERKADA, PALANTIR)
        net = FakeNet(self.three_good())
        summary = self.ws.run(net)
        self.assertEqual((summary["exit"], summary["exit_code"]), ("finished", 0))
        self.assertEqual(summary["counts"]["boards_read"], 3)
        self.assertEqual(summary["counts"]["postings"], 5)
        self.assertEqual(net.calls, [url(*OPENAI), url(*VERKADA), url(*PALANTIR)])
        self.assertEqual(self.ws.state("greenhouse", "verkada")["seen_ids"], ["101", "102"])
        self.assertTrue(self.ws.screen[0].startswith("Exit: finished (code 0)."))
        run_dir = self.ws.run_dirs()[0]
        kinds = [e["kind"] for e in self.ws.trace(run_dir)]
        self.assertEqual(kinds[0], "run_start")
        self.assertEqual(kinds[-1], "exit")
        self.assertEqual([e["kind"] for e in self.ws.trace(run_dir) if e["kind"] == "state_write"], ["state_write"] * 3)

    def test_a_404_board_is_unverified_without_a_retry_and_the_run_is_incomplete(self):
        # Wrong version 1a: a 404 board read as zero postings and reported "0 new".
        self.ws.boards(OPENAI, VERKADA, PALANTIR, BAD + ({"deliberate_failure": True},))
        plan = self.three_good()
        plan[url(*BAD)] = [answer(*BAD, status=404, raw=NOT_FOUND)]
        net = FakeNet(plan)
        summary = self.ws.run(net)
        self.assertEqual((summary["exit"], summary["exit_code"]), ("incomplete", 1))
        bad = board_entry(summary, "greenhouse-no-such-board-js2-test")
        self.assertEqual(bad["status"], "unverified")
        self.assertIn("HTTP 404", bad["reason"])
        self.assertIsNone(bad["postings"])  # not 0: no value is filled in for it
        self.assertEqual(net.count(url(*BAD)), 1)  # a retry cannot fix a 404
        self.assertIsNone(self.ws.state(*BAD))
        self.assertEqual(summary["counts"]["boards_read"], 3)
        self.assertIn("greenhouse-no-such-board-js2-test unverified", summary["exit_line"])
        report = (self.ws.run_dirs()[0] / "report.md").read_text(encoding="utf-8")
        self.assertTrue(report.startswith("Exit: incomplete (code 1)."))
        self.assertIn("**Needs you:**", report)

    def test_an_empty_board_is_unverified_not_zero_new(self):
        # Wrong version 1b: an empty jobs list read as zero postings.
        self.ws.boards(VERKADA)
        summary = self.ws.run(FakeNet({url(*VERKADA): [answer(*VERKADA, [])]}))
        self.assertEqual(summary["exit"], "incomplete")
        self.assertEqual(board_entry(summary, "greenhouse-verkada")["status"], "unverified")
        self.assertIn("empty", board_entry(summary, "greenhouse-verkada")["reason"])

    def test_a_failed_board_is_never_reported_finished(self):
        # Wrong version 1c: a run with an unverified board reported finished.
        for failure in ([timeout(), timeout()], [answer(*VERKADA, raw=b"not json")],
                        [Redirected("the board answered 301 with a redirect to 'https://evil.example/'")]):
            with self.subTest(failure=type(failure[0]).__name__):
                ws = Workspace()
                self.addCleanup(ws.cleanup)
                ws.boards(OPENAI, VERKADA)
                plan = {url(*OPENAI): [answer(*OPENAI, [ashby_job("a-1")])], url(*VERKADA): failure}
                summary = ws.run(FakeNet(plan))
                self.assertEqual((summary["exit"], summary["exit_code"]), ("incomplete", 1))

    # The error policy

    def test_a_timeout_gets_one_retry_after_five_seconds(self):
        self.ws.boards(VERKADA)
        net = FakeNet({url(*VERKADA): [timeout(), answer(*VERKADA, [greenhouse_job(101)])]})
        summary = self.ws.run(net)
        self.assertEqual(summary["exit"], "finished")
        self.assertEqual(self.ws.sleeps, [gate.RETRY_WAIT])
        self.assertEqual(net.count(url(*VERKADA)), 2)
        self.assertEqual(summary["used"]["requests"], 2)  # the retry counts against the budget
        attempts = board_entry(summary, "greenhouse-verkada")["attempts"]
        self.assertEqual([a["retry"] for a in attempts], [False, True])
        requests = [e for e in self.ws.trace(self.ws.run_dirs()[0]) if e["kind"] == "request"]
        self.assertEqual([e["retry"] for e in requests], [False, True])

    def test_a_second_timeout_leaves_the_board_unverified(self):
        self.ws.boards(VERKADA)
        net = FakeNet({url(*VERKADA): [timeout(), timeout()]})
        summary = self.ws.run(net)
        self.assertEqual(summary["exit"], "incomplete")
        self.assertEqual(net.count(url(*VERKADA)), 2)
        self.assertIn("after one retry", board_entry(summary, "greenhouse-verkada")["reason"])

    def test_http_503_then_200_is_read_after_one_retry(self):
        self.ws.boards(VERKADA)
        net = FakeNet({url(*VERKADA): [answer(*VERKADA, status=503, raw=b"busy"),
                                       answer(*VERKADA, [greenhouse_job(101)])]})
        summary = self.ws.run(net)
        self.assertEqual(summary["exit"], "finished")
        self.assertEqual([a["status"] for a in board_entry(summary, "greenhouse-verkada")["attempts"]], [503, 200])

    def test_a_redirect_is_not_followed_or_retried(self):
        self.ws.boards(VERKADA)
        net = FakeNet({url(*VERKADA): [Redirected("the board answered 302 with a redirect to 'https://evil.example/'")]})
        summary = self.ws.run(net)
        self.assertEqual(summary["exit"], "incomplete")
        self.assertEqual(net.calls, [url(*VERKADA)])

    def test_a_failed_board_keeps_its_state_and_nothing_counts_as_gone(self):
        # Wrong version 2: a failed board's postings reported as gone.
        self.ws.boards(VERKADA, PALANTIR)
        first = FakeNet({url(*VERKADA): [answer(*VERKADA, [greenhouse_job(101), greenhouse_job(102)])],
                         url(*PALANTIR): [answer(*PALANTIR, [lever_job("l-1")])]})
        self.ws.run(first)
        before = (self.ws.root / "state" / "greenhouse-verkada.json").read_bytes()
        second = FakeNet({url(*VERKADA): [answer(*VERKADA, status=404, raw=NOT_FOUND)],
                          url(*PALANTIR): [answer(*PALANTIR, [lever_job("l-1"), lever_job("l-2")])]})
        summary = self.ws.run(second)
        self.assertEqual(summary["counts"]["gone"], 0)
        self.assertEqual(board_entry(summary, "greenhouse-verkada")["gone"], [])
        self.assertEqual(summary["counts"]["new"], 1)  # only Palantir's l-2
        self.assertEqual((self.ws.root / "state" / "greenhouse-verkada.json").read_bytes(), before)

    # Budgets

    def test_the_request_budget_counts_retries_and_stops_before_sending(self):
        # Wrong versions 4a (a retry not counted) and 4b (the budget checked after sending).
        self.ws.boards(VERKADA, PALANTIR, OPENAI)
        net = FakeNet({url(*VERKADA): [timeout(), answer(*VERKADA, [greenhouse_job(101)])],
                       url(*PALANTIR): [answer(*PALANTIR, [lever_job("l-1")])],
                       url(*OPENAI): [answer(*OPENAI, [ashby_job("a-1")])]})
        summary = self.ws.run(net, budgets=gate.Budgets().lowered(requests=3))
        self.assertEqual(len(net.calls), 3)
        self.assertEqual(net.count(url(*OPENAI)), 0)
        self.assertEqual((summary["exit"], summary["exit_code"]), ("budget-exhausted", 4))
        self.assertEqual(board_entry(summary, "ashby-openai")["status"], "not visited")
        self.assertTrue(any("requests budget" in r for r in summary["reasons"]))
        self.assertIsNone(self.ws.state(*OPENAI))

    def test_a_request_budget_of_one_sends_exactly_one_request(self):
        self.ws.boards(VERKADA, PALANTIR)
        net = FakeNet(self.three_good())
        summary = self.ws.run(net, budgets=gate.Budgets().lowered(requests=1))
        self.assertEqual(net.calls, [url(*VERKADA)])
        self.assertEqual(summary["exit"], "budget-exhausted")

    def test_no_retry_is_sent_when_the_request_budget_is_used_up(self):
        self.ws.boards(VERKADA)
        net = FakeNet({url(*VERKADA): [timeout(), answer(*VERKADA, [greenhouse_job(101)])]})
        summary = self.ws.run(net, budgets=gate.Budgets().lowered(requests=1))
        self.assertEqual(net.count(url(*VERKADA)), 1)
        self.assertEqual(self.ws.sleeps, [])
        self.assertEqual(summary["exit"], "budget-exhausted")
        self.assertEqual(board_entry(summary, "greenhouse-verkada")["status"], "unverified")

    def test_the_time_budget_is_checked_before_each_request(self):
        self.ws.boards(VERKADA, PALANTIR)
        net = FakeNet(self.three_good())
        summary = self.ws.run(net, monotonic=Clock(step=200.0), budgets=gate.Budgets().lowered(seconds=500))
        self.assertEqual(summary["exit"], "budget-exhausted")
        self.assertTrue(any("seconds budget" in r for r in summary["reasons"]))
        self.assertLess(len(net.calls), 2)

    def test_postings_past_the_claude_budget_wait_and_are_judged_first_next_run(self):
        self.ws.boards(OPENAI)
        self.ws.run(FakeNet({url(*OPENAI): [answer(*OPENAI, [ashby_job("a-1")])]}))  # baseline
        three_new = [ashby_job("a-1"), ashby_job("a-2"), ashby_job("a-3"), ashby_job("a-4")]
        summary = self.ws.run(FakeNet({url(*OPENAI): [answer(*OPENAI, three_new)]}),
                              budgets=gate.Budgets().lowered(claude_calls=2))
        self.assertEqual(self.ws.judges.claude_calls, ["a-2", "a-3"])
        self.assertEqual((summary["exit"], summary["counts"]["waiting_for_claude"]), ("budget-exhausted", 1))
        self.assertEqual(self.ws.state(*OPENAI)["pending_claude"], ["a-4"])
        new = board_entry(summary, "ashby-openai")["new"]
        self.assertEqual([i["claude_verdict"] for i in new], ["not_relevant", "not_relevant",
                                                              "waiting for Claude (budget)"])
        self.assertTrue(all(i["rule_verdict"] in ("relevant", "not_relevant") for i in new))  # the rule judged all
        again = self.ws.run(FakeNet({url(*OPENAI): [answer(*OPENAI, three_new + [ashby_job("a-5")])]}),
                            budgets=gate.Budgets().lowered(claude_calls=2))
        self.assertEqual(self.ws.judges.claude_calls[2:], ["a-4", "a-5"])  # the waiting one first
        self.assertEqual((again["exit"], self.ws.state(*OPENAI)["pending_claude"]), ("finished", []))

    def test_judged_after_waiting_counts_only_the_postings_claude_judged_this_run(self):
        # Found in live run 2026-11-08T222101Z: the report counted all 55 waiting postings as judged, though only
        # 20 were. A run with 2 waiting and a budget of 1 judges 1 of them; the other still waits.
        self.ws.boards(OPENAI)
        self.ws.run(FakeNet({url(*OPENAI): [answer(*OPENAI, [ashby_job("a-1")])]}))  # baseline
        jobs = [ashby_job("a-1"), ashby_job("a-2"), ashby_job("a-3")]
        self.ws.run(FakeNet({url(*OPENAI): [answer(*OPENAI, jobs)]}), budgets=gate.Budgets().lowered(claude_calls=0))
        self.ws.screen.clear()
        summary = self.ws.run(FakeNet({url(*OPENAI): [answer(*OPENAI, jobs)]}),
                              budgets=gate.Budgets().lowered(claude_calls=1))
        openai = board_entry(summary, "ashby-openai")
        self.assertEqual([i["id"] for i in openai["judged_after_waiting"]], ["a-2"])
        self.assertEqual(openai["still_waiting"], ["a-3"])
        self.assertEqual((summary["counts"]["judged_after_waiting"], summary["counts"]["waiting_for_claude"]), (1, 1))
        self.assertIn("1 judged by Claude after waiting", summary["counts_line"])
        waited = [line for line in self.ws.screen if line.startswith("WAITED ")]
        self.assertEqual(len(waited), 1)
        self.assertIn("a-2", waited[0])
        report = (self.ws.run_dirs()[-1] / "report.md").read_text(encoding="utf-8")
        self.assertIn("Judged now, after waiting for Claude (1)", report)

    def test_boards_over_the_boards_budget_are_not_visited(self):
        names = ["b1", "b2", "b3", "b4", "b5", "b6"]
        self.ws.boards(*[("greenhouse", n) for n in names])
        net = FakeNet({url("greenhouse", n): [answer("greenhouse", n, [greenhouse_job(1)])] for n in names})
        summary = self.ws.run(net)
        self.assertEqual(len(net.calls), gate.MAX_BOARDS)
        self.assertEqual(net.count(url("greenhouse", "b6")), 0)
        self.assertEqual(summary["exit"], "budget-exhausted")
        self.assertEqual(board_entry(summary, "greenhouse-b6")["status"], "not visited")

    def test_budget_exhausted_wins_over_incomplete_and_both_reasons_are_listed(self):
        self.ws.boards(BAD, VERKADA, PALANTIR)
        net = FakeNet({url(*BAD): [answer(*BAD, status=404, raw=NOT_FOUND)],
                       url(*VERKADA): [answer(*VERKADA, [greenhouse_job(101)])]})
        summary = self.ws.run(net, budgets=gate.Budgets().lowered(requests=2))
        self.assertEqual(summary["exit"], "budget-exhausted")
        self.assertTrue(any("requests budget" in r for r in summary["reasons"]))
        self.assertTrue(any("unverified" in r for r in summary["reasons"]))

    # The repeat rule

    def test_a_board_listed_twice_is_visited_once(self):
        self.ws.boards(VERKADA, PALANTIR, VERKADA)
        net = FakeNet(self.three_good())
        summary = self.ws.run(net)
        self.assertEqual(net.count(url(*VERKADA)), 1)
        self.assertEqual(summary["repeats_skipped"], ["greenhouse-verkada"])
        self.assertEqual(summary["exit"], "finished")

    def test_the_repeat_rule_allows_one_retry_and_nothing_more(self):
        target = url(*VERKADA)
        net = FakeNet({target: [answer(*VERKADA, [greenhouse_job(1)])] * 4})
        ledger = loop.Ledger(10)
        ledger.send(net, target, False, lambda used: None)
        with self.assertRaises(Refused):
            ledger.send(net, target, False, lambda used: None)  # the same action again, not as a retry
        ledger.send(net, target, True, lambda used: None)  # the one retry the error policy allows
        with self.assertRaises(Refused):
            ledger.send(net, target, True, lambda used: None)  # a second retry
        self.assertEqual(len(net.calls), 2)

    # Inputs that stop the run before anything is fetched

    def test_a_board_list_that_gives_a_url_or_a_bad_name_is_broken_input(self):
        for entry in ({"system": "greenhouse", "name": "verkada", "url": "https://evil.example/"},
                      {"system": "greenhouse", "name": "Verkada"}, {"system": "workday", "name": "acme"}):
            with self.subTest(entry=entry):
                (self.ws.root / "boards.json").write_text(json.dumps({"boards": [entry]}), encoding="utf-8")
                net = FakeNet()
                with self.assertRaises(BrokenInput):
                    self.ws.run(net)
                self.assertEqual(net.calls, [])
        self.assertEqual(self.ws.run_dirs(), [])

    def test_moving_layer_1_state_needs_approval_before_anything_is_fetched(self):
        js1 = {"schema": 1, "board": url(*OPENAI), "seen_ids": ["a-1", "a-2"],
               "last_run": {"run_id": "2026-10-31T231042Z", "posting_ids": ["a-1", "a-2"],
                            "titles": {"a-1": "Software Engineer, Example Team", "a-2": "Software Engineer, Example Team"}},
               "runs": [{"run_id": "2026-10-30T093102Z"}, {"run_id": "2026-10-31T231042Z"}]}
        (self.ws.root / "state" / "seen.json").write_text(json.dumps(js1), encoding="utf-8")
        self.ws.boards(OPENAI)
        net = FakeNet({url(*OPENAI): [answer(*OPENAI, [ashby_job("a-1"), ashby_job("a-2"), ashby_job("a-3")])]})
        with self.assertRaises(NeedsApproval):
            self.ws.run(net)
        self.assertEqual((net.calls, self.ws.run_dirs()), ([], []))
        self.assertTrue((self.ws.root / "state" / "seen.json").exists())
        summary = self.ws.run(net, approve="move layer 1's OpenAI state into the layer 2 format")
        self.assertEqual(board_entry(summary, "ashby-openai")["baseline"], False)
        self.assertEqual([i["id"] for i in board_entry(summary, "ashby-openai")["new"]], ["a-3"])
        moved = self.ws.state(*OPENAI)
        self.assertEqual(moved["seen_ids"], ["a-1", "a-2", "a-3"])
        self.assertEqual([r["run_id"] for r in moved["runs"]][:2], ["2026-10-30T093102Z", "2026-10-31T231042Z"])
        self.assertFalse((self.ws.root / "state" / "seen.json").exists())
        trace = self.ws.trace(self.ws.run_dirs()[0])
        self.assertTrue(any(e["kind"] == "approval" for e in trace))
        deleted = [e for e in trace if e["kind"] == "state_write" and e["write"].startswith("deleted")]
        self.assertEqual([(e["path"], e["write"]) for e in deleted], [("state/seen.json", "deleted (approved)")])

    def test_a_refused_request_stops_the_run_with_exit_3_and_saves_no_state(self):
        self.ws.boards(VERKADA, PALANTIR)
        original = providers.TEMPLATES["lever"]
        providers.TEMPLATES["lever"] = "https://api.lever.co.evil.example/v0/postings/{name}?mode=json"
        self.addCleanup(providers.TEMPLATES.__setitem__, "lever", original)
        net = FakeNet(self.three_good())
        with self.assertRaises(Refused):
            self.ws.run(net)
        self.assertEqual(net.calls, [url(*VERKADA)])
        self.assertIsNone(self.ws.state(*VERKADA))
        run_dir = self.ws.run_dirs()[0]
        last = self.ws.trace(run_dir)[-1]
        self.assertEqual((last["kind"], last["status"], last["code"]), ("exit", "error", gate.REFUSED_CODE))
        self.assertTrue((run_dir / "error.txt").exists())

    # The evidence

    def test_every_answer_is_saved_byte_for_byte_with_its_hash(self):
        self.ws.boards(VERKADA)
        reply = answer(*VERKADA, [greenhouse_job(101)])
        self.ws.run(FakeNet({url(*VERKADA): [reply]}))
        folder = self.ws.run_dirs()[0] / "boards" / "greenhouse-verkada"
        saved = gzip.decompress((folder / "attempt-1.json.gz").read_bytes())
        self.assertEqual(saved, reply.body)
        meta = json.loads((folder / "attempt-1.meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["sha256"], hashlib.sha256(reply.body).hexdigest())
        self.assertEqual(meta["status"], 200)

    def test_the_trace_pairs_each_request_with_what_came_back_and_the_report_comes_before_the_states(self):
        self.ws.boards(VERKADA, BAD, PALANTIR)
        plan = self.three_good()
        plan[url(*VERKADA)] = [timeout(), answer(*VERKADA, [greenhouse_job(101)])]
        plan[url(*BAD)] = [answer(*BAD, status=404, raw=NOT_FOUND)]
        self.ws.run(FakeNet(plan))
        trace = self.ws.trace(self.ws.run_dirs()[0])
        self.assertEqual([e["step"] for e in trace], list(range(1, len(trace) + 1)))
        for index, entry in enumerate(trace):
            if entry["kind"] == "request":
                self.assertIn(trace[index + 1]["kind"], ("answer", "no_answer"))
        steps = {e["kind"]: e["step"] for e in trace}
        first_state = min(e["step"] for e in trace if e["kind"] == "state_write")
        self.assertLess(steps["report"], first_state)
        text = (self.ws.run_dirs()[0] / "trace.jsonl").read_text(encoding="utf-8")
        self.assertNotIn(str(self.ws.root.parent), text)  # repo-relative paths only
        self.assertTrue((self.ws.run_dirs()[0] / "trace.md").exists())

    def test_the_loop_writes_only_inside_runs_and_state(self):
        before = {p for p in self.ws.root.rglob("*")}
        self.ws.boards(VERKADA, BAD)
        plan = {url(*VERKADA): [answer(*VERKADA, [greenhouse_job(101)])],
                url(*BAD): [answer(*BAD, status=404, raw=NOT_FOUND)]}
        self.ws.run(FakeNet(plan))
        created = {p for p in self.ws.root.rglob("*")} - before - {self.ws.root / "boards.json"}
        outside = [p for p in created if p.relative_to(self.ws.root).parts[0] not in ("runs", "state")]
        self.assertEqual(outside, [])

    def test_a_replay_reads_the_saved_answers_and_says_it_is_a_replay(self):
        self.ws.boards(VERKADA, BAD)
        plan = {url(*VERKADA): [answer(*VERKADA, [greenhouse_job(101)])],
                url(*BAD): [answer(*BAD, status=404, raw=NOT_FOUND)]}
        live = self.ws.run(FakeNet(plan))
        (self.ws.root / "state" / "replay").mkdir()
        (self.ws.root / "runs" / "replay").mkdir()
        replayed = self.ws.run(FakeNet(), replay=self.ws.run_dirs()[0], state="state/replay", runs="runs/replay")
        self.assertIn("replay of the saved answers", replayed["source"])
        self.assertEqual(replayed["exit"], live["exit"])
        self.assertEqual(board_entry(replayed, "greenhouse-verkada")["postings"], 1)
        self.assertEqual(board_entry(replayed, "greenhouse-no-such-board-js2-test")["status"], "unverified")


if __name__ == "__main__":
    unittest.main()
