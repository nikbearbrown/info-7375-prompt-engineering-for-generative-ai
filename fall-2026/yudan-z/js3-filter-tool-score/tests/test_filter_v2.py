"""Tests for the v2 changes, one per kept step (SCORE-CHANGES.md)."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from agent import filter as filt  # noqa: E402

V1 = filt.load(os.path.join(ROOT, "filter", "filter-v1.json"))
V2 = filt.load(os.path.join(ROOT, "filter", "filter-v2.json"))
V3 = filt.load(os.path.join(ROOT, "filter", "filter-v3.json"))
V4 = filt.load(os.path.join(ROOT, "filter", "filter-v4.json"))
FILLER = " The team works across the company on many projects and partners closely with leaders." * 3


def post(title="Deployment Strategist", location="New York, NY, US", text=""):
    return {"key": "t/t/1", "title": title, "location": location, "text": text + FILLER}


class V2Tests(unittest.TestCase):
    def test_v2a_non_analyst_entry_role_reaches_mira(self):
        p = post(text="You will work with customers. We sponsor visas.")
        self.assertEqual(filt.score(p, V1)["decision"], "reject")
        self.assertEqual(filt.score(p, V2)["decision"], "keep")

    def test_v2b_clearance_is_excluded(self):
        r = filt.score(post(text="What We Require Active Top Secret Clearance. We sponsor visas."), V2)
        self.assertEqual(r["decision"], "reject")

    def test_v2c_immigration_sponsorship_phrase_is_contradicted(self):
        r = filt.score(post(text="This position is not eligible for immigration sponsorship."), V2)
        self.assertEqual(r["decision"], "reject")
        self.assertEqual(r["claims"][-1]["label"], "contradicted")
        # v1 read the same sentence as support: it mentions sponsorship (relevance, not entailment)
        self.assertEqual(filt.score(post(text="This position is not eligible for immigration sponsorship."), V1)["claims"][-1]["label"], "supported")

    def test_v2d_phd_title_is_excluded(self):
        self.assertEqual(filt.score(post(title="PhD Data Science Internship", text="We sponsor visas."), V2)["decision"], "reject")

    def test_v2_silence_on_sponsorship_still_abstains(self):
        self.assertEqual(filt.score(post(text="You will work with customers."), V2)["decision"], "cannot tell")

    def test_v2_senior_still_rejected(self):
        self.assertEqual(filt.score(post(title="Senior Deployment Strategist", text="We sponsor visas."), V2)["decision"], "reject")

    def test_v3_excel_the_verb_is_not_the_skill(self):
        verb = post(text="An inclusive culture where everyone can excel. We sponsor visas.")
        self.assertIn("Excel", filt.score(verb, V2)["parts"]["topics"])
        self.assertNotIn("Excel", filt.score(verb, V3)["parts"]["topics"])
        self.assertIn("Excel", filt.score(post(text="Advanced Excel and SQL. We sponsor visas."), V3)["parts"]["topics"])

    def test_v3_topic_words_cannot_rescue_a_senior_title(self):
        p = post(title="Sr Data Scientist", text="SQL, Python, Tableau, Excel, statistics. We sponsor visas.")
        self.assertEqual(filt.score(p, V3)["decision"], "reject")

    def test_v4_relevant_sentence_is_not_entailment(self):
        for sent in ("We will sponsor you for relocation if you need to move for this role.",
                     "Earn executive sponsorship and create urgency."):
            p = post(text=sent)
            self.assertEqual(filt.score(p, V3)["claims"][-1]["label"], "supported")  # the v3 bug
            r = filt.score(p, V4)
            self.assertEqual(r["claims"][-1]["label"], "insufficient")
            self.assertEqual(r["decision"], "cannot tell")

    def test_v4_a_real_sponsorship_sentence_is_supported(self):
        r = filt.score(post(text="Visa sponsorship is available for this role."), V4)
        self.assertEqual(r["claims"][-1]["label"], "supported")
        self.assertEqual(r["decision"], "keep")

    def test_v4_known_limit_a_qualified_yes_is_read_as_yes(self):
        """Counterexample to the abstention rule (SHORTLIST.md section 3). This test pins the WRONG
        behaviour on purpose, so that a future fix has to change it knowingly."""
        r = filt.score(post(text="Visa sponsorship is available for senior roles only."), V4)
        self.assertEqual(r["claims"][-1]["label"], "supported")
        self.assertEqual(r["decision"], "keep")


if __name__ == "__main__":
    unittest.main()
