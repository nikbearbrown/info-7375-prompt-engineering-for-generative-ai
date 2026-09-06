"""Deterministic boundary and behavior tests for week 13."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertEqual(len(m.fingerprint(m.demo()["proposal"])), 64)

    def test_02(self):
        p=m.demo()["proposal"]; self.assertEqual(m.fingerprint(p), m.fingerprint(dict(reversed(list(p.items())))))

    def test_03(self):
        with self.assertRaises(ValueError): m.fingerprint({})

    def test_04(self):
        p=m.demo()["proposal"]; self.assertTrue(m.approved(p, {"approved":True,"approver":"human","fingerprint":m.fingerprint(p)}))

    def test_05(self):
        p=m.demo()["proposal"]; d={"approved":True,"approver":"human","fingerprint":m.fingerprint(p)}; p["target"]="elsewhere"; self.assertFalse(m.approved(p,d))

    def test_06(self):
        self.assertFalse(m.approved(m.demo()["proposal"], {"approved":True}))

if __name__ == "__main__":
    unittest.main()
