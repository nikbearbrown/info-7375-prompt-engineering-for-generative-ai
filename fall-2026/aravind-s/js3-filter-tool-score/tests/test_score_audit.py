"""The audit scorer (tools/score_audit.py): the exact bound, the verdict table, and the sealed-hash check.

Built on a constructed two-card audit folder in a temporary directory; nothing here reads the real audit.
"""

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from .loop_helpers import REPO

spec = importlib.util.spec_from_file_location("score_audit", REPO / "tools" / "score_audit.py")
score_audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score_audit)


def build(root: Path, verdicts: list, answers: list, tamper: bool = False) -> Path:
    audit = root / "js3" / "audit" / "RUN"
    (audit / "sealed").mkdir(parents=True)
    run = root / "js3" / "filter-run" / "RUN"
    run.mkdir(parents=True)
    raw = json.dumps({"filter_run": "RUN", "seed": 1, "answers": answers}).encode()
    (audit / "sealed" / "answers.json").write_bytes(raw)
    digest = hashlib.sha256(raw + (b" " if tamper else b"")).hexdigest()
    (audit / "SAMPLE.md").write_text(f"sealed (SHA-256 `{digest}`)\n", encoding="utf-8")
    rows = "\n".join(f"| {c:02d} | {v} | {note} |" for c, v, note in verdicts)
    (audit / "VERDICTS.md").write_text("| Card | Keep / Reject / ? | Note |\n|---|---|---|\n" + rows + "\n", encoding="utf-8")
    (run / "verdicts.json").write_text(json.dumps({"records": [{"fate": "rejected"}] * 9 + [{"fate": "kept"}]}),
                                       encoding="utf-8")
    return audit


def answer(card, group, fate, rule=None, failed=None, score=None):
    return {"card": card, "title": f"T{card}", "group": group, "fate": fate, "deciding_rule": rule,
            "failed_rules": failed or [], "score": score}


class ScoreAuditTest(unittest.TestCase):
    def test_bound_matches_the_published_values_for_30(self):
        # The values written in the JS3 checklist before any verdict: 9.5%, 14.9%, 19.5%, 23.9%.
        for k, expected in [(0, 0.095), (1, 0.149), (2, 0.195), (3, 0.239)]:
            self.assertAlmostEqual(score_audit.upper_bound(k, 30), expected, delta=0.0006)

    def test_bound_edges(self):
        self.assertEqual(score_audit.upper_bound(5, 5), 1.0)
        with self.assertRaises(ValueError):
            score_audit.upper_bound(0, 0)

    def test_miss_wrong_keep_and_question_mark(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit = build(Path(tmp),
                          [(1, "Keep", "a miss"), (2, "Reject", "agree"), (3, "Reject", "wrong keep"), (4, "?", "unsure")],
                          [answer(1, "random reject", "rejected", "R4", ["R4"]),
                           answer(2, "random reject", "rejected", "R2", ["R2", "R3"]),
                           answer(3, "kept sample", "kept", score=60),
                           answer(4, "random reject", "rejected", "R5", ["R5"])])
            s = score_audit.score(audit, audit.parents[1] / "filter-run" / "RUN")
            outcomes = {r["card"]: r["outcome"] for r in s["rows"]}
            self.assertEqual(outcomes, {1: "miss", 2: "agree", 3: "wrong keep", 4: "?"})
            self.assertEqual((s["k"], s["n"], s["q"], s["rejected_total"]), (1, 2, 1, 9))
            text = score_audit.write_results(audit, audit.parents[1] / "filter-run" / "RUN", s)
            self.assertIn("1 misses in 2 judged random rejects (1 marked ?)", text)
            self.assertIn("| R4 | 1 | 01 | 1 |", text)

    def test_checks_after_the_reveal_are_reported_beside_the_frozen_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit = build(Path(tmp), [(1, "Keep", "a miss"), (2, "Reject", "agree")],
                          [answer(1, "random reject", "rejected", "R4", ["R4", "R5"]),
                           answer(2, "random reject", "rejected", "R2", ["R2"])])
            (audit / "AFTER-REVEAL.md").write_text(
                "| Card | Verdict after the reveal | When | Why | Words |\n|---|---|---|---|---|\n"
                "| 01 | Reject | today | the card hid a line | \"No, reject it\" |\n", encoding="utf-8")
            s = score_audit.score(audit, audit.parents[1] / "filter-run" / "RUN")
            self.assertEqual((s["k"], s["n"]), (1, 2))  # the frozen result is unchanged
            self.assertEqual((s["after"]["k"], s["after"]["n"]), (0, 2))
            text = score_audit.write_results(audit, audit.parents[1] / "filter-run" / "RUN", s)
            self.assertIn("1 misses in 2 judged random rejects", text)
            self.assertIn("With these checks: 0 misses in 2 judged random rejects", text)
            self.assertIn("| 01 | Keep | Reject | today |", text)

    def test_refuses_answers_that_do_not_match_the_published_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit = build(Path(tmp), [(1, "Keep", "x")], [answer(1, "random reject", "rejected", "R4", ["R4"])],
                          tamper=True)
            with self.assertRaises(SystemExit):
                score_audit.score(audit, audit.parents[1] / "filter-run" / "RUN")

    def test_refuses_a_card_without_a_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit = build(Path(tmp), [(1, "Keep", "x")],
                          [answer(1, "random reject", "rejected", "R4", ["R4"]), answer(2, "kept sample", "kept", score=55)])
            with self.assertRaises(SystemExit):
                score_audit.score(audit, audit.parents[1] / "filter-run" / "RUN")


if __name__ == "__main__":
    unittest.main()
