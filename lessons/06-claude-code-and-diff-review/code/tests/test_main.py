"""Deterministic boundary and behavior tests for week 6."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertTrue(m.review(["a"], ["a"], True, True)["merge_ready"])

    def test_02(self):
        self.assertFalse(m.review(["b"], ["a"], True, True)["merge_ready"])

    def test_03(self):
        self.assertFalse(m.review([], ["a"], True, True)["merge_ready"])

    def test_04(self):
        self.assertFalse(m.review(["a"], ["a"], False, True)["merge_ready"])

    def test_05(self):
        self.assertFalse(m.review(["a"], ["a"], True, False)["merge_ready"])

    def test_06(self):
        self.assertIn("+new", m.diff("old\n", "new\n"))

if __name__ == "__main__":
    unittest.main()
