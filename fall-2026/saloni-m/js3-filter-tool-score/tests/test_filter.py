"""The filter and its wrong versions (FILTER.md §1, §2, §5). Offline; no network, no model."""
import json
import os
import re
import unittest

from js3.filter import DEFAULT_DOC, HERE, load_filter, rank, score, years_required, phd_required
from js3.text import has_phrase
from tests.wrong_versions import count_rank, substring_score

FLT = load_filter()
LONG = " ".join(["We build things."] * 40)  # > 300 chars of neutral text


def P(title, text=LONG, uid=None):
    return {"uid": uid or title, "title": title, "text": text}


class TestFilterDocument(unittest.TestCase):
    def test_doc_has_one_block_and_version(self):
        self.assertEqual(FLT["filter_version"], "1.0")
        self.assertEqual(FLT["threshold"], 3)

    def test_every_phrase_in_the_block_is_named_in_the_reasons_table(self):
        with open(DEFAULT_DOC, encoding="utf-8") as f:
            doc = f.read()
        table = doc.split("## 2.")[1].split("## 3.")[0]
        for p in FLT["role_title"]["phrases"]:
            self.assertIn(f"`{p}`", table, f"role phrase {p!r} has no reason line in FILTER.md §2")

    def test_sources_config_matches_filter_doc_section_4(self):
        with open(DEFAULT_DOC, encoding="utf-8") as f:
            sec4 = f.read().split("## 4.")[1].split("## 5.")[0]
        with open(os.path.join(HERE, "config", "sources.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        for b in cfg["boards"]:
            self.assertIn(f"`{b['board']}`", sec4)
        for h in cfg["allowed_hosts"]:
            self.assertIn(h, sec4)


class TestRules(unittest.TestCase):
    def test_role_title_keeps(self):
        r = score(P("Machine Learning Engineer, New Grad"), FLT)
        self.assertEqual((r["decision"], r["score"]), ("keep", 3))

    def test_seniority_veto_beats_any_score(self):
        r = score(P("Senior ML Engineer", "Python SQL Spark Airflow. " * 30), FLT)
        self.assertEqual(r["decision"], "reject")
        self.assertTrue(r["vetoed"])

    def test_topic_words_alone_never_keep(self):
        r = score(P("Software Engineer, Platform", "Python SQL Spark Airflow LLM evaluation. " * 20), FLT)
        self.assertEqual((r["score"], r["decision"]), (2, "reject"))

    def test_topic_cap_is_two(self):
        r = score(P("ML Engineer", "Python SQL Spark Airflow LLM evaluation. " * 20), FLT)
        self.assertEqual(r["score"], 5)

    def test_years_penalty(self):
        r = score(P("ML Engineer", LONG + " You have 5+ years of experience in production ML."), FLT)
        self.assertEqual((r["score"], r["decision"]), (0, "reject"))

    def test_three_to_five_years_is_not_penalised(self):
        self.assertEqual(years_required("3-5 years of industry experience")[0], 3)
        r = score(P("ML Engineer", LONG + " 3-5 years of industry experience."), FLT)
        self.assertEqual(r["decision"], "keep")

    def test_phd_required_vs_preferred(self):
        self.assertTrue(phd_required("A PhD in computer science is required.")[0])
        self.assertFalse(phd_required("A PhD is preferred but not required.")[0])
        self.assertFalse(phd_required("PhD or equivalent experience required.")[0])

    def test_short_text_is_flagged_and_text_rules_not_applied(self):
        r = score(P("Data Engineer", "Python. 10+ years of experience."), FLT)
        self.assertTrue(r["text_missing"])
        self.assertEqual(r["score"], 3)  # R4 not applied: a missing body is not a body


class TestWrongVersions(unittest.TestCase):
    """FILTER.md §5. Each wrong version must produce a different answer from the real filter."""

    def test_wv1_substring_match_is_caught(self):
        p = P("HTML Email Developer")
        self.assertFalse(has_phrase(p["title"], "ml"))
        self.assertEqual(score(p, FLT)["decision"], "reject")
        self.assertEqual(substring_score(p, FLT)["decision"], "keep")  # the wrong version keeps it

    def test_wv2_count_ranking_is_caught(self):
        senior = P("Senior Staff ML Engineer", "Python. " * 300, uid="senior")
        grad = P("ML Engineer, New Grad", LONG + " Python.", uid="grad")
        right = [r["uid"] for r in rank([score(senior, FLT), score(grad, FLT)])]
        wrong = [p["uid"] for p in count_rank([senior, grad], FLT)]
        self.assertEqual(right[0], "grad")
        self.assertEqual(wrong[0], "senior")


if __name__ == "__main__":
    unittest.main()
