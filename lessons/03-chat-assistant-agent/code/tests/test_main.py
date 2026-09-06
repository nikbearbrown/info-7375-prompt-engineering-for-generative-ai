"""Deterministic boundary and behavior tests for week 3."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertEqual(m.missing("chat", ["read", "write"]), ["read", "write"])

    def test_02(self):
        self.assertEqual(m.missing("agent", ["read"]), [])

    def test_03(self):
        self.assertEqual(m.classify(["read"]), "assistant")

    def test_04(self):
        self.assertEqual(m.classify(["write"]), "agent")

    def test_05(self):
        with self.assertRaises(ValueError): m.classify(["delete-everything"])

    def test_06(self):
        with self.assertRaises(ValueError): m.missing("unknown", [])

if __name__ == "__main__":
    unittest.main()
