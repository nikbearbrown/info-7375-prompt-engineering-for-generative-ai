"""The filter (FILTER.md section 1): deterministic, offline, boundary cases. Each WF test names the wrong version it catches."""
import copy
import json
import unittest

from helpers import HERE  # noqa: F401  (puts src/ on sys.path)
from jsa3 import filter as F

CFG = json.loads((HERE / "config/filter.json").read_text())
LONG = "We build agents. " * 40


def post(title="Software Engineer", location="Boston, MA", text="", board="greenhouse/x", pid="1"):
    return {"id": pid, "board": board, "title": title, "location": location, "url": "u", "text": text}


class TitleRules(unittest.TestCase):
    def test_role_word_in_title_keeps(self):
        r = F.evaluate(post("Machine Learning Engineer", text="Some text."), CFG)
        self.assertEqual((r["verdict"], r["role_match"]), ("keep", "Machine Learning"))

    def test_WF1_exclude_is_whole_word(self):
        # WF1: substring "intern" would reject this, and it carries a target term.
        r = F.evaluate(post("Applied AI Architect, International Policy", text="x"), CFG)
        self.assertIsNone(r["exclude_match"])
        self.assertEqual(r["verdict"], "keep")

    def test_exclude_word_rejects_even_with_role_word(self):
        r = F.evaluate(post("Senior ML Engineer", text="python sql llm"), CFG)
        self.assertEqual((r["verdict"], r["exclude_match"]), ("reject", "Senior"))

    def test_role_word_is_whole_word(self):
        self.assertIsNone(F.first_term("LLMOps Platform Engineer", CFG["role_words_title"]))


class Location(unittest.TestCase):
    def test_home_relocate_remote_us(self):
        L = CFG["location"]
        for loc in ("Boston, MA", "San Francisco, CA | London, UK", "Remote - USA", "Remote-Friendly, United States", "US-Remote"):
            self.assertEqual(F.location_check(loc, L)[0], "pass", loc)
        for loc in ("London, UK", "Remote - Ireland", "Dublin, Ireland"):
            self.assertEqual(F.location_check(loc, L)[0], "fail", loc)

    def test_same_place_spellings_are_optional(self):
        L = copy.deepcopy(CFG["location"])
        self.assertEqual(F.location_check("San Francisco, California", L)[0], "fail")   # v0.1: exact match only
        L["same_place"] = {"San Francisco, California": "San Francisco, CA"}
        self.assertEqual(F.location_check("San Francisco, California", L), ("pass", "San Francisco, CA"))

    def test_location_fail_rejects_before_text(self):
        r = F.evaluate(post("ML Engineer", location="Tokyo, Japan", text=""), CFG)
        self.assertEqual(r["verdict"], "reject")

    def test_missing_location_is_cannot_tell(self):
        r = F.evaluate(post("ML Engineer", location="", text="python"), CFG)
        self.assertEqual((r["verdict"], r["cannot_tell"]), ("cannot_tell", ["no location"]))


class TextRules(unittest.TestCase):
    def test_threshold_boundary(self):
        two = F.evaluate(post(text="Python and SQL."), CFG)
        three = F.evaluate(post(text="Python, SQL and LLMs."), CFG)
        self.assertEqual((two["score"], two["verdict"]), (2, "reject"))
        self.assertTrue(F.is_close_call(two, CFG))
        self.assertEqual((three["score"], three["verdict"]), (3, "keep"))

    def test_WF2_repeats_count_once(self):
        # WF2: a raw count would give 40 and keep this posting on one word.
        r = F.evaluate(post(text=LONG), CFG)
        self.assertEqual(r["score"], 1)
        self.assertEqual(r["topic_hits"][0]["count"], 40)
        self.assertEqual(r["verdict"], "reject")

    def test_WF4_no_text_is_cannot_tell_not_reject(self):
        r = F.evaluate(post(text=None), CFG)
        self.assertEqual(r["verdict"], "cannot_tell")
        self.assertIn("no posting text", r["cannot_tell"])
        self.assertIsNone(r["score"])

    def test_phrase_forms_and_word_edges(self):
        hits = {h["word"] for h in F.topic_hits("large  language models; machine learning; pythonic; agentic; evals", CFG["topic_words_text"], [])}
        self.assertEqual(hits, {"llm", "machine learning", "agents", "evaluation"})  # "pythonic" is not "python"

    def test_ignore_list_is_per_board(self):
        cfg = copy.deepcopy(CFG)
        cfg["ignore_words_by_board"] = {"greenhouse/x": ["python"]}
        self.assertEqual(F.evaluate(post(text="Python SQL LLM"), cfg)["score"], 2)
        self.assertEqual(F.evaluate(post(text="Python SQL LLM", board="ashby/y"), cfg)["score"], 3)

    def test_record_is_recomputable(self):
        r = F.evaluate(post(text="We want Python. Also SQL and agents."), CFG)
        for h in r["topic_hits"]:
            self.assertIn(h["form"].lower(), h["snippet"].lower())
        self.assertEqual(r, F.evaluate(post(text="We want Python. Also SQL and agents."), CFG))


if __name__ == "__main__":
    unittest.main()
