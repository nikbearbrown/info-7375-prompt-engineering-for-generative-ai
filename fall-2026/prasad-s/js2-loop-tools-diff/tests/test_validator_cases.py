"""Runs tests/expected/validator_cases.json against the §6 reply validator."""

import unittest

from support import load_table, persona, table_posting

from agent.replies import validate_reply

TABLE = load_table("validator_cases.json")


class ValidatorCases(unittest.TestCase):
    def test_every_case(self):
        resume = persona()
        posting = table_posting(TABLE["posting"])
        for row in TABLE["cases"]:
            with self.subTest(case=row["id"]):
                result = validate_reply("\n".join(row["reply_lines"]), resume, posting)
                outcome = "accepted" if result.ok else "rejected"
                self.assertEqual(outcome, row["expect"], result.reasons)


if __name__ == "__main__":
    unittest.main()
