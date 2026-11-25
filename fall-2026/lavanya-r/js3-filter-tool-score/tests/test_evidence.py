"""Tests for the evidence rules (FILTER.md section 2), written before
agent/evidence.py. Postings and labels here are CONSTRUCTED for the test.
"""

import unittest

LONG = " Filler sentence about the team and its mission." * 6


def post(text):
    return {"key": "t/x/1", "title": "Software Engineer, Applied AI",
            "locations": ["San Francisco, CA"], "text": text + LONG}


def check(p, claim, label, quote):
    from agent import evidence
    return evidence.check_label(p, {"claim": claim, "label": label,
                                    "quote": quote})


class TestQuoteRule(unittest.TestCase):
    def test_supported_needs_a_quote_found_verbatim(self):
        p = post("You will build pipelines with MLflow and Databricks.")
        r = check(p, "The role uses MLflow.", "supported",
                  "build pipelines with MLflow")
        self.assertEqual(r["final"], "supported")

    def test_whitespace_and_curly_quotes_normalised(self):
        p = post("You’ll  build\npipelines with MLflow.")
        r = check(p, "The role uses MLflow.", "supported",
                  "You'll build pipelines with MLflow")
        self.assertEqual(r["final"], "supported")

    def test_quote_not_in_posting_is_insufficient(self):
        p = post("You will build pipelines with Spark.")
        r = check(p, "The role uses MLflow.", "supported",
                  "build pipelines with MLflow")
        self.assertEqual(r["final"], "insufficient")
        self.assertIn("quote not found", r["why"])

    def test_w5_word_present_but_no_quote_is_not_supported(self):
        # Wrong version W5: 'supported' because the word appears somewhere.
        p = post("Our recruiting team uses MLflow-style dashboards.")
        r = check(p, "The role uses MLflow.", "supported", "")
        self.assertEqual(r["final"], "insufficient")

    def test_contradicted_also_needs_a_quote(self):
        p = post("You have 5+ years of experience.")
        self.assertEqual(check(p, "Open to under one year of experience.",
                               "contradicted", "5+ years of experience")["final"],
                         "contradicted")
        self.assertEqual(check(p, "Open to under one year of experience.",
                               "contradicted", "")["final"], "insufficient")

    def test_title_and_location_count_as_posting_text(self):
        p = post("We build things.")
        self.assertEqual(check(p, "It is an AI role.", "supported",
                               "Applied AI")["final"], "supported")
        self.assertEqual(check(p, "It is in the US.", "supported",
                               "San Francisco, CA")["final"], "supported")

    def test_quote_may_include_the_prompts_field_labels(self):
        # Added after the first real check: Claude quoted "Title: ..." as the
        # labelling prompt showed it.
        p = post("We build things.")
        self.assertEqual(check(p, "It is an AI role.", "supported",
                               "Title: Software Engineer, Applied AI")["final"],
                         "supported")
        self.assertEqual(check(p, "It is an AI role.", "supported",
                               "Title: Data Scientist")["final"], "insufficient")

    def test_unknown_label_rejected(self):
        with self.assertRaises(ValueError):
            check(post("x"), "c", "probably", "x")


class TestAbstention(unittest.TestCase):
    def test_e1_short_text_abstains(self):
        from agent import evidence
        p = {"key": "t", "title": "Software Engineer", "locations": ["NYC"],
             "text": "Join us."}
        self.assertEqual(evidence.answer(p, [])["answer"], "I cannot tell")

    def test_e2_silent_on_sponsorship_abstains(self):
        from agent import evidence
        labels = [{"claim": "The employer will sponsor a US work visa.",
                   "topic": "sponsorship", "final": "insufficient"}]
        a = evidence.answer(post("We build agents."), labels)
        self.assertEqual(a["sponsorship"], "I cannot tell")

    def test_e3_conflicting_quotes_abstain(self):
        from agent import evidence
        labels = [{"claim": "Open to under one year of experience.",
                   "topic": "experience", "final": "supported"},
                  {"claim": "Open to under one year of experience.",
                   "topic": "experience", "final": "contradicted"}]
        a = evidence.answer(post("0-2 years. Also 5+ years."), labels)
        self.assertEqual(a["experience"], "I cannot tell")


if __name__ == "__main__":
    unittest.main()
