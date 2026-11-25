"""Source-grounded shortlist (FILTER.md "Evidence rules" + abstention rule),
written BEFORE js3/shortlist.py existed. No network: Claude is replaced by a
fake client that returns a fixed raw HTTP body, the same shape JS1's
judge.call_claude reads.

Interface fixed here:
    shortlist.validate(raw_text, posting) -> {"verdict", "claims"} or raises
        JudgmentInvalid. Never repairs. A "contradicted_by" quote that is not
        in the posting's own text is INVALID (a contradiction must be
        checkable); a "quote" that is not in the text is NOT invalid - it is
        labeled insufficient by the grounding layer.
    shortlist.label(posting, claims) -> labeled claims; every claim goes
        through js3.grounding.label_claim; contradicted_by -> "contradicted".
    shortlist.judge(posting, resume, client, transcript_dir) -> result with
        status ok | JUDGMENT_INVALID | JUDGMENT_ERROR; always writes a
        transcript (full request + raw response body).
    shortlist.render(result) -> str shown to the user; a relevant verdict
        with any contradicted claim must show the contradiction explicitly.
"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.test_wrong_versions import posting

CONTENT = ("&lt;p&gt;Build LLM agents in Python with RAG pipelines.&lt;/p&gt;"
           "&lt;p&gt;Fully remote within the US.&lt;/p&gt;"
           "&lt;p&gt;This role requires 3 days a week in our Boston office.&lt;/p&gt;")
P = posting(11, "AI Engineer", CONTENT)
RESUME = {"name": "Test Persona", "key_skills": ["Python", "RAG"], "years_of_experience": 1}


def claims_json(verdict="relevant", claims=None, **extra):
    obj = {"verdict": verdict, "claims": claims if claims is not None else [
        {"claim": "Builds LLM agents in Python, matching key_skills.",
         "quote": "Build LLM agents in Python with RAG pipelines.", "contradicted_by": None}]}
    obj.update(extra)
    return json.dumps(obj)


class FakeRaw:
    def __init__(self, body):
        self.text = json.dumps(body)


class FakeClient:
    def __init__(self, text, stop="end_turn", model="claude-opus-5-5"):
        body = {"id": "msg_fake", "model": model, "stop_reason": stop, "usage": {"output_tokens": 1},
                "content": [{"type": "thinking", "thinking": ""}, {"type": "text", "text": text}]}
        create = mock.Mock(return_value=FakeRaw(body))
        self.messages = mock.Mock()
        self.messages.with_raw_response.create = create


def sl():
    import js3.shortlist
    return js3.shortlist


class Validate(unittest.TestCase):
    def assertInvalid(self, raw):
        with self.assertRaises(sl().JudgmentInvalid):
            sl().validate(raw, P)

    def test_valid_object_passes(self):
        out = sl().validate(claims_json(), P)
        self.assertEqual(out["verdict"], "relevant")

    def test_rejects_extra_or_missing_keys(self):
        self.assertInvalid(claims_json(confidence=0.9))
        self.assertInvalid(json.dumps({"verdict": "relevant"}))

    def test_rejects_bad_verdict_and_fences(self):
        self.assertInvalid(claims_json(verdict="Relevant"))
        self.assertInvalid("```json\n" + claims_json() + "\n```")

    def test_rejects_empty_claims_and_malformed_claim(self):
        self.assertInvalid(claims_json(claims=[]))
        self.assertInvalid(claims_json(claims=[{"claim": "x", "quote": None}]))       # missing key
        self.assertInvalid(claims_json(claims=[{"claim": "", "quote": None, "contradicted_by": None}]))
        self.assertInvalid(claims_json(claims=[{"claim": "x", "quote": 5, "contradicted_by": None}]))

    def test_unfindable_contradiction_quote_is_invalid(self):
        self.assertInvalid(claims_json(claims=[{"claim": "Remote.", "quote": "Fully remote within the US.",
                                                "contradicted_by": "On-site five days a week."}]))

    def test_unfindable_supporting_quote_is_not_invalid(self):
        sl().validate(claims_json(claims=[{"claim": "x", "quote": "Not in the posting at all.",
                                           "contradicted_by": None}]), P)


class Label(unittest.TestCase):
    def test_every_label_comes_from_the_grounding_check(self):
        claims = [
            {"claim": "real", "quote": "Build LLM agents in Python with RAG pipelines.", "contradicted_by": None},
            {"claim": "fabricated", "quote": "Five years of PyTorch required.", "contradicted_by": None},
            {"claim": "inference", "quote": None, "contradicted_by": None},
        ]
        self.assertEqual([c["label"] for c in sl().label(P, claims)],
                         ["supported", "insufficient", "insufficient"])

    def test_wrong_version_never_hardcodes_supported(self):
        # FILTER.md wrong version 2, at the shortlist layer.
        r = sl().label(P, [{"claim": "x", "quote": "invented text", "contradicted_by": None}])
        self.assertNotEqual(r[0]["label"], "supported")

    def test_self_flagged_contradiction_is_contradicted_and_keeps_both_quotes(self):
        r = sl().label(P, [{"claim": "Remote-friendly, fits open_to_remote.",
                            "quote": "Fully remote within the US.",
                            "contradicted_by": "This role requires 3 days a week in our Boston office."}])[0]
        self.assertEqual(r["label"], "contradicted")
        self.assertEqual(r["quote_label"], "supported")
        self.assertEqual(r["contradicted_by"], "This role requires 3 days a week in our Boston office.")


class Judge(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_no_api_key_refuses_to_fabricate(self):
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            with self.assertRaises(sl().MissingAPIKey):
                sl().get_client()

    def test_ok_result_and_full_transcript(self):
        r = sl().judge(P, RESUME, FakeClient(claims_json()), transcript_dir=self.tmp)
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["claims"][0]["label"], "supported")
        t = json.loads(Path(r["transcript"]).read_text())
        self.assertEqual(t["request"]["system"], sl().SYSTEM_PROMPT)
        self.assertIn("Build LLM agents", t["request"]["messages"][0]["content"])
        self.assertEqual(t["response_body"]["id"], "msg_fake")

    def test_invalid_output_is_unavailable_not_repaired(self):
        r = sl().judge(P, RESUME, FakeClient("not json"), transcript_dir=self.tmp)
        self.assertEqual(r["status"], "JUDGMENT_INVALID")
        self.assertIsNone(r["verdict"])
        self.assertTrue(Path(r["transcript"]).exists())   # the failure is kept too

    def test_wrong_model_or_stop_reason_is_invalid(self):
        self.assertEqual(sl().judge(P, RESUME, FakeClient(claims_json(), model="other"),
                                    transcript_dir=self.tmp)["status"], "JUDGMENT_INVALID")
        self.assertEqual(sl().judge(P, RESUME, FakeClient(claims_json(), stop="max_tokens"),
                                    transcript_dir=self.tmp)["status"], "JUDGMENT_INVALID")

    def test_transcripts_are_never_overwritten(self):
        a = sl().judge(P, RESUME, FakeClient(claims_json()), transcript_dir=self.tmp)["transcript"]
        b = sl().judge(P, RESUME, FakeClient(claims_json()), transcript_dir=self.tmp)["transcript"]
        self.assertNotEqual(a, b)


class AbstentionRule(unittest.TestCase):
    CONTRA = [{"claim": "Build LLM agents.", "quote": "Build LLM agents in Python with RAG pipelines.",
               "contradicted_by": None},
              {"claim": "Remote-friendly, fits open_to_remote.", "quote": "Fully remote within the US.",
               "contradicted_by": "This role requires 3 days a week in our Boston office."}]

    def result(self, claims, verdict="relevant"):
        tmp = Path(tempfile.mkdtemp())
        return sl().judge(P, RESUME, FakeClient(claims_json(verdict, claims)), transcript_dir=tmp)

    def test_relevant_with_contradiction_surfaces_it(self):
        text = sl().render(self.result(self.CONTRA))
        self.assertIn("CONTRADICTION", text)
        self.assertIn("Remote-friendly, fits open_to_remote.", text)               # not dropped
        self.assertIn("This role requires 3 days a week in our Boston office.", text)
        self.assertIn("Fully remote within the US.", text)

    def test_contradiction_appears_before_the_supported_claims(self):
        text = sl().render(self.result(self.CONTRA))
        self.assertLess(text.index("CONTRADICTION"), text.index("Build LLM agents."))

    def test_no_contradiction_no_warning(self):
        self.assertNotIn("CONTRADICTION", sl().render(self.result(self.CONTRA[:1])))

    def test_every_claim_is_rendered_with_its_label(self):
        text = sl().render(self.result(self.CONTRA))
        self.assertIn("[supported]", text)
        self.assertIn("[contradicted]", text)


if __name__ == "__main__":
    unittest.main()
