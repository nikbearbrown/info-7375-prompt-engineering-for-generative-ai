"""The logic of the three diagnostics of 2026-11-24 (tools/baselines.py, tools/boilerplate_check.py,
tools/card_rebuild_check.py), on CONSTRUCTED inputs. tests/test_results_rebuild.py checks their committed reports.
"""

import importlib.util
import unittest
from fractions import Fraction
from itertools import combinations

from job_agent import filter as flt

from .loop_helpers import REPO


def tool(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


baselines = tool("baselines")
boilerplate = tool("boilerplate_check")
cards = tool("card_rebuild_check")
RULES = flt.load_rules(version="1.0")
SHARED = "We build APIs for every team."


def posting(n: int, description: str) -> dict:
    return {"id": f"p{n}", "title": f"Software Engineer, Team {n}", "employmentType": "FullTime",
            "location": "San Francisco", "jobUrl": f"https://example.test/p{n}", "publishedAt": "2026-11-01T00:00:00Z",
            "address": {"postalAddress": {"addressCountry": "United States", "addressRegion": "California",
                                          "addressLocality": "San Francisco"}}, "descriptionPlain": description}


class BaselinesTest(unittest.TestCase):
    def test_the_chance_that_a_draw_holds_none_is_exact(self):
        moved = {0, 1}
        draws = list(combinations(range(6), 3))
        none = sum(1 for d in draws if not moved & set(d))
        self.assertEqual(baselines.none_drawn(6, 2, 3), Fraction(none, len(draws)))
        self.assertEqual(baselines.none_drawn(69, 0, 15), 1)
        self.assertEqual(baselines.none_drawn(5, 4, 3), 0)  # fewer unmoved postings than the draw

    def test_the_constant_answers_and_the_filter_count_only_judged_cards(self):
        rows = [{"fate": "kept", "his": "Keep"}, {"fate": "kept", "his": "?"}, {"fate": "rejected", "his": "Keep"},
                {"fate": "rejected", "his": "Reject"}]
        self.assertEqual(baselines.tally(rows, "his"),
                         {"cards": 4, "judged": 3, "reject_all": 1, "keep_all": 2, "filter": 2})

    def test_only_the_cutoff_changes_skip_the_judging(self):
        self.assertTrue(baselines.only_the_cutoff_differs(RULES, baselines.hx.variant(RULES, "X5")))
        self.assertTrue(baselines.only_the_cutoff_differs(RULES, baselines.hx.variant(RULES, "X6")))
        for name in ("X1", "X2", "X3", "X4"):
            self.assertFalse(baselines.only_the_cutoff_differs(RULES, baselines.hx.variant(RULES, name)), name)


class BoilerplateTest(unittest.TestCase):
    def run_of(self, postings: dict) -> dict:
        profile = flt.load_profile()
        records = [flt.judge(p, profile, RULES, k[0]) for k, p in postings.items()]
        sentences, share, titles, size = boilerplate.index(postings, RULES)
        return {"rules": RULES, "kept": [r for r in records if r["fate"] == "kept"], "sentences": sentences,
                "share": share, "titles": titles, "board_size": size}

    def test_a_point_depends_on_boilerplate_only_when_no_other_sentence_earns_it(self):
        postings = {("b", f"p{n}"): posting(n, SHARED + "\nYou will join the team.") for n in range(2, 5)}
        postings[("b", "p0")] = posting(0, SHARED + "\nYou will design SQL schemas.")
        postings[("b", "p1")] = posting(1, SHARED + "\nYou will build APIs for payments.")
        result = boilerplate.without_boilerplate(self.run_of(postings), lambda size: 5)
        p0, p1 = result[("b", "p0")], result[("b", "p1")]
        self.assertEqual((p0["recorded"], p0["depends"]), (["APIs"], ["APIs"]))  # only the shared line earns APIs
        self.assertEqual((p0["record"]["score"], p0["changed"]["score"]), (60, 55))  # Databases stays
        self.assertEqual((p1["recorded"], p1["depends"]), (["APIs"], []))  # its own line earns APIs too
        self.assertEqual(p1["changed"]["score"], p1["record"]["score"])
        below = boilerplate.without_boilerplate(self.run_of(postings), lambda size: 6)  # 5 sharers are not 6
        self.assertEqual(sum(len(v["depends"]) for v in below.values()), 0)

    def test_sentences_match_after_whitespace_bullets_and_case(self):
        self.assertEqual(boilerplate.normalized("-  We  BUILD apis "), boilerplate.normalized("we build APIs"))
        self.assertEqual(boilerplate.quote("x" * 130), "x" * 120 + " ...")


class CardRebuildTest(unittest.TestCase):
    OLD = ("# Cards\n\n## Card 01\n\n**Software Engineer**\n\n- Board: b\n\n**Sentences about status, sponsorship or "
           "clearance:**\n\n- You must be authorized to work in the U.S.\n- We are unable to sponsor visas.\n\n---\n\n"
           "## Card 02\n\n**Software Engineer**\n\n- Board: b\n\n**Sentences about status, sponsorship or "
           "clearance:**\n\n- none\n\n---\n")

    def test_a_joined_line_and_a_new_line_a_rule_reads(self):
        new = self.OLD.replace("the U.S.\n- We are", "the U.S. We are").replace("- none", "- U.S. Person Required")
        changed = cards.compare(self.OLD, new, RULES)["changed"]
        self.assertEqual(sorted(changed), [1, 2])
        joined, added = changed[1][0], changed[2][0]
        self.assertEqual((len(joined["lost"]), len(joined["gained"]), joined["words"]), (2, 1, []))
        self.assertEqual([(r["rule"], r["phrase"], r["on_old_card"]) for r in joined["read"]],
                         [("R5", "unable to sponsor", True)])
        self.assertTrue(cards.assessment(changed[1]).startswith("No:"))
        self.assertEqual(added["words"], ["U.S.", "Person", "Required"])
        self.assertEqual([(r["rule"], r["on_old_card"]) for r in added["read"]], [("R5", False)])
        self.assertTrue(cards.assessment(changed[2]).startswith("Yes:"))

    def test_what_reads_a_line(self):
        block = "Sentences with a number of years"
        self.assertEqual(cards.readers("- 5+ years of experience in Go", block, RULES), [("R7", "5+ years")])
        self.assertEqual(cards.readers("- You can start in January 2027", block, RULES), [("R6", "January 2027")])
        self.assertEqual(cards.readers("- We build APIs.", block, RULES), [])
        self.assertEqual([r for r, _ in cards.readers("- To comply with U.S. export control laws", block, RULES)],
                         ["R5's caution, never a reason to reject"])
        self.assertEqual(cards.readers("- Locations: New York, NY", "facts", RULES)[0][0], "R2")


if __name__ == "__main__":
    unittest.main()
