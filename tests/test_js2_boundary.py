"""BOUNDARY_TESTS.md as tests: every case's actual decision must equal its written prediction."""
import unittest

from tests.js2_boundary_cases import CASES, run_case


class TestBoundary(unittest.TestCase):
    def test_every_case_matches_its_prediction(self):
        for case_id, what, predicted, fn in CASES:
            with self.subTest(case=case_id, what=what):
                self.assertEqual(run_case(fn), predicted)

    def test_at_least_ten_cases(self):
        self.assertGreaterEqual(len(CASES), 10)


if __name__ == "__main__":
    unittest.main()
