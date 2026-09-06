"""Deterministic boundary and behavior tests for week 11."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertEqual(m.dispatch("add", {"a":2,"b":3}), 5)

    def test_02(self):
        with self.assertRaises(ValueError): m.dispatch("shell", {})

    def test_03(self):
        with self.assertRaises(ValueError): m.dispatch("add", {"a":True,"b":2})

    def test_04(self):
        self.assertEqual(m.demo()[0]["tool_use_id"], "demo-1")

    def test_05(self):
        self.assertTrue(m.results([{"type":"tool_use","id":"x","name":"bad","input":{}}])[0]["is_error"])

    def test_06(self):
        self.assertEqual(m.loop(lambda _: {"stop_reason":"max_tokens","content":[]}, {"messages":[]})["status"], "stopped")

if __name__ == "__main__":
    unittest.main()
