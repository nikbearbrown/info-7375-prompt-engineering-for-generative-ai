"""Tests for the JS3 filter, written from FILTER.md before agent/filter.py existed."""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import filter as filt  # noqa: E402

CFG = filt.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "filter", "filter-v1.json"))
FILLER = " The team works across the company on many projects and partners closely with leaders." * 3


def post(title="Data Analyst", location="New York, NY, US", text=""):
    return {"key": "t/t/1", "title": title, "location": location, "text": text + FILLER}


def claim(result, name):
    return [c for c in result["claims"] if c["claim"] == name][0]


class FilterTests(unittest.TestCase):
    def test_keep_basic_role_and_topics(self):
        r = filt.score(post(text="You will use SQL and Python. Visa sponsorship is available."), CFG)
        self.assertEqual(r["score"], 6)
        self.assertTrue(r["keep"])
        self.assertFalse(r["abstain"])

    def test_senior_title_is_penalised(self):
        r = filt.score(post(title="Senior Data Analyst", text="SQL and Python. We sponsor visas."), CFG)
        self.assertEqual(r["score"], 3)
        self.assertFalse(r["keep"])

    def test_w1_whole_words_only(self):
        r = filt.score(post(title="Analyticsplatform Engineer", text="Excellent communication. Pythonic style."), CFG)
        self.assertEqual(r["parts"]["role"], [])
        self.assertEqual(r["parts"]["topics"], [])

    def test_w2_topic_words_cannot_beat_role(self):
        stuffed = filt.score(post(title="Software Engineer", text="SQL Python Tableau Looker Excel dashboards statistics A/B testing. We sponsor visas."), CFG)
        role = filt.score(post(title="Data Analyst", text="SQL. We sponsor visas."), CFG)
        self.assertFalse(stuffed["keep"])
        self.assertLess(stuffed["score"], role["score"])

    def test_w3_missing_location_abstains(self):
        r = filt.score(post(location="", text="SQL and Python. We sponsor visas."), CFG)
        self.assertTrue(r["abstain"])
        self.assertFalse(r["keep"])
        self.assertEqual(claim(r, "the job is in the US")["label"], "insufficient")

    def test_w4_silence_is_insufficient_not_supported(self):
        r = filt.score(post(text="SQL and Python."), CFG)
        self.assertEqual(claim(r, "the posting does not rule out sponsorship")["label"], "insufficient")
        self.assertTrue(r["abstain"])

    def test_no_sponsorship_phrase_is_contradicted(self):
        r = filt.score(post(text="SQL and Python. We will not sponsor visas for this role."), CFG)
        self.assertEqual(claim(r, "the posting does not rule out sponsorship")["label"], "contradicted")
        self.assertFalse(r["keep"])

    def test_short_description_abstains(self):
        r = filt.score({"key": "t/t/2", "title": "Data Analyst", "location": "New York, NY, US", "text": "SQL."}, CFG)
        self.assertTrue(r["abstain"])

    def test_every_claim_has_a_label_and_evidence(self):
        r = filt.score(post(text="SQL and Python. Visa sponsorship is available."), CFG)
        for c in r["claims"]:
            self.assertIn(c["label"], ("supported", "contradicted", "insufficient"))
            self.assertIn("evidence", c)

    def test_threshold_and_weights_come_from_the_file(self):
        cfg = copy.deepcopy(CFG)
        cfg["threshold"] = 7
        r = filt.score(post(text="You will use SQL and Python. Visa sponsorship is available."), cfg)
        self.assertFalse(r["keep"])


if __name__ == "__main__":
    unittest.main()
