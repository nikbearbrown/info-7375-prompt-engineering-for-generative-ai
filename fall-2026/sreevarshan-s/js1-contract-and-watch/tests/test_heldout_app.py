"""Held-out app prompts and reply scoring. No Claude call, no network."""

import json
import tempfile
import unittest
from pathlib import Path

from experiments import heldout_app
from js1 import claude_judge

ROOT = Path(__file__).resolve().parent.parent
RESUME = json.loads((ROOT / "persona" / "priya-nair.resume.json").read_text(encoding="utf-8"))
PROFILE = json.loads((ROOT / "persona" / "priya-nair.profile.json").read_text(encoding="utf-8"))
FIXTURES = Path(__file__).parent / "fixtures"
RAW = FIXTURES / "constructed_postings.json"   # CONSTRUCTED postings


class HeldoutAppTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_build_writes_the_exact_judge_prompts(self):
        paths = heldout_app.build(RESUME, PROFILE, raw=RAW, out_dir=self.tmp, ids=(8000002,))
        self.assertEqual([p.name for p in paths], ["8000002-baseline.txt", "8000002-revised.txt"])
        posting = next(j for j in json.loads(RAW.read_text(encoding="utf-8"))["jobs"] if j["id"] == 8000002)
        candidate = claude_judge.candidate_fields(RESUME, PROFILE)
        for path, prompt in zip(paths, ("baseline", "revised")):
            expected = claude_judge.build_prompt((ROOT / "prompts" / f"{prompt}.txt").read_text(encoding="utf-8"),
                                                 posting, candidate)
            self.assertEqual(path.read_text(encoding="utf-8"), expected)

    def test_score_valid_invalid_missing(self):
        labels = self.tmp / "HAND_LABELS.md"
        labels.write_text("| posting_id | label | reason | notes |\n|---|---|---|---|\n"
                          "| 8000002 | not relevant | senior | |\n", encoding="utf-8")
        replies = self.tmp / "replies"
        replies.mkdir()
        (replies / "8000002-baseline.txt").write_text(json.dumps(
            {"posting_id": 8000002, "verdict": "not relevant", "skills_cited": [],
             "explanation": "The title is senior."}), encoding="utf-8")
        results = self.tmp / "results.md"
        [row] = heldout_app.score(RESUME, PROFILE, raw=RAW, hand_labels=labels, replies_dir=replies,
                                  results=results, ids=(8000002,))
        self.assertTrue(row["baseline_pass"])
        self.assertEqual(row["revised"]["status"], "missing")
        self.assertFalse(row["revised_pass"])
        (replies / "8000002-revised.txt").write_text("```json\n{}\n```", encoding="utf-8")
        [row] = heldout_app.score(RESUME, PROFILE, raw=RAW, hand_labels=labels, replies_dir=replies,
                                  results=results, ids=(8000002,))
        self.assertEqual(row["revised"]["status"], "invalid")
        self.assertFalse(row["revised_pass"])
        text = results.read_text(encoding="utf-8")
        self.assertIn("- **Baseline:** 1/1", text)
        self.assertIn("- **Revised:** 0/1", text)


if __name__ == "__main__":
    unittest.main()
