"""Decision 2b: the code's budgets must equal GATE.md §2. Changing one without the other fails here."""
import json
import re
import unittest

from helpers import HERE


class GateMatchesConfig(unittest.TestCase):
    def test_budgets(self):
        gate = (HERE / "GATE.md").read_text()
        sec = gate.split("## 2. Budgets", 1)[1].split("## 3.", 1)[0]
        found = {name: int(re.search(rf"\| {re.escape(name)}[^|]*\| \*\*(\d+)", sec).group(1))
                 for name in ("Boards per run", "HTTP requests per run", "Wall-clock seconds per run", "Timeout per request")}
        cfg = json.loads((HERE / "config/budgets.json").read_text())
        self.assertEqual([found["Boards per run"], found["HTTP requests per run"], found["Wall-clock seconds per run"], found["Timeout per request"]],
                         [cfg["max_boards"], cfg["max_requests"], cfg["max_seconds"], cfg["request_timeout_seconds"]])


class Rule(unittest.TestCase):
    def test_whole_word_terms(self):
        from jsa.rule import matches_term
        self.assertTrue(matches_term("ML Engineer, Intern", "Intern"))
        self.assertFalse(matches_term("Internal Tools Engineer", "Intern"))
        self.assertFalse(matches_term("Leadership Coach", "Lead"))


if __name__ == "__main__":
    unittest.main()
