"""The two "Wrong versions" tests from CONTRACT.md, written before the
implementation existed.

The implementation under test is chosen by the JS1_IMPL environment variable
(default: agent.rule). Run against the deliberately wrong stub with:

    JS1_IMPL=agent.wrong_stub python3 -m unittest -v tests.test_wrong_versions

Postings here are CONSTRUCTED test fixtures, not real board data.
"""
import importlib
import json
import os
import unittest
from pathlib import Path

impl = importlib.import_module(os.environ.get("JS1_IMPL", "agent.rule"))

ROOT = Path(__file__).resolve().parent.parent
RESUME = json.loads((ROOT / "resume.json").read_text())

# Constructed: matches 0 of the 6 skills -> "not relevant".
POSTING_NOT_RELEVANT = {
    "id": 1001,
    "title": "Senior Backend Engineer, Ruby on Rails",
    "content": "<p>You will maintain our Rails monolith and PostgreSQL schemas.</p>",
}
# Constructed: matches Python, PyTorch, LLM (3 of 6) -> "relevant".
POSTING_RELEVANT = {
    "id": 2002,
    "title": "Machine Learning Engineer, LLM Platform",
    "content": "<p>Ship Python services and train PyTorch models.</p>",
}


class WrongVersion1LabelPostingMismatch(unittest.TestCase):
    """CONTRACT.md wrong version 1: verdicts zipped against postings in the
    wrong order. Two postings with clearly different expected verdicts;
    verdict[0] must correspond to posting[0]'s id, not posting[1]'s."""

    def test_verdict_0_belongs_to_posting_0(self):
        postings = [POSTING_NOT_RELEVANT, POSTING_RELEVANT]
        results = impl.evaluate(postings, RESUME)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], postings[0]["id"])
        self.assertNotEqual(results[0]["id"], postings[1]["id"])
        self.assertEqual(results[0]["verdict"], "not relevant")
        self.assertEqual(results[1]["id"], postings[1]["id"])
        self.assertEqual(results[1]["verdict"], "relevant")


class WrongVersion2JustificationCitesNothing(unittest.TestCase):
    """CONTRACT.md wrong version 2: correct verdict, generic justification.
    The justification must contain at least one literal skill or field value
    from either the resume or the posting JSON - not just prose."""

    @staticmethod
    def _literal_values(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                yield from WrongVersion2JustificationCitesNothing._literal_values(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from WrongVersion2JustificationCitesNothing._literal_values(v)
        elif isinstance(obj, str) and obj.strip():
            yield obj

    def test_justification_contains_a_literal_value(self):
        for posting in (POSTING_NOT_RELEVANT, POSTING_RELEVANT):
            with self.subTest(posting_id=posting["id"]):
                result = impl.evaluate([posting], RESUME)[0]
                literals = list(self._literal_values(RESUME)) + list(
                    self._literal_values(posting)
                )
                self.assertTrue(
                    any(lit in result["justification"] for lit in literals),
                    f"justification cites no resume/posting value: "
                    f"{result['justification']!r}",
                )


if __name__ == "__main__":
    unittest.main()
