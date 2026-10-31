"""Text preparation (CONTRACT.md, The rule > Text preparation): Greenhouse `content` -> requirements sentences."""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser

QUOTES = {"’": "'", "‘": "'", "“": '"', "”": '"'}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "strong", "b", "div"}
BLOCK_TAGS = {"li", "p", "br", "div", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "tr"}
TRAILING = ":.-–—"
SENTENCE_SPLIT = re.compile(r"(?<=[.!?]) ")


def whole_word(term: str) -> re.Pattern:
    """The contract's whole-word match: (?<![a-z0-9])TERM(?![a-z0-9]), TERM regex-escaped, on lowercased text."""
    return re.compile(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])")


def normalize_quotes(text: str) -> str:
    for curly, straight in QUOTES.items():
        text = text.replace(curly, straight)
    return text


def heading_key(text: str) -> str:
    """Lowercase, trim, then strip trailing : . - – — (step 3)."""
    return text.lower().strip().rstrip(TRAILING)


class _CutFinder(HTMLParser):
    """Records where each heading-capable element starts in the source and what its whole text is."""

    def __init__(self, source: str, cut_headings: set):
        super().__init__(convert_charrefs=True)
        self.cut_headings = cut_headings
        self.line_starts = [0] + [i + 1 for i, c in enumerate(source) if c == "\n"]
        self.open: list[list] = []          # [tag, start offset, text parts]
        self.cut_at: int | None = None

    def handle_starttag(self, tag, attrs):
        if tag in HEADING_TAGS:
            line, col = self.getpos()
            self.open.append([tag, self.line_starts[line - 1] + col, []])

    def handle_endtag(self, tag):
        for i in range(len(self.open) - 1, -1, -1):
            if self.open[i][0] == tag:
                _, start, parts = self.open.pop(i)
                if heading_key("".join(parts)) in self.cut_headings and (self.cut_at is None or start < self.cut_at):
                    self.cut_at = start
                return

    def handle_data(self, data):
        for element in self.open:
            element[2].append(data)


class _Lines(HTMLParser):
    """Step 4: every block tag (start or end) becomes a newline; all other tags vanish."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)


def cut_boilerplate(markup: str, cut_headings) -> str:
    finder = _CutFinder(markup, set(cut_headings))
    finder.feed(markup)
    finder.close()
    return markup if finder.cut_at is None else markup[:finder.cut_at]


def requirements_sentences(content: str | None, cut_headings, drop_phrases) -> list[str]:
    markup = normalize_quotes(html.unescape(content or ""))          # steps 1-2
    markup = cut_boilerplate(markup, cut_headings)                    # step 3
    p = _Lines()
    p.feed(markup)
    p.close()
    # Entities that were double-escaped (&amp;rsquo;) only become curly quotes while parsing, so step 2 runs again.
    text = normalize_quotes("".join(p.parts))
    lines = [re.sub(r"[ \t]+", " ", ln).strip().lower() for ln in text.split("\n")]
    sentences = [s.strip() for ln in lines if ln for s in SENTENCE_SPLIT.split(ln)]      # step 5
    return [s for s in sentences if s and not any(ph in s for ph in drop_phrases)]


def requirements_text(sentences: list[str]) -> str:
    return "\n".join(sentences)
