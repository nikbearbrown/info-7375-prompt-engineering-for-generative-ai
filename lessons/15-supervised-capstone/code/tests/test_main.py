"""Deterministic boundary and behavior tests for week 15."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("lesson_main", Path(__file__).resolve().parents[1] / "main.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LessonTests(unittest.TestCase):
    def test_01(self):
        self.assertEqual(len(m.ARTIFACTS), 10)

    def test_02(self):
        with tempfile.TemporaryDirectory() as d: self.assertEqual(len(m.validate_packet(d)["issues"]), 10)

    def test_03(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "brief.md").write_text("short"); self.assertIn("brief: insufficient content", m.validate_packet(d)["issues"])

    def test_04(self):
        with tempfile.TemporaryDirectory() as d:
            for name in m.ARTIFACTS: Path(d, name+".md").write_text("Evidence and discussion. "*5)
            self.assertTrue(m.validate_packet(d)["structurally_complete"])

    def test_05(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "brief.md").symlink_to("/etc/hosts"); self.assertIn("brief: outside packet", m.validate_packet(d)["issues"])

    def test_06(self):
        with tempfile.TemporaryDirectory() as d: self.assertIn("understanding", m.validate_packet(d)["human_review"])

if __name__ == "__main__":
    unittest.main()
