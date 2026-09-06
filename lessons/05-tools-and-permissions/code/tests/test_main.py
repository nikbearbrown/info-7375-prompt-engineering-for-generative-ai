"""Deterministic boundary and behavior tests for week 5."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertEqual(m.authorize("/tmp/course", "x", "read").name, "x")

    def test_02(self):
        with self.assertRaises(PermissionError): m.authorize("/tmp/course", "../x", "read")

    def test_03(self):
        with self.assertRaises(PermissionError): m.authorize("/tmp/course", "/tmp/course-other/x", "read")

    def test_04(self):
        with self.assertRaises(PermissionError): m.authorize("/tmp/course", "x", "write")

    def test_05(self):
        self.assertEqual(m.authorize("/tmp/course", "x", "write", True).name, "x")

    def test_06(self):
        with self.assertRaises(PermissionError): m.authorize("/tmp/course", "x", "execute", True)

if __name__ == "__main__":
    unittest.main()
