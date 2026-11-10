"""The rule R1-R4, one test per branch, against the expected verdicts in tests/fixtures/README.md."""
import unittest

from tests import helpers


class RuleBranches(helpers.ContractTest):
    modules = ("agent.rules",)

    def judge(self, posting_id):
        return self.rules.evaluate(helpers.posting(posting_id), helpers.resume(), helpers.requirements())

    def assert_verdict(self, posting_id, verdict, failed_check):
        result = self.judge(posting_id)
        self.assertEqual(result["posting_id"], posting_id)
        self.assertEqual(result["verdict"], verdict)
        self.assertEqual(result["failed_check"], failed_check)
        self.assertEqual(result["label"], "record")
        if failed_check:
            failed = [c for c in result["citations"] if c["check"] == failed_check]
            self.assertTrue(failed, "the justification must name the check that failed")

    def test_r1_fail_title_has_no_data_term(self):
        self.assert_verdict(9000000001, "not_relevant", "R1")

    def test_r2_fail_manager_title(self):
        self.assert_verdict(9000000002, "not_relevant", "R2")

    def test_r3_fail_toronto(self):
        self.assert_verdict(9000000003, "not_relevant", "R3")

    def test_r3_fail_london(self):
        self.assert_verdict(9000000004, "not_relevant", "R3")

    def test_r3_pass_multi_city_with_one_us_part(self):
        self.assert_verdict(9000000005, "relevant", None)

    def test_r4_fail_only_unshipped_skills(self):
        self.assert_verdict(9000000006, "not_relevant", "R4")

    def test_r4_pass_skill_inside_html(self):
        self.assert_verdict(9000000007, "relevant", None)

    def test_all_checks_pass(self):
        result = self.judge(9000000008)
        self.assertEqual(result["verdict"], "relevant")
        self.assertEqual({c["check"] for c in result["citations"]}, {"R1", "R2", "R3", "R4"})


class RuleBoundaries(helpers.ContractTest):
    modules = ("agent.rules",)

    def judge_title(self, title):
        posting = dict(helpers.posting(9000000008), id=9000000099, title=title)
        return self.rules.evaluate(posting, helpers.resume(), helpers.requirements())

    def test_whole_word_lead_inside_leadership_does_not_exclude(self):
        self.assertEqual(self.judge_title("Data Analyst, Leadership Insights")["verdict"], "relevant")

    def test_whole_word_data_inside_metadata_does_not_match(self):
        self.assertEqual(self.judge_title("Metadata Designer")["failed_check"], "R1")

    def test_case_insensitive(self):
        self.assertEqual(self.judge_title("DATA ANALYST")["verdict"], "relevant")
        self.assertEqual(self.judge_title("data analyst intern")["failed_check"], "R2")

    def test_shipped_skills_are_exactly_the_four_lists(self):
        skills = self.rules.shipped_skills(helpers.resume(), helpers.requirements())
        self.assertEqual(
            [s for _, s in skills],
            ["Python", "SQL", "Databricks", "Unity Catalog", "Power BI",
             "LangGraph", "MLflow", "Mem0", "Delta Lake", "AWS"],
        )


if __name__ == "__main__":
    unittest.main()
