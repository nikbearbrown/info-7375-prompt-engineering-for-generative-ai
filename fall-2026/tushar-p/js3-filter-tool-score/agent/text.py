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
_HEADING_TAGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})
_LIST_MARKER = re.compile(r"^[-•*–]\s")

# Block kinds (FILTER.md v0.2 "Heading"): "heading" is a Greenhouse <h1>–<h6>; "item" is a list
# item (Greenhouse <li>, Ashby line starting with a list marker); everything else is "text".
HEADING, ITEM, TEXT = "heading", "item", "text"


class _BlockCollector(_TextCollector):
    """Like _TextCollector, but marks block boundaries and the innermost block element of each piece."""

    def __init__(self):
        super().__init__()
        self.stack: list[str] = []
        self.kinds: list[str | None] = []  # parallel to self.parts; None for a break

    def _break(self):
        self.parts.append(_BREAK)
        self.kinds.append(None)

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        if tag in _BLOCK_TAGS:
            self._break()
            if tag not in ("br", "hr"):
                self.stack.append(tag)

    def handle_endtag(self, tag):
        super().handle_endtag(tag)
        if tag in _BLOCK_TAGS:
            self._break()
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass

    def handle_startendtag(self, tag, attrs):
        if tag in _BLOCK_TAGS:
            self._break()

    def handle_data(self, data):
        if not self._skipping:
            self.parts.append(data)
            top = self.stack[-1] if self.stack else None
            self.kinds.append(HEADING if top in _HEADING_TAGS else ITEM if top == "li" else TEXT)


def html_blocks_with_kinds(content: str | None) -> list[tuple[str, str]]:
    """(text, kind) for each non-empty HTML block of a Greenhouse posting.

    A block's kind is that of its first non-blank piece of text. Joining the texts with spaces
    gives exactly strip_html(content).
    """
    collector = _BlockCollector()
    collector.feed(html.unescape(content or ""))
    collector.close()
    blocks, pieces, kind = [], [], None
    for part, k in zip(collector.parts + [_BREAK], collector.kinds + [None]):
        if part == _BREAK:
            text = normalize(" ".join(pieces))
            if text:
                blocks.append((text, kind))
            pieces, kind = [], None
        else:
            pieces.append(part)
            if kind is None and part.strip():
                kind = k
    return blocks


def html_blocks(content: str | None) -> list[str]:
    """The visible text of a Greenhouse posting, one string per HTML block, empty blocks dropped.

    Joining the blocks with spaces gives exactly strip_html(content).
    """
    return [text for text, _ in html_blocks_with_kinds(content)]


def plain_blocks_with_kinds(text: str | None) -> list[tuple[str, str]]:
    """(line, kind) for each non-blank line of a plain-text posting (Ashby descriptionPlain)."""
    out = []
    for line in (text or "").splitlines():
        b = normalize(line)
        if b:
            out.append((b, ITEM if _LIST_MARKER.match(b) else TEXT))
    return out


def plain_blocks(text: str | None) -> list[str]:
    """One string per non-blank line of a plain-text posting (Ashby descriptionPlain)."""
    return [b for b, _ in plain_blocks_with_kinds(text)]


def word_pattern(phrase: str, ignore_case: bool = True) -> re.Pattern:
    body = r"\s+".join(re.escape(word) for word in phrase.split())
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(rf"(?<![{_WORD_CHAR}]){body}(?![{_WORD_CHAR}])", flags)


def contains_word(text: str, phrase: str, ignore_case: bool = True) -> bool:
    return word_pattern(phrase, ignore_case).search(text) is not None
