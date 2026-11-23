"""HTML stripping and whole-word matching."""

import html
import re
from html.parser import HTMLParser

# A "word" character for whole-word matching. Hyphen, slash, dot and spaces are boundaries,
# so "US-Remote" contains the word "US" and "JavaScript" does not contain "Java".
_WORD_CHAR = "A-Za-z0-9"


class _TextCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skipping = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skipping += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skipping:
            self._skipping -= 1

    def handle_data(self, data):
        if not self._skipping:
            self.parts.append(data)


def normalize(text: str) -> str:
    """Collapse whitespace runs to one space and trim the ends."""
    return re.sub(r"\s+", " ", text).strip()


def strip_html(content: str | None) -> str:
    """Visible text of a Greenhouse posting.

    Greenhouse escapes its HTML ("&lt;p&gt;"), so unescape once, then drop the tags.
    Text from separate elements is joined with spaces so "<li>Python</li><li>Java</li>"
    does not become "PythonJava".
    """
    collector = _TextCollector()
    collector.feed(html.unescape(content or ""))
    collector.close()
    return normalize(" ".join(collector.parts))


def word_pattern(phrase: str, ignore_case: bool = True) -> re.Pattern:
    body = r"\s+".join(re.escape(word) for word in phrase.split())
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(rf"(?<![{_WORD_CHAR}]){body}(?![{_WORD_CHAR}])", flags)


def contains_word(text: str, phrase: str, ignore_case: bool = True) -> bool:
    return word_pattern(phrase, ignore_case).search(text) is not None
