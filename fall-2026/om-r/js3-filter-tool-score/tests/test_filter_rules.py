"""Rules 1 and 2 of FILTER.md v1.0.0, written BEFORE js3/filter.py existed.
Constructed fixtures only; no network. Run against the real module only
(the wrong stubs target the two wrong versions, not these rules)."""
import unittest

from tests.test_wrong_versions import posting


def classify(p):
    from js3.filter import classify as c
    return c(p)


class Rule1SkillWords(unittest.TestCase):
    def test_two_of_six_in_content_is_relevant(self):
        r = classify(posting(1, "Software Engineer", "We use Python to build RAG services."))
        self.assertEqual(r["bucket"], "relevant")
        self.assertEqual([m["skill"] for m in r["matched_skills"]], ["Python", "RAG"])

    def test_title_and_content_matches_combine(self):
        r = classify(posting(2, "LLM Engineer", "Strong Python required."))
        self.assertEqual(r["bucket"], "relevant")

    def test_one_of_six_is_rejected_with_reason(self):
        r = classify(posting(3, "Data Engineer", "Python, Spark and Airflow."))
        self.assertEqual(r["bucket"], "rejected")
        self.assertTrue(any("rule 1" in x for x in r["reasons"]), r["reasons"])

    def test_whole_word_case_insensitive(self):
        self.assertEqual(classify(posting(4, "x", "python and pytorch"))["bucket"], "relevant")
        # "Pythonic" and "drag" must not count as Python / RAG.
        self.assertEqual(classify(posting(5, "x", "Pythonic code, drag and drop"))["bucket"], "rejected")

    def test_plural_llms_is_the_documented_false_negative(self):
        # Inherited JS1 gap, kept on purpose (FILTER.md rule 1 reasoning).
        self.assertEqual(classify(posting(6, "x", "Python and LLMs"))["bucket"], "rejected")

    def test_multiword_skill_across_whitespace(self):
        r = classify(posting(7, "x", "Python with vector\n databases"))
        self.assertEqual(r["bucket"], "relevant")

    def test_greenhouse_escaped_html_is_unescaped_before_matching(self):
        r = classify(posting(8, "x", "&lt;li&gt;Python&lt;/li&gt;&lt;li&gt;PyTorch&lt;/li&gt;"))
        self.assertEqual(r["bucket"], "relevant")

    def test_matched_quote_is_exact_substring_of_field_text(self):
        from js3.filter import field_text
        p = posting(9, "x", "&lt;p&gt;Ship LLM features in Python daily.&lt;/p&gt;")
        for m in classify(p)["matched_skills"]:
            self.assertIn(m["quote"], field_text(p, m["field"]))


class Rule2SalesGtmExclusion(unittest.TestCase):
    SKILLS = "Python and LLM experience. "

    def test_sales_title_without_ai_building_phrase_is_rejected(self):
        r = classify(posting(10, "Account Executive, AI", self.SKILLS + "Sell our platform."))
        self.assertEqual(r["bucket"], "rejected")
        self.assertEqual(r["sales_title_word"], "Account Executive")
        self.assertTrue(any("rule 2" in x for x in r["reasons"]), r["reasons"])

    def test_sales_title_with_ai_building_phrase_is_relevant(self):
        r = classify(posting(11, "Solutions Architect", self.SKILLS + "You will fine-tune models."))
        self.assertEqual(r["bucket"], "relevant")
        self.assertEqual(r["ai_building_phrase"], "fine-tune")

    def test_each_listed_title_word_triggers(self):
        for word in ["Sales", "Account Executive", "Solutions Architect", "Compensation", "Recruiter", "HR"]:
            with self.subTest(word=word):
                r = classify(posting(12, f"Senior {word} Partner", self.SKILLS))
                self.assertEqual(r["bucket"], "rejected")

    def test_title_words_are_whole_word(self):
        # "HR" inside "Throughput", "Sales" inside "Salesforce" must not trigger.
        for title in ["Throughput Engineer", "Salesforce Developer"]:
            with self.subTest(title=title):
                self.assertEqual(classify(posting(13, title, self.SKILLS))["bucket"], "relevant")

    def test_sales_word_in_content_only_does_not_trigger(self):
        r = classify(posting(14, "ML Engineer", self.SKILLS + "Partner with Sales."))
        self.assertEqual(r["bucket"], "relevant")

    def test_ai_phrase_must_be_in_content_not_title(self):
        r = classify(posting(15, "Sales Engineer, LLM application", "Python and RAG."))
        self.assertEqual(r["bucket"], "rejected")

    def test_ai_phrases_are_literal(self):
        # FILTER.md lists "train", not "training": literal whole-word match.
        r = classify(posting(16, "Sales Engineer", self.SKILLS + "Customer training sessions."))
        self.assertEqual(r["bucket"], "rejected")


if __name__ == "__main__":
    unittest.main()
