"""GATE.md, Budgets: the numbers in the code are the numbers in GATE.md, and a flag may only lower them
(wrong version 4c: a flag that raises a budget)."""

import re
import unittest
from pathlib import Path

from job_agent import gate
from job_agent.errors import Refused

GATE = (Path(__file__).resolve().parent.parent / "GATE.md").read_text(encoding="utf-8")


def table_number(label: str) -> int:
    match = re.search(rf"^\| {re.escape(label)} \| (\d+)", GATE, re.MULTILINE)
    if not match:
        raise AssertionError(f"GATE.md has no budget row {label!r}")
    return int(match.group(1))


class GateNumbersTest(unittest.TestCase):
    def test_the_budgets_match_the_gate_table(self):
        self.assertEqual(table_number("Boards"), gate.MAX_BOARDS)
        self.assertEqual(table_number("HTTP requests, retries included"), gate.MAX_REQUESTS)
        self.assertEqual(table_number("Claude calls"), gate.MAX_CLAUDE_CALLS)
        self.assertEqual(table_number("Wall clock"), gate.MAX_SECONDS)

    def test_the_request_timeout_and_the_retry_wait_match_the_gate(self):
        self.assertIn(f"One request may take at most {gate.REQUEST_TIMEOUT} seconds.", GATE)
        self.assertIn(f"one retry after {gate.RETRY_WAIT} seconds", GATE)

    def test_the_exit_codes_match_the_gate_table(self):
        for status, code in gate.EXIT_CODES.items():
            self.assertRegex(GATE, rf"\| {re.escape(status)} \| {code} \|")
        self.assertIn(f"| error | {gate.BROKEN_INPUT_CODE} or {gate.REFUSED_CODE} |", GATE)

    def test_the_gate_version_is_the_one_the_file_states(self):
        self.assertIn(f"Version {gate.GATE_VERSION},", GATE)


class LoweringTest(unittest.TestCase):
    def test_a_flag_may_lower_a_budget(self):
        lowered = gate.Budgets().lowered(requests=3, claude_calls=0)
        self.assertEqual((lowered.requests, lowered.claude_calls, lowered.boards, lowered.seconds),
                         (3, 0, gate.MAX_BOARDS, gate.MAX_SECONDS))

    def test_a_flag_that_raises_a_budget_is_refused(self):
        # Wrong version 4c: a flag that raises a budget.
        for name, limit in (("boards", gate.MAX_BOARDS), ("requests", gate.MAX_REQUESTS),
                            ("claude_calls", gate.MAX_CLAUDE_CALLS), ("seconds", gate.MAX_SECONDS)):
            with self.subTest(budget=name):
                with self.assertRaises(Refused) as caught:
                    gate.Budgets().lowered(**{name: limit + 1})
                self.assertIn("new version of GATE.md", str(caught.exception))

    def test_the_same_value_as_the_limit_is_not_a_raise(self):
        self.assertEqual(gate.Budgets().lowered(requests=gate.MAX_REQUESTS).requests, gate.MAX_REQUESTS)

    def test_a_negative_or_non_number_value_is_refused(self):
        for value in (-1, "5", 2.5, True):
            with self.subTest(value=value):
                with self.assertRaises(Refused):
                    gate.Budgets().lowered(requests=value)


if __name__ == "__main__":
    unittest.main()
