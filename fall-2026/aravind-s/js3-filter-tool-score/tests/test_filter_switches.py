"""The two optional v1.1 switches in job_agent/filter.py: absent (as in FILTER.md v1.0), nothing changes.

splitter_keeps keeps "U.S." (and the like) inside a sentence; ranking.caution_penalty takes points off a kept posting
that has an export-control caution. Both are candidates measured in js3/score/, not adopted rules.
"""

import copy
import unittest

from job_agent import filter as flt

from .test_filter import posting

RULES = flt.load_rules(version="1.0")
JANE = flt.load_profile()


class SwitchesTest(unittest.TestCase):
    def test_v1_0_has_neither_switch(self):
        self.assertNotIn("splitter_keeps", RULES)
        self.assertNotIn("caution_penalty", RULES["ranking"])

    def test_splitter_keeps_us_inside_a_sentence_only_when_asked(self):
        text = "Applicants must be U.S. citizens with an active clearance. We build APIs."
        self.assertIn("Applicants must be U.S.", flt.split_sentences(text)[0])
        kept, _ = flt.split_sentences(text, ["U.S.", "e.g.", "i.e."])
        self.assertEqual(kept, ["Applicants must be U.S. citizens with an active clearance.", "We build APIs."])

    def test_splitter_keeps_leaves_the_month_fix_alone(self):
        sentences, merges = flt.split_sentences("Start in Dec. 2026 in the U.S. office.", ["U.S."])
        self.assertEqual(sentences, ["Start in Dec. 2026 in the U.S. office."])
        self.assertEqual(merges, ["Start in Dec. 2026 in the U.S. office."])

    def test_caution_penalty_only_when_set(self):
        p = posting(description="We build APIs and design SQL schemas. To comply with U.S. export control laws, "
                                "candidates may need to meet legal status requirements.")
        base = flt.judge(p, JANE, RULES)
        self.assertEqual(base["fate"], "kept")
        self.assertTrue(base["cautions"])
        rules = copy.deepcopy(RULES)
        rules["ranking"]["caution_penalty"] = -10
        changed = flt.judge(p, JANE, rules)
        self.assertEqual(changed["score"], base["score"] - 10)
        self.assertEqual(changed["fate"], "kept")  # a penalty moves the score, never the fate

    def test_v1_0_judgments_unchanged_by_the_new_code(self):
        p = posting(description="To comply with a U.S. government contract, applicants must be U.S. citizens.")
        record = flt.judge(p, JANE, RULES)
        self.assertEqual((record["fate"], record["deciding_rule"]), ("rejected", "R5"))


if __name__ == "__main__":
    unittest.main()
