"""Deterministic boundary and behavior tests for week 4."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertEqual(m.run([], {})["status"], "incomplete")

    def test_02(self):
        self.assertEqual(m.run([{"name":"finish"}], {})["status"], "finished")

    def test_03(self):
        self.assertEqual(m.run([{"name":"lookup","key":"x"}], {}, 1)["status"], "budget-exhausted")

    def test_04(self):
        self.assertEqual(m.run([{"name":"lookup","key":"x"}], {"x":"y"})["trace"][0]["observation"], "y")

    def test_05(self):
        self.assertIn("not allowed", m.run([{"name":"shell"}], {})["trace"][0]["observation"])

    def test_06(self):
        with self.assertRaises(ValueError): m.run([], {}, 0)

if __name__ == "__main__":
    unittest.main()
