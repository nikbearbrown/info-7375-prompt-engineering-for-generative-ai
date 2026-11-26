"""Deterministic boundary and behavior tests for week 8."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertEqual(m.Server().handle({})["error"]["code"], -32600)

    def test_02(self):
        self.assertEqual(m.Server().handle({"jsonrpc":"2.0","id":1,"method":"tools/list"})["error"]["code"], -32000)

    def test_03(self):
        self.assertIn("tools", m.demo()["result"])

    def test_04(self):
        s=m.Server(); self.assertIsNone(s.handle({"jsonrpc":"2.0","method":"notifications/initialized"})); self.assertFalse(s.ready)

    def test_05(self):
        s=m.Server(); s.handle({"jsonrpc":"2.0","id":1,"method":"initialize"}); s.handle({"jsonrpc":"2.0","method":"notifications/initialized"}); self.assertEqual(s.handle({"jsonrpc":"2.0","id":2,"method":"bad"})["error"]["code"], -32601)

    def test_06(self):
        s=m.Server(); s.ready=True; self.assertTrue(s.handle({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"lookup","arguments":{"key":"missing"}}})["result"]["isError"])

if __name__ == "__main__":
    unittest.main()
