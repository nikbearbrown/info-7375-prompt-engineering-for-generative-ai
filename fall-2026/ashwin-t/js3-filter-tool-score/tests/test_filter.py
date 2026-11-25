"""FILTER.md v1.0 cases against the real filter, plus whole-corpus invariants."""
import json
import unittest

from jobfilter.corpus import load
from jobfilter.filter import KEEP, REJECT, REVIEW, Filter, load_config, rank
from tests.cases import CASES, posting

F = Filter(load_config("v1.0"))


class Cases(unittest.TestCase):
    def test_every_case(self):
        for name, p, decision, score, _ in CASES:
            with self.subTest(name):
                d = F.classify(p)
                self.assertEqual(d["decision"], decision, d.get("reasons"))
                if score is not None:
                    self.assertEqual(d["score"], score)

    def test_review_says_i_cannot_tell(self):
        d = F.classify(posting(location="Remote, Global"))
        self.assertTrue(d["reasons"][0].startswith("I cannot tell"))

    def test_gate_reject_score_is_marked_diagnostic(self):
        d = F.classify(posting(title="Senior Software Engineer"))
        self.assertTrue(d["score_is_diagnostic"])
        d = F.classify(posting(title="Account Executive"))
        self.assertEqual(d["components"]["title"], 0)

    def test_missing_url_is_disclosed_not_invented(self):
        d = F.classify(posting(absolute_url=None))
        self.assertIsNone(d["url"])
        self.assertIn("none invented", d["disclosure"])


class Locations(unittest.TestCase):
    def check(self, value, kind, score):
        r = F.classify_location_value(value)
        self.assertEqual((r["kind"], r["score"]), (kind, score), value)

    def test_formats_seen_in_the_corpus(self):
        self.check("Boston", "boston-area", 2)
        self.check("Flex - Cambridge, Massachusetts", "boston-area", 2)
        self.check("Remote - United States of America", "us-remote", 2)
        self.check("Washington, D.C.", "us-location", 1)
        self.check("Remote, San Francisco, CA, US", "us-location", 1)
        self.check("Remote, AMER", "unresolved", 0)
        self.check("Remote - Canada - Ontario", "outside-us", None)
        self.check("Bogotá, Colombia", "outside-us", None)

    def test_munich_de_is_read_as_delaware(self):
        """A recorded false friend of v1.0's literal city+state rule, not a desired behavior."""
        self.check("Munich, DE", "us-location", 1)

    def test_semicolon_lists_are_alternatives(self):
        d = F.classify(posting(location="Denver, CO; Boston, MA"))
        self.assertEqual(d["components"]["location"], 2)

    def test_repeated_bare_office_is_not_a_new_alternative(self):
        d = F.classify(posting(location="London, UK", offices=["London"], content="python redis docker"))
        self.assertEqual(d["decision"], REJECT)
        self.assertEqual(d["location"]["status"], "outside-us")


class Corpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = load()
        cls.decisions = F.run(cls.corpus["postings"])

    def test_counts_match_the_source_record(self):
        by_board = {}
        for p in self.corpus["postings"]:
            by_board[p["board"]] = by_board.get(p["board"], 0) + 1
        self.assertEqual(by_board, {"klaviyo": 151, "hubspotjobs": 126, "notion": 153, "supabase": 71, "palantir": 304})
        failed = [s for s in self.corpus["sources"] if s["status"] == "failed"]
        self.assertEqual([s["board"] for s in failed], ["klaviyo-nonexistent-js2"])

    def test_every_posting_gets_exactly_one_decision(self):
        self.assertEqual(len(self.decisions), 805)
        self.assertEqual(len({d["key"] for d in self.decisions}), 805)
        self.assertTrue(all(d["decision"] in {KEEP, REJECT, REVIEW} for d in self.decisions))

    def test_no_kept_posting_breaks_a_gate(self):
        for d in rank(self.decisions):
            self.assertTrue(d["gate"]["passed"])
            self.assertGreaterEqual(d["n_topic_groups"], 2)
            self.assertGreaterEqual(d["score"], 7)
            self.assertEqual(d["location"]["status"], "eligible")

    def test_ranking_order(self):
        r = rank(self.decisions)
        keys = [(-d["score"], -d["components"]["location"], d["key"]) for d in r]
        self.assertEqual(keys, sorted(keys))

    def test_config_numbers_are_the_documented_ones(self):
        w = load_config("v1.0")["weights"]
        self.assertEqual(w, {"title": 3, "topic": 1, "topic_cap": 4, "location_preferred": 2,
                             "location_us_other": 1, "location_unresolved": 0, "min_topic_groups": 2,
                             "threshold": 7})


if __name__ == "__main__":
    unittest.main()
