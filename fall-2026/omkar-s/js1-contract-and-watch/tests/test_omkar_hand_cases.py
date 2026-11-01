"""Omkar's own test: verdicts he works out BY HAND from CONTRACT.md on real saved postings,
before reading rule.py. Rows go in omkar_hand_cases.csv (the harness is Claude's; the verdicts are his).
The how_checked notes were typed by Claude Code from Omkar's picks and his own grep output (2026-10-30).
Postings are looked up in the earliest saved raw response in runs/ (or evidence/pre-build-curl/)."""
import csv
import glob
import json
import os
import unittest

from jsagent import persona, rule

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")


def _board():
    files = sorted(glob.glob(os.path.join(ROOT, "runs", "raw-klaviyo-*.json"))) or \
        sorted(glob.glob(os.path.join(ROOT, "evidence", "pre-build-curl", "klaviyo-*.json")))
    with open(files[0]) as f:
        return {str(j["id"]): j for j in json.load(f)["jobs"]}


with open(os.path.join(HERE, "omkar_hand_cases.csv")) as f:
    ROWS = list(csv.DictReader(f))


@unittest.skipUnless(ROWS, "Omkar has not written any hand cases yet (tests/omkar_hand_cases.csv is empty)")
class OmkarHandCases(unittest.TestCase):
    def test_rule_matches_omkars_hand_verdicts(self):
        board = _board()
        resume = persona.load(os.path.join(ROOT, "persona", "aarav-patel.example.json"))
        for row in ROWS:
            with self.subTest(posting=row["posting_id"]):
                got = rule.judge(board[row["posting_id"]], resume)
                self.assertEqual(got["verdict"], row["expected_verdict"].strip(), "\n".join(got["justification"]))


if __name__ == "__main__":
    unittest.main()
