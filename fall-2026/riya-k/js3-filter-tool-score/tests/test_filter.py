"""Filter v1 tests: FILTER.md wrong versions W1-W3, gates, abstention, and that the JSON matches the document.

W4 (threshold tuned on held-out labels) is in tests/test_heldout.py. Offline, standard library only.
"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from js3 import evidence, filter as F  # noqa: E402

FLT = F.load_filter()
LONG = " Lorem ipsum filler text about the team and the company." * 8  # > 300 chars so A1 does not fire


def post(title, content="", location="New York, NY", employment=None, pid="t1"):
    return {"id": pid, "board": "test:t", "title": title, "content": content + LONG,
            "location": {"name": location}, "employment": employment}


def decide(p, flt=FLT):
    return F.apply(p, flt, evidence.claims)


class W1SubstringMatching(unittest.TestCase):
    def test_ai_inside_words_does_not_count(self):
        p = post("Maintenance Coordinator", "Maintain the email system. Explain the domain. We use NoSQL and MySQLish.")
        parts = F.score_parts(p, FLT)
        self.assertEqual(parts["role"]["hits"], [])
        self.assertNotIn("SQL", parts["skill"]["hits"])
        self.assertEqual(decide(p)["decision"], "rejected")

    def test_whole_word_still_matches(self):
        parts = F.score_parts(post("AI Engineer", "Python and SQL, MLflow."), FLT)
        self.assertEqual(parts["role"]["counted"], ["AI"])
        self.assertEqual(parts["skill"]["counted"], ["Python", "SQL", "MLflow"])


class W2ScoreWithoutGates(unittest.TestCase):
    RICH = "Python SQL AWS MLflow LangGraph. RAG, evaluation, agents."

    def test_london_score_11_rejected(self):
        r = decide(post("Applied AI Engineer", self.RICH, location="London, UK"))
        self.assertEqual(r["score"], 11)
        self.assertEqual(r["decision"], "rejected")
        self.assertTrue(r["gates_failed"][0].startswith("G1"))

    def test_staff_score_11_rejected(self):
        r = decide(post("Staff Machine Learning Engineer", self.RICH))
        self.assertEqual(r["score"], 11)
        self.assertEqual(r["decision"], "rejected")

    def test_same_posting_kept_when_gates_pass(self):
        self.assertEqual(decide(post("Machine Learning Engineer", self.RICH))["decision"], "kept")


class W3TitleBlind(unittest.TestCase):
    def test_sales_engineer_with_all_skills_rejected(self):
        r = decide(post("Sales Engineer", "Python, SQL, AWS, MLflow. agents and evaluation."))
        self.assertGreaterEqual(r["score"], FLT["threshold"])  # the score alone would keep it ...
        self.assertEqual(r["decision"], "rejected")              # ... gate G5 does not
        self.assertIn("G5 no ROLE word in title", r["gates_failed"])


class Gates(unittest.TestCase):
    def test_intern_and_part_time(self):
        self.assertEqual(decide(post("Data Science Intern", "Python SQL AWS"))["decision"], "rejected")
        self.assertEqual(decide(post("Data Engineer (Contract)", "Python SQL AWS"))["decision"], "rejected")
        self.assertEqual(decide(post("Data Engineer", "Python SQL AWS", employment="PartTime"))["decision"], "rejected")

    def test_threshold_boundary(self):
        five = decide(post("Data Engineer", "Python only."))        # 4 + 1 + 1 = 6
        self.assertEqual(five["score"], 6)
        four = decide(post("Data Platform Lead", "Python only."))   # 4 + 0 + 1 = 5
        self.assertEqual((four["score"], four["decision"]), (5, "rejected"))


class Abstention(unittest.TestCase):
    def test_a1_short_text(self):
        p = {"id": "s", "board": "t", "title": "AI Engineer", "content": "Python SQL", "location": {"name": "NY"}}
        self.assertTrue(decide(p)["abstain"].startswith("A1"))

    def test_a2_bare_remote(self):
        self.assertTrue(decide(post("AI Engineer", "Python SQL", location="Remote"))["abstain"].startswith("A2"))

    def test_a3_at_threshold_with_insufficient_claim(self):
        r = decide(post("Data Engineer", "Python only."))  # score 6, no years stated -> C4 insufficient
        self.assertEqual(r["decision"], "cannot_tell")
        self.assertTrue(r["abstain"].startswith("A3"))

    def test_a3_not_above_threshold(self):
        r = decide(post("Data Engineer", "Python and SQL."))  # score 7
        self.assertEqual(r["decision"], "kept")


class Evidence(unittest.TestCase):
    def label(self, content, claim="C4"):
        cs = evidence.claims(post("AI Engineer", content), FLT)
        return next(c for c in cs if c["claim"].startswith(claim))["label"]

    def test_years(self):
        self.assertEqual(self.label("5+ years of experience in Python."), "contradicted")
        self.assertEqual(self.label("2+ years of relevant experience."), "supported")
        self.assertEqual(self.label("3-5 years of experience."), "supported")   # smallest stated number is 3
        self.assertEqual(self.label("Founded 10 years ago."), "insufficient")   # not about experience
        self.assertEqual(self.label("Python."), "insufficient")

    def test_absent_skill_is_not_a_contradiction(self):
        cs = evidence.claims(post("AI Engineer", "Python."), FLT)
        self.assertFalse(any(c["label"] == "contradicted" and c["claim"].startswith("C2") for c in cs))
        self.assertFalse(any("SQL" in c["claim"] for c in cs))

    def test_location_labels(self):
        self.assertEqual(self.label("x", "C3"), "supported")
        cs = evidence.claims(post("AI Engineer", "x", location="Tokyo, Japan"), FLT)
        self.assertEqual(next(c for c in cs if c["claim"].startswith("C3"))["label"], "contradicted")


class FilterFileMatchesDocument(unittest.TestCase):
    """The JSON is a machine copy of FILTER.md: the numbers in the §1b table must be the same."""

    def test_points_and_threshold(self):
        doc = (ROOT / "FILTER.md").read_text()
        self.assertIn(f"KEEP if score ≥ {FLT['threshold']}", doc)
        for name, label in [("role", "ROLE"), ("job_type", "JOB-TYPE"), ("skill", "SKILL"), ("topic", "TOPIC")]:
            row = next(l for l in doc.splitlines() if l.startswith(f"| {label} |"))
            spec = FLT["score"][name]
            want = f"+{spec['points']}, once" if spec["max_hits"] == 1 else f"+{spec['points']} each, max {spec['max_hits']}"
            self.assertIn(want, row, f"{label} row")
            for w in spec["words"]:
                self.assertTrue(re.search(re.escape(w), row), f"{w} missing from FILTER.md {label} row")


if __name__ == "__main__":
    unittest.main()


class V11(unittest.TestCase):
    """FILTER.md v1.1 rules (G6, years pattern, US cities, cut 'agents'); v1 behaviour must stay unchanged."""
    F11 = F.load_filter(ROOT / "filters" / "filter-v1.1.json")

    def test_g6_rejects_more_than_3_years(self):
        p = post("Data Engineer", "Python and SQL. 5+ years of experience as a data engineer.")
        self.assertEqual(decide(p)["decision"], "kept")            # v1 only labels C4 ...
        r = decide(p, self.F11)
        self.assertEqual(r["decision"], "rejected")                  # ... v1.1 rejects
        self.assertTrue(any(g.startswith("G6") for g in r["gates_failed"]))

    def test_g6_keeps_3_years(self):
        self.assertEqual(decide(post("Data Engineer", "Python and SQL. 3+ years of experience."), self.F11)["decision"], "kept")

    def test_years_pattern_or_more_and_words(self):
        self.assertEqual(evidence.stated_years("8 or more years leading experience programs", "v1"), [])
        self.assertEqual(evidence.stated_years("8 or more years of experience", "v1.1")[0][0], 8)
        self.assertEqual(evidence.stated_years("less than two years of engineering experience", "v1.1")[0][0], 2)

    def test_us_city_ends_bare_remote_abstention(self):
        p = post("AI Engineer", "Python and SQL.", location="San Francisco; Remote")
        self.assertTrue(decide(p)["abstain"].startswith("A2"))       # v1: city unknown -> cannot tell
        self.assertEqual(decide(p, self.F11)["decision"], "kept")    # v1.1: San Francisco is US

    def test_agents_cut(self):
        p = post("Data Engineer", "build data and AI apps, analytics and agents. Python.")
        self.assertIn("agents", F.score_parts(p, FLT)["topic"]["counted"])
        self.assertNotIn("agents", F.score_parts(p, self.F11)["topic"]["counted"])
