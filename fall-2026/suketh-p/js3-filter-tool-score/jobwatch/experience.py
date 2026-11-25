"""FILTER.md v0.2's one change: the experience-minimum rule.

The rule is the student's choice, an option Claude Code worded (FILTER.md, "After the reject
audit"): "Reject when the description sets a minimum of 3+ years that is not marked preferred."
v0.1 has no such rule (screen.EXPERIENCE_MINIMUM_YEARS is None); v0.2 sets it to 3
(variants/v0.2-experience-minimum.json).

How a description is read is Claude Code's reading, written before the held-out comparison ran
and pinned by tests/test_experience.py. The 30 held-out postings were not read to write it.

  * Blocks. The decoded HTML is split into blocks: each paragraph, list item, heading, table
    cell or line. A block is a heading when it is an h1-h6, or when it is bold from end to end
    and at most 100 characters ("<p><strong>What we look for:</strong></p>"). Every block sits
    under the last heading above it.
  * Statements of years. A number (digits, or one to twenty in words), with an optional "+",
    "or more" or range, followed by "years" or "yrs". A range reads at its lower end ("2-4
    years" is 2). A singular "year" never counts, so "4-year degree" is not experience.
  * Not a requirement: the word just before the number is after, every, last, past, first,
    next, previous, recent or within, or the word just after "years" is ago, thereafter or old
    ("Paid month off after 4 years", "In your last three years of work").
  * Marked preferred: the statement's own block, or the heading it sits under, contains
    preferred, nice to have, bonus, a plus, pluses or may also.
  * The minimum a posting sets is the largest number in a statement not marked preferred.

Known limits: alternatives inside one sentence ("5 years, or 2 with a PhD") are not read as
alternatives; "up to 5 years" reads as a minimum of 5; a block that calls something else
preferred ("3+ years required; Go preferred") marks its years preferred too; a section title the
board writes as plain text, not as a heading or a bold paragraph, is not seen as a heading."""

import re
from html.parser import HTMLParser

from jobwatch.normalize import contains_phrase, decode_entities, tokens

BLOCK_TAGS = frozenset("p li h1 h2 h3 h4 h5 h6 div td th tr ul ol br section table dd dt blockquote".split())
HEADING_TAGS = frozenset("h1 h2 h3 h4 h5 h6".split())
BOLD_TAGS = frozenset(("strong", "b"))
BOLD_HEADING_MAX = 100
PREFERRED_MARKERS = ("preferred", "nice to have", "bonus", "a plus", "pluses", "may also")
NOT_BEFORE = frozenset(("after", "every", "last", "past", "first", "next", "previous", "recent", "within"))
NOT_AFTER = frozenset(("ago", "thereafter", "old"))
NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
                "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
                "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20}
_NUMBER = r"(\d{1,2}|" + "|".join(NUMBER_WORDS) + r")"
YEARS_PATTERN = (r"(?:\b([a-z]+)\s+)?\b" + _NUMBER + r"(?:\s*\+)?(?:\s*(?:-|–|—|to)\s*" + _NUMBER + r")?"
                 r"(?:\s*\+)?(?:\s+or\s+more)?[\s-]*(?:years|yrs)\b(?:\W+([a-z]+))?")
YEARS = re.compile(YEARS_PATTERN, re.I)


class _Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []                      # [(is_heading, text)]
        self._text, self._bold = [], []
        self._heading_depth = self._bold_depth = 0

    def _flush(self):
        text = " ".join("".join(self._text).split())
        bold = " ".join("".join(self._bold).split())
        if text:
            heading = self._heading_depth > 0 or (bold == text and len(text) <= BOLD_HEADING_MAX)
            self.blocks.append((heading, text))
        self._text, self._bold = [], []

    def handle_starttag(self, tag, attrs):
        if tag in BLOCK_TAGS:
            self._flush()
        if tag in HEADING_TAGS:
            self._heading_depth += 1
        elif tag in BOLD_TAGS:
            self._bold_depth += 1

    def handle_startendtag(self, tag, attrs):
        if tag in BLOCK_TAGS:
            self._flush()

    def handle_endtag(self, tag):
        if tag in BLOCK_TAGS:
            self._flush()
        if tag in HEADING_TAGS:
            self._heading_depth = max(0, self._heading_depth - 1)
        elif tag in BOLD_TAGS:
            self._bold_depth = max(0, self._bold_depth - 1)

    def handle_data(self, data):
        self._text.append(data)
        if self._bold_depth:
            self._bold.append(data)

    def close(self):
        super().close()
        self._flush()


def _number(text):
    return int(text) if text.isdigit() else NUMBER_WORDS[text.lower()]


def _lower_end(first, second):
    return min(first, second) if second is not None else first


def _is_requirement(word_before, word_after):
    return word_before not in NOT_BEFORE and word_after not in NOT_AFTER


def _preferred(block_tokens, heading_tokens):
    return any(contains_phrase(block_tokens, m) or contains_phrase(heading_tokens, m) for m in PREFERRED_MARKERS)


def blocks(description):
    parser = _Blocks()
    parser.feed(decode_entities(description or ""))
    parser.close()
    return parser.blocks


def read(description):
    """{"minimum_years": the largest stated minimum not marked preferred, or None, "statements": [...]}."""
    statements, heading = [], ""
    for is_heading, text in blocks(description):
        block_tokens, heading_tokens = tokens(text), tokens(heading)
        for m in YEARS.finditer(text):
            before, first, second, after = m.group(1), m.group(2), m.group(3), m.group(4)
            if not _is_requirement((before or "").lower(), (after or "").lower()):
                continue
            statements.append({"years": _lower_end(_number(first), _number(second) if second else None),
                               "preferred": _preferred(block_tokens, heading_tokens),
                               "text": text[:300], "heading": heading})
        if is_heading:
            heading = text
    minimums = [s["years"] for s in statements if not s["preferred"]]
    return {"minimum_years": max(minimums) if minimums else None, "statements": statements}
