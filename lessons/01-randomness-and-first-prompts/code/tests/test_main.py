"""Deterministic boundary and behavior tests for week 1."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertAlmostEqual(sum(m.probabilities([1, 2, 3])), 1)

    def test_02(self):
        self.assertEqual(m.probabilities([1000, 1000]), [0.5, 0.5])

    def test_03(self):
        self.assertGreater(m.probabilities([0, 2], .5)[1], m.probabilities([0, 2], 2)[1])

    def test_04(self):
        self.assertEqual(m.sample([1, 2]), m.sample([1, 2]))

    def test_05(self):
        with self.assertRaises(ValueError): m.probabilities([1], 0)

    def test_06(self):
        with self.assertRaises(ValueError): m.probabilities([float("inf")])

if __name__ == "__main__":
    unittest.main()
