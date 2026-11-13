"""The 20 labeled postings come from the seeded rule in LABELING-RULE.md, and nobody picked them by hand."""

import importlib.util
import json
import unittest

from .helpers import REPO

spec = importlib.util.spec_from_file_location("select_postings", REPO / "tools" / "select_postings.py")
select_postings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(select_postings)


class SelectionTest(unittest.TestCase):
    def test_the_committed_selection_and_sheet_are_what_the_seeded_rule_gives(self):
        selection, sheet = select_postings.select()
        self.assertEqual((REPO / "labels" / "selection.json").read_text(encoding="utf-8"),
                         json.dumps(selection, indent=2, ensure_ascii=False) + "\n")
        self.assertEqual((REPO / "labels" / "SHEET.md").read_text(encoding="utf-8"), sheet)

    def test_each_set_has_five_relevant_and_five_not_by_the_rule_and_no_overlap(self):
        selection, sheet = select_postings.select()
        for key in ("development", "held_out"):
            verdicts = [item["rule_verdict"] for item in selection[key]]
            self.assertEqual((verdicts.count("relevant"), verdicts.count("not_relevant")), (5, 5))
        ids = [item["id"] for key in ("development", "held_out") for item in selection[key]]
        self.assertEqual(len(set(ids)), 20)
        self.assertTrue(all("engineer" in item["title"].lower() for key in ("development", "held_out")
                            for item in selection[key]))

    def test_the_sheet_never_shows_the_rules_verdict(self):
        _, sheet = select_postings.select()
        self.assertNotIn("rule_verdict", sheet)
        self.assertNotIn("not_relevant", sheet.split("## Development set", 1)[1])


if __name__ == "__main__":
    unittest.main()
