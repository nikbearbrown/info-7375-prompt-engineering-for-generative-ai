"""One change to one object at a time, and how a flip is judged. CONSTRUCTED postings."""
import json
import unittest

from helpers import ROOT, evaluate, rules
import experiment as X

ONE_TOPIC = "<p>You will build data pipelines.</p><p>Python.</p>"  # one topic, one skill, no year count
X1 = {"id": "X1", "path": ["scoring", "threshold"], "from": 65, "to": 55}
X2 = {"id": "X2", "path": ["titles", "related_min_topics"], "from": 1, "to": 2, "default": 1}


class OneChange(unittest.TestCase):
    def test_exactly_one_value_changes_and_the_original_is_untouched(self):
        base = rules()
        new = X.apply_change(base, X1)
        self.assertEqual(new["filter"]["scoring"]["threshold"], 55)
        self.assertEqual(base["filter"]["scoring"]["threshold"], 65)
        diff = {k for k, v in X.leaves(new["filter"]).items() if X.leaves(base["filter"]).get(k) != v}
        self.assertEqual(diff, {("scoring", "threshold")})

    def test_a_change_whose_starting_value_is_wrong_is_refused(self):
        with self.assertRaises(ValueError):
            X.apply_change(rules(), {**X1, "from": 70})

    def test_a_setting_absent_from_the_rules_uses_its_default(self):
        self.assertNotIn("related_min_topics", rules()["filter"]["titles"])
        self.assertEqual(X.apply_change(rules(), X2)["filter"]["titles"]["related_min_topics"], 2)

    def test_threshold_55_moves_a_55_point_posting_from_rejected_to_review(self):
        kw = dict(title="Software Engineer, Payments", body=ONE_TOPIC)
        base = evaluate(**kw)
        self.assertEqual((base["score"], base["decision"], base["decision_step"]), (55, "rejected", 2))
        self.assertEqual(evaluate(rules=X.apply_change(rules(), X1), **kw)["decision"], "review")

    def test_two_topic_rule_turns_a_one_topic_related_title_into_no_role(self):
        kw = dict(title="Software Engineer, Payments", body=ONE_TOPIC)
        self.assertEqual(evaluate(**kw)["role"], "related")
        changed = evaluate(rules=X.apply_change(rules(), X2), **kw)
        self.assertEqual((changed["role"], changed["decision"]), ("none", "rejected"))

    def test_the_registered_candidates_all_apply_cleanly(self):
        cand = json.loads((ROOT / "experiments" / "candidates.json").read_text(encoding="utf-8"))
        self.assertTrue(cand["changes"])
        for ch in cand["changes"]:
            with self.subTest(ch=ch["id"]):
                X.apply_change(rules(), ch)


class JudgingAFlip(unittest.TestCase):
    flip = {"from": "rejected", "to": "review"}

    def test_outcomes(self):
        self.assertEqual(X.score_flip(self.flip, "review"), "improved")
        self.assertEqual(X.score_flip(self.flip, "confirmed"), "improved")
        self.assertEqual(X.score_flip(self.flip, "rejected"), "regressed")
        self.assertEqual(X.score_flip(self.flip, "cannot tell"), "cannot tell")
        self.assertEqual(X.score_flip(self.flip, None), "unlabeled")
        self.assertEqual(X.score_flip({"from": "review", "to": "rejected"}, "rejected"), "improved")

    def test_verdict_words_from_both_sheets(self):
        self.assertEqual(X.judged({"MY_VERDICT": "should have been kept for review"}), "review")
        self.assertEqual(X.judged({"MY_VERDICT": "Keep for review"}), "review")
        self.assertEqual(X.judged({"MY_VERDICT": "reject"}), "rejected")
        self.assertIsNone(X.judged({"MY_VERDICT": "  "}))
        with self.assertRaises(ValueError):
            X.judged({"MY_VERDICT": "maybe", "board": "b", "posting_id": "1"})


class WhatTheLabelsSay(unittest.TestCase):
    @staticmethod
    def rows(*outcomes):
        return [{"outcome": o} for o in outcomes]

    def test_every_flip_labeled_is_a_count_not_an_estimate(self):
        text = " ".join(X.what_the_labels_say({"flip_count": 4}, self.rows("improved", "regressed"),
                                              self.rows("improved", "improved")))
        self.assertIn("count, not an estimate", text)
        self.assertIn("3 better and 1 worse", text)
        self.assertNotIn("Wilson", text)

    def test_a_sample_is_estimated_over_the_flips_outside_the_tuning_labels(self):
        text = " ".join(X.what_the_labels_say({"flip_count": 44}, self.rows("improved", "regressed", "regressed"),
                                              self.rows(*["improved"] * 9 + ["regressed"] * 6)))
        self.assertIn("random sample of the 41 flips", text)
        self.assertIn("do not show", text)  # 36%-80% includes 50%


class Intervals(unittest.TestCase):
    def test_known_values(self):
        lo, hi = X.wilson(1, 30)
        self.assertAlmostEqual(lo, 0.0059, places=4)
        self.assertAlmostEqual(hi, 0.1667, places=4)
        lo, hi = X.exact(1, 30)
        self.assertAlmostEqual(lo, 0.000844, places=5)
        self.assertAlmostEqual(hi, 0.1722, places=4)
        self.assertAlmostEqual(X.exact(0, 30)[1], 0.1157, places=4)
        self.assertIsNone(X.wilson(0, 0))


if __name__ == "__main__":
    unittest.main()
