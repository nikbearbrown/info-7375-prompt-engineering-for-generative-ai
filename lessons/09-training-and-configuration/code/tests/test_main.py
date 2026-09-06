"""Deterministic boundary and behavior tests for week 9."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertEqual(m.sigmoid(0), .5)

    def test_02(self):
        self.assertAlmostEqual(m.sigmoid(-1000), 0)

    def test_03(self):
        r=m.demo(); self.assertLess(r["loss"][-1], r["loss"][0])

    def test_04(self):
        self.assertGreater(m.demo()["w"], 0)

    def test_05(self):
        with self.assertRaises(ValueError): m.train([])

    def test_06(self):
        with self.assertRaises(ValueError): m.train([(1,2)])

if __name__ == "__main__":
    unittest.main()
