"""Posting text as plain text: HTML tags stripped, entities decoded, whitespace collapsed.

Greenhouse sends its description HTML entity-escaped ("&lt;p&gt;"), so it is unescaped once
before parsing. Block-level tags become line breaks so sentences don't run together.
"""
import html
import re
from html.parser import HTMLParser

BLOCK = {"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "table", "section"}


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def html_to_text(markup, escaped=False):
    if not markup:
        return ""
    if escaped:
        markup = html.unescape(markup)
    parser = _Text()
    parser.feed(markup)
    parser.close()
    return clean("".join(parser.parts))


def clean(text):
    """Collapse runs of spaces within lines and blank lines between them."""
    lines = [" ".join(line.split()) for line in (text or "").replace("\xa0", " ").splitlines()]
    return re.sub(r"\n{2,}", "\n", "\n".join(line for line in lines if line)).strip()
