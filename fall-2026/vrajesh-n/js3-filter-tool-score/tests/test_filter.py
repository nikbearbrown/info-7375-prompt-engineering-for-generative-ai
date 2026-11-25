"""Tests for FILTER.md v1. Written before earlybird/rule.py was changed. Run: python -m unittest discover -s tests"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from earlybird import rule  # noqa: E402
from earlybird.resume import load_resume  # noqa: E402
from cases import CASES  # noqa: E402
from wrong_filters import WRONG  # noqa: E402

RESUME = load_resume(ROOT / "data/resume/rohan-desai.example.json")  # fictional persona, needs sponsorship


def mismatches(judge):
    bad = []
    for name, p, verdict, check in CASES:
        out = judge(p, RESUME)
        if out["verdict"] != verdict or out.get("failed_check") != check:
            bad.append(f"{name}: got {out['verdict']}/{out.get('failed_check')}, want {verdict}/{check}")
    return bad


class RealFilter(unittest.TestCase):
    def test_every_case(self):
        self.assertEqual(mismatches(rule.judge), [])

    def test_cannot_tell_names_the_missing_field(self):
        p = [c for c in CASES if c[0] == "location missing"][0][1]
        self.assertIn("location", rule.judge(p, RESUME)["justification"])


class WrongFiltersAreCaught(unittest.TestCase):
    def test_each_wrong_filter_fails_at_least_one_case(self):
        for name, judge in WRONG.items():
            with self.subTest(name):
                self.assertTrue(mismatches(judge), f"{name} passed every case, so the tests cannot catch it")

    def test_each_wrong_filter_fails_its_own_case(self):
        expect = {"W1 no seniority rule": "Senior in title", "W2 training as topic word": "training in description only",
                  "W3 ignores clearance": "clearance required"}
        for name, judge in WRONG.items():
            with self.subTest(name):
                self.assertTrue(any(m.startswith(expect[name]) for m in mismatches(judge)))


if __name__ == "__main__":
    unittest.main()
