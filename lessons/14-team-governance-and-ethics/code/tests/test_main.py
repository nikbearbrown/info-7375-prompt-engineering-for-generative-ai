"""Deterministic boundary and behavior tests for week 14."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertEqual(m.assess({})["status"], "incomplete")

    def test_02(self):
        self.assertEqual(m.demo()["status"], "ready-for-human-review")

    def test_03(self):
        r={k:"x" for k in m.FIELDS}; r.update(data_classes=["public"],retention_days=-1)
        with self.assertRaises(ValueError): m.assess(r)

    def test_04(self):
        r={k:"x" for k in m.FIELDS}; r.update(data_classes=["personal"],retention_days=0); self.assertEqual(m.assess(r)["status"], "review-required")

    def test_05(self):
        r={k:"x" for k in m.FIELDS}; r.update(data_classes=["public"],retention_days=1,external_write=True); self.assertIn("external action approval",m.assess(r)["issues"])

    def test_06(self):
        r={k:"x" for k in m.FIELDS}; r.update(data_classes="public",retention_days=1)
        with self.assertRaises(ValueError): m.assess(r)

if __name__ == "__main__":
    unittest.main()
