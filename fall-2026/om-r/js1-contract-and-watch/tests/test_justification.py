"""Stricter justification requirements (beyond CONTRACT.md's minimum),
written before the implementation existed:

- a "relevant" justification names every matched skill and quotes the exact
  posting field text it was found in;
- building a justification around a term that is not really in the posting
  raises instead of passing silently.

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


class TheRule(unittest.TestCase):
    def test_two_skills_is_relevant(self):
        p = {"id": 1, "title": "Python Engineer", "content": "<p>Uses PyTorch.</p>"}
        self.assertEqual(impl.verdict(p), "relevant")

    def test_one_skill_is_not_relevant(self):
        p = {"id": 2, "title": "Python Engineer", "content": "<p>Django.</p>"}
        self.assertEqual(impl.verdict(p), "not relevant")

    def test_whole_word_only(self):
        # "Pythonic" and "dragon" contain "Python"/"rag" but not as whole words.
        p = {"id": 3, "title": "Pythonic dragon tamer", "content": "<p>storage</p>"}
        self.assertEqual(impl.matched_skills(p), [])

    def test_case_insensitive_and_multiword(self):
        p = {"id": 4, "title": "rag pipelines", "content": "<p>Vector Databases at scale</p>"}
        self.assertEqual(
            sorted(m.skill for m in impl.matched_skills(p)), ["RAG", "vector databases"]
        )

    def test_skill_counted_once_across_fields(self):
        p = {"id": 5, "title": "Python Engineer", "content": "<p>Python, Python.</p>"}
        self.assertEqual(impl.verdict(p), "not relevant")

    def test_greenhouse_escaped_html_content(self):
        # Greenhouse returns content as HTML-escaped HTML.
        p = {"id": 6, "title": "Engineer",
             "content": "&lt;p&gt;Python and &lt;strong&gt;LangChain&lt;/strong&gt;&lt;/p&gt;"}
        self.assertEqual(impl.verdict(p), "relevant")


class Justification(unittest.TestCase):
    POSTING = {
        "id": 7,
        "title": "ML Engineer, LLM Platform",
        "content": "<p>Build RAG services in Python on our platform.</p>",
    }

    def test_names_each_matched_skill_and_quotes_its_field(self):
        j = impl.justify(self.POSTING, RESUME)
        for skill, field in (("LLM", "posting.title"), ("RAG", "posting.content"),
                             ("Python", "posting.content")):
            self.assertIn(f'"{skill}"', j)
            self.assertIn(field, j)
        self.assertIn('"ML Engineer, LLM Platform"', j)  # exact title quoted
        self.assertIn("resume.key_skills", j)

    def test_quotes_are_exact_substrings_of_the_posting(self):
        for m in impl.matched_skills(self.POSTING):
            self.assertIn(m.quote, impl.field_text(self.POSTING, m.field))

    def test_fabricated_match_raises(self):
        fake = impl.Match(skill="LangChain", field="title", quote="ML Engineer, LLM Platform")
        with self.assertRaises(impl.JustificationError):
            impl.build_justification(self.POSTING, RESUME, [fake])

    def test_fabricated_quote_raises(self):
        fake = impl.Match(skill="Python", field="content", quote="we love Python")
        with self.assertRaises(impl.JustificationError):
            impl.build_justification(self.POSTING, RESUME, [fake])

    def test_skill_not_in_resume_raises(self):
        resume = dict(RESUME, key_skills=["SQL"])
        with self.assertRaises(impl.JustificationError):
            impl.justify(self.POSTING, resume)


if __name__ == "__main__":
    unittest.main()
