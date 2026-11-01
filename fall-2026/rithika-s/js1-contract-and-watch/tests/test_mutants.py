"""check_verdicts passes on the real rule and fails on each wrong version."""

import unittest

import fixtures
import mutants
from agent import rule
from agent.check import check_verdicts

RESUME, TARGET = fixtures.load_example_inputs()
POSTINGS = fixtures.ALL


class CheckerTests(unittest.TestCase):

    def test_checker_passes_on_real_implementation(self):
        verdicts = rule.evaluate_all(POSTINGS, RESUME, TARGET)
        self.assertEqual(check_verdicts(POSTINGS, verdicts), [])

    def test_checker_fails_on_misaligned_labels(self):
        verdicts = mutants.misaligned_labels(POSTINGS, RESUME, TARGET)
        # The mutant keeps ids aligned, so only the evidence check can see it.
        self.assertEqual([v["posting_id"] for v in verdicts],
                         [p["id"] for p in POSTINGS])
        problems = check_verdicts(POSTINGS, verdicts)
        self.assertTrue(problems)
        self.assertTrue(any("does not appear there" in p for p in problems),
                        problems)

    def test_checker_fails_on_empty_justification(self):
        verdicts = mutants.empty_justification(POSTINGS, RESUME, TARGET)
        problems = check_verdicts(POSTINGS, verdicts)
        self.assertEqual(len(problems), 2 * len(POSTINGS), problems)
        self.assertTrue(any("no résumé/target field" in p for p in problems))
        self.assertTrue(any("no posting field" in p for p in problems))

    def test_checker_flags_familiar_with_not_shipped_citation(self):
        posting = fixtures.ONE_SKILL
        verdict = rule.evaluate(posting, RESUME, TARGET)
        verdict["citations"].append({
            "field": "skills.familiar_with_not_shipped", "term": "Ray",
            "posting_fields": ["posting.content"], "matched": True})
        problems = check_verdicts([posting], [verdict])
        self.assertTrue(any("disallowed field" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
