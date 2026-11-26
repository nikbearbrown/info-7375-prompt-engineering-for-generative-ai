import unittest

from js3.stats import clopper_pearson


class TestCP(unittest.TestCase):
    def test_known_values(self):
        lo, hi = clopper_pearson(0, 35)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 1 - 0.025 ** (1 / 35), places=6)  # closed form when k = 0
        lo, hi = clopper_pearson(35, 35)
        self.assertAlmostEqual(lo, 0.025 ** (1 / 35), places=6)
        self.assertEqual(hi, 1.0)

    def test_interval_contains_estimate(self):
        lo, hi = clopper_pearson(3, 35)
        self.assertLess(lo, 3 / 35)
        self.assertGreater(hi, 3 / 35)


if __name__ == "__main__":
    unittest.main()
