"""Agreement counting and the exact interval. Labels and records here are CONSTRUCTED."""

import math
import unittest

from jobwatch import measure


def rec(fate, score=2):
    return {"fate": fate, "score": score}


class CompareTest(unittest.TestCase):
    def test_each_outcome(self):
        labels = {("b", "1"): "yes", ("b", "2"): "no", ("b", "3"): "no", ("b", "4"): "yes", ("b", "5"): "cannot tell",
                  ("b", "6"): "yes"}
        records = {("b", "1"): rec("kept"), ("b", "2"): rec("rejected"), ("b", "3"): rec("kept"),
                   ("b", "4"): rec("rejected"), ("b", "5"): rec("kept"), ("b", "6"): rec("review")}
        rows = measure.compare(labels, records)
        self.assertEqual([r["outcome"] for r in rows],
                         ["agree", "agree", "false inclusion", "false exclusion", "cannot tell", "agree"])
        self.assertEqual(measure.summary(rows), {"agree": 3, "false inclusion": 1, "false exclusion": 1,
                                                 "cannot tell": 1, "labelled": 6, "decided": 5})


class IntervalTest(unittest.TestCase):
    def test_zero_of_thirty_matches_the_closed_form(self):
        lower, upper = measure.clopper_pearson(0, 30)
        self.assertEqual(lower, 0.0)
        self.assertAlmostEqual(upper, 1 - 0.025 ** (1 / 30), places=9)   # 0.1157

    def test_all_of_n_mirrors_zero_of_n(self):
        lower, upper = measure.clopper_pearson(30, 30)
        self.assertAlmostEqual(lower, 0.025 ** (1 / 30), places=9)
        self.assertEqual(upper, 1.0)

    def test_one_of_thirty_against_known_values(self):
        lower, upper = measure.clopper_pearson(1, 30)
        self.assertAlmostEqual(lower, 0.000844, places=5)
        self.assertAlmostEqual(upper, 0.1722, places=3)

    def test_the_interval_holds_the_estimate(self):
        for k in range(0, 31, 5):
            lower, upper = measure.clopper_pearson(k, 30)
            self.assertLessEqual(lower, k / 30)
            self.assertGreaterEqual(upper, k / 30)
        with self.assertRaises(ValueError):
            measure.clopper_pearson(31, 30)


if __name__ == "__main__":
    unittest.main()
