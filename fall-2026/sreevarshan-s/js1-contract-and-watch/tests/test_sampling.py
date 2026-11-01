"""Sampling prompts and reply checker. No Claude call, no network."""

import json
import tempfile
import unittest
from pathlib import Path

from experiments import sampling
from js1 import claude_judge

ROOT = Path(__file__).resolve().parent.parent
RESUME = json.loads((ROOT / "persona" / "priya-nair.resume.json").read_text(encoding="utf-8"))
PROFILE = json.loads((ROOT / "persona" / "priya-nair.profile.json").read_text(encoding="utf-8"))
FIXTURES = Path(__file__).parent / "fixtures"


class SamplingTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_build_writes_the_exact_judge_prompt(self):
        raw = FIXTURES / "constructed_postings.json"   # CONSTRUCTED postings
        [path] = sampling.build(RESUME, PROFILE, raw=raw, out_dir=self.tmp, ids=(8000002,))
        posting = next(j for j in json.loads(raw.read_text(encoding="utf-8"))["jobs"] if j["id"] == 8000002)
        expected = claude_judge.build_prompt((ROOT / "prompts" / "baseline.txt").read_text(encoding="utf-8"),
                                             posting, claude_judge.candidate_fields(RESUME, PROFILE))
        self.assertEqual(path.read_text(encoding="utf-8"), expected)

    def test_check_valid_and_invalid(self):
        good = self.tmp / "8000002-1.txt"
        good.write_text(json.dumps({"posting_id": 8000002, "verdict": "not relevant", "skills_cited": [],
                                    "explanation": "The title is senior."}), encoding="utf-8")
        self.assertEqual(sampling.check(good, RESUME, PROFILE), ("valid", "not relevant"))
        fenced = self.tmp / "8000002-2.txt"
        fenced.write_text("```json\n" + good.read_text(encoding="utf-8") + "\n```", encoding="utf-8")
        self.assertEqual(sampling.check(fenced, RESUME, PROFILE)[0], "invalid")
        wrong_id = self.tmp / "8000001-1.txt"
        wrong_id.write_text(good.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertEqual(sampling.check(wrong_id, RESUME, PROFILE)[0], "invalid")


if __name__ == "__main__":
    unittest.main()
