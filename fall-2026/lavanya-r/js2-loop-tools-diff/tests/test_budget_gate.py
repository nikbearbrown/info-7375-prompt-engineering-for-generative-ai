"""GATE.md 2: a budget changes only by a written decision. The numbers the
code uses (config/budgets.json) must equal the table in GATE.md."""

import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


class TestBudgetsMatchGate(unittest.TestCase):
    def test_config_equals_gate_table(self):
        gate = (ROOT / "GATE.md").read_text()
        cfg = json.loads((ROOT / "config/budgets.json").read_text())

        def row(label):
            m = re.search(rf"^\| {label}[^|]*\| \*\*(\d+)\*\*", gate, re.M)
            self.assertIsNotNone(m, f"GATE.md has no row for {label}")
            return int(m.group(1))

        self.assertEqual(cfg["boards"], row("Boards"))
        self.assertEqual(cfg["requests"], row(r"Requests"))
        self.assertEqual(cfg["seconds"], row(r"Seconds \(wall clock"))
        m = re.search(r"Seconds per single request \(timeout\) \| (\d+)", gate)
        self.assertEqual(cfg["request_timeout_seconds"], int(m.group(1)))

    def test_no_command_line_flag_changes_budgets(self):
        src = (ROOT / "agent/loop.py").read_text()
        flags = re.findall(r'add_argument\("(--[a-z-]+)"', src)
        self.assertEqual(sorted(flags), ["--approve-state", "--boards",
                                         "--budgets", "--fixtures",
                                         "--seeded"])


if __name__ == "__main__":
    unittest.main()
