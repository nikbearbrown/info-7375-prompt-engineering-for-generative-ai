"""Readable text and verbatim quotes.

`readable()` mirrors the inherited JS1 `html_to_text` (unescape once, parse, drop script/style,
join text parts with spaces) but keeps line breaks at block tags so quotes can be cut at
bullet/paragraph boundaries. normalize(readable(x)) == normalize(html_to_text(x)) is checked
for every corpus posting by js3/corpus.py and by tests/test_corpus.py.
"""
import html
import re
from html.parser import HTMLParser

from inherited.rules import contains_phrase, normalize

BLOCK_TAGS = {"p", "br", "li", "ul", "ol", "div", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "section", "table"}
MAX_QUOTE = 300


class _Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def readable(raw):
    """Description as served (Greenhouse entity-escaped HTML, or plain text) -> readable lines."""
    if not raw:
        return ""
    p = _Blocks()
    p.feed(html.unescape(raw))
    p.close()
    joined = " ".join(p.parts)
    lines = (" ".join(line.split()) for line in joined.split("\n"))
    return "\n".join(line for line in lines if line)


def segments(text):
    """Lines, then sentences within a line. Every segment is a verbatim substring of `text`."""
    out = []
    for line in (text or "").split("\n"):
        out.extend(s for s in re.split(r"(?<=[.!?;])\s+", line) if s)
    return out


def quote_for(text, phrase):
    """Shortest verbatim span (segment, or comma-chunk of a long segment) whose normalized
    form contains `phrase` as whole words; None if no single segment contains it."""
    for seg in segments(text):
        if contains_phrase(normalize(seg), phrase):
            if len(seg) <= MAX_QUOTE:
                return seg
            for chunk in seg.split(", "):
                if contains_phrase(normalize(chunk), phrase):
                    return chunk[:MAX_QUOTE] if len(chunk) > MAX_QUOTE and contains_phrase(
                        normalize(chunk[:MAX_QUOTE]), phrase) else chunk
            return seg
    return None
