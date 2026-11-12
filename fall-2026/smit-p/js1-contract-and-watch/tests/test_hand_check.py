"""Compare predictions read from the posting text (hand-check/predictions.json) with the rule.

The predictions were meant to be Smit's hand check. On 2026-10-30 Smit asked Claude to
write them instead; the file's "by" field says so. The harness was written by Claude.
Skips until predictions exist.

    python3 -m unittest discover -s tests -p 'test_hand_check.py' -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import rule  # noqa: E402

PRED = os.path.join(ROOT, "hand-check", "predictions.json")


class HandPredictions(unittest.TestCase):
    def setUp(self):
        with open(PRED, encoding="utf-8") as f:
            self.pred = json.load(f)
        if not any(p["verdict"] for p in self.pred["predictions"].values()):
            self.skipTest("hand-check/predictions.json not filled in yet")
        with open(os.path.join(ROOT, self.pred["source"]), encoding="utf-8") as f:
            self.jobs = {j["id"]: j for j in json.load(f)["jobs"]}
        with open(os.path.join(ROOT, "persona", "aarav-patel.resume.json"), encoding="utf-8") as f:
            self.resume = json.load(f)

    def test_verdicts_match_my_hand_prediction(self):
        for pid, p in self.pred["predictions"].items():
            with self.subTest(posting=pid):
                self.assertEqual(rule.judge(self.jobs[int(pid)], self.resume)["verdict"], p["verdict"])

    def test_skills_match_my_hand_count(self):
        for pid, p in self.pred["predictions"].items():
            with self.subTest(posting=pid):
                v = rule.judge(self.jobs[int(pid)], self.resume)
                got = {c["resume_value"].lower() for c in v["citations"] if c["effect"] == "skill found"}
                self.assertEqual(got, {s.lower() for s in p["skills_found"]})


if __name__ == "__main__":
    unittest.main()
