"""Tests for agent/shortlist.py (FILTER.md section 2), written before agent/shortlist.py.

    python3 -m unittest -v tests.test_shortlist
"""

from __future__ import annotations

import unittest

from agent import shortlist as S
from agent.postings import load_run

RUN = "evidence/run-20261123-185425Z"
SKILLS = ["Python", "Go", "React", "TypeScript", "SQL", "Java"]


def posting(title="Software Engineer, Backend", location="Remote US", text="", uid="t:1"):
    return {"uid": uid, "board": "t", "title": title, "location": location, "text": text, "url": "https://example.test"}


def claims(p):
    return {c["id"]: c for c in S.claims_for(p, SKILLS)}


class QuotesAreVerbatim(unittest.TestCase):
    """Section 2: every quote is copied exactly (a substring of the posting)."""

    def test_every_quote_on_the_real_shortlist(self):
        ps = {p["uid"]: p for p in load_run(RUN)}
        entries = S.build("evidence/filter-v1.2/decisions.jsonl", RUN, SKILLS)
        n = 0
        for e in entries:
            for uid in e["uids"]:
                p = ps[uid]
                whole = "\n".join([p["title"], p["location"] or "", p["text"]])
                for c in e["claims"]:
                    for q in c["quotes"]:
                        self.assertIn(q, whole, (uid, c["id"]))
                        n += 1
        self.assertGreater(n, 0)


class Labels(unittest.TestCase):
    def test_role_from_title(self):
        self.assertEqual(claims(posting())["role"]["label"], "supported")
        self.assertEqual(claims(posting("Sales Engineer"))["role"]["label"], "insufficient")

    def test_years_supported_contradicted_insufficient(self):
        self.assertEqual(claims(posting(text="2+ years of experience in software development."))["years"]["label"], "supported")
        self.assertEqual(claims(posting(text="3+ years of experience in test automation."))["years"]["label"], "contradicted")
        self.assertEqual(claims(posting(text="You will build services."))["years"]["label"], "insufficient")
        self.assertEqual(claims(posting(text="No fixed minimum years of experience required."))["years"]["label"], "supported")

    def test_relevance_is_not_entailment(self):
        # "2+ years" is relevant to level and supports "asks at most 2 years",
        # but does not say "entry-level"; "track record" says the opposite.
        c = claims(posting(text="2+ years of experience in software development.\n"
                                "Strong track record of successfully delivering large-scope technical projects."))
        self.assertEqual(c["years"]["label"], "supported")
        self.assertEqual(c["entry"]["label"], "contradicted")

    def test_years_alone_do_not_support_entry(self):
        c = claims(posting(text="2+ years of experience in software development."))
        self.assertEqual(c["entry"]["label"], "insufficient")

    def test_contradicted_beats_supported_and_keeps_both_quotes(self):
        c = claims(posting(text="Open to new grads.\nA track record of delivering high-quality code."))["entry"]
        self.assertEqual(c["label"], "contradicted")
        self.assertEqual(len(c["quotes"]), 2)

    def test_title_level_is_not_support(self):
        # W2 lesson: "Engineer I" in the title is a level name, not a statement.
        self.assertEqual(claims(posting("Software Engineer I"))["entry"]["label"], "insufficient")

    def test_location_never_inferred(self):
        self.assertEqual(claims(posting(location="Remote US"))["us"]["label"], "supported")
        self.assertEqual(claims(posting(location="Remote Canada"))["us"]["label"], "contradicted")
        self.assertEqual(claims(posting(location=""))["us"]["label"], "insufficient")

    def test_nice_to_have_skill_is_not_support(self):
        c = claims(posting(text="Experience with Kafka or SQL is a plus."))["skill"]
        self.assertEqual(c["label"], "insufficient")
        c = claims(posting(text="You will write Python services every day."))["skill"]
        self.assertEqual(c["label"], "supported")


class Abstention(unittest.TestCase):
    def test_two_insufficient_goes_to_cannot_tell(self):
        e = S.entry([posting("Software Engineer I", text="You will build things.")], SKILLS, score=0.8)
        self.assertEqual(e["list"], "cannot_tell")

    def test_one_insufficient_is_ranked(self):
        e = S.entry([posting(text="2+ years of experience. You will write Python services.")], SKILLS, score=0.9)
        self.assertEqual(e["list"], "ranked")

    def test_contradicted_is_flagged_not_ranked(self):
        e = S.entry([posting(text="3+ years of experience. You will write Python services.")], SKILLS, score=0.6)
        self.assertEqual(e["list"], "contradicted")


class Grouping(unittest.TestCase):
    def test_same_board_and_title_is_one_entry(self):
        ds = [{"uid": "a", "board": "t", "title": "Software Engineer", "keep": True, "score": 0.9},
              {"uid": "b", "board": "t", "title": "Software Engineer", "keep": True, "score": 0.9}]
        self.assertEqual([g["uids"] for g in S.group(ds)], [["a", "b"]])


if __name__ == "__main__":
    unittest.main()
