"""The claims scorer (tools/score_claims.py): label pairs, agreement by type, and the sealed-hash check.

Built on a constructed three-claim kit in a temporary directory; nothing here reads the real claims kit.
"""

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from .loop_helpers import REPO

spec = importlib.util.spec_from_file_location("score_claims", REPO / "tools" / "score_claims.py")
score_claims = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score_claims)

HEADER = ("| Claim | What the shortlist claims | Passages | Supported | Contradicted | Insufficient | Note |\n"
          "|---|---|---|---|---|---|---|\n")


def build(root: Path, rows: str, tamper: bool = False) -> Path:
    kit = root / "RUN"
    (kit / "sealed").mkdir(parents=True)
    checker = {"kit": "claims", "postings": [{"posting": 1, "title": "Software Engineer, X", "score": 65}],
               "claims": [
                   {"claim": "01.1", "posting": 1, "type": 1, "group": None, "text": "Full time.", "label": "supported",
                    "why": "FullTime"},
                   {"claim": "01.5", "posting": 1, "type": 5, "group": None, "text": "No status rule.",
                    "label": "insufficient", "why": "none found"},
                   {"claim": "01.8a", "posting": 1, "type": 8, "group": "Developer tools", "text": "Developer tools.",
                    "label": "supported", "why": "the sentence that earned the points"}]}
    raw = json.dumps(checker).encode()
    (kit / "sealed" / "checker-labels.json").write_bytes(raw)
    digest = hashlib.sha256(raw + (b"!" if tamper else b"")).hexdigest()
    (kit / "README.md").write_text(f"checker labels, SHA-256 `{digest}`\n", encoding="utf-8")
    (kit / "LABELS.md").write_text(HEADER + rows, encoding="utf-8")
    return kit


ROWS = ("| 01.1 | Full time. | employmentType: \"FullTime\" | x | | | |\n"
        "| 01.5 | No status rule. | none found | | | x | nothing said |\n"
        "| 01.8a | Developer tools. | \"build systems that consume signals\" | | | x | build is a verb here |\n")


class ScoreClaimsTest(unittest.TestCase):
    def test_pairs_agreement_and_the_relevance_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit = build(Path(tmp), ROWS)
            s = score_claims.score(kit)
            self.assertEqual([r["agree"] for r in s["rows"]], [True, True, False])
            text = score_claims.write_results(kit, s)
            self.assertIn("the checker agrees with him on 2 of 3 claims", text)
            self.assertIn("| insufficient | supported | 1 |", text)
            self.assertIn("| 01.8a | Software Engineer, X (65) | Developer tools | build is a verb here |", text)

    def test_flip_checks_are_reported_beside_the_frozen_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit = build(Path(tmp), ROWS)
            (kit / "FLIP-CHECKS.md").write_text(
                "| Claim | Frozen label | Checker | The sentence(s) found | Label after | His words |\n|---|---|---|---|---|---|\n"
                "| 01.8a | insufficient | supported | \"Create tooling for developers.\" | supported | \"01.8a -> S\" |\n",
                encoding="utf-8")
            s = score_claims.score(kit)
            self.assertEqual(sum(r["agree"] for r in s["rows"]), 2)  # the frozen labels are unchanged
            self.assertEqual(s["agree_after"], 3)
            text = score_claims.write_results(kit, s)
            self.assertIn("| 01.8a | insufficient | supported | supported | \"01.8a -> S\" |", text)
            self.assertIn("agrees with him on 3 of 3 claims (frozen: 2 of 3)", text)

    def test_refuses_a_checker_file_that_does_not_match_the_published_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit = build(Path(tmp), ROWS, tamper=True)
            with self.assertRaises(SystemExit):
                score_claims.score(kit)

    def test_refuses_a_row_without_exactly_one_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit = build(Path(tmp), ROWS.replace("| 01.1 | Full time. | employmentType: \"FullTime\" | x | | | |",
                                                "| 01.1 | Full time. | employmentType: \"FullTime\" | x | | x | |"))
            with self.assertRaises(SystemExit):
                score_claims.score(kit)

    def test_read_labels_keeps_escaped_pipes_inside_passages(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "LABELS.md"
            path.write_text(HEADER + "| 02.4 | Title. | title: \"A \\| B\" | x | | | ok |\n", encoding="utf-8")
            self.assertEqual(score_claims.read_labels(path), {"02.4": ("supported", "ok")})


if __name__ == "__main__":
    unittest.main()
