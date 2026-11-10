"""The five checks in CONTRACT.md, one boundary at a time. Postings here are
constructed (see fixtures.py)."""

import unittest

from agent import rule
from tests.fixtures import RELEVANT, resume, variant


def failed(verdict):
    return [c["check"] for c in verdict["justification"] if not c["passed"]]


class TestRule(unittest.TestCase):
    def setUp(self):
        self.resume = resume()

    def judge(self, p):
        return rule.judge(p, self.resume)

    def test_all_five_pass_is_relevant(self):
        v = self.judge(RELEVANT)
        self.assertEqual(v["verdict"], "relevant")
        self.assertEqual(failed(v), [])
        self.assertEqual(v["kind"], "record")

    def test_every_check_is_reported_even_after_a_failure(self):
        v = self.judge(variant(title="Senior Account Executive",
                               location="Paris, France", body="<p>Hi</p>"))
        self.assertEqual(len(v["justification"]), 5)
        self.assertEqual(failed(v), ["good_title", "no_bad_title_word",
                                     "us_location", "at_least_2_skills"])

    # 1. good title
    def test_title_without_good_word_fails(self):
        self.assertEqual(failed(self.judge(variant(title="Data Engineer"))),
                         ["good_title"])

    def test_software_engineering_intern_passes_via_intern_only(self):
        v = self.judge(variant(title="Software Engineering Intern (Summer)"))
        self.assertEqual(v["verdict"], "relevant")
        self.assertEqual(v["justification"][0]["matched"], ["Intern"])

    def test_internal_is_not_intern_and_maintain_is_not_ai(self):
        v = self.judge(variant(title="Maintainer, Internal Tools"))
        self.assertIn("good_title", failed(v))

    def test_ai_slash_ml_matches_both(self):
        v = self.judge(variant(title="AI/ML Engineer"))
        self.assertEqual(v["justification"][0]["matched"], ["AI", "ML"])

    # 2. bad title word
    def test_bad_word_rules_out_even_with_good_word(self):
        for title in ["Senior AI Engineer", "Sr. Software Engineer",
                      "Staff ML Engineer", "Manager I, Applied AI",
                      "Sales Engineer - AI Accounts",
                      "AI Research Scientist", "Tech Lead, ML"]:
            with self.subTest(title=title):
                v = self.judge(variant(title=title))
                self.assertEqual(v["verdict"], "not_relevant")
                self.assertIn("no_bad_title_word", failed(v))

    def test_leading_is_not_lead(self):
        v = self.judge(variant(title="AI Engineer, Leading-edge Agents"))
        self.assertEqual(v["verdict"], "relevant")

    # 3. US location
    def test_any_us_part_of_a_multi_location_counts(self):
        v = self.judge(variant(location="Paris, France; New York, New York, USA"))
        self.assertEqual(v["verdict"], "relevant")
        self.assertEqual(v["justification"][2]["matched"],
                         ["New York, New York, USA"])

    def test_us_remote_counts_and_non_us_fails(self):
        self.assertEqual(self.judge(variant(location="California, USA, Remote"))
                         ["verdict"], "relevant")
        self.assertEqual(failed(self.judge(variant(location="Paris, France"))),
                         ["us_location"])

    def test_rule_v2_state_names_count_as_us(self):
        # Databricks' real formats from the 2026-10-30 run 2 response.
        for loc in ["San Francisco, California", "New York City, New York",
                    "Bellevue, Washington; Seattle, Washington",
                    "Washington, D.C.", "Remote - California"]:
            with self.subTest(loc=loc):
                self.assertEqual(self.judge(variant(location=loc))["verdict"],
                                 "relevant")

    def test_rule_v2_non_us_still_fails(self):
        for loc in ["Bengaluru, India", "Toronto, Canada", "London, United "
                    "Kingdom", "Mexico City, Mexico", "Singapore"]:
            with self.subTest(loc=loc):
                self.assertEqual(failed(self.judge(variant(location=loc))),
                                 ["us_location"])

    # 4. at least 2 skills, whole words
    def test_one_skill_is_not_enough(self):
        self.assertEqual(failed(self.judge(variant(body="<p>Python only</p>"))),
                         ["at_least_2_skills"])

    def test_postgresql_and_nosql_do_not_count_as_sql(self):
        v = self.judge(variant(body="<p>Python with PostgreSQL and NoSQL</p>"))
        self.assertEqual(v["justification"][3]["matched"], ["Python"])

    def test_familiar_with_not_shipped_does_not_count(self):
        v = self.judge(variant(body="<p>Ray and Kubeflow</p>"))
        self.assertEqual(v["justification"][3]["matched"], [])

    def test_multi_word_skill_and_cited_resume_fields(self):
        v = self.judge(variant(body="<p>Delta&nbsp;Lake on Databricks</p>"))
        check = v["justification"][3]
        self.assertEqual(check["matched"], ["Databricks", "Delta Lake"])
        self.assertEqual(check["resume_fields"],
                         ["skills.data_bi", "skills.database_cloud"])

    # 5. no "we can't sponsor"
    def test_visa_phrase_rules_out(self):
        for body in ["We are unable to sponsor visas.",
                     "Datadog can’t sponsor for this role.",
                     "Must be authorized to work without sponsorship."]:
            with self.subTest(body=body):
                v = self.judge(variant(body=f"<p>Python, AWS. {body}</p>"))
                self.assertEqual(failed(v), ["no_cant_sponsor"])

    def test_event_sponsor_wording_does_not_rule_out(self):
        # The real 2026-10-29 Datadog board used "sponsor" only like this.
        v = self.judge(variant(body="<p>Python, AWS. Plan sponsored events "
                               "and act as executive sponsor.</p>"))
        self.assertEqual(v["verdict"], "relevant")

    def test_sponsor_check_skipped_when_persona_needs_no_sponsorship(self):
        self.resume["work_authorization"]["needs_sponsorship"] = False
        v = self.judge(variant(body="<p>Python, AWS. Unable to sponsor.</p>"))
        self.assertEqual(v["verdict"], "relevant")


if __name__ == "__main__":
    unittest.main()
