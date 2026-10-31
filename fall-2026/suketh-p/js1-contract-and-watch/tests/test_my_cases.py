"""Regression-test draft by me using saved real postings."""

import gzip
import unittest
from pathlib import Path

from jobwatch import board, rule
from tests.helpers import persona

ROOT = Path(__file__).resolve().parents[1]

CASES = [
    ("20261031T125015Z-live", 5464234008, "relevant", []),
    ("20261028T102612Z-live", 5436684008,
     "not_relevant", ["title_seniority"]),
    ("20261028T102612Z-live", 5198108008,
     "not_relevant", ["skills"]),
]


class RealPostingCases(unittest.TestCase):
    def test_saved_real_postings(self):
        resume = persona()
        snapshots = {}

        for run, posting_id, verdict, failed in CASES:
            with self.subTest(posting_id=posting_id):
                if run not in snapshots:
                    path = ROOT / "runs" / run / "raw_response.json.gz"
                    with gzip.open(path, "rb") as raw:
                        snapshots[run] = {
                            p.id: p
                            for p in board.parse_board(raw.read())
                        }

                record = rule.rule_verdict(
                    resume, snapshots[run][posting_id]
                )
                self.assertEqual(record["verdict"], verdict)
                self.assertEqual(record["failed_conditions"], failed)


if __name__ == "__main__":
    unittest.main()
