"""Runs tests/expected/refusal_cases.json: the fetch allow-list and the persona check.

JS2: the URL cases run through agent.policy, built from this folder's
config.json (CONTRACT v0.5 items 1-2, v0.6 item 3), since JS1's one-URL
check is superseded. The table itself is unchanged.
"""

import copy
import unittest

from support import JS1, load_table, persona

from agent.config import parse_config
from agent.persona import persona_refusal_reasons
from agent.policy import Policy, PolicyRefusal

TABLE = load_table("refusal_cases.json")


class UrlCases(unittest.TestCase):
    def test_every_case(self):
        config = parse_config((JS1 / "config.json").read_bytes())
        policy = Policy(JS1, config.board_pairs)
        for row in TABLE["url_cases"]:
            with self.subTest(case=row["id"]):
                try:
                    policy.check("fetch", row["url"])
                    outcome, reasons = "allowed", []
                except PolicyRefusal as exc:
                    outcome, reasons = "refused", exc.reasons
                self.assertEqual(outcome, row["expect"], reasons)


class ResumeCases(unittest.TestCase):
    def test_every_case(self):
        base = persona()
        for row in TABLE["resume_cases"]:
            with self.subTest(case=row["id"]):
                resume = copy.deepcopy(base)
                resume.update(copy.deepcopy(row.get("change", {})))
                for field in row.get("remove", []):
                    del resume[field]
                reasons = persona_refusal_reasons(resume)
                outcome = "runs" if not reasons else "refused"
                self.assertEqual(outcome, row["expect"], reasons)


if __name__ == "__main__":
    unittest.main()
