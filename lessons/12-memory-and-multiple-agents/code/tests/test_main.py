"""Deterministic boundary and behavior tests for week 12."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertEqual(m.Memory().read("x")["version"], 0)

    def test_02(self):
        s=m.Memory(); self.assertEqual(s.write("x",1,"a",0), 1)

    def test_03(self):
        s=m.Memory(); s.write("x",1,"a",0); self.assertEqual(s.read("x")["source"], "a")

    def test_04(self):
        s=m.Memory(); s.write("x",1,"a",0)
        with self.assertRaises(ValueError): s.write("x",2,"b",0)

    def test_05(self):
        with self.assertRaises(ValueError): m.Memory().write("x",1,"",0)

    def test_06(self):
        s=m.Memory(); s.write("x",[],"a",0); s.read("x")["value"].append(1); self.assertEqual(s.read("x")["value"], [])

if __name__ == "__main__":
    unittest.main()
