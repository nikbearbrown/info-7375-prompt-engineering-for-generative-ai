"""Runs tests/expected/rule_cases.json against the §4 rule judge."""

import unittest

from support import load_table, persona, table_posting

from agent.rule import judge

TABLE = load_table("rule_cases.json")


class RuleCases(unittest.TestCase):
    def test_every_case(self):
        resume = persona()
        for row in TABLE["cases"]:
            with self.subTest(case=row["id"]):
                verdict, justification = judge(table_posting(row), resume)
                conditions = justification["conditions"]
                # All three conditions are always evaluated and reported (§4, §2).
                self.assertEqual(set(conditions), {"C1", "C2", "C3"})
                self.assertEqual(conditions["C1"]["result"], row["expect_C1"], "C1")
                self.assertEqual(conditions["C2"]["result"], row["expect_C2"], "C2")
                self.assertEqual(conditions["C3"]["result"], row["expect_C3"], "C3")
                self.assertEqual(verdict, row["expect_verdict"])


if __name__ == "__main__":
    unittest.main()
