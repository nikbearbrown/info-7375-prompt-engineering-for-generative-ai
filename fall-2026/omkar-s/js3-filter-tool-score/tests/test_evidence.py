"""Evidence labels and abstention (FILTER.md section 2) on CONSTRUCTED postings. Catches WV3."""
import unittest

from js3 import scorer
from js3 import textutil as tu
from tests.helpers import cfg, persona, posting


def labelled(html, title="Software Engineer", location="Boston, MA", version=None):
    p = posting(title=title, location=location, body=tu.clean(html), html=html)
    c = cfg(version)
    r = scorer.evaluate(p, persona(), c)
    cl = scorer.claims(p, r, c)
    return r, {x["claim"]: x for x in cl}, scorer.shortlist_status(cl, c)


class SkillClaims(unittest.TestCase):
    def test_skill_under_requirements_is_supported(self):
        _, cl, _ = labelled("<h3>Requirements</h3><ul><li>2+ years of experience with Python and AWS</li></ul>")
        self.assertEqual(cl["CL-skill:Python"]["label"], "supported")
        self.assertIn("Python", cl["CL-skill:Python"]["quote"])

    def test_skill_only_in_company_blurb_is_insufficient(self):  # WV3: relevance is not entailment
        r, cl, st = labelled("<h3>About us</h3><p>Our platform runs on Python, Kafka and AWS.</p>"
                             "<h3>Requirements</h3><ul><li>2+ years of experience shipping web products</li></ul>")
        self.assertIn("Python", r["skills_found"])          # relevant: the word is on the page, K1 counts it
        self.assertEqual(cl["CL-skill:Python"]["label"], "insufficient")  # not entailed: nobody asked for it
        self.assertEqual(st[0], "kept_cannot_tell")
        self.assertTrue(any(x.startswith("AB2") for x in st[1]))

    def test_nice_to_haves_ends_requirements_from_v1_3(self):
        html = ("<h3>Requirements</h3><ul><li>2+ years of experience</li><li>Python</li></ul>"
                "<h3>Special Sauce (Nice to Haves)</h3><ul><li>Kafka and Redis</li></ul>")
        self.assertEqual(labelled(html, version="1.2")[1]["CL-skill:Kafka"]["label"], "supported")
        self.assertEqual(labelled(html)[1]["CL-skill:Kafka"]["label"], "insufficient")

    def test_tech_stack_heading_is_not_a_requirement_from_v1_4(self):
        html = ("<h3>Who You Are</h3><ul><li>2+ years of experience</li><li>Python, AWS</li></ul>"
                "<h3>Technologies We Use (not exhaustive)</h3><ul><li>Kafka, Redis</li></ul>")
        self.assertEqual(labelled(html, version="1.3")[1]["CL-skill:Redis"]["label"], "supported")
        self.assertEqual(labelled(html)[1]["CL-skill:Redis"]["label"], "insufficient")
        self.assertEqual(labelled(html)[1]["CL-skill:Python"]["label"], "supported")

    def test_skill_as_subheading_inside_requirements_is_supported(self):  # the 06:24 bug fix
        html = ("<h3>What you'll need</h3><p>2+ years of experience</p><p><strong>Python</strong></p>"
                "<p>You write clean services.</p><p>AWS for hosting.</p>")
        self.assertEqual(labelled(html)[1]["CL-skill:Python"]["label"], "supported")

    def test_inline_bold_is_not_a_heading(self):
        lines = tu.lines_with_headings("<p>You know <strong>Python</strong> well.</p>")
        self.assertEqual(lines, [(False, "You know Python well.")])

    def test_negated_skill_is_contradicted(self):
        _, cl, _ = labelled("<h3>Requirements</h3><ul><li>2+ years of experience; no Java experience needed</li><li>Python, AWS</li></ul>")
        self.assertEqual(cl["CL-skill:Java"]["label"], "contradicted")


class LevelAndRole(unittest.TestCase):
    def test_level_insufficient_says_cannot_tell(self):  # AB3
        _, cl, st = labelled("<h3>Requirements</h3><ul><li>Python</li><li>AWS</li></ul>")
        self.assertEqual(cl["CL-level"]["label"], "insufficient")
        self.assertIn("AB3: level: I cannot tell from the posting", st[1])

    def test_level_supported_by_entry_phrase(self):
        _, cl, _ = labelled("<h3>Requirements</h3><ul><li>New grad welcome</li><li>Python, AWS</li></ul>")
        self.assertEqual(cl["CL-level"]["label"], "supported")

    def test_generic_engineer_title_is_insufficient_role(self):
        _, cl, st = labelled("<h3>Requirements</h3><ul><li>2+ years of experience</li><li>Python, AWS, SQL, Kafka</li></ul>",
                             title="Product Engineer")
        self.assertEqual(cl["CL-role"]["label"], "insufficient")
        self.assertEqual(st[0], "kept_cannot_tell")

    def test_worth_reading_needs_everything(self):
        _, cl, st = labelled("<h3>Requirements</h3><ul><li>2+ years of experience</li><li>Python and AWS</li></ul>")
        self.assertEqual(st, ("worth_reading", []))


if __name__ == "__main__":
    unittest.main()
