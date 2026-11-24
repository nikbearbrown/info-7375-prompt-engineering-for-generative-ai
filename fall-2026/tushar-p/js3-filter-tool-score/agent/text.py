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


# HTML elements that end one block of text and start the next (FILTER.md v0.2 "Sentence").
_BLOCK_TAGS = frozenset({"p", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "div", "br", "tr",
                         "td", "th", "table", "section", "blockquote", "pre", "dl", "dt", "dd", "hr"})
_BREAK = "\x00"


class _BlockCollector(_TextCollector):
    """Like _TextCollector, but marks block boundaries so the text can be split into blocks."""

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        if tag in _BLOCK_TAGS:
            self.parts.append(_BREAK)

    def handle_endtag(self, tag):
        super().handle_endtag(tag)
        if tag in _BLOCK_TAGS:
            self.parts.append(_BREAK)

    def handle_startendtag(self, tag, attrs):
        if tag in _BLOCK_TAGS:
            self.parts.append(_BREAK)


def html_blocks(content: str | None) -> list[str]:
    """The visible text of a Greenhouse posting, one string per HTML block, empty blocks dropped.

    Joining the blocks with spaces gives exactly strip_html(content).
    """
    collector = _BlockCollector()
    collector.feed(html.unescape(content or ""))
    collector.close()
    joined = " ".join(collector.parts)
    return [b for b in (normalize(chunk) for chunk in joined.split(_BREAK)) if b]


def plain_blocks(text: str | None) -> list[str]:
    """One string per non-blank line of a plain-text posting (Ashby descriptionPlain)."""
    return [b for b in (normalize(line) for line in (text or "").splitlines()) if b]


def word_pattern(phrase: str, ignore_case: bool = True) -> re.Pattern:
    body = r"\s+".join(re.escape(word) for word in phrase.split())
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(rf"(?<![{_WORD_CHAR}]){body}(?![{_WORD_CHAR}])", flags)


def contains_word(text: str, phrase: str, ignore_case: bool = True) -> bool:
    return word_pattern(phrase, ignore_case).search(text) is not None
