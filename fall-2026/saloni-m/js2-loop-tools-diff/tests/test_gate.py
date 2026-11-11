"""Config must match the written decision in GATE.md (budgets change only by a new GATE entry)."""
import json
import os
import unittest

from jsagent.gate import mismatches, read_gate

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestGate(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(HERE, "GATE.md"), encoding="utf-8") as f:
            self.gate = read_gate(f.read())
        with open(os.path.join(HERE, "config", "run.json"), encoding="utf-8") as f:
            self.cfg = json.load(f)

    def test_gate_values_as_written(self):
        self.assertEqual(self.gate["budgets"], {"max_boards": 5, "max_requests": 10, "max_seconds": 60,
                                                "request_timeout_seconds": 10})
        self.assertEqual(self.gate["allowed_hosts"], ["api.ashbyhq.com", "boards-api.greenhouse.io"])

    def test_config_matches_gate(self):
        self.assertEqual(mismatches(self.cfg, self.gate), [])

    def test_a_changed_budget_is_detected(self):
        cfg = json.loads(json.dumps(self.cfg))
        cfg["budgets"]["max_requests"] = 50
        self.assertEqual(len(mismatches(cfg, self.gate)), 1)

    def test_an_added_host_is_detected(self):
        cfg = json.loads(json.dumps(self.cfg))
        cfg["allowed_hosts"].append("api.lever.co")
        self.assertEqual(len(mismatches(cfg, self.gate)), 1)

    def test_config_has_three_real_boards_two_systems_and_one_deliberate_failure(self):
        real = [b for b in self.cfg["boards"] if "deliberate_failure" not in b]
        self.assertGreaterEqual(len(real), 3)
        self.assertGreaterEqual(len({b["system"] for b in real}), 2)
        self.assertEqual(len([b for b in self.cfg["boards"] if "deliberate_failure" in b]), 1)


if __name__ == "__main__":
    unittest.main()
