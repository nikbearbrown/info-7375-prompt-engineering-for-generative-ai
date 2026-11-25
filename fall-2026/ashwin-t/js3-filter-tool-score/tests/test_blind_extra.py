"""The blind human checks: fixed draws, no overlap with the earlier audit, nothing leaked onto the cards."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from jobfilter import blind_extra as B
from jobfilter.audit import SELECTION


class BlindExtra(unittest.TestCase):
    def test_engineering_draw_is_fixed_and_twenty(self):
        self.assertEqual(B.engineering_reject_keys(), B.engineering_reject_keys())
        self.assertEqual(len(set(B.engineering_reject_keys())), 20)

    def test_engineering_draw_avoids_every_earlier_audit_posting(self):
        used = set(json.loads(SELECTION.read_text())["sheet_order"])
        self.assertFalse(used & set(B.engineering_reject_keys()))

    def test_engineering_draw_is_v10_rejects_with_engineering_titles(self):
        dec = {d["key"]: d for d in B._decisions()}
        for k in B.engineering_reject_keys():
            self.assertEqual(dec[k]["decision"], "REJECT")
            self.assertRegex(dec[k]["title"], B.ENG_TITLE)

    def test_claim_draw_is_fixed_fifteen_distinct(self):
        self.assertEqual(B.claim_ids(), B.claim_ids())
        self.assertEqual(len(set(B.claim_ids())), 15)

    def test_cards_hide_scores_and_ai_labels(self):
        eng = B.ENG_CARDS.read_text(encoding="utf-8").lower()
        self.assertNotIn("score", eng.split("### 101")[1])
        self.assertNotIn("codex", B.CLAIM_CARDS.read_text(encoding="utf-8").lower().split("### h1")[1])
        hand = B.HAND_CARDS.read_text(encoding="utf-8")
        self.assertNotIn("score 8", hand)
        self.assertNotIn('"score"', hand)

    def test_refuses_to_overwrite_a_filled_sheet(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "s.csv"
            path.write_text("n,verdict,reason\n1,Y,because\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                B._write_csv(path, ["n", "verdict", "reason"], [[1, "", ""]])

    def test_blank_sheets_report_zero_answers(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(B, "REPORT", Path(d) / "r.md"):
                text = B.report().read_text(encoding="utf-8")
        filled = any((r["verdict"] or "").strip() for r in csv.DictReader(B.ENG_SHEET.open(encoding="utf-8")))
        if not filled:
            self.assertIn("Answered: 0 of 20", text)


if __name__ == "__main__":
    unittest.main()
