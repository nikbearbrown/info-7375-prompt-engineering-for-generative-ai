"""W11: config/budgets.json must match the values in GATE.md section 2.

GATE.md is the source of truth; this test only reads it.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE_PATH = ROOT / "GATE.md"
BUDGETS_PATH = ROOT / "config" / "budgets.json"
BOARDS_PATH = ROOT / "config" / "boards.json"


def gate_budgets(text):
    """Parse the '- name: value' lines of GATE.md section 2."""
    section = text.split("## 2. Budgets", 1)[1].split("\n## ", 1)[0]
    return {name: int(value) for name, value in
            re.findall(r"^- (max_[a-z_]+): (\d+)\s*$", section, re.M)}


def gate_board_urls(text):
    """Board name -> endpoint from the GATE.md boards table."""
    rows = re.findall(r"^\| ([a-z0-9-]+) \| (\w+) \| `(https://[^`]+)` \|",
                      text, re.M)
    return {name: (ats.lower(), url) for name, ats, url in rows}


class BudgetsConfigTests(unittest.TestCase):

    def test_W11_budgets_json_matches_gate_section_2(self):
        expected = gate_budgets(GATE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(expected), 5, expected)
        actual = json.loads(BUDGETS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)

    def test_boards_json_matches_gate_boards_table(self):
        expected = gate_board_urls(GATE_PATH.read_text(encoding="utf-8"))
        boards = json.loads(BOARDS_PATH.read_text(encoding="utf-8"))["boards"]
        self.assertEqual({b["name"]: (b["ats"], b["url"]) for b in boards},
                         expected)


if __name__ == "__main__":
    unittest.main()
