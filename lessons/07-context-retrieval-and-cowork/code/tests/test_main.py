"""Deterministic boundary and behavior tests for week 7."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertEqual(m.vector("Hi HI")["hi"], 2)

    def test_02(self):
        self.assertEqual(m.cosine({}, {"a":1}), 0)

    def test_03(self):
        self.assertAlmostEqual(m.cosine({"a":2}, {"a":1}), 1)

    def test_04(self):
        self.assertEqual(m.retrieve("cat", {"a":"cat","b":"dog"})[0][0], "a")

    def test_05(self):
        self.assertEqual(m.retrieve("cat", {"a":"dog"}), [])

    def test_06(self):
        with self.assertRaises(ValueError): m.retrieve("x", {}, 0)

if __name__ == "__main__":
    unittest.main()
