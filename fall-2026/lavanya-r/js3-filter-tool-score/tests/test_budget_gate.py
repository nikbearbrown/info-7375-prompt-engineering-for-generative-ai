"""GATE.md 2: a budget changes only by a written decision. The numbers the
code uses (config/budgets.json) must equal the table in GATE.md."""

import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


class TestRuntimeGateCheck(unittest.TestCase):
    """The running agent itself refuses budgets that differ from GATE.md."""

    def setUp(self):
        from agent import loop
        self.loop = loop
        self.gate = (ROOT / "GATE.md").read_text()
        cfg = json.loads((ROOT / "config/budgets.json").read_text())
        self.limits = {k: v for k, v in cfg.items() if not k.startswith("_")}

    def test_real_config_matches(self):
        self.assertEqual(self.loop.budget_mismatches(self.gate, self.limits),
                         [])

    def test_raised_budget_is_refused(self):
        for key in ["boards", "requests", "seconds",
                    "request_timeout_seconds"]:
            with self.subTest(key=key):
                raised = {**self.limits, key: self.limits[key] + 1}
                self.assertNotEqual(
                    self.loop.budget_mismatches(self.gate, raised), [])

    def test_main_exits_error_before_any_request(self):
        import io
        from contextlib import redirect_stdout
        from unittest import mock
        real_read = self.loop.Policy.read_bytes

        def fake_read(policy, path):
            if str(path).endswith("budgets.json"):
                return json.dumps({**self.limits, "requests": 999}).encode()
            return real_read(policy, path)
        with mock.patch.object(self.loop.Policy, "read_bytes", fake_read), \
                mock.patch.object(self.loop.net, "make_get",
                                  side_effect=AssertionError("network")), \
                redirect_stdout(io.StringIO()) as out:
            code = self.loop.main([])
        self.assertEqual(code, 1)
        self.assertIn("REFUSING TO RUN", out.getvalue())


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
