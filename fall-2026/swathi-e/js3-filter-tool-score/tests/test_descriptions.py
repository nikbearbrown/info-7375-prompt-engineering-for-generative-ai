"""Tests for descriptions.py (sections and plain text), written before the code.

S1-S4 and G7 come from the test design Claude Code proposed on 2026-11-17 and
Swathi approved, checking FILTER.md's "Revision (2026-11-17, before any JS3
filter code): R2 sections". Descriptions built in this file are SIMULATED (no
board returned them); S1 also reads the REAL saved Nov 5 Plaid response,
read-only. Written by Claude Code. Every test runs inside no_network().

descriptions.py is imported inside each test, so each test reports its own
missing piece instead of the whole file failing on one import.
"""
from contextlib import contextmanager
import importlib
import json
from pathlib import Path
import re
import socket
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

REAL_NOV5_PLAID = HERE / "runs" / "2026-11-05T23-11-48-228373-0500" / "005-plaid-request.json"
FRAUD_ANALYST = "1bcfe93d-97bd-4618-b81e-dc308ef69d30"


@contextmanager
def no_network():
    def refuse(*args, **kwargs):
        raise AssertionError("a network connection was attempted")
    with patch.object(socket, "create_connection", refuse), patch.object(socket.socket, "connect", refuse):
        yield


def descriptions():
    return importlib.import_module("descriptions")


def kinds(sections):
    return {s.heading.lower(): s.kind for s in sections}


class Sections(unittest.TestCase):
    def test_S1_headings_found_and_cleaned(self):
        """S1, FILTER.md Revision (R2 sections): headings come from h1-h6 tags and from paragraphs
        that are only bold text; a trailing ":", &nbsp; and curly quotes are cleaned. SIMULATED
        Stripe-style and Databricks-style HTML, plus the REAL saved Plaid posting 1bcfe93d."""
        d = descriptions()
        html = ("<h2><strong>Responsibilities:</strong></h2><p>Write SQL.</p>"
                "<p><strong>What you’ll do&nbsp;</strong></p><ul><li>Ship models.</li></ul>"
                "<h3>Minimum Requirements</h3><p>Python.</p>")
        with no_network():
            sections = d.split_sections(html)
        found = kinds(sections)
        self.assertEqual(found.get("responsibilities"), "counts")
        self.assertEqual(found.get("what you'll do"), "counts")
        self.assertEqual(found.get("minimum requirements"), "counts")
        text = {s.heading.lower(): s.text for s in sections}
        self.assertIn("Write SQL.", text["responsibilities"])
        self.assertIn("Ship models.", text["what you'll do"])

        job = next(j for j in json.loads(REAL_NOV5_PLAID.read_bytes())["jobs"] if j["id"] == FRAUD_ANALYST)
        with no_network():
            real = kinds(d.split_sections(job["descriptionHtml"]))
        self.assertEqual(real.get("responsibilities"), "counts")
        self.assertEqual(real.get("qualifications"), "counts")

    def test_S2_greenhouse_intro_and_conclusion_are_boilerplate(self):
        """S2, FILTER.md Revision (R2 sections): Greenhouse's content-intro and content-conclusion
        blocks are boilerplate, whatever their headings say. SIMULATED Databricks-style HTML."""
        d = descriptions()
        html = ('<div class="content-intro"><p><strong>Responsibilities</strong></p><p>Intro text.</p></div>'
                "<p><strong>The impact you will have:</strong></p><ul><li>Real work.</li></ul>"
                '<div class="content-conclusion"><p><strong>About Databricks</strong></p>'
                "<p>Company text.</p><p><strong>Benefits</strong></p><p>Benefit text.</p></div>")
        with no_network():
            sections = d.split_sections(html)
        by_text = {}
        for s in sections:
            for marker in ("Intro text.", "Real work.", "Company text.", "Benefit text."):
                if marker in s.text:
                    by_text[marker] = s.kind
        self.assertEqual(by_text, {"Intro text.": "boilerplate", "Real work.": "counts",
                                   "Company text.": "boilerplate", "Benefit text.": "boilerplate"})

    def test_S3_unknown_heading_or_no_heading_does_not_count(self):
        """S3, FILTER.md Revision (R2 sections): text under an unknown heading, under "About the team",
        or with no heading at all does not count. SIMULATED HTML."""
        d = descriptions()
        html = ("<p>Text before any heading.</p>"
                "<h2>About the team</h2><p>Team text.</p>"
                "<h2>Our Culture</h2><p>Culture text.</p>"
                "<h2>About Stripe</h2><p>Company text.</p>"
                "<h2>Our Commitment to Diversity and Inclusion</h2><p>Diversity text.</p>"
                "<h2>Pay Range Transparency</h2><p>Pay text.</p>"
                "<h2>Compliance</h2><p>Compliance text.</p>")
        with no_network():
            sections = d.split_sections(html)
        for s in sections:
            with self.subTest(heading=s.heading):
                self.assertNotEqual(s.kind, "counts")
        found = kinds(sections)
        for heading in ("about stripe", "our commitment to diversity and inclusion", "pay range transparency",
                        "compliance"):
            self.assertEqual(found.get(heading), "boilerplate", heading)

    def test_S4_heading_lists_match_filter_md(self):
        """S4, FILTER.md Revision (R2 sections): the "counts" and boilerplate heading lists in
        descriptions.py are exactly the lists in that revision."""
        d = descriptions()
        filter_md = (HERE / "FILTER.md").read_text(encoding="utf-8")
        section = filter_md.split("## Revision (2026-11-17, before any JS3 filter code): R2 sections", 1)[1]
        section = " ".join(section.split("\n## ", 1)[0].split())
        counts = re.search(r'"counts" list: (.*?)\. - ', section).group(1)
        boiler = re.search(r"never count for R2: (.*?)\. Greenhouse", section).group(1)
        as_set = lambda text: {item.strip() for item in text.split(",")}
        self.assertEqual(set(d.COUNTS_HEADINGS), as_set(counts))
        self.assertEqual(set(d.BOILERPLATE_HEADINGS), as_set(boiler))


class PlainText(unittest.TestCase):
    def test_G7_html_to_text(self):
        """G7, FILTER.md Expected sources (the description is read as text). SIMULATED HTML: entities
        are decoded, &nbsp; becomes a space, block tags and <br> start new lines, list items are
        separate lines, and runs of spaces collapse."""
        d = descriptions()
        html = "<p>SQL &amp; Python&nbsp;skills</p><ul><li>One</li><li>Two   words</li></ul><p>A<br>B</p>"
        with no_network():
            text = d.html_to_text(html)
        lines = [line for line in text.split("\n") if line.strip()]
        self.assertEqual(lines, ["SQL & Python skills", "One", "Two words", "A", "B"])


if __name__ == "__main__":
    unittest.main()
