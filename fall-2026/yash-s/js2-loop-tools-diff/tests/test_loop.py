"""Tests for the bounded loop (agent.py) against GATE.md sections 1-4 and 6.

run from the js2-loop-tools-diff folder:
  python3 -m unittest discover -s tests -v

Offline: a fake network answers from a script, and a fake clock controls time.
Wrong versions (GATE.md section 6):
  1 failed board reported as zero new jobs -> test_wrong_version_1_failed_board_is_not_zero_new
  2 string-prefix folder check             -> test_policy.Files.test_08_look_alike_folder_prefix_refused
  3 retries not counted against the budget -> test_wrong_version_3_every_retry_counts
"""
import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
sys.path.insert(0, str(FOLDER))
import agent  # noqa: E402
import policy  # noqa: E402

PERSONA = FOLDER / "persona" / "priya-nair.resume.example.json"
NOW = datetime(2026, 11, 9, 12, 0, 0, tzinfo=timezone.utc)


def gh(*jobs):
    """A constructed Greenhouse-shaped response."""
    return json.dumps({"jobs": [{"id": i, "title": t, "content": "&lt;p&gt;Python and SQL&lt;/p&gt;",
                                 "location": {"name": "Remote - US"}, "absolute_url": f"https://example.com/{i}"}
                                for i, t in jobs]}).encode()


def ashby(*jobs):
    """A constructed Ashby-shaped response."""
    return json.dumps({"jobs": [{"id": i, "title": t, "descriptionHtml": "<p>Python</p>", "location": "San Francisco",
                                 "jobUrl": f"https://example.com/{i}"} for i, t in jobs]}).encode()


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class LoopTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for d in ("config", "runs", "state", "persona"):
            (self.root / d).mkdir()
        shutil.copy(PERSONA, self.root / "persona" / "resume.json")
        self.clock = FakeClock()
        self.calls = []

    def boards(self, *specs):
        return [{"name": n, "ats": a, "slug": s} for n, a, s in specs]

    def run_agent(self, boards, script, per_request=0.0, config=None, persona=None):
        cfg = self.root / "config" / "run.json"
        cfg.write_text(json.dumps(config if config is not None else {"boards": boards}))

        def get(url, timeout, board, pol):
            self.calls.append({"slug": board["slug"], "url": url, "timeout": timeout})
            self.clock.t += per_request
            outcome = script[board["slug"]].pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome
        return agent.run(cfg, self.root / "runs", self.root / "state", [self.root / "persona", self.root / "config"],
                         persona or self.root / "persona" / "resume.json", get=get, clock=self.clock, now=NOW)

    def board(self, summary, name):
        return next(b for b in summary["boards"] if b["name"] == name)

    def write_state(self, ats, slug, ids):
        (self.root / "state" / f"{ats}-{slug}.state.json").write_text(json.dumps({"board": slug, "seen_ids": ids}))


THREE = (("Databricks", "greenhouse", "databricks"), ("Anthropic", "greenhouse", "anthropic"), ("OpenAI", "ashby", "openai"))


class Exits(LoopTest):
    """GATE.md section 1."""

    def ok_script(self):
        return {"databricks": [(200, gh((1, "Data Engineer")))], "anthropic": [(200, gh((7, "ML Engineer")))],
                "openai": [(200, ashby(("a-1", "AI Engineer")))]}

    def test_every_board_ok_is_finished(self):
        s, _ = self.run_agent(self.boards(*THREE), self.ok_script())
        self.assertEqual((s["exit_status"], s["exit_code"]), ("finished", 0))
        self.assertEqual(s["used"]["requests"], 3)

    def test_wrong_version_1_failed_board_is_not_zero_new(self):
        script = self.ok_script() | {"databricks-misspelled": [(404, b'{"status": 404}')]}
        s, _ = self.run_agent(self.boards(*THREE, ("Deliberate failure", "greenhouse", "databricks-misspelled")), script)
        bad = self.board(s, "Deliberate failure")
        self.assertEqual((s["exit_status"], s["exit_code"]), ("incomplete", 1))
        self.assertEqual((bad["status"], bad["error"], bad["postings"]), ("failed", "HTTP 404", None))
        self.assertNotIn("Deliberate failure", {p["board"] for p in s["new_postings"]})
        self.assertIn("failed", (self.root / "runs" / s["run"] / "report.md").read_text().split("Deliberate failure")[1].split("\n")[0])

    def test_404_is_never_retried(self):
        self.run_agent(self.boards(("Bad", "greenhouse", "nope")), {"nope": [(404, b"")]})
        self.assertEqual(len(self.calls), 1)

    def test_timeout_is_retried_once_and_counted(self):
        s, _ = self.run_agent(self.boards(("Databricks", "greenhouse", "databricks")),
                              {"databricks": [agent.Temporary("timeout"), (200, gh((1, "x")))]})
        self.assertEqual((s["exit_status"], s["used"]["requests"], self.board(s, "Databricks")["attempts"]), ("finished", 2, 2))

    def test_two_timeouts_leave_the_board_unavailable(self):
        s, _ = self.run_agent(self.boards(("Databricks", "greenhouse", "databricks")),
                              {"databricks": [agent.Temporary("timeout"), agent.Temporary("timeout")]})
        self.assertEqual((s["exit_status"], self.board(s, "Databricks")["status"]), ("incomplete", "unavailable"))
        self.assertEqual(len(self.calls), 2)

    def test_server_error_is_retried_once(self):
        s, _ = self.run_agent(self.boards(("Databricks", "greenhouse", "databricks")),
                              {"databricks": [(503, b"busy"), (200, gh((1, "x")))]})
        self.assertEqual((s["exit_status"], len(self.calls)), ("finished", 2))

    def test_board_budget(self):
        five = self.boards(*THREE, ("Figma", "greenhouse", "figma"), ("Notion", "ashby", "notion"))
        script = self.ok_script() | {"figma": [(200, gh((3, "x")))], "notion": [(200, ashby(("n", "y")))]}
        s, _ = self.run_agent(five, script)
        self.assertEqual((s["exit_status"], s["budget_hit"]), ("budget-exhausted", "boards"))
        self.assertEqual(self.board(s, "Notion")["status"], "not checked")
        self.assertEqual(len(self.calls), 4)

    def test_wrong_version_3_every_retry_counts(self):
        specs = (*THREE, ("Figma", "greenhouse", "figma"))
        script = {slug: [agent.Temporary("t"), agent.Temporary("t")] for _, _, slug in specs}
        s, _ = self.run_agent(self.boards(*specs), script)
        self.assertEqual(len(self.calls), agent.BUDGETS["requests"])
        self.assertEqual((s["exit_status"], s["budget_hit"], s["used"]["requests"]), ("budget-exhausted", "requests", 6))
        self.assertEqual(self.board(s, "Figma")["status"], "not checked")

    def test_time_budget(self):
        s, _ = self.run_agent(self.boards(*THREE), self.ok_script(), per_request=70.0)
        self.assertEqual((s["exit_status"], s["budget_hit"]), ("budget-exhausted", "seconds"))
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(self.board(s, "OpenAI")["status"], "not checked")

    def test_no_request_gets_more_time_than_is_left(self):
        self.run_agent(self.boards(*THREE), self.ok_script(), per_request=50.0)
        self.assertEqual([c["timeout"] for c in self.calls], [30.0, 30.0, 20.0])

    def test_policy_violation_is_an_error_and_stops(self):
        script = self.ok_script() | {"databricks": [policy.PolicyViolation("refusing redirect (302)")]}
        s, _ = self.run_agent(self.boards(*THREE), script)
        self.assertEqual((s["exit_status"], s["exit_code"]), ("error", 2))
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.board(s, "OpenAI")["status"], "not checked")

    def test_corrupted_state_is_an_error_and_is_not_overwritten(self):
        bad = self.root / "state" / "greenhouse-databricks.state.json"
        bad.write_text("not json")
        s, _ = self.run_agent(self.boards(*THREE), self.ok_script())
        self.assertEqual(s["exit_status"], "error")
        self.assertEqual(bad.read_text(), "not json")

    def test_unknown_ats_is_an_error_before_any_request(self):
        s, _ = self.run_agent(None, {}, config={"boards": [{"name": "X", "ats": "lever", "slug": "x"}]})
        self.assertEqual((s["exit_status"], len(self.calls)), ("error", 0))

    def test_a_config_cannot_set_budgets(self):
        s, _ = self.run_agent(None, {}, config={"boards": [{"name": "D", "ats": "greenhouse", "slug": "databricks"}],
                                                "budgets": {"requests": 100}})
        self.assertEqual((s["exit_status"], len(self.calls)), ("error", 0))

    def test_a_real_looking_resume_is_refused(self):
        fake = self.root / "persona" / "real.json"
        fake.write_text(json.dumps({"personal": {"email": "someone@mail.test", "phone": "(617) 555-0100"}}))
        s, _ = self.run_agent(self.boards(*THREE), self.ok_script(), persona=fake)
        self.assertEqual((s["exit_status"], len(self.calls)), ("error", 0))


class RepeatRule(LoopTest):
    """GATE.md section 3."""

    def test_the_same_request_is_made_once(self):
        s, _ = self.run_agent(self.boards(("Databricks", "greenhouse", "databricks"), ("Again", "greenhouse", "databricks")),
                              {"databricks": [(200, gh((1, "x")))]})
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.board(s, "Again")["repeat_of"], "Databricks")
        self.assertEqual(s["exit_status"], "finished")


class Responses(LoopTest):
    """GATE.md section 4: what counts as an observation."""

    def test_invalid_json_fails_the_board_keeps_raw_and_state(self):
        self.write_state("greenhouse", "databricks", [1])
        s, run_dir = self.run_agent(self.boards(("Databricks", "greenhouse", "databricks")),
                                    {"databricks": [(200, b'{"jobs": [ {"id": ')]})
        self.assertEqual((s["exit_status"], self.board(s, "Databricks")["status"]), ("incomplete", "failed"))
        self.assertEqual((run_dir / "raw-greenhouse-databricks-attempt1-http200.json").read_bytes(), b'{"jobs": [ {"id": ')
        self.assertEqual(json.loads((self.root / "state" / "greenhouse-databricks.state.json").read_text())["seen_ids"], [1])

    def test_missing_jobs_list_fails_the_board(self):
        s, _ = self.run_agent(self.boards(("Databricks", "greenhouse", "databricks")), {"databricks": [(200, b'{"error": 1}')]})
        self.assertEqual(self.board(s, "Databricks")["status"], "failed")

    def test_a_well_formed_empty_list_is_a_valid_observation(self):
        """GATE.md: the agent accepts {"jobs": []}. This is the finished-wrong-answer case the
        independent checker must catch; see test_independent_check."""
        self.write_state("greenhouse", "databricks", [1, 2, 3])
        s, _ = self.run_agent(self.boards(("Databricks", "greenhouse", "databricks")), {"databricks": [(200, b'{"jobs": []}')]})
        self.assertEqual((s["exit_status"], self.board(s, "Databricks")["postings"]), ("finished", 0))


class State(LoopTest):
    """GATE.md section 4, State Updates, and the JS1 rules carried over."""

    def test_baseline_reports_zero_new_and_records_every_id(self):
        s, _ = self.run_agent(self.boards(("Anthropic", "greenhouse", "anthropic")), {"anthropic": [(200, gh((7, "a"), (8, "b")))]})
        b = self.board(s, "Anthropic")
        self.assertEqual((b["baseline"], b["new_count"]), (True, 0))
        self.assertEqual(json.loads((self.root / "state" / "greenhouse-anthropic.state.json").read_text())["seen_ids"], [7, 8])

    def test_only_ids_not_seen_before_are_new(self):
        self.write_state("greenhouse", "databricks", [1])
        s, _ = self.run_agent(self.boards(("Databricks", "greenhouse", "databricks")),
                              {"databricks": [(200, gh((1, "old"), (2, "Data Engineer")))]})
        self.assertEqual([p["id"] for p in s["new_postings"]], [2])
        self.assertIn(s["new_postings"][0]["record"], ("relevant", "not relevant"))

    def test_ashby_string_ids_are_tracked(self):
        self.write_state("ashby", "openai", ["a-1"])
        s, _ = self.run_agent(self.boards(("OpenAI", "ashby", "openai")), {"openai": [(200, ashby(("a-1", "x"), ("a-2", "y")))]})
        self.assertEqual([p["id"] for p in s["new_postings"]], ["a-2"])

    def test_a_failed_board_keeps_its_previous_state(self):
        self.write_state("greenhouse", "databricks", [1, 2])
        before = (self.root / "state" / "greenhouse-databricks.state.json").read_bytes()
        self.run_agent(self.boards(("Databricks", "greenhouse", "databricks")), {"databricks": [(404, b"")]})
        self.assertEqual((self.root / "state" / "greenhouse-databricks.state.json").read_bytes(), before)

    def test_a_posting_that_returns_is_not_new(self):
        self.write_state("greenhouse", "databricks", [1, 2])
        self.run_agent(self.boards(("Databricks", "greenhouse", "databricks")), {"databricks": [(200, gh((1, "a")))]})
        s, _ = self.run_agent(self.boards(("Databricks", "greenhouse", "databricks")), {"databricks": [(200, gh((1, "a"), (2, "b")))]})
        self.assertEqual(s["new_postings"], [])

    def test_the_js1_state_format_is_accepted(self):
        (self.root / "state" / "greenhouse-databricks.state.json").write_text(json.dumps(
            {"board": "databricks", "updated_at": "2026-10-31T06:18:34Z", "last_run_file": "run.json", "seen_ids": [1]}))
        s, _ = self.run_agent(self.boards(("Databricks", "greenhouse", "databricks")), {"databricks": [(200, gh((1, "a"), (5, "b")))]})
        self.assertEqual([p["id"] for p in s["new_postings"]], [5])


class Evidence(LoopTest):
    """GATE.md: raw first, create-only, and a trace of every action."""

    def test_raw_response_saved_byte_for_byte(self):
        body = gh((1, "x"))
        s, run_dir = self.run_agent(self.boards(("Databricks", "greenhouse", "databricks")), {"databricks": [(200, body)]})
        self.assertEqual((run_dir / "raw-greenhouse-databricks-attempt1-http200.json").read_bytes(), body)

    def test_two_runs_in_the_same_second_keep_separate_folders(self):
        _, a = self.run_agent(self.boards(("D", "greenhouse", "databricks")), {"databricks": [(200, gh((1, "x")))]})
        _, b = self.run_agent(self.boards(("D", "greenhouse", "databricks")), {"databricks": [(200, gh((1, "x")))]})
        self.assertNotEqual(a, b)
        self.assertTrue((a / "summary.json").exists() and (b / "summary.json").exists())

    def test_trace_records_every_request_retry_observation_and_the_exit(self):
        s, run_dir = self.run_agent(self.boards(("D", "greenhouse", "databricks"), ("Bad", "greenhouse", "nope")),
                                    {"databricks": [agent.Temporary("t"), (200, gh((1, "x")))], "nope": [(404, b"")]})
        events = [json.loads(line) for line in (run_dir / "trace.jsonl").read_text().splitlines()]
        kinds = [e["event"] for e in events]
        self.assertEqual(kinds.count("request"), 3)
        self.assertEqual(kinds.count("retry"), 1)
        self.assertEqual(kinds.count("observation"), 3)
        self.assertEqual(events[-1], events[-1] | {"event": "exit", "status": "incomplete"})


if __name__ == "__main__":
    unittest.main()
