"""Every wrong version must make the tests fail.

JS1: check_verdicts passes on the real rule and fails on each wrong version.
JS2: the JS2 suite passes on the real agent and fails on each of W1-W11
from GATE.md section 6 (mutants in tests/mutants.py).
"""

import io
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


# The JS2 suite the mutants are run against.
JS2_SUITE = ("test_policy", "test_loop", "test_budgets_config",
             "test_independent_check")


def run_js2_suite():
    suite = unittest.TestSuite(
        unittest.defaultTestLoader.loadTestsFromName(name)
        for name in JS2_SUITE)
    result = unittest.TextTestRunner(stream=io.StringIO(),
                                     verbosity=0).run(suite)
    failed = {test.id().rsplit(".", 1)[-1]
              for test, _ in result.failures + result.errors}
    return result, failed


class GateMutantTests(unittest.TestCase):
    """GATE.md section 6: the JS2 suite fails on every wrong version."""

    def test_js2_suite_passes_on_real_agent(self):
        result, failed = run_js2_suite()
        self.assertTrue(result.wasSuccessful(), sorted(failed))
        self.assertGreater(result.testsRun, 0)

    def test_every_gate_wrong_version_has_a_mutant(self):
        names = {key.split("-")[0] for key in mutants.GATE_MUTANTS}
        self.assertEqual(names, {f"W{i}" for i in range(1, 12)})

    def test_js2_suite_fails_on_every_mutant(self):
        for name, (mutant, must_fail) in mutants.GATE_MUTANTS.items():
            with self.subTest(mutant=name):
                with mutant():
                    result, failed = run_js2_suite()
                self.assertFalse(result.wasSuccessful(),
                                 f"{name} survived the JS2 suite")
                self.assertIn(must_fail, failed,
                              f"{name}: failing tests were {sorted(failed)}")
        # Every patch was undone: the real agent passes again.
        result, failed = run_js2_suite()
        self.assertTrue(result.wasSuccessful(), sorted(failed))


if __name__ == "__main__":
    unittest.main()
