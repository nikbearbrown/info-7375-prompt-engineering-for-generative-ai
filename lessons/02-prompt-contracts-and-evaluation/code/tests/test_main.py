"""Deterministic boundary and behavior tests for week 2."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertTrue(m.validate('{"answer":"x","sources":["a"]}', {"a"}))

    def test_02(self):
        self.assertFalse(m.validate('not json', {"a"}))

    def test_03(self):
        self.assertFalse(m.validate('{"answer":1,"sources":["a"]}', {"a"}))

    def test_04(self):
        self.assertFalse(m.validate('{"answer":"x","sources":["b"]}', {"a"}))

    def test_05(self):
        self.assertFalse(m.validate('{"answer":"x","sources":["a"],"extra":1}', {"a"}))

    def test_06(self):
        with self.assertRaises(ValueError): m.pass_rate([], {"a"})

if __name__ == "__main__":
    unittest.main()
