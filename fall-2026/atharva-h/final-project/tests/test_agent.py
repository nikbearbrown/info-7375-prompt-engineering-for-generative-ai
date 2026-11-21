"""CONTRACT.md tests 4-11: the loop, its stops, the gate, state, and scoring."""

import json
import os
import stat
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from sponsorsql import agent, evaluate, gate
from sponsorsql.adapters import ClaudeCLIAdapter, ModelUnavailable, RecordedAdapter, ScriptedAdapter
from sponsorsql.config import Budget
from tests import fixtures

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "evals" / "PROMPT-CONTRACT-v1.md"
BOSTON_Q = "How many certified H-1B Data Analyst cases have a recorded worksite in Boston, MA?"
GOOD = fixtures.reply("SELECT COUNT(*) FROM (" + fixtures.BOSTON_ROWS_SQL + ")")


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.db = fixtures.build(self.dir / "fixture.sqlite")

    def tearDown(self):
        self.tmp.cleanup()

    def run_agent(self, question, replies, **kw):
        adapter = kw.pop("adapter", None) or ScriptedAdapter(replies)
        state = agent.run(question, adapter, self.db, CONTRACT, qid=kw.pop("qid", "T"),
                          expected_sha=fixtures.FIXTURE_SHA, state_dir=self.dir / "state",
                          outputs_dir=self.dir / "outputs", gate_mode=kw.pop("gate_mode", "none"), **kw)
        return state, adapter

    def test_good_answer_runs_and_shows_matching_rows(self):
        state, _ = self.run_agent(BOSTON_Q, [GOOD])
        self.assertEqual(state.stop_reason, "answered_not_released")
        self.assertEqual(state.result["rows"], [[3]])
        self.assertEqual(state.result["evidence_rows"], 3)
        self.assertIn("matches 3 matching rows", state.result["check"])

    # 5. contact and prediction questions are refused before any model call
    def test_screened_questions_never_reach_the_model(self):
        for q in ("What is the email of the employer contact at Example Data LLC?",
                  "Will my H-1B be approved if Sample Corp files for me?",
                  "What are my chances of getting sponsored by Fictional Inc?",
                  "Please delete the withdrawn rows from the table."):
            with self.subTest(q=q):
                state, adapter = self.run_agent(q, [GOOD])
                self.assertEqual(state.stop_reason, "refused_by_policy")
                self.assertEqual(adapter.calls, 0)

    # 6. unparseable replies are recorded, retried within budget, then stop
    def test_unparseable_replies_exhaust_the_proposal_budget(self):
        state, adapter = self.run_agent(BOSTON_Q, ["not json", "{also not json"])
        self.assertEqual(state.stop_reason, "budget_exhausted")
        self.assertEqual(adapter.calls, 2)
        self.assertEqual(sum(1 for s in state.steps if s["step"] == "reject_reply"), 2)

    def test_retry_after_unparseable_reply_can_succeed(self):
        state, adapter = self.run_agent(BOSTON_Q, ["not json", GOOD])
        self.assertEqual(state.stop_reason, "answered_not_released")
        self.assertEqual(adapter.calls, 2)

    # 7. a clarification request stops as a deferral and runs no SQL
    def test_clarification_defers_without_sql(self):
        state, _ = self.run_agent("What do analysts earn?", [fixtures.reply("", "", "", clarify=True)])
        self.assertEqual(state.stop_reason, "deferred_clarification")
        self.assertFalse(any(s["step"] == "act" for s in state.steps))

    def test_two_policy_denials_stop_the_loop(self):
        state, _ = self.run_agent(BOSTON_Q, [fixtures.reply("DELETE FROM lca"),
                                             fixtures.reply("SELECT * FROM metadata", answer_type="table")])
        self.assertEqual(state.stop_reason, "stopped_policy_denials")
        self.assertEqual(state.used["denials"], 2)

    def test_runaway_query_stops_on_budget(self):
        slow = fixtures.reply("SELECT COUNT(*) FROM lca a, lca b, lca c, lca d, lca e, lca f, lca g")
        state, _ = self.run_agent(BOSTON_Q, [slow], budget=replace(Budget(), statement_seconds=0.05))
        self.assertEqual(state.stop_reason, "budget_exhausted")

    def test_wrong_source_database_stops_before_anything_runs(self):
        adapter = ScriptedAdapter([GOOD])
        state = agent.run(BOSTON_Q, adapter, self.db, CONTRACT, state_dir=self.dir / "state",
                          outputs_dir=self.dir / "outputs", gate_mode="none")  # real checksum expected
        self.assertEqual(state.stop_reason, "source_mismatch")
        self.assertEqual(adapter.calls, 0)

    # 8. the gate exports only for an approval bound to this exact view
    def _approve_file(self, view_hash, decision="approve"):
        path = self.dir / "decision.json"
        path.write_text(json.dumps({"view_hash": view_hash, "decision": decision, "approver": "test"}))
        return path

    def test_matching_approval_exports_and_stale_approval_does_not(self):
        first, _ = self.run_agent(BOSTON_Q, [GOOD])           # learn the view hash
        good_file = self._approve_file(first.view_hash)
        approved, _ = self.run_agent(BOSTON_Q, [GOOD], gate_mode="file", decision_file=good_file)
        self.assertEqual(approved.stop_reason, "approved_and_exported")
        self.assertTrue(Path(approved.export_path).is_file())

        stale_file = self._approve_file("0" * 64)
        stale, _ = self.run_agent(BOSTON_Q, [GOOD], gate_mode="file", decision_file=stale_file)
        self.assertEqual(stale.stop_reason, "deferred_by_human")
        self.assertIsNone(stale.export_path)
        self.assertEqual(len(list((self.dir / "outputs").rglob("*.md"))), 1)  # only the approved one

    def test_refusal_and_interactive_gate(self):
        first, _ = self.run_agent(BOSTON_Q, [GOOD])
        refused, _ = self.run_agent(BOSTON_Q, [GOOD], gate_mode="file",
                                    decision_file=self._approve_file(first.view_hash, "refuse"))
        self.assertEqual(refused.stop_reason, "refused_by_human")
        answers = iter(["x", "d", "checking later"])
        shown = []
        deferred, _ = self.run_agent(BOSTON_Q, [GOOD], gate_mode="interactive",
                                     input_fn=lambda _: next(answers), output_fn=shown.append)
        self.assertEqual(deferred.stop_reason, "deferred_by_human")
        self.assertTrue(any("SQL that produced the answer" in s for s in shown))

    def test_export_refuses_without_matching_approval(self):
        bad = gate.Decision("approve", "test", "", "0" * 64)
        with self.assertRaises(PermissionError):
            gate.export_report(self.dir / "outputs", "x", "some view", bad)

    # 9. every run writes a state file and a ledger line with the stop reason
    def test_state_and_ledger_are_written(self):
        state, _ = self.run_agent(BOSTON_Q, [GOOD])
        saved = json.loads((self.dir / "state" / "runs" / f"{state.run_id}.json").read_text())
        self.assertEqual(saved["stop_reason"], "answered_not_released")
        ledger = (self.dir / "state" / "ledger.jsonl").read_text().splitlines()
        self.assertEqual(json.loads(ledger[-1])["stop_reason"], "answered_not_released")

    # 11. a count that disagrees with its matching rows is flagged
    def test_count_versus_rows_mismatch_is_flagged(self):
        state, _ = self.run_agent(BOSTON_Q, [fixtures.reply("SELECT 999")])
        self.assertIn("MISMATCH", state.result["check"])

    def test_recorded_adapter_replays_only_saved_replies(self):
        path = self.dir / "recorded.json"
        path.write_text(json.dumps({"provenance": {"source": "test", "date": "2026-11-21"},
                                    "responses": {"T": GOOD}}))
        state, _ = self.run_agent(BOSTON_Q, [], adapter=RecordedAdapter(path))
        self.assertEqual(state.stop_reason, "answered_not_released")
        missing, _ = self.run_agent(BOSTON_Q, [], adapter=RecordedAdapter(path), qid="nope")
        self.assertEqual(missing.stop_reason, "budget_exhausted")


class ScoringTests(unittest.TestCase):
    # 10. a known-wrong answer fails and a known-right answer passes
    KEY = {"q2_boston_cases": 40,
           "q5_wage_levels": {"I": 1027, "II": 1609, "[blank]": 402},
           "q1_massachusetts_employers_top10": [{"name": "A Corp", "cases": 8}, {"name": "B Inc", "cases": 5}]}

    def test_count_comparator(self):
        self.assertTrue(evaluate.compare("q2", ["n"], [[40]], self.KEY)[0])
        self.assertFalse(evaluate.compare("q2", ["n"], [[41]], self.KEY)[0])

    def test_level_comparator_treats_null_as_blank(self):
        rows = [["I", 1027], ["II", 1609], [None, 402]]
        self.assertTrue(evaluate.compare("q5", ["level", "cases"], rows, self.KEY)[0])
        rows[0][1] = 1026
        self.assertFalse(evaluate.compare("q5", ["level", "cases"], rows, self.KEY)[0])

    def test_ranking_comparator_trims_and_keeps_order(self):
        self.assertTrue(evaluate.compare("q1", ["e", "c"], [["A Corp ", 8], ["B Inc", 5]], self.KEY)[0])
        self.assertFalse(evaluate.compare("q1", ["e", "c"], [["B Inc", 5], ["A Corp", 8]], self.KEY)[0])


class ClaudeCLIAdapterTests(unittest.TestCase):
    """The live adapter, exercised against a stand-in script (no real model call)."""

    def _fake(self, body):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False)
        tmp.write("#!/usr/bin/env python3\nimport json, sys\n" + body)
        tmp.close()
        os.chmod(tmp.name, os.stat(tmp.name).st_mode | stat.S_IEXEC)
        self.addCleanup(os.remove, tmp.name)
        return tmp.name

    def test_success_returns_result_text(self):
        fake = self._fake('print(json.dumps({"is_error": False, "result": "{\\"ok\\": 1}"}))\n')
        self.assertEqual(ClaudeCLIAdapter(fake).propose("q", "prompt", 0), '{"ok": 1}')

    def test_not_logged_in_raises_model_unavailable(self):
        fake = self._fake('print(json.dumps({"is_error": True, "result": "Not logged in"})); sys.exit(1)\n')
        with self.assertRaises(ModelUnavailable):
            ClaudeCLIAdapter(fake).propose("q", "prompt", 0)


if __name__ == "__main__":
    unittest.main()
