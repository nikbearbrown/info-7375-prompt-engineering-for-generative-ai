"""Runs tests/expected/refusal_cases.json: the fetch allow-list and the persona check."""

import copy
import unittest

from support import JS1, load_table, persona

from agent.config import load_config, url_refusal_reasons
from agent.persona import persona_refusal_reasons

TABLE = load_table("refusal_cases.json")


class UrlCases(unittest.TestCase):
    def test_every_case(self):
        allow_list = load_config(JS1 / "config.json")["allow_list"]
        for row in TABLE["url_cases"]:
            with self.subTest(case=row["id"]):
                reasons = url_refusal_reasons(row["url"], allow_list)
                outcome = "allowed" if not reasons else "refused"
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
