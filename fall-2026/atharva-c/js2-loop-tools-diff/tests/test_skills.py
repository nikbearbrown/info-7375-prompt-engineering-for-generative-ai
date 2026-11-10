"""React/Go skill-matching tests, written BEFORE the patch (review packet).

Expected answers are Atharva's labels from Nov 9, 2026:
- the 5 real Wealthfront matches in evidence/skills-defect-repro-20261109.txt
  (#1 "react to new insights" and #3 "go-to designer" are NOT skills;
  #2, #4, #5 are), and
- 6 extra cases he chose (lowercase "go", React Native, ReactJS, React.js, Golang).

Accepted as a known miss (not tested): "Go build something people love." --
capital Go at the start of a sentence is allowed to match.
"""

import json
import unittest
from pathlib import Path

from agent.skills import lever_text, match_skills

ROOT = Path(__file__).resolve().parent.parent
WEALTHFRONT = ROOT / "evidence/run-20261109-041358Z/raw/03-wealthfront-a1.json"

# (phrase, skill, should_match)
CASES = [
    # the 5 real Wealthfront matches
    ("you'll be trusted to move quickly to react to new insights", "React", False),
    ("proficiency with at least one language such as Go, Python, or Ruby", "Go", True),
    ("Become the go-to designer for investing initiatives", "Go", False),
    ("build tools and services using Go and Java", "Go", True),
    ("at least one modern front-end framework (React, Vue, Angular, etc)", "React", True),
    # extra cases
    ("ready to hit the ground running and go", "Go", False),
    ("Experience with React Native", "React", True),
    ("built with ReactJS", "React", True),
    ("a single-page app in React.js", "React", True),
    ("backend services in Golang", "Go", True),
]


class SkillPhraseTests(unittest.TestCase):
    def test_labeled_phrases(self):
        for phrase, skill, should in CASES:
            with self.subTest(phrase=phrase, skill=skill):
                got = skill in match_skills(phrase, [skill])
                self.assertEqual(got, should,
                                 f"{skill!r} in {phrase!r}: expected match={should}, got {got}")


class RealPostingTests(unittest.TestCase):
    """The same labels, checked on the real saved postings (23 Wealthfront jobs)."""

    @classmethod
    def setUpClass(cls):
        postings = json.loads(json.loads(WEALTHFRONT.read_text())["body"])
        cls.by_id = {p["id"]: p for p in postings}

    def matched(self, posting_id):
        text = " ".join(lever_text(self.by_id[posting_id]).split())
        return match_skills(text, ["Go", "React"])

    def test_director_pm_is_not_react(self):
        self.assertNotIn("React", self.matched("a577f609-b61b-4c26-b0a5-e74f2004d669"))

    def test_product_designer_is_not_go(self):
        self.assertNotIn("Go", self.matched("cab92a5e-7cc5-48ea-9755-5f9f2fdcfad9"))

    def test_network_engineer_is_go(self):
        self.assertIn("Go", self.matched("93383267-2d57-45d0-bb6a-7d9c5d8b6f3c"))

    def test_devops_engineer_is_go(self):
        self.assertIn("Go", self.matched("91c149ed-18fa-4e72-a3a6-386840aae86e"))

    def test_frontend_engineer_is_react(self):
        self.assertIn("React", self.matched("a4a9fd4e-d33a-4767-995f-7a2286bc9762"))


if __name__ == "__main__":
    unittest.main()
