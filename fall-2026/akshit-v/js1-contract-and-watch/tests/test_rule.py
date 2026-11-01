"""The rule, step by step, on CONSTRUCTED postings."""
import unittest

from agent import rule
from tests.helpers import JACK, constructed_posting


def verdict(title, content=""):
    return rule.judge(constructed_posting(1, title, content), JACK)


class Step1Disqualify(unittest.TestCase):
    def test_each_disqualifying_word(self):
        for word in rule.DISQUALIFYING_WORDS:
            r = verdict(f"{word} Data Engineer", "Python SQL Spark Airflow Kafka dbt")
            self.assertEqual(r["verdict"], "not_relevant", word)
            self.assertEqual(r["branch"], "disqualified", word)

    def test_disqualifying_stops_checking(self):
        r = verdict("Staff Data Engineer", "Python SQL Spark Airflow")
        self.assertEqual(r["skills_found"], [])

    def test_senior_and_lead_are_allowed(self):
        self.assertEqual(verdict("Senior Data Engineer", "Python SQL Spark")["verdict"], "relevant")
        self.assertEqual(verdict("Lead Data Engineer", "Python SQL Spark")["verdict"], "relevant")

    def test_words_not_substrings(self):
        # "Internal" is not the word "Intern"; "Contractor" is not "Contract" (contract says "words").
        self.assertNotEqual(verdict("Internal Data Platform Engineer", "Python SQL Spark")["branch"], "disqualified")


class Step2to4(unittest.TestCase):
    def test_a_title_match_and_3_skills(self):
        r = verdict("Data Platform Engineer", "Python, SQL and Spark")
        self.assertEqual((r["verdict"], r["title_matches"]), ("relevant", ["Data Platform"]))

    def test_a_title_match_with_2_skills_is_not_enough(self):
        self.assertEqual(verdict("Data Engineer", "Python and SQL")["verdict"], "not_relevant")

    def test_b_no_title_match_needs_4(self):
        self.assertEqual(verdict("Backend Engineer", "Python SQL Spark Kafka")["verdict"], "relevant")
        self.assertEqual(verdict("Backend Engineer", "Python SQL Spark")["verdict"], "not_relevant")

    def test_title_match_is_case_insensitive(self):
        self.assertEqual(verdict("senior data engineer", "python sql spark")["verdict"], "relevant")

    def test_justification_cites_fields_and_evidence(self):
        r = verdict("Data Platform Engineer", "Python, SQL and Spark")
        self.assertEqual(r["cited_resume_fields"], ["target_titles", "skills"])
        self.assertEqual(r["cited_posting_fields"], ["title", "content"])
        for evidence in ("Data Platform", "Python", "SQL", "Spark"):
            self.assertIn(evidence, r["because"])


if __name__ == "__main__":
    unittest.main()
