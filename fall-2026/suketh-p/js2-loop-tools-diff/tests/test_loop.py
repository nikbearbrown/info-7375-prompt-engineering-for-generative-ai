"""The bounded loop: exits, budgets, repeat rule, error policy, history and trace,
each as GATE.md states it. Two exits come from the student's answers on 2026-11-08:
an approval that names the wrong run or file is treated as missing (incomplete), and
a redirect leaves the board unverified while the run keeps going.

Every board response is CONSTRUCTED (tests/fakes.py), every request is simulated,
time is a fake clock, and every Approval is a SIMULATED approval fixture.

GATE.md wrong version 1 (an empty jobs list treated as a usable board) has no test
here on purpose: the student writes that test first, for the review packet."""

import gzip
import hashlib
import json
import unittest

from jobwatch import boards, loop
from jobwatch.boards import Board
from jobwatch.loop import Budget
from jobwatch.net import ConnectionFailed
from jobwatch.policy import Approval
from tests.fakes import (ANTHROPIC_URL, BAD_SLUG_URL, DATABRICKS_URL, GH_404_BODY, LINEAR_URL, NORMAL,
                         WITH_FAILURE_CONTROL, Fail, FakeClock, FakeTransport, Project, Reply, ashby,
                         ashby_job, ashby_url_key, gh_job, greenhouse)

U1 = "00000000-0000-4000-8000-000000000001"
U2 = "00000000-0000-4000-8000-000000000002"
WALL = "2026-11-08T12:00:00Z"
RELEVANT_103 = gh_job(103, "Software Engineer, Inference", "San Francisco, CA",
                      "<p>You write Python and PyTorch daily.</p>")


def normal_script(extra=None):
    script = {
        ANTHROPIC_URL: Reply(body=greenhouse(gh_job(101), gh_job(102))),
        DATABRICKS_URL: Reply(body=greenhouse(gh_job(201))),
        LINEAR_URL: Reply(body=ashby(ashby_job(U1), ashby_job(U2))),
    }
    script.update(extra or {})
    return script


def by_board(result):
    return {b["board"]: b for b in result["boards"]}


class LoopCase(unittest.TestCase):
    def setUp(self):
        self.project = Project()
        self.addCleanup(self.project.cleanup)
        self.clock = FakeClock()

    def run_loop(self, run_id, requested, script, approval="matching", budget=None, configured=None):
        if approval == "matching":
            approval = Approval(run_id, "state/state.json")  # simulated approval fixture
        self.transport = FakeTransport(self.clock, script)
        return loop.run(root=self.project.root, run_id=run_id, requested=requested, approval=approval,
                        fetch=self.transport, clock=self.clock, wall=lambda: WALL,
                        budget=budget or Budget(), configured=configured or boards.CONFIGURED)

    def baseline(self, run_id="R1", script=None):
        result = self.run_loop(run_id, NORMAL, script or normal_script())
        self.assertEqual(result["status"], "finished", result["reason"])
        return result


class ExitTest(LoopCase):
    def test_three_usable_boards_with_approval_finish_and_advance_the_state(self):
        result = self.baseline()
        self.assertTrue(result["state_advanced"])
        boards_seen = by_board(result)
        self.assertEqual({name: (b["outcome"], b["jobs"], b["baseline"], b["new_keys"]) for name, b in boards_seen.items()},
                         {"greenhouse/anthropic": ("usable", 2, True, []),
                          "greenhouse/databricks": ("usable", 1, True, []),
                          "ashby/linear": ("usable", 2, True, [])})
        self.assertEqual(sorted(self.project.state()["boards"]),
                         ["ashby/linear", "greenhouse/anthropic", "greenhouse/databricks"])
        self.assertEqual(self.project.results("R1")["status"], "finished")

    def test_the_failure_run_is_incomplete_and_leaves_the_state_byte_identical(self):
        self.baseline("R1")
        before = self.project.state_bytes()
        result = self.run_loop("R2", WITH_FAILURE_CONTROL, normal_script({BAD_SLUG_URL: Reply(404, GH_404_BODY)}))
        self.assertEqual(result["status"], "incomplete")
        self.assertFalse(result["state_advanced"])
        self.assertEqual(self.project.state_bytes(), before)
        bad = by_board(result)["greenhouse/jobwatch-no-such-board-js2"]
        self.assertEqual((bad["role"], bad["outcome"], bad["jobs"]), ("failure-control", "failed-as-expected", None))
        for name in NORMAL:
            self.assertEqual((by_board(result)[name]["outcome"], by_board(result)[name]["provisional"]), ("usable", True))

    def test_a_failed_normal_board_makes_the_run_incomplete_and_its_count_unknown(self):
        result = self.run_loop("R1", NORMAL, normal_script({LINEAR_URL: Reply(500, b"server error")}))
        self.assertEqual(result["status"], "incomplete")
        linear = by_board(result)["ashby/linear"]
        self.assertEqual((linear["outcome"], linear["jobs"]), ("unverified", None))
        self.assertIn("500", linear["reason"])
        self.assertIsNone(self.project.state_bytes())

    def test_without_approval_a_complete_check_ends_incomplete_and_writes_no_state(self):
        result = self.run_loop("R1", NORMAL, normal_script(), approval=None)
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("approval", result["reason"])
        self.assertIsNone(self.project.state_bytes())

    def test_an_approval_for_another_run_is_treated_as_missing(self):
        result = self.run_loop("R1", NORMAL, normal_script(), approval=Approval("R0", "state/state.json"))
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("approval", result["reason"])
        self.assertIsNone(self.project.state_bytes())

    def test_an_approval_for_another_file_is_treated_as_missing(self):
        result = self.run_loop("R1", NORMAL, normal_script(), approval=Approval("R1", "state/other.json"))
        self.assertEqual(result["status"], "incomplete")
        self.assertIsNone(self.project.state_bytes())

    def test_no_usable_normal_board_is_an_error(self):
        script = normal_script({ANTHROPIC_URL: Reply(503), DATABRICKS_URL: Reply(503), LINEAR_URL: Reply(503)})
        result = self.run_loop("R1", NORMAL, script)
        self.assertEqual(result["status"], "error")
        self.assertIsNone(self.project.state_bytes())

    def test_a_failure_control_that_answers_200_is_an_error_after_the_other_boards(self):
        self.baseline("R1")
        before = self.project.state_bytes()
        result = self.run_loop("R2", WITH_FAILURE_CONTROL,
                               normal_script({BAD_SLUG_URL: Reply(200, greenhouse(gh_job(1)))}))
        self.assertEqual(result["status"], "error")
        self.assertIn("failure control", result["reason"])
        self.assertEqual(self.transport.urls(), [ANTHROPIC_URL, DATABRICKS_URL, LINEAR_URL, BAD_SLUG_URL])
        self.assertEqual(by_board(result)["greenhouse/jobwatch-no-such-board-js2"]["outcome"], "failure-control-broke")
        self.assertEqual(self.project.state_bytes(), before)

    def test_an_unconfigured_board_is_a_policy_denial_and_nothing_is_requested(self):
        result = self.run_loop("R1", NORMAL + ["greenhouse/stripe"], normal_script())
        self.assertEqual(result["status"], "error")
        self.assertIn("greenhouse/stripe", result["reason"])
        self.assertEqual(self.transport.calls, [])

    def test_a_damaged_state_is_an_error_and_nothing_is_requested(self):
        self.project.state_path.parent.mkdir()
        self.project.state_path.write_text("{", encoding="utf-8")
        result = self.run_loop("R1", NORMAL, normal_script())
        self.assertEqual(result["status"], "error")
        self.assertEqual(self.transport.calls, [])
        self.assertEqual(self.project.state_bytes(), b"{")

    def test_a_failed_state_write_is_an_error(self):
        (self.project.root / "state").write_text("a file where the state folder should be", encoding="utf-8")
        result = self.run_loop("R1", NORMAL, normal_script())
        self.assertEqual(result["status"], "error")
        self.assertIn("state", result["reason"])
        self.assertFalse(result["state_advanced"])
        self.assertEqual(self.project.results("R1")["status"], "error")

    def test_an_invalid_run_id_is_an_error_and_creates_nothing(self):
        result = self.run_loop("../R1", NORMAL, normal_script())
        self.assertEqual(result["status"], "error")
        self.assertEqual(self.transport.calls, [])
        self.assertFalse((self.project.root / "runs").exists())

    def test_a_run_id_whose_folder_exists_is_an_error_and_the_folder_is_untouched(self):
        earlier = self.project.run_dir("R1")
        earlier.mkdir(parents=True)
        (earlier / "trace.json").write_text("earlier evidence", encoding="utf-8")
        result = self.run_loop("R1", NORMAL, normal_script())
        self.assertEqual(result["status"], "error")
        self.assertEqual(self.transport.calls, [])
        self.assertEqual((earlier / "trace.json").read_text(encoding="utf-8"), "earlier evidence")

    def test_N5_a_redirect_is_not_followed_and_the_board_is_unverified(self):
        script = normal_script({ANTHROPIC_URL: Reply(301, b"moved", location="https://example.com/jobs")})
        result = self.run_loop("R1", NORMAL, script)
        self.assertEqual(self.transport.urls(), [ANTHROPIC_URL, DATABRICKS_URL, LINEAR_URL])
        anthropic = by_board(result)["greenhouse/anthropic"]
        self.assertEqual(anthropic["outcome"], "unverified")
        self.assertIn("redirect", anthropic["reason"])
        self.assertEqual(result["status"], "incomplete")
        self.assertIsNone(self.project.state_bytes())


class BudgetTest(LoopCase):
    FIVE = tuple(Board("greenhouse", f"b{n}") for n in range(1, 6))

    def five_board_script(self):
        return {f"https://boards-api.greenhouse.io/v1/boards/b{n}/jobs?content=true": Reply(body=greenhouse(gh_job(n)))
                for n in range(1, 6)}

    def test_a_board_past_the_board_budget_is_not_checked(self):
        result = self.run_loop("R1", [b.name for b in self.FIVE], self.five_board_script(), configured=self.FIVE)
        self.assertEqual(result["status"], "budget-exhausted")
        self.assertEqual(len(self.transport.calls), 4)
        fifth = by_board(result)["greenhouse/b5"]
        self.assertEqual((fifth["outcome"], fifth["jobs"]), ("not-checked", None))
        self.assertIn("board", fifth["reason"])
        self.assertEqual(result["used"]["boards"], 4)
        self.assertIsNone(self.project.state_bytes())

    def test_the_request_budget_stops_the_loop(self):
        result = self.run_loop("R1", NORMAL, normal_script(), budget=Budget(max_requests=2))
        self.assertEqual(result["status"], "budget-exhausted")
        self.assertEqual(self.transport.urls(), [ANTHROPIC_URL, DATABRICKS_URL])
        self.assertEqual(by_board(result)["ashby/linear"]["outcome"], "not-checked")
        self.assertEqual(result["used"]["requests"], 2)

    def test_no_request_starts_once_the_run_deadline_has_passed(self):
        script = normal_script({ANTHROPIC_URL: Reply(body=greenhouse(gh_job(101)), seconds=1.0)})
        result = self.run_loop("R1", NORMAL, script, budget=Budget(max_seconds=1.0))
        self.assertEqual(result["status"], "budget-exhausted")
        self.assertEqual(self.transport.urls(), [ANTHROPIC_URL])
        self.assertIsNone(self.project.state_bytes())

    def test_a_request_cut_off_by_the_run_deadline_is_budget_exhausted(self):
        script = normal_script({ANTHROPIC_URL: Reply(body=greenhouse(gh_job(101)), seconds=0.6),
                                DATABRICKS_URL: Reply(body=greenhouse(gh_job(201)), seconds=0.6)})
        result = self.run_loop("R1", NORMAL, script, budget=Budget(max_seconds=1.0))
        self.assertEqual(result["status"], "budget-exhausted")
        self.assertEqual(self.transport.urls(), [ANTHROPIC_URL, DATABRICKS_URL])
        self.assertEqual(by_board(result)["greenhouse/databricks"]["outcome"], "unverified")
        self.assertEqual(by_board(result)["ashby/linear"]["outcome"], "not-checked")

    def test_each_request_gets_at_most_five_seconds(self):
        self.run_loop("R1", NORMAL, normal_script())
        for call in self.transport.calls:
            self.assertAlmostEqual(call["deadline"] - call["started"], 5.0)

    def test_a_request_gets_only_the_time_the_run_has_left(self):
        script = normal_script({ANTHROPIC_URL: Reply(body=greenhouse(gh_job(101)), seconds=4.0)})
        self.run_loop("R1", NORMAL, script, budget=Budget(max_seconds=7.0))
        databricks = self.transport.calls[1]
        self.assertAlmostEqual(databricks["deadline"] - databricks["started"], 3.0)

    def test_a_board_slower_than_five_seconds_times_out_and_the_run_continues(self):
        script = normal_script({DATABRICKS_URL: Reply(body=greenhouse(gh_job(201)), seconds=6.0)})
        result = self.run_loop("R1", NORMAL, script)
        self.assertEqual(self.transport.urls(), [ANTHROPIC_URL, DATABRICKS_URL, LINEAR_URL])
        databricks = by_board(result)["greenhouse/databricks"]
        self.assertEqual((databricks["outcome"], databricks["jobs"]), ("unverified", None))
        self.assertIn("timeout", databricks["reason"])
        self.assertEqual(result["status"], "incomplete")

    def test_time_used_after_the_last_request_still_counts(self):
        script = {ANTHROPIC_URL: Reply(body=greenhouse(gh_job(101)), seconds=0.5),
                  DATABRICKS_URL: Reply(body=greenhouse(gh_job(201)), seconds=0.5),
                  LINEAR_URL: Reply(body=ashby(ashby_job(U1)), seconds=1.0)}
        result = self.run_loop("R1", NORMAL, script, budget=Budget(max_seconds=2.0))
        self.assertEqual(result["status"], "budget-exhausted")
        self.assertEqual(len(self.transport.calls), 3)
        self.assertIsNone(self.project.state_bytes())
        self.assertEqual(self.project.results("R1")["status"], "budget-exhausted")


class RepeatRuleTest(LoopCase):
    def test_a_board_listed_twice_is_fetched_once(self):
        result = self.run_loop("R1", NORMAL + ["  GreenHouse/Anthropic "], normal_script())
        self.assertEqual(self.transport.urls(), [ANTHROPIC_URL, DATABRICKS_URL, LINEAR_URL])
        self.assertEqual(result["status"], "finished")
        events = [e["event"] for e in self.project.trace("R1")["events"]]
        self.assertEqual(events.count("duplicate"), 1)

    def test_a_failed_board_listed_twice_still_gets_one_attempt(self):
        script = normal_script({ANTHROPIC_URL: Reply(500)})
        self.run_loop("R1", ["greenhouse/anthropic", "greenhouse/anthropic"] + NORMAL[1:], script)
        self.assertEqual(self.transport.urls().count(ANTHROPIC_URL), 1)

    def test_a_failed_request_is_not_retried(self):
        result = self.run_loop("R1", NORMAL, normal_script({DATABRICKS_URL: Fail(ConnectionFailed)}))
        self.assertEqual(self.transport.urls().count(DATABRICKS_URL), 1)
        self.assertEqual(result["status"], "incomplete")

    def test_duplicates_do_not_use_up_the_board_budget(self):
        result = self.run_loop("R1", NORMAL + ["ashby/linear"], normal_script(), budget=Budget(max_boards=3))
        self.assertEqual(result["status"], "finished")


class HistoryTest(LoopCase):
    def test_a_later_run_reports_only_keys_never_seen_for_that_board_with_a_rule_record(self):
        self.baseline("R1")
        script = normal_script({ANTHROPIC_URL: Reply(body=greenhouse(gh_job(101), gh_job(102), RELEVANT_103))})
        result = self.run_loop("R2", NORMAL, script)
        self.assertEqual(result["status"], "finished")
        anthropic = by_board(result)["greenhouse/anthropic"]
        self.assertEqual((anthropic["baseline"], anthropic["new_keys"]), (False, ["103"]))
        [record] = anthropic["new_postings"]
        self.assertEqual((record["posting_id"], record["verdict"]), ("103", "relevant"))
        self.assertEqual(by_board(result)["ashby/linear"]["new_keys"], [])

    def test_baseline_postings_get_no_rule_records(self):
        result = self.baseline("R1")
        self.assertEqual([b["new_postings"] for b in result["boards"]], [[], [], []])

    def test_the_same_key_on_another_board_is_new_there(self):
        self.baseline("R1")
        script = normal_script({DATABRICKS_URL: Reply(body=greenhouse(gh_job(201), gh_job(101)))})
        result = self.run_loop("R2", NORMAL, script)
        self.assertEqual(by_board(result)["greenhouse/databricks"]["new_keys"], ["101"])

    def test_a_posting_that_disappears_and_returns_is_not_new(self):
        self.baseline("R1")
        self.run_loop("R2", NORMAL, normal_script({ANTHROPIC_URL: Reply(body=greenhouse(gh_job(101)))}))
        result = self.run_loop("R3", NORMAL, normal_script())
        self.assertEqual(by_board(result)["greenhouse/anthropic"]["new_keys"], [])

    def test_an_edited_title_does_not_make_a_posting_new(self):
        self.baseline("R1")
        script = normal_script({ANTHROPIC_URL: Reply(body=greenhouse(gh_job(101, "Renamed Role"), gh_job(102)))})
        self.assertEqual(by_board(self.run_loop("R2", NORMAL, script))["greenhouse/anthropic"]["new_keys"], [])

    def test_ashby_postings_are_tracked_by_job_url(self):
        self.baseline("R1")
        script = normal_script({LINEAR_URL: Reply(body=ashby(ashby_job(U1), ashby_job(U2), ashby_job("u3-new")))})
        result = self.run_loop("R2", NORMAL, script)
        self.assertEqual(by_board(result)["ashby/linear"]["new_keys"], [ashby_url_key("u3-new")])

    def test_an_incomplete_run_does_not_use_up_a_baseline(self):
        self.run_loop("R1", WITH_FAILURE_CONTROL, normal_script({BAD_SLUG_URL: Reply(404, GH_404_BODY)}))
        result = self.baseline("R2")
        self.assertEqual([b["baseline"] for b in result["boards"]], [True, True, True])

    def test_provisional_new_postings_are_reported_again_by_the_next_finished_run(self):
        self.baseline("R1")
        new_anthropic = {ANTHROPIC_URL: Reply(body=greenhouse(gh_job(101), gh_job(102), RELEVANT_103))}
        failing = dict(new_anthropic, **{BAD_SLUG_URL: Reply(404, GH_404_BODY)})
        r2 = self.run_loop("R2", WITH_FAILURE_CONTROL, normal_script(failing))
        self.assertEqual((by_board(r2)["greenhouse/anthropic"]["new_keys"], by_board(r2)["greenhouse/anthropic"]["provisional"]),
                         (["103"], True))
        r3 = self.run_loop("R3", NORMAL, normal_script(new_anthropic))
        self.assertEqual(by_board(r3)["greenhouse/anthropic"]["new_keys"], ["103"])

    def test_conflicting_records_with_one_key_leave_the_board_unverified(self):
        script = normal_script({ANTHROPIC_URL: Reply(body=greenhouse(gh_job(101, "A"), gh_job(101, "B")))})
        result = self.run_loop("R1", NORMAL, script)
        anthropic = by_board(result)["greenhouse/anthropic"]
        self.assertEqual((anthropic["outcome"], anthropic["jobs"]), ("unverified", None))
        self.assertEqual(result["status"], "incomplete")


class TraceTest(LoopCase):
    def test_every_request_is_traced_with_board_time_elapsed_status_and_raw_file(self):
        self.run_loop("R1", WITH_FAILURE_CONTROL, normal_script({BAD_SLUG_URL: Reply(404, GH_404_BODY, seconds=0.1)}))
        trace = self.project.trace("R1")
        requests = [e for e in trace["events"] if e["event"] == "request"]
        self.assertEqual([(e["board"], e["status"]) for e in requests],
                         [("greenhouse/anthropic", 200), ("greenhouse/databricks", 200),
                          ("ashby/linear", 200), ("greenhouse/jobwatch-no-such-board-js2", 404)])
        for event in requests:
            raw = gzip.decompress((self.project.run_dir("R1") / event["raw"]).read_bytes())
            self.assertEqual(hashlib.sha256(raw).hexdigest(), event["sha256"])
            self.assertEqual(event["at"], WALL)
        self.assertAlmostEqual(requests[3]["elapsed_s"], 0.1)
        self.assertEqual(gzip.decompress((self.project.run_dir("R1") / requests[3]["raw"]).read_bytes()), GH_404_BODY)

    def test_the_raw_body_is_saved_even_when_it_cannot_be_parsed(self):
        result = self.run_loop("R1", NORMAL, normal_script({LINEAR_URL: Reply(200, b"<html>not json</html>")}))
        self.assertEqual(by_board(result)["ashby/linear"]["outcome"], "unverified")
        [event] = [e for e in self.project.trace("R1")["events"] if e.get("board") == "ashby/linear" and e["event"] == "request"]
        self.assertEqual(gzip.decompress((self.project.run_dir("R1") / event["raw"]).read_bytes()),
                         b"<html>not json</html>")

    def test_a_request_that_got_no_response_has_no_raw_file(self):
        self.run_loop("R1", NORMAL, normal_script({DATABRICKS_URL: Fail(ConnectionFailed)}))
        [event] = [e for e in self.project.trace("R1")["events"]
                   if e.get("board") == "greenhouse/databricks" and e["event"] == "request"]
        self.assertEqual((event["status"], event["raw"]), (None, None))
        self.assertIn("connection", event["reason"])

    def test_boards_a_budget_left_unchecked_are_in_the_trace(self):
        self.run_loop("R1", NORMAL, normal_script(), budget=Budget(max_requests=2))
        [event] = [e for e in self.project.trace("R1")["events"] if e["event"] == "not-checked"]
        self.assertEqual(event["board"], "ashby/linear")

    def test_the_trace_ends_with_the_exit_and_the_budget_used(self):
        result = self.run_loop("R1", WITH_FAILURE_CONTROL, normal_script({BAD_SLUG_URL: Reply(404, GH_404_BODY)}))
        trace = self.project.trace("R1")
        self.assertEqual(trace["events"][-1]["event"], "exit")
        self.assertEqual((trace["status"], trace["used"]["requests"], trace["used"]["boards"]), ("incomplete", 4, 4))
        self.assertEqual(trace["budget"], {"max_boards": 4, "max_requests": 4, "max_seconds": 30.0,
                                           "max_request_seconds": 5.0})
        self.assertEqual(result["used"], trace["used"])
        self.assertEqual(json.loads((self.project.run_dir("R1") / "results.json").read_text())["status"], "incomplete")


if __name__ == "__main__":
    unittest.main()
