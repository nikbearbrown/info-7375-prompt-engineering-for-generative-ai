"""Job descriptions as plain text and as sections (FILTER.md, R2 sections revision).

The HTML is parsed once into lines. html_to_text joins all lines; split_sections
groups the same lines under their headings. So any text quoted from a section is
also an exact substring of html_to_text() of the whole description.

A heading is an h1-h6 element, or a p/div whose only text is bold (<strong>/<b>).
A section's kind is "counts" (heading on Swathi's counts list), "boilerplate"
(heading on her boilerplate list, or inside Greenhouse's content-intro /
content-conclusion blocks), or "unknown" (any other heading, "About the team",
or text before the first heading). Only "counts" sections count for R2 and R7.
Standard library only.
"""
from collections import namedtuple
from html.parser import HTMLParser
import re

COUNTS_HEADINGS = ("responsibilities", "what you'll do", "the impact you will have", "minimum requirements",
                   "qualifications", "what we look for", "who you are", "preferred qualifications")
BOILERPLATE_HEADINGS = ("about the company", "who we are", "benefits", "diversity", "compliance", "pay range",
                        "interview process", "mission")
BOILERPLATE_BLOCKS = ("content-intro", "content-conclusion")
NOT_COUNTED_ABOUT = ("about the team", "about the role", "about you")

Section = namedtuple("Section", "heading kind text")

_BLOCK_TAGS = {"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "table",
               "section", "article", "header", "footer", "blockquote", "hr", "dd", "dt", "pre"}
_HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
_BOLD_TAGS = {"strong", "b"}
_SKIP_TAGS = {"script", "style"}
_QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "\xa0": " "})


def clean_heading(text):
    """Display form of a heading: &nbsp; and curly quotes normalized, trailing ':' removed."""
    text = re.sub(r"\s+", " ", (text or "").translate(_QUOTES)).strip()
    return text.rstrip(":").strip()


def heading_kind(heading):
    h = clean_heading(heading).lower()
    if h in COUNTS_HEADINGS:
        return "counts"
    if h in NOT_COUNTED_ABOUT:
        return "unknown"
    if h.startswith("about "):  # "about the company": About Databricks, About Stripe, About Plaid ...
        return "boilerplate"
    if any(word in h for word in BOILERPLATE_HEADINGS[1:]):
        return "boilerplate"
    return "unknown"


class _Lines(HTMLParser):
    """Collects (text, is_heading, in_boilerplate_block) lines."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines = []
        self._buf = []
        self._bold_chars = 0
        self._chars = 0
        self._bold_depth = 0
        self._heading_depth = 0
        self._skip_depth = 0
        self._div_stack = []  # True for a boilerplate block div

    def _in_boilerplate(self):
        return any(self._div_stack)

    def _flush(self, block_tag=None):
        text = re.sub(r"[ \t\r\f\v]+", " ", "".join(self._buf).replace("\xa0", " ")).strip()
        if text:
            heading = self._heading_depth > 0 or (
                block_tag in ("p", "div") and self._chars > 0 and self._bold_chars == self._chars and len(text) <= 80)
            self.lines.append((text, heading, self._in_boilerplate()))
        self._buf, self._bold_chars, self._chars = [], 0, 0

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
            return
        if tag in _BLOCK_TAGS:
            self._flush()
        if tag == "div":
            classes = (dict(attrs).get("class") or "").split()
            self._div_stack.append(any(c in BOILERPLATE_BLOCKS for c in classes))
        if tag in _HEADING_TAGS:
            self._heading_depth += 1
        if tag in _BOLD_TAGS:
            self._bold_depth += 1

    def handle_endtag(self, tag):
        if tag in _SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if tag in _BLOCK_TAGS:
            self._flush(tag)
        if tag in _HEADING_TAGS:
            self._heading_depth = max(0, self._heading_depth - 1)
        if tag in _BOLD_TAGS:
            self._bold_depth = max(0, self._bold_depth - 1)
        if tag == "div" and self._div_stack:
            self._div_stack.pop()

    def handle_data(self, data):
        if self._skip_depth:
            return
        self._buf.append(data)
        n = len(data.strip())
        self._chars += n
        if self._bold_depth:
            self._bold_chars += n

    def close(self):
        super().close()
        self._flush()


def _lines(html):
    parser = _Lines()
    parser.feed(html or "")
    parser.close()
    return parser.lines


def html_to_text(html):
    """Plain text: entities decoded, &nbsp; as a space, one line per block, spaces collapsed."""
    return "\n".join(text for text, _, _ in _lines(html))


def split_sections(html):
    """List of Section(heading, kind, text), in document order."""
    sections = []
    current = None
    for text, is_heading, boiler in _lines(html):
        if is_heading:
            kind = "boilerplate" if boiler else heading_kind(text)
            current = [clean_heading(text), kind, boiler, []]
            sections.append(current)
            continue
        if current is None or current[2] != boiler:
            current = ["", "boilerplate" if boiler else "unknown", boiler, []]
            sections.append(current)
        current[3].append(text)
    return [Section(h, k, "\n".join(lines)) for h, k, _, lines in sections]
