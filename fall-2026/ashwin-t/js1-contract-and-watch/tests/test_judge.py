"""The AI JUDGMENT validator (CONTRACT.md, Out 3). Every reply here is CONSTRUCTED, not Claude output."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from jobwatch import judge, watch
from jobwatch.rule import RELEVANT
from tests.helpers import RESUME, ROOT, board_bytes, make_posting

POSTING = make_posting(7855798003, "Software Engineer II - Recommendations",
                       "<p>Proficient in Python. Redis and Kubernetes.</p><p>2+ years of experience.</p>")


def reply(**overrides):
    body = {"posting_id": "7855798003", "verdict": "NOT_RELEVANT",
            "reason": "Asks for 2+ years; the persona is a new grad.",
            "evidence": [{"resume_field": "experience_level", "posting_field": "content",
                          "posting_quote": "2+ years of experience"}]}
    body.update(overrides)
    return json.dumps(body)


def errors_for(text):
    return judge.validate_reply(text, POSTING, RESUME)[1]


class Validator(unittest.TestCase):
    def test_a_well_formed_supported_reply_passes(self):
        self.assertEqual(errors_for(reply()), [])
        skill = [{"resume_field": "skills[0]", "posting_field": "content", "posting_quote": "Proficient in Python"}]
        self.assertEqual(errors_for(reply(verdict="RELEVANT", evidence=skill)), [])

    def test_wrong_posting_id_is_rejected(self):
        self.assertTrue(any("rule 2" in e for e in errors_for(reply(posting_id="8041054003"))))

    def test_anything_but_bare_json_is_rejected(self):
        for text in ("```json\n" + reply() + "\n```", "Sure! " + reply(), "", "[1, 2]"):
            self.assertTrue(errors_for(text), text[:30])

    def test_missing_extra_keys_and_unknown_verdict_are_rejected(self):
        extra = json.loads(reply())
        extra["confidence"] = 0.9
        self.assertTrue(errors_for(json.dumps(extra)))
        self.assertTrue(errors_for(reply(verdict="MAYBE")))
        self.assertTrue(errors_for(reply(reason="  ")))
        self.assertTrue(errors_for(reply(evidence=[])))

    def test_fabricated_quote_is_rejected(self):
        fake = [{"resume_field": "skills[1]", "posting_field": "content", "posting_quote": "Strong Java experience"}]
        errs = errors_for(reply(verdict="RELEVANT", evidence=fake))
        self.assertTrue(any("rule 8" in e for e in errs))
        self.assertTrue(any("rule 9" in e for e in errs))

    def test_real_quote_but_unsupported_skill_is_rejected(self):
        # The quote exists, but it does not support skills[1] = Java.
        sneaky = [{"resume_field": "skills[1]", "posting_field": "content", "posting_quote": "Proficient in Python"}]
        errs = errors_for(reply(verdict="RELEVANT", evidence=sneaky))
        self.assertTrue(any("rule 9" in e for e in errs))

    def test_unknown_fields_and_empty_quotes_are_rejected(self):
        for ev in ([{"resume_field": "skills[99]", "posting_field": "content", "posting_quote": "python"}],
                   [{"resume_field": "salary", "posting_field": "content", "posting_quote": "python"}],
                   [{"resume_field": "skills[0]", "posting_field": "benefits", "posting_quote": "python"}],
                   [{"resume_field": "skills[0]", "posting_field": "content", "posting_quote": ""}]):
            self.assertTrue(errors_for(reply(evidence=ev)), ev)

    def test_wrong_json_types_are_rejected_not_crashed_on(self):
        # Found by Ashwin's review on 2026-10-31: posting_field [] raised TypeError instead of failing validation.
        for field, value in (("posting_field", []), ("posting_field", {}), ("posting_field", 7),
                             ("resume_field", []), ("resume_field", None), ("posting_quote", 5), ("posting_quote", [])):
            ev = [{"resume_field": "skills[0]", "posting_field": "content", "posting_quote": "Proficient in Python"}]
            ev[0][field] = value
            self.assertTrue(errors_for(reply(verdict="RELEVANT", evidence=ev)), (field, value))


class JudgeAndRule(unittest.TestCase):
    def test_invalid_reply_keeps_the_rule_record_and_invents_nothing(self):
        d = Path(tempfile.mkdtemp())
        fixture = d / "board.json"
        state = d / "seen_ids.json"
        fixture.write_bytes(board_bytes([]))
        watch.run(ROOT / "data/supriya-sharma.resume.json", state, d / "runs", fixture=fixture,
                  collected_at="2026-10-30T12:00:00Z")
        fixture.write_bytes(board_bytes([POSTING]))
        fake = lambda prompt: {"ok": True, "text": "I think it is relevant!", "called_at": "t", "model": "fake"}
        s = watch.run(ROOT / "data/supriya-sharma.resume.json", state, d / "runs", fixture=fixture,
                      collected_at="2026-10-30T12:00:00Z", caller=fake, prompt_path=ROOT / "prompts/baseline-v1.md")
        r = json.loads((Path(s["run_dir"]) / "report.json").read_text())["results"][0]
        self.assertEqual(r["rule_record"]["verdict"], RELEVANT)
        self.assertEqual(r["ai_judgment"]["status"], judge.VALIDATION_FAILED)
        self.assertIsNone(r["ai_judgment"]["verdict"])
        self.assertFalse(r["disagreement"])
        self.assertIn("UNAVAILABLE — VALIDATION FAILED", (Path(s["run_dir"]) / "report.md").read_text())

    def test_prompt_marks_posting_as_untrusted_data(self):
        _, template = judge.load_prompt(ROOT / "prompts/baseline-v1.md")
        prompt = judge.build_prompt(template, POSTING, RESUME)
        self.assertIn("untrusted", prompt)
        self.assertIn('"posting_id": "7855798003"', prompt)
        self.assertNotIn("<p>", prompt)

    def test_claude_call_is_tool_free_and_isolated(self):
        seen = {}

        def runner(cmd, **kw):
            seen.update(cmd=cmd, cwd=kw["cwd"], input=kw["input"])
            out = json.dumps({"result": reply(), "is_error": False, "session_id": "s",
                              "modelUsage": {"claude-test": {}}})
            return subprocess.CompletedProcess(cmd, 0, out, "")
        result = judge.call_claude("PROMPT", runner=runner)
        self.assertTrue(result["ok"])
        self.assertEqual(result["model"], "claude-test")
        self.assertEqual(seen["cmd"][seen["cmd"].index("--tools") + 1], "")
        self.assertIn("--no-session-persistence", seen["cmd"])
        self.assertEqual(seen["input"], "PROMPT")
        self.assertFalse(Path(seen["cwd"]).exists())        # the empty folder is gone afterwards

    def test_claude_failures_are_reported_not_guessed(self):
        bad = judge.call_claude("P", runner=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 1, "", "auth"))
        self.assertFalse(bad["ok"])
        caller = lambda prompt: bad
        j = judge.judge(POSTING, RESUME, "baseline-v1", "<<RESUME_JSON>><<POSTING_JSON>>", caller)
        self.assertEqual((j["status"], j["verdict"]), (judge.CALL_FAILED, None))


if __name__ == "__main__":
    unittest.main()
