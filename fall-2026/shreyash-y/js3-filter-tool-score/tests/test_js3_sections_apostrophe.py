"""Found by Shreyash's hand label of posting 8 (klaviyo:8215593003, 2026-11-25): his note said "No
experience requirement is shown". The ad's requirements heading is "What We’re Looking For:" with a
curly apostrophe, and js3/sections.py only knew a straight one, so the section was classed 'other' and
the label tool's requirements excerpt left out "7+ years of experience in a software engineering role."
Written by Claude Code before the fix."""
import unittest

from js3 import sections


class CurlyApostrophes(unittest.TestCase):
    def test_requirements_heading_with_a_curly_apostrophe(self):
        self.assertEqual(sections.kind_of("What We’re Looking For:"), "req")
        self.assertEqual(sections.kind_of("What We're Looking For:"), "req")

    def test_benefits_headings_with_curly_apostrophes(self):
        self.assertEqual(sections.kind_of("What’s in it for you"), "perk")
        self.assertEqual(sections.kind_of("Why you’ll love working here"), "perk")

    def test_responsibilities_heading_with_a_curly_apostrophe(self):
        self.assertEqual(sections.kind_of("What You’ll Do"), "resp")

    def test_the_real_posting_8_requirements_are_a_requirements_section(self):
        from js3 import corpus
        p = {x["key"]: x for x in corpus.load()}["klaviyo:8215593003"]
        i = p["content"].index("7+ years of experience in a software engineering role")
        kinds = [k for a, b, k, h in sections.blocks_for_plain(p["content"]) if a <= i < b]
        stored = [k for a, b, k, h in p["blocks"] if a <= i < b]
        self.assertEqual(stored, ["req"], "the corpus stores the section as requirements")


if __name__ == "__main__":
    unittest.main()
