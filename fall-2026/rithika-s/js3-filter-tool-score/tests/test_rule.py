"""Rule tests on CONSTRUCTED postings."""

import unittest

import fixtures
from agent import rule

RESUME, TARGET = fixtures.load_example_inputs()


def verdict_for(posting):
    return rule.evaluate(posting, RESUME, TARGET)


class RuleTests(unittest.TestCase):

    def test_all_conditions_hold_is_relevant_with_field_paths(self):
        v = verdict_for(fixtures.RELEVANT)
        self.assertEqual(v["verdict"], "relevant")
        self.assertIsNone(v["failed_condition"])
        self.assertIn("skills.languages: Python matched in posting.content",
                      v["justification"])
        self.assertIn("skills.data_bi: Databricks matched in posting.content",
                      v["justification"])
        self.assertIn("target.target_title_keywords: machine learning matched "
                      "in posting.title", v["justification"])

    def test_exclusion_wins_over_title_and_skills(self):
        v = verdict_for(fixtures.EXCLUDED)
        self.assertEqual(v["verdict"], "not_relevant")
        self.assertEqual(v["failed_condition"], 1)
        self.assertIn("target.excluded_terms: clearance matched in "
                      "posting.content", v["justification"])

    def test_exclusion_in_title_also_wins(self):
        posting = fixtures.constructed(
            9100, "ML Engineer (Clearance Required)",
            "<p>Python, SQL, AWS.</p>")
        v = verdict_for(posting)
        self.assertEqual(v["failed_condition"], 1)
        self.assertEqual(v["citations"][0]["posting_fields"], ["posting.title"])

    def test_title_gate(self):
        v = verdict_for(fixtures.WRONG_TITLE)
        self.assertEqual((v["verdict"], v["failed_condition"]),
                         ("not_relevant", 2))
        self.assertIn("target.target_title_keywords: ai engineer not matched "
                      "in posting.title", v["justification"])

    def test_exactly_one_skill_is_not_relevant(self):
        v = verdict_for(fixtures.ONE_SKILL)
        self.assertEqual((v["verdict"], v["failed_condition"]),
                         ("not_relevant", 3))
        matched = [c["term"] for c in v["citations"] if c["matched"]]
        self.assertEqual(matched, ["Python"])

    def test_exactly_two_skills_is_relevant(self):
        v = verdict_for(fixtures.TWO_SKILLS)
        self.assertEqual(v["verdict"], "relevant")
        skills = [c["term"] for c in v["citations"]
                  if c["field"].startswith("skills.")]
        self.assertEqual(skills, ["Python", "AWS"])

    def test_sql_does_not_match_inside_postgresql(self):
        content = rule.prepare(fixtures.ONE_SKILL["content"])
        self.assertIn("postgresql", content)
        self.assertFalse(rule.contains(content, "SQL"))
        self.assertTrue(rule.contains("we use sql.", "SQL"))
        self.assertFalse(rule.contains("nosql stores", "SQL"))

    def test_ray_and_kubeflow_never_count(self):
        v = verdict_for(fixtures.ONE_SKILL)
        fields = {c["field"] for c in v["citations"]}
        self.assertNotIn("skills.familiar_with_not_shipped", fields)
        only_familiar = fixtures.constructed(
            9101, "ML Engineer", "<p>Ray, Kubeflow, Ray Serve.</p>")
        self.assertEqual(verdict_for(only_familiar)["failed_condition"], 3)

    def test_html_entities_are_unescaped(self):
        self.assertIn("&amp;", fixtures.ENTITIES["content"])
        self.assertEqual(rule.prepare(fixtures.ENTITIES["content"]),
                         "power bi reports, mlflow&langgraph agents.")
        v = verdict_for(fixtures.ENTITIES)
        self.assertEqual(v["verdict"], "relevant")
        matched = {c["term"] for c in v["citations"]
                   if c["matched"] and c["field"].startswith("skills.")}
        self.assertEqual(matched, {"Power BI", "MLflow", "LangGraph"})

    def test_title_match_is_whole_word(self):
        posting = fixtures.constructed(
            9102, "Senior Email Engineer", "<p>Python and SQL.</p>")
        self.assertEqual(verdict_for(posting)["failed_condition"], 2)


if __name__ == "__main__":
    unittest.main()
