"""Each wrong version in mutants.py is caught; the real agent passes the same check."""
import unittest

from tests import helpers, mutants


def misaligned_ids(verdicts):
    """Ids whose verdict differs from the one predicted by hand for that posting."""
    expected = {p["id"]: p["expected_verdict"] for p in helpers.postings()}
    return [v["posting_id"] for v in verdicts if v["verdict"] != expected[v["posting_id"]]]


class Mutants(helpers.ContractTest):
    modules = ("agent.rules", "agent.validator")

    def uncited_or_unsupported(self, verdicts):
        """Verdicts with no citation, or with a citation the support check rejects."""
        by_id = {p["id"]: p for p in helpers.postings()}
        bad = []
        for v in verdicts:
            supports = [self.validator.support_check(c, by_id[v["posting_id"]]) for c in v["citations"]]
            if not supports or "not supported" in supports:
                bad.append(v["posting_id"])
        return bad

    def judge(self, judge_all):
        return judge_all(helpers.postings(), helpers.resume(), helpers.requirements())

    def test_1_shifted_labels_are_caught(self):
        self.assertEqual(misaligned_ids(self.judge(self.rules.judge_all)), [])
        self.assertNotEqual(misaligned_ids(self.judge(mutants.shifted_judge_all)), [])

    def test_2_uncited_justification_is_caught(self):
        self.assertEqual(self.uncited_or_unsupported(self.judge(self.rules.judge_all)), [])
        self.assertNotEqual(self.uncited_or_unsupported(self.judge(mutants.uncited_judge_all)), [])

    def test_3_skills_read_from_string_is_caught(self):
        r4_fail = helpers.posting(9000000006)
        real = self.rules.evaluate(r4_fail, helpers.resume(), helpers.requirements())
        wrong = self.rules.evaluate(r4_fail, helpers.resume(), helpers.requirements(),
                                    skills_fn=mutants.string_skills)
        self.assertEqual(real["failed_check"], "R4")
        self.assertNotEqual(wrong["failed_check"], "R4",
                            "the mutant should wrongly match single letters such as 'a'")
        self.assertTrue(any(len(s) == 1 for _, s in mutants.string_skills(helpers.resume(), helpers.requirements())))


if __name__ == "__main__":
    unittest.main()
