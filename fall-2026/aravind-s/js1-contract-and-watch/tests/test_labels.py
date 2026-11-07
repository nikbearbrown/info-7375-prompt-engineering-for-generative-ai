"""The 20 hand labels stay paired with the postings they were made for (the brief's example of a wrong version)."""

import json
import unittest

from .helpers import REPO

SELECTION = json.loads((REPO / "labels" / "selection.json").read_text(encoding="utf-8"))
LABELS = json.loads((REPO / "labels" / "labels.json").read_text(encoding="utf-8"))


class LabelsTest(unittest.TestCase):
    def test_each_label_is_paired_with_its_selected_posting_in_order(self):
        selected = [("development", item) for item in SELECTION["development"]]
        selected += [("held_out", item) for item in SELECTION["held_out"]]
        self.assertEqual(len(LABELS["labels"]), 20)
        for n, ((part, item), label) in enumerate(zip(selected, LABELS["labels"]), start=1):
            with self.subTest(n=n):
                self.assertEqual((label["n"], label["set"], label["id"]), (n, part, item["id"]))
                self.assertEqual(label["title"], item["title"].strip())

    def test_labels_and_reasons_take_only_the_allowed_values(self):
        for label in LABELS["labels"]:
            with self.subTest(n=label["n"]):
                self.assertIn(label["label"], ("relevant", "not_relevant"))
                if label["label"] == "relevant":
                    self.assertIsNone(label["reason"])
                else:
                    self.assertIn(label["reason"], ("fails a contract check", "senior scope in words", "missing specialty"))

    def test_the_counts_match_the_labels(self):
        for part in ("development", "held_out"):
            mine = [label["label"] for label in LABELS["labels"] if label["set"] == part]
            self.assertEqual(LABELS["counts"][part], {"relevant": mine.count("relevant"),
                                                      "not_relevant": mine.count("not_relevant")})


if __name__ == "__main__":
    unittest.main()
