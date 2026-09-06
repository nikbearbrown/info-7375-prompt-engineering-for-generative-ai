"""Deterministic boundary and behavior tests for week 10."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertEqual(m.order([]), [])

    def test_02(self):
        self.assertEqual(m.order([{"id":"b","after":["a"]},{"id":"a"}]), ["a","b"])

    def test_03(self):
        with self.assertRaises(ValueError): m.order([{"id":"a","after":["a"]}])

    def test_04(self):
        with self.assertRaises(ValueError): m.order([{"id":"a","after":["z"]}])

    def test_05(self):
        with self.assertRaises(ValueError): m.order([{"id":"a"},{"id":"a"}])

    def test_06(self):
        self.assertEqual(len(m.missing_fields({})), 8)

if __name__ == "__main__":
    unittest.main()
