"""The Claude judge's output validator: accept the fixed format, reject anything else.

No network or model calls here. The model runner is replaced with canned text.
"""
import json
import unittest
from pathlib import Path

from jsagent import claude_judge, fetch, resume

ROOT = Path(__file__).resolve().parent.parent
POSTINGS = fetch.parse_postings((ROOT / "tests" / "fixtures" / "board_small.json").read_bytes())
RESUME = resume.load_resume(ROOT / "persona" / "evan-gordon.resume.json")
PID = "1001"

GOOD = {
    "posting_id": PID,
    "verdict": "relevant",
    "resume_fields": ["search.target_titles", "skills.languages"],
    "posting_fields": ["title", "content"],
    "reason": "Title matches a target title and the posting asks for Python.",
}


def text(obj):
    return json.dumps(obj)


class TestValidator(unittest.TestCase):
    def check(self, raw):
        return claude_judge.validate_output(raw, PID, RESUME)

    def test_accepts_good(self):
        parsed, errors = self.check(text(GOOD))
        self.assertEqual(errors, [])
        self.assertEqual(parsed["verdict"], "relevant")

    def test_accepts_surrounding_whitespace(self):
        self.assertEqual(self.check("\n" + text(GOOD) + "\n")[1], [])

    def test_rejects_code_fence(self):
        self.assertTrue(self.check("```json\n" + text(GOOD) + "\n```")[1])

    def test_rejects_prose_prefix(self):
        self.assertTrue(self.check("Here is my verdict: " + text(GOOD))[1])

    def test_rejects_extra_key(self):
        self.assertTrue(self.check(text({**GOOD, "confidence": 0.9}))[1])

    def test_rejects_missing_key(self):
        bad = dict(GOOD)
        del bad["reason"]
        self.assertTrue(self.check(text(bad))[1])

    def test_rejects_bad_verdict(self):
        for v in ["yes", "Relevant", "maybe", True]:
            self.assertTrue(self.check(text({**GOOD, "verdict": v}))[1], v)

    def test_rejects_wrong_posting_id(self):
        self.assertTrue(self.check(text({**GOOD, "posting_id": "1002"}))[1])

    def test_rejects_unknown_resume_path(self):
        self.assertTrue(self.check(text({**GOOD, "resume_fields": ["skills.rust"]}))[1])

    def test_rejects_contact_field_citation(self):
        self.assertTrue(self.check(text({**GOOD, "resume_fields": ["personal.email"]}))[1])

    def test_rejects_empty_citations(self):
        self.assertTrue(self.check(text({**GOOD, "resume_fields": []}))[1])
        self.assertTrue(self.check(text({**GOOD, "posting_fields": []}))[1])

    def test_rejects_unknown_posting_field(self):
        self.assertTrue(self.check(text({**GOOD, "posting_fields": ["salary"]}))[1])

    def test_rejects_long_reason(self):
        self.assertTrue(self.check(text({**GOOD, "reason": "x" * 501}))[1])

    def test_rejects_non_object(self):
        self.assertTrue(self.check("[1, 2]")[1])
        self.assertTrue(self.check("")[1])


class TestJudgeLabelsAndRejection(unittest.TestCase):
    def posting(self):
        return {p["id"]: p for p in POSTINGS}[PID]

    def test_valid_output_is_labeled_judgment(self):
        out = claude_judge.judge(self.posting(), RESUME, ROOT / "prompts" / "judge_v1_baseline.txt",
                                 runner=lambda s, u, m: (text(GOOD), {"session_id": "fake"}))
        self.assertEqual(out["kind"], "judgment")
        self.assertEqual(out["status"], "valid")
        self.assertIn("model", out)
        self.assertIn("date", out)

    def test_invalid_output_is_rejected_not_repaired(self):
        out = claude_judge.judge(self.posting(), RESUME, ROOT / "prompts" / "judge_v1_baseline.txt",
                                 runner=lambda s, u, m: ("Sure! It's relevant.", {}))
        self.assertEqual(out["status"], "rejected")
        self.assertNotIn("verdict", out)
        self.assertEqual(out["raw"], "Sure! It's relevant.")

    def test_long_content_sent_whole_or_flagged(self):
        # Regression: Run 2 sent only 6000 chars, hiding a "10+ years" requirement at char 6284.
        p = dict(self.posting(), content="x " * 4000 + "10+ years of experience required.")
        self.assertIn("10+ years", claude_judge.build_user_message(p, RESUME))
        out = claude_judge.judge(p, RESUME, ROOT / "prompts" / "judge_v1_baseline.txt",
                                 runner=lambda s, u, m: (text(GOOD), {}))
        self.assertFalse(out["content_truncated"])
        huge = dict(p, content="y" * (claude_judge.MAX_CONTENT + 10))
        out = claude_judge.judge(huge, RESUME, ROOT / "prompts" / "judge_v1_baseline.txt",
                                 runner=lambda s, u, m: (text(GOOD), {}))
        self.assertTrue(out["content_truncated"])

    def test_user_message_has_no_contact_fields(self):
        msg = claude_judge.build_user_message(self.posting(), RESUME)
        for f in ["name", "email", "phone"]:
            self.assertNotIn(RESUME["personal"][f], msg)
        self.assertIn(PID, msg)


if __name__ == "__main__":
    unittest.main()
