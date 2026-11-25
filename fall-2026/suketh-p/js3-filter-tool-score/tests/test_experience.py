"""FILTER.md v0.2's one change, the experience-minimum rule, as tests written before
jobwatch/experience.py existed. Every posting and description here is CONSTRUCTED, except in
V01UnchangedTest, which reads the committed corpus and audit.

The rule is the student's choice (FILTER.md, "After the reject audit"): "Reject when the
description sets a minimum of 3+ years that is not marked preferred." How a description is read
(blocks, headings, what counts as a statement of years, what "marked preferred" means) is Claude
Code's reading; each test names the part it pins down. The 30 held-out postings were not read to
write these tests."""

import json
import unittest
from pathlib import Path

from jobwatch import corpus, experience, screen, variants

ROOT = Path(__file__).resolve().parent.parent
V02 = json.loads((ROOT / "variants" / "v0.2-experience-minimum.json").read_text(encoding="utf-8"))


def minimum(html):
    return experience.read(html)["minimum_years"]


def item(description, title="Software Engineer, Model Serving"):
    return screen.Item(board="greenhouse/anthropic", key="1", title=title, location="San Francisco, CA",
                       description=description, captured_at="2026-11-24T22:36:19Z")


def with_v02(description, title="Software Engineer, Model Serving"):
    return variants.rescore([item(description, title)], V02)[("greenhouse/anthropic", "1")]


REQUIREMENTS = "<h2 class=\"heading\"><strong>You may be a good fit if you</strong></h2>"


class ReadingTest(unittest.TestCase):
    def test_a_requirement_list_item_sets_the_minimum(self):
        self.assertEqual(minimum(REQUIREMENTS + "<ul><li><p>Have 5+ years of software engineering experience</p></li></ul>"), 5)

    def test_a_preferred_heading_marks_its_items_preferred(self):
        self.assertIsNone(minimum("<h2><strong>Preferred qualifications</strong></h2>"
                                  "<ul><li><p>5+ years of software engineering experience</p></li></ul>"))
        self.assertIsNone(minimum("<h2>Strong candidates may also have:</h2><ul><li>6+ years of Rust</li></ul>"))

    def test_five_years_preferred_in_the_item_itself(self):
        # The student's FILTER.md sentence: "A posting says 'Five years preferred.'"
        self.assertIsNone(minimum("<h3>Requirements</h3><ul><li>Five years preferred.</li></ul>"))

    def test_a_bold_paragraph_is_a_heading(self):
        self.assertIsNone(minimum("<p><strong>Nice to have:</strong></p><ul><li>6+ years building data pipelines</li></ul>"))
        self.assertEqual(minimum("<p><strong>What we look for:</strong></p><ul><li>6+ years building data pipelines</li></ul>"), 6)

    def test_a_bold_prefix_is_not_a_heading(self):
        html = ("<h2>Requirements</h2><p><strong>Bonus:</strong> experience with Rust</p>"
                "<ul><li>4+ years of Python</li></ul>")
        self.assertEqual(minimum(html), 4)

    def test_the_largest_stated_minimum_counts(self):
        self.assertEqual(minimum("<ul><li>10+ years in SAP technical roles</li><li>3+ years as a technical lead</li></ul>"), 10)

    def test_a_range_reads_its_lower_end(self):
        self.assertEqual(minimum("<li>2-4 years of experience</li>"), 2)
        self.assertEqual(minimum("<li>7–10 years in customer-facing technical roles</li>"), 7)

    def test_words_and_other_forms(self):
        self.assertEqual(minimum("<li>three or more years of experience</li>"), 3)
        self.assertEqual(minimum("<li>at least 4 years of experience</li>"), 4)
        self.assertEqual(minimum("<li>a minimum of 5 years in backend roles</li>"), 5)
        self.assertEqual(minimum("<li>Strong software engineering background (6+ years or equivalent)</li>"), 6)

    def test_the_word_experience_is_not_needed(self):
        self.assertEqual(minimum("<li>Have 8+ years in security governance, risk, and compliance</li>"), 8)

    def test_benefits_and_history_are_not_requirements(self):
        self.assertIsNone(minimum("<li>Paid month off after 4 years &amp; every 2 years thereafter</li>"))
        self.assertIsNone(minimum("<p>In your last three years of work, you have built applications with LLMs.</p>"))
        self.assertIsNone(minimum("<p>Founded 12 years ago, we have grown over the past 10 years.</p>"))

    def test_a_four_year_degree_is_not_experience(self):
        self.assertIsNone(minimum("<li>4-year degree in Computer Science</li>"))
        self.assertIsNone(minimum("<li>A 4 year degree or equivalent</li>"))

    def test_escaped_html_is_decoded_first(self):
        # Greenhouse sends content as escaped HTML.
        self.assertEqual(minimum("&lt;ul&gt;&lt;li&gt;5+ years of Go&lt;/li&gt;&lt;/ul&gt;"), 5)

    def test_a_blank_description_sets_no_minimum(self):
        self.assertIsNone(minimum(""))

    def test_statements_are_recorded_with_their_heading(self):
        found = experience.read("<h2><strong>Preferred qualifications</strong></h2><ul><li><p>5+ years of software "
                                "engineering experience</p></li></ul>")
        self.assertEqual(found, {"minimum_years": None, "statements": [
            {"years": 5, "preferred": True, "text": "5+ years of software engineering experience",
             "heading": "Preferred qualifications"}]})


class RuleTest(unittest.TestCase):
    def test_the_rule_is_off_in_v0_1(self):
        self.assertIsNone(screen.EXPERIENCE_MINIMUM_YEARS)
        record = screen.score(item(REQUIREMENTS + "<ul><li>6+ years of experience</li></ul>"))
        self.assertEqual((record["fate"], record["score"]), ("kept", 3))
        self.assertNotIn("experience", record)

    def test_three_years_is_enough_to_reject(self):
        record = with_v02(REQUIREMENTS + "<ul><li>3+ years of experience</li></ul>")
        self.assertEqual((record["fate"], record["reasons"], record["filter_version"]), ("rejected", ["experience"], "v0.2"))

    def test_two_years_does_not_reject(self):
        self.assertEqual(with_v02(REQUIREMENTS + "<ul><li>2+ years of experience</li></ul>")["fate"], "kept")

    def test_preferred_years_do_not_reject(self):
        record = with_v02("<h2>Preferred qualifications</h2><ul><li>8+ years of experience</li></ul>")
        self.assertEqual((record["fate"], record["experience"]["minimum_years"]), ("kept", None))

    def test_the_rule_reads_only_the_description(self):
        self.assertEqual(with_v02("<p>Build model serving systems.</p>", title="Software Engineer (5+ years)")["fate"], "kept")

    def test_the_record_shows_what_the_rule_read(self):
        record = with_v02(REQUIREMENTS + "<ul><li>Have 5+ years of software engineering experience</li></ul>")
        self.assertEqual(record["experience"], {"threshold": 3, "minimum_years": 5, "statements": [
            {"years": 5, "preferred": False, "text": "Have 5+ years of software engineering experience",
             "heading": "You may be a good fit if you"}]})

    def test_the_v0_2_variant_changes_one_object(self):
        self.assertEqual(set(V02["set"]), {"jobwatch.screen.EXPERIENCE_MINIMUM_YEARS", "jobwatch.screen.FILTER_VERSION"})
        self.assertEqual((V02["set"]["jobwatch.screen.EXPERIENCE_MINIMUM_YEARS"], V02["set"]["jobwatch.screen.FILTER_VERSION"]),
                         (3, "v0.2"))


class V01UnchangedTest(unittest.TestCase):
    """With the rule off, today's code gives every committed v0.1 record unchanged."""

    def test_every_committed_v0_1_record_is_reproduced(self):
        items, _ = corpus.load(ROOT / "runs" / "2026-11-24-js3-corpus")
        committed = {}
        with open(ROOT / "audit" / "v0.1" / "audit.jsonl", encoding="utf-8") as fh:
            for line in fh:
                record = json.loads(line)
                record.pop("rank")
                committed[(record["board"], record["key"])] = record
        now = {(i.board, i.key): json.loads(json.dumps(screen.score(i))) for i in items}
        self.assertEqual(len(now), 1551)
        self.assertEqual(now, committed)


if __name__ == "__main__":
    unittest.main()
