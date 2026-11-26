"""Evidence rules (FILTER.md §3) and wrong version 3. Offline."""
import unittest

from js3.evidence import abstain, label_claim, label_justification
from js3.filter import load_filter
from tests.wrong_versions import absence_as_support_label

FLT = load_filter()
SEN = FLT["seniority_veto_title"]
BODY = ("You will build ML pipelines in Python and SQL on Databricks. "
        "We are looking for 2+ years of experience shipping models. " * 6)
POST = {"uid": "t:1", "title": "ML Engineer", "location": "Boston, MA", "text": BODY}


def C(kind, term, quote, claim="x"):
    return {"kind": kind, "term": term, "quote": quote, "claim": claim}


class TestLabels(unittest.TestCase):
    def test_supported_needs_verbatim_quote_with_term(self):
        self.assertEqual(label_claim(C("skill", "Python", "ML pipelines in Python and SQL"), POST, SEN)[0], "supported")

    def test_quote_case_and_spacing_ignored(self):
        self.assertEqual(label_claim(C("skill", "SQL", "PYTHON  and   sql"), POST, SEN)[0], "supported")

    def test_paraphrased_quote_is_insufficient(self):
        self.assertEqual(label_claim(C("skill", "Python", "uses Python daily"), POST, SEN)[0], "insufficient")

    def test_quote_without_the_term_is_insufficient(self):
        self.assertEqual(label_claim(C("skill", "MLflow", "ML pipelines in Python"), POST, SEN)[0], "insufficient")

    def test_experience_number_must_be_in_quote(self):
        self.assertEqual(label_claim(C("experience", "2 years", "2+ years of experience shipping models"), POST, SEN)[0], "supported")
        self.assertEqual(label_claim(C("experience", "3 years", "2+ years of experience"), POST, SEN)[0], "insufficient")

    def test_experience_contradicted_by_five_plus(self):
        p = {**POST, "text": BODY + " Requires 6+ years of experience in distributed systems."}
        self.assertEqual(label_claim(C("experience", "2 years", "2+ years of experience shipping models"), p, SEN)[0], "contradicted")

    def test_seniority_contradicted_by_title(self):
        p = {**POST, "title": "Staff ML Engineer"}
        self.assertEqual(label_claim(C("seniority", "not senior", "ML Engineer"), p, SEN)[0], "contradicted")

    def test_degree_contradicted(self):
        p = {**POST, "text": BODY + " A PhD in machine learning is required."}
        self.assertEqual(label_claim(C("degree", "no PhD", ""), p, SEN)[0], "contradicted")

    def test_skill_not_required_is_contradicted(self):
        p = {**POST, "text": BODY + " Prior Spark experience is not required."}
        self.assertEqual(label_claim(C("skill", "Spark", "Prior Spark experience"), p, SEN)[0], "contradicted")


class TestWrongVersion3(unittest.TestCase):
    def test_wv3_absence_as_support_is_caught(self):
        empty = {"uid": "t:2", "title": "ML Engineer", "text": ""}
        claim = C("experience", "3 years", "", "does not require more than 3 years")
        self.assertEqual(absence_as_support_label(claim, empty), "supported")  # the wrong version
        self.assertEqual(label_claim(claim, empty, SEN)[0], "insufficient")


class TestAbstain(unittest.TestCase):
    def test_short_text_abstains(self):
        p = {"uid": "t:3", "title": "ML Engineer", "text": "Join us."}
        lab = label_justification([C("role", "ML Engineer", "ML Engineer")], p, SEN)
        self.assertTrue(abstain(p, lab, {"decision": "keep"}, 300))

    def test_half_insufficient_abstains(self):
        lab = label_justification([C("skill", "Python", "ML pipelines in Python"),
                                   C("skill", "Ray", "we use Ray")], POST, SEN)
        self.assertTrue(abstain(POST, lab, {"decision": "keep"}, 300))

    def test_mostly_supported_answers(self):
        lab = label_justification([C("skill", "Python", "ML pipelines in Python"),
                                   C("skill", "SQL", "Python and SQL"),
                                   C("role", "ML Engineer", "ML Engineer")], POST, SEN)
        self.assertEqual(abstain(POST, lab, {"decision": "keep"}, 300), [])


if __name__ == "__main__":
    unittest.main()
