"""Shortlist evidence rules (FILTER.md section 2). No network: Claude's responses are fixtures shaped like the real API."""
import unittest

from helpers import HERE  # noqa: F401
from jsa3 import shortlist as S

POST = {"id": "9", "title": "Applied AI Engineer", "location": "San Francisco, CA",
        "text": "You will build LLM agents in Python. Requirements: 7+ years of software engineering experience."}


def response(claims, stop="end_turn"):
    import json
    return {"stop_reason": stop, "content": [{"type": "text", "text": json.dumps({"claims": claims})}]}


class Prelabel(unittest.TestCase):
    def test_WF3_never_supported_even_when_the_word_matches(self):
        # WF3: the word "LLM" is in the quote and the text; a relevance check would call C4 supported.
        c = {"id": "C4", "claim": "The work uses LLMs, a skill Priya has.", "quote": "You will build LLM agents in Python."}
        self.assertEqual(S.prelabel(c, POST), "not reviewed")

    def test_contradicting_quote_is_still_only_not_reviewed(self):
        c = {"id": "C3", "claim": "The level fits early-career.", "quote": "7+ years of software engineering experience"}
        self.assertEqual(S.prelabel(c, POST), "not reviewed")  # Mayank labels it contradicted, not the code

    def test_missing_or_invented_quote_is_insufficient(self):
        self.assertTrue(S.prelabel({"id": "C2", "claim": "x", "quote": ""}, POST).startswith("insufficient"))
        self.assertTrue(S.prelabel({"id": "C2", "claim": "x", "quote": "Remote anywhere in the US"}, POST).startswith("insufficient"))

    def test_quote_match_ignores_whitespace_and_case(self):
        self.assertTrue(S.quote_found("you will  build llm\nagents", POST))


class Parse(unittest.TestCase):
    def test_claims_from_response_and_failures(self):
        good = response([{"id": "C1", "claim": "a", "quote": "b"}])
        self.assertEqual(len(S.claims_from(good)), 1)
        self.assertEqual(S.claims_from({"error": {"status": 529}}), [])
        self.assertEqual(S.claims_from(response([], stop="refusal")), [])

    def test_select_ranks_role_word_then_score_and_only_keeps(self):
        recs = [{"verdict": "keep", "role_match": None, "score": 5, "board": "b", "id": "1"},
                {"verdict": "keep", "role_match": "LLM", "score": 1, "board": "b", "id": "2"},
                {"verdict": "reject", "role_match": None, "score": 7, "board": "b", "id": "3"}]
        self.assertEqual([r["id"] for r in S.select(recs, 5)], ["2", "1"])

    def test_only_this_module_names_the_api_host(self):
        for f in (HERE / "src").rglob("*.py"):
            if f.name != "shortlist.py":
                self.assertNotIn("api.anthropic.com", f.read_text(), f)


if __name__ == "__main__":
    unittest.main()
