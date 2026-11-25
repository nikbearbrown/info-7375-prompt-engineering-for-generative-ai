"""The measurement and audit arithmetic: undefined ratios stay undefined, the interval is right, and the
audit draw never touches a held-out posting."""
import unittest

import audit
import measure


def posting(key, title, text="SQL Tableau Excel", locations=("New York, NY",)):
    return {"key": key, "title": title, "text": text, "locations": list(locations), "location": locations[0],
            "country": None}


class Measure(unittest.TestCase):
    def test_zero_denominator_is_undefined_never_zero_or_one(self):
        self.assertEqual(measure.ratio(0, 0), "0/0 (undefined)")
        self.assertEqual(measure.ratio(2, 4), "2/4 = 0.50")

    def test_counts(self):
        pairs = [(True, True), (True, False), (False, True), (False, False), (False, False)]
        self.assertEqual(measure.counts(pairs), (1, 1, 1, 2))


class Audit(unittest.TestCase):
    def test_wilson_interval_known_values(self):
        lo, hi = audit.wilson(0, 30)
        self.assertEqual(round(lo, 3), 0.0)
        self.assertAlmostEqual(hi, 0.114, places=3)
        lo, hi = audit.wilson(5, 10)
        self.assertAlmostEqual(lo, 0.237, places=3)
        self.assertAlmostEqual(hi, 0.763, places=3)
        self.assertIsNone(audit.wilson(0, 0))

    def test_draw_excludes_held_out_and_groups_do_not_overlap(self):
        postings = ([posting(f"k/{i}", "Data Analyst") for i in range(15)] +
                    [posting(f"r/{i}", "Software Engineer") for i in range(40)] +
                    [posting(f"n/{i}", "Financial Analyst", text="SQL Excel") for i in range(15)])
        held = {"k/0", "r/0", "n/0"}
        rows, pool = audit.draw(postings, held, seed=1)
        keys = [p["key"] for _, p, _ in rows]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertFalse(held & set(keys))
        self.assertEqual(pool["pool"], 67)
        by_group = {}
        for name, p, v in rows:
            by_group.setdefault(name, []).append(v)
        self.assertEqual({k: len(v) for k, v in by_group.items()}, {"kept": 10, "reject": 30, "near": 10})
        self.assertTrue(all(v["verdict"] == "keep" for v in by_group["kept"]))
        self.assertTrue(all(not v["rejected_by"] and v["verdict"] == "reject" for v in by_group["near"]))

    def test_draw_is_repeatable_from_the_seed(self):
        postings = [posting(f"r/{i}", "Engineer") for i in range(40)] + [posting("k/1", "Data Analyst")]
        a = [p["key"] for _, p, _ in audit.draw(postings, set(), seed=7)[0]]
        b = [p["key"] for _, p, _ in audit.draw(postings, set(), seed=7)[0]]
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
