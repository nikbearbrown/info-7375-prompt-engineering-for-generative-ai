"""Judgment-step validator: wrong-version tests, plus judge() failure handling.

The validator under test is chosen by JS1_JUDGE_IMPL (default: agent.judge).
Run against the deliberately lenient stub with:

    JS1_JUDGE_IMPL=agent.wrong_validator_stub python3 -m unittest -v tests.test_judge

Every "Claude output" string below is a CONSTRUCTED test input, not a real
API response. FakeClient is a test double; it never stands in for Claude in
the agent itself.
"""
import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agent import judge

impl = importlib.import_module(os.environ.get("JS1_JUDGE_IMPL", "agent.judge"))

ROOT = Path(__file__).resolve().parent.parent
RESUME = json.loads((ROOT / "resume.json").read_text())
POSTING = {
    "id": 2002,
    "title": "Machine Learning Engineer, LLM Platform",
    "content": "&lt;p&gt;Ship Python services that serve retrieval results.&lt;/p&gt;",
}
GOOD = json.dumps({"verdict": "relevant",
                   "justification": "resume.key_skills lists Python; posting.content asks for Python services."})


class WrongVersionsRejected(unittest.TestCase):
    """Each of these must be REJECTED, not repaired and accepted."""

    def assertRejected(self, raw):
        with self.assertRaises(impl.JudgmentInvalid, msg=f"accepted: {raw!r}"):
            impl.validate(raw, POSTING, RESUME)

    def test_markdown_fences_rejected(self):
        self.assertRejected("```json\n" + GOOD + "\n```")

    def test_extra_confidence_key_rejected(self):
        self.assertRejected(json.dumps({**json.loads(GOOD), "confidence": 0.9}))

    def test_capitalized_verdict_rejected(self):
        self.assertRejected(json.dumps({**json.loads(GOOD), "verdict": "Relevant"}))

    def test_other_verdict_strings_rejected(self):
        for v in ("RELEVANT", "irrelevant", "not_relevant", "relevant ", "maybe", True, None):
            with self.subTest(verdict=v):
                self.assertRejected(json.dumps({**json.loads(GOOD), "verdict": v}))

    def test_prose_around_json_rejected(self):
        self.assertRejected("Here is my answer:\n" + GOOD)
        self.assertRejected(GOOD + "\nLet me know if you need more.")

    def test_missing_key_rejected(self):
        self.assertRejected(json.dumps({"verdict": "relevant"}))

    def test_duplicate_key_rejected(self):
        self.assertRejected('{"verdict": "relevant", "verdict": "not relevant", '
                            '"justification": "Python"}')

    def test_non_object_rejected(self):
        self.assertRejected(json.dumps([json.loads(GOOD)]))

    def test_ungrounded_justification_rejected(self):
        self.assertRejected(json.dumps({"verdict": "relevant",
                                        "justification": "Seems like a good fit."}))

    def test_skills_absent_from_posting_rejected(self):
        # LangGraph and SQL are in resume.key_skills but NOT in POSTING:
        # naming them grounds nothing (the loophole closed on 2026-10-30).
        self.assertRejected(json.dumps({"verdict": "not relevant",
                                        "justification": "resume.key_skills has LangGraph and SQL; "
                                                         "posting.title is ML platform work"}))

    def test_posting_word_not_in_key_skills_rejected(self):
        # "retrieval" is in the posting but not in resume.key_skills, and unquoted.
        self.assertRejected(json.dumps({"verdict": "relevant",
                                        "justification": "posting.content mentions retrieval work"}))

    def test_fabricated_quote_rejected(self):
        # Quoted, long enough, but not in the posting, and names no key skill.
        self.assertRejected(json.dumps({"verdict": "relevant",
                                        "justification": 'posting.content says "deep expertise in Kubernetes"'}))


class ValidAccepted(unittest.TestCase):
    def test_key_skill_named(self):
        self.assertEqual(impl.validate(GOOD, POSTING, RESUME)["verdict"], "relevant")

    def test_verbatim_posting_quote_without_key_skill(self):
        raw = json.dumps({"verdict": "not relevant",
                          "justification": 'posting.content: "serve retrieval results" is not a target role'})
        self.assertEqual(impl.validate(raw, POSTING, RESUME)["verdict"], "not relevant")

    def test_judge_may_disagree_with_rule(self):
        # The rule says "relevant" here (LLM + Python). The judgment may say
        # otherwise, as long as a cited skill really is in the posting.
        raw = json.dumps({"verdict": "not relevant",
                          "justification": "posting.content only asks for Python services; "
                                           "resume.target_roles wants AI Engineer work"})
        self.assertEqual(impl.validate(raw, POSTING, RESUME)["verdict"], "not relevant")

    def test_absent_skill_alongside_present_one_accepted(self):
        # Saying the posting lacks a skill is fair reasoning; Python grounds it.
        raw = json.dumps({"verdict": "not relevant",
                          "justification": "posting.content asks for Python but never mentions PyTorch"})
        self.assertEqual(impl.validate(raw, POSTING, RESUME)["verdict"], "not relevant")

    def test_skill_matching_uses_rules_whole_word_standard(self):
        p = dict(POSTING, content="&lt;p&gt;Pythonic tooling and vector   databases.&lt;/p&gt;")
        # "Python" is not a whole word in "Pythonic": does not ground.
        with self.assertRaises(impl.JudgmentInvalid):
            impl.validate(json.dumps({"verdict": "relevant", "justification": "needs Python"}), p, RESUME)
        # Multi-word skill across collapsed whitespace, case-insensitive: grounds.
        ok = json.dumps({"verdict": "relevant", "justification": "resume.key_skills: Vector Databases"})
        self.assertEqual(impl.validate(ok, p, RESUME)["verdict"], "relevant")


class FakeClient:
    """Test double returning a fixed CONSTRUCTED body."""
    def __init__(self, text, stop_reason="end_turn", model=judge.MODEL):
        self.calls = 0
        body = {"model": model, "stop_reason": stop_reason,
                "content": [{"type": "thinking", "thinking": ""}, {"type": "text", "text": text}]}
        outer = self

        class _Raw:
            def create(self, **kw):
                outer.calls += 1
                outer.kwargs = kw
                return mock.Mock(text=json.dumps(body))

        self.messages = mock.Mock(with_raw_response=_Raw())


@unittest.skipIf(os.environ.get("JS1_JUDGE_IMPL"), "judge() tests target agent.judge only")
class JudgeFailureHandling(unittest.TestCase):
    def setUp(self):
        self.log = Path(tempfile.mkdtemp()) / "events.jsonl"

    def test_invalid_output_logged_and_unavailable_no_retry_no_fallback(self):
        client = FakeClient("```json\n" + GOOD + "\n```")
        r = judge.judge(POSTING, RESUME, client, log_path=self.log)
        self.assertEqual(client.calls, 1)  # no silent retry
        self.assertEqual(r["status"], "JUDGMENT_INVALID")
        self.assertIsNone(r["verdict"])  # not the rule's verdict, not a default
        events = [json.loads(l) for l in self.log.read_text().splitlines()]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "JUDGMENT_INVALID")
        self.assertIn("```json", events[0]["raw_output"])

    def test_truncated_output_is_invalid(self):
        r = judge.judge(POSTING, RESUME, FakeClient(GOOD, stop_reason="max_tokens"), log_path=self.log)
        self.assertEqual(r["status"], "JUDGMENT_INVALID")
        self.assertIsNone(r["verdict"])

    def test_api_error_logged_and_unavailable(self):
        client = mock.Mock()
        client.messages.with_raw_response.create.side_effect = ConnectionError("boom")
        r = judge.judge(POSTING, RESUME, client, log_path=self.log)
        self.assertEqual(r["status"], "JUDGMENT_ERROR")
        self.assertIsNone(r["verdict"])
        self.assertTrue(self.log.exists())

    def test_valid_output_accepted_and_not_logged(self):
        client = FakeClient(GOOD)
        r = judge.judge(POSTING, RESUME, client, log_path=self.log)
        self.assertEqual((r["status"], r["verdict"]), ("ok", "relevant"))
        self.assertFalse(self.log.exists())
        self.assertEqual(client.kwargs["model"], "claude-opus-5-5")
        self.assertNotIn("temperature", client.kwargs)

    def test_model_pinned_no_fallback_requested(self):
        client = FakeClient(GOOD)
        judge.judge(POSTING, RESUME, client, log_path=self.log)
        self.assertNotIn("fallbacks", client.kwargs.get("extra_body", {}))
        self.assertNotIn("anthropic-beta", client.kwargs.get("extra_headers") or {})

    def test_other_served_model_is_invalid(self):
        r = judge.judge(POSTING, RESUME, FakeClient(GOOD, model="claude-opus-5"), log_path=self.log)
        self.assertEqual(r["status"], "JUDGMENT_INVALID")
        self.assertIsNone(r["verdict"])

    def test_missing_api_key_refuses_instead_of_faking(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(judge.MissingAPIKey):
                judge.get_client()


@unittest.skipIf(os.environ.get("JS1_JUDGE_IMPL"), "prompt tests target agent.judge only")
class PromptVersions(unittest.TestCase):
    def test_production_judge_v1_unchanged(self):
        # Pinned to the exact prompt recorded in all 20 Sampling Report calls.
        import hashlib
        self.assertEqual(hashlib.sha256(judge.PROMPTS["judge-v1"].encode()).hexdigest(),
                         "f9a101fe0335edcdb227faf8f17d264b32b3d9efeb5966f7d6ed1dd5b59d7a19")
        self.assertIs(judge.PROMPTS["judge-v1"], judge.SYSTEM_PROMPT)
        self.assertEqual(judge.PROMPT_VERSION, "judge-v1")

    def test_dev_v1_is_dev_v0_plus_exactly_one_sentence(self):
        v0, v1 = judge.PROMPTS["judge-dev-v0"], judge.PROMPTS["judge-dev-v1"]
        s = judge.DEV_REVISION_SENTENCE
        self.assertNotIn(s, v0)
        self.assertEqual(v1.count(s), 1)
        self.assertEqual(v1.replace(" " + s, "", 1), v0)

    def test_dev_prompts_scope_out_candidate_attributes(self):
        v0 = judge.PROMPTS["judge-dev-v0"]
        self.assertIn("Ignore the candidate's seniority level, years of experience, location, "
                      "remote status, and visa/sponsorship needs entirely", v0)
        self.assertNotIn("relevant to one job seeker", v0)

    def test_chosen_prompt_is_sent_and_recorded(self):
        for version in ("judge-dev-v0", "judge-dev-v1"):
            with self.subTest(version=version):
                client = FakeClient(GOOD)
                log = Path(tempfile.mkdtemp()) / "e.jsonl"
                r = judge.judge(POSTING, RESUME, client, log_path=log, prompt_version=version)
                self.assertEqual(client.kwargs["system"], judge.PROMPTS[version])
                self.assertEqual(r["prompt_version"], version)

    def test_default_is_still_production_prompt(self):
        client = FakeClient(GOOD)
        r = judge.judge(POSTING, RESUME, client, log_path=Path(tempfile.mkdtemp()) / "e.jsonl")
        self.assertEqual(client.kwargs["system"], judge.SYSTEM_PROMPT)
        self.assertEqual(r["prompt_version"], "judge-v1")

    def test_unknown_prompt_rejected(self):
        with self.assertRaises(ValueError):
            judge.judge(POSTING, RESUME, FakeClient(GOOD), prompt_version="judge-dev-v2")


if __name__ == "__main__":
    unittest.main()
