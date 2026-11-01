"""Watch-run judgment prompts and reply table. No Claude call, no network."""

import json
import tempfile
import unittest
from pathlib import Path

from experiments import watch_app
from js1 import claude_judge

ROOT = Path(__file__).resolve().parent.parent
RESUME = json.loads((ROOT / "persona" / "priya-nair.resume.json").read_text(encoding="utf-8"))
PROFILE = json.loads((ROOT / "persona" / "priya-nair.profile.json").read_text(encoding="utf-8"))
RAW = Path(__file__).parent / "fixtures" / "constructed_postings.json"   # CONSTRUCTED postings


class WatchAppTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.rule = self.tmp / "rule.json"
        self.rule.write_text(json.dumps({"run": "CONSTRUCTED", "records": [
            {"posting_id": 8000002, "title": "Senior Data Engineer ", "verdict": "not relevant", "label": "record"},
        ]}), encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_build_writes_the_exact_judge_prompt_for_each_record(self):
        [path] = watch_app.build(RESUME, PROFILE, rule=self.rule, raw=RAW, out_dir=self.tmp / "prompts")
        self.assertEqual(path.name, "8000002.txt")
        posting = next(j for j in json.loads(RAW.read_text(encoding="utf-8"))["jobs"] if j["id"] == 8000002)
        expected = claude_judge.build_prompt((ROOT / "prompts" / "baseline.txt").read_text(encoding="utf-8"),
                                             posting, claude_judge.candidate_fields(RESUME, PROFILE))
        self.assertEqual(path.read_text(encoding="utf-8"), expected)

    def test_score_puts_record_next_to_judgment(self):
        replies, results = self.tmp / "replies", self.tmp / "results.md"
        replies.mkdir()
        [row] = watch_app.score(RESUME, PROFILE, rule=self.rule, replies_dir=replies, results=results)
        self.assertEqual(row["judgment"]["status"], "missing")
        (replies / "8000002.txt").write_text(json.dumps(
            {"posting_id": 8000002, "verdict": "not relevant", "skills_cited": [],
             "explanation": "The title is senior."}), encoding="utf-8")
        [row] = watch_app.score(RESUME, PROFILE, rule=self.rule, replies_dir=replies, results=results)
        self.assertEqual((row["record"], row["judgment"]["verdict"]), ("not relevant", "not relevant"))
        text = results.read_text(encoding="utf-8")
        self.assertIn("| rule verdict (record) | Claude verdict (judgment) |", text)
        self.assertIn("| 8000002 | Senior Data Engineer | not relevant | not relevant | yes |", text)
        self.assertIn("2026-10-31", text)


if __name__ == "__main__":
    unittest.main()
