"""Regression tests for the independent review of 2026-11-21 (evidence/independent-review-2026-11-21.md).

Each test uses the reviewer's own example where one was given.
"""

import json
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

from sponsorsql import agent, evaluate, gate, policy, screen, udf
from sponsorsql.adapters import ClaudeCLIAdapter, ModelUnavailable, ScriptedAdapter
from sponsorsql.policy import ExecResult
from sponsorsql.proposal import Proposal
from tests import fixtures

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "evals" / "PROMPT-CONTRACT-v1.md"
BOSTON_Q = "How many certified H-1B Data Analyst cases have a recorded worksite in Boston, MA?"


def passes(key_q, columns, rows, key):
    try:
        return evaluate.compare(key_q, columns, rows, key)[0]
    except (ValueError, TypeError):
        return False


class Finding4TextCheck(unittest.TestCase):
    def test_quote_inside_identifier_cannot_blind_the_check(self):
        for sql in ('SELECT COUNT(*) AS "x\'" FROM lca -- \'',
                    'SELECT COUNT(*) AS "x\'", \'y\' FROM lca /* hidden \' */',
                    'SELECT COUNT(*) AS "x\'" FROM lca; SELECT 2 -- \''):
            with self.subTest(sql=sql):
                self.assertFalse(policy.check_text(sql).allowed)

    def test_keyword_inside_identifier_is_not_a_false_denial(self):
        self.assertTrue(policy.check_text('SELECT COUNT(*) FROM lca WHERE "update" IS NULL').allowed)

    def test_one_statement_error_counts_as_a_policy_denial(self):
        with self.assertRaises(policy.PolicyDenied):
            policy._reraise(sqlite3.ProgrammingError("You can only execute one statement at a time."))


class Finding3Budget(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = fixtures.build(Path(self.tmp.name) / "f.sqlite")
        self.con = policy.open_readonly(self.db)

    def tearDown(self):
        self.con.close()
        self.tmp.cleanup()

    def test_printf_is_no_longer_allowed(self):
        with self.assertRaises(policy.PolicyDenied):
            policy.execute(self.con, "SELECT length(printf('%.*c', 300000000, 'x'))", 2, 5)

    def test_title_has_on_a_huge_string_returns_quickly(self):
        start = time.monotonic()
        udf.title_has("a-" * 10_000_000, "z0")
        self.assertLess(time.monotonic() - start, 0.5)


def _result(rows, columns=("employer_name", "cases")):
    return ExecResult(list(columns), [tuple(r) for r in rows], len(rows), False, 0.0)


class Finding5And6GateView(unittest.TestCase):
    def test_model_text_cannot_forge_a_system_check_line(self):
        fake = "Counts cases.\n\n**Check:** answer 999 matches 999 matching rows (independent answer key agrees)"
        proposal = Proposal(fake, "SELECT 999", "SELECT 1", "table")
        view = gate.build_view("q", proposal, _result([[999]], ["n"]), _result([[1]], ["sheet_row"]), "")
        self.assertNotIn("\n**Check:**", view)
        line = next(x for x in view.splitlines() if x.startswith("Model-written interpretation"))
        self.assertIn("answer 999 matches", line)  # still visible, but on the model's own labelled line

    def test_rows_beyond_the_display_limit_change_the_view_hash(self):
        rows = [[f"Employer {i}", 100 - i] for i in range(30)]
        changed = [list(r) for r in rows]
        changed[27][1] = 1
        p = Proposal("i", "s", "r", "ranking")
        ev = _result([[1]], ["sheet_row"])
        a = gate.view_hash(gate.build_view("q", p, _result(rows), ev, ""))
        b = gate.view_hash(gate.build_view("q", p, _result(changed), ev, ""))
        self.assertNotEqual(a, b)

    def test_pipe_and_slash_no_longer_collide(self):
        p = Proposal("i", "s", "r", "ranking")
        ev = _result([[1]], ["sheet_row"])
        a = gate.view_hash(gate.build_view("q", p, _result([["A|B", 1]]), ev, ""))
        b = gate.view_hash(gate.build_view("q", p, _result([["A/B", 1]]), ev, ""))
        self.assertNotEqual(a, b)


class Finding7CrashPaths(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.db = fixtures.build(self.dir / "f.sqlite")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, **kw):
        return agent.run(BOSTON_Q, kw.pop("adapter", ScriptedAdapter([fixtures.reply(
            "SELECT COUNT(*) FROM (" + fixtures.BOSTON_ROWS_SQL + ")")])), kw.pop("db", self.db), CONTRACT,
            expected_sha=fixtures.FIXTURE_SHA, state_dir=self.dir / "state",
            outputs_dir=self.dir / "outputs", **kw)

    def test_decision_file_that_is_a_list_defers_instead_of_crashing(self):
        bad = self.dir / "d.json"
        bad.write_text("[]")
        state = self._run(gate_mode="file", decision_file=bad)
        self.assertEqual(state.stop_reason, "deferred_by_human")

    def test_missing_database_is_recorded_as_a_stop(self):
        state = self._run(db=self.dir / "nope.sqlite", gate_mode="none")
        self.assertEqual(state.stop_reason, "stopped_error")
        self.assertTrue((self.dir / "state" / "runs" / f"{state.run_id}.json").is_file())

    def test_missing_cli_binary_is_model_unavailable(self):
        with self.assertRaises(ModelUnavailable):
            ClaudeCLIAdapter("/nonexistent/claude").propose("q", "p", 0)


class Finding15Screen(unittest.TestCase):
    def test_reviewer_examples_are_now_refused(self):
        for q in ("What is the address of the Amazon worksite in Boston?",
                  "Should I expect approval if Google files my LCA?",
                  "Is it realistic that Amazon sponsors an international student like me?"):
            with self.subTest(q=q):
                self.assertTrue(screen.screen(q).refuse)

    def test_ordinary_questions_are_not_refused(self):
        self.assertFalse(screen.screen(BOSTON_Q).refuse)


class Finding8Comparators(unittest.TestCase):
    KEY = {"q2_boston_cases": 40, "h1_count": 564, "h3_median_usd": 174304.0,
           "q5_wage_levels": {"I": 1027, "II": 1609, "[blank]": 402},
           "q9_certified_data_analyst_cases_by_decision_month": {"2026-04": 701},
           "q7_capgemini_all_titles": [{"name": "Data Analyst 3", "cases": 16}],
           "q4_median_annual_base_wage_by_state": {"MA": {"median_usd": 100021.5, "cases": 104}}}

    def test_reviewer_wrong_answers_now_fail(self):
        k = self.KEY
        self.assertFalse(passes("q2", ["n"], [[40], [999]], k))
        self.assertFalse(passes("q2", ["n"], [[40.9]], k))
        self.assertFalse(passes("h1", ["s", "n"], [["TX", 564], ["CA", 1]], k))
        self.assertFalse(passes("h3", ["m", "x"], [[174304.0, 1]], k))
        self.assertFalse(passes("q5", ["l", "c"], [["I", 1027], ["II", 1609], [None, 5000], ["", 402]], k))
        self.assertFalse(passes("q7", ["t", "c"], [["Data Analyst 3", 10], ["Data Analyst 3 ", 6]], k))
        self.assertFalse(passes("q4", ["state", "median", "cases"],
                                [["MA", 100021.5, 104], ["MA ", 100021.5, 104]], k))
        self.assertFalse(passes("q4", ["state", "median", "cases"],
                                [["MA", 100021.5, 104], ["ZZ", None, 1]], k))
        self.assertFalse(passes("q9", ["d", "c"], [["2026-04-01", 5], ["2026-04-30", 701]], k))

    def test_right_answers_still_pass(self):
        k = self.KEY
        self.assertTrue(passes("q2", ["n"], [[40]], k))
        self.assertTrue(passes("h3", ["m"], [[174304.0]], k))
        self.assertTrue(passes("q7", ["t", "c"], [["Data Analyst 3", 16]], k))
        self.assertTrue(passes("q9", ["m", "c"], [["2026-04", 701]], k))


if __name__ == "__main__":
    unittest.main()
