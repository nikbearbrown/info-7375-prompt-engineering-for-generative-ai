"""Text normalization and whole-word phrase matching (CONTRACT.md, The rule, Step 1)."""
from __future__ import annotations

import html
import re
from typing import Optional

_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")

# A "word character" for boundaries. Hyphens and punctuation are NOT word characters,
# so "java-based" contains the word "java", but "javascript" does not.
_WORD = "a-z0-9"


def normalize(value: Optional[str]) -> str:
    """Decode HTML entities, remove tags, lowercase, collapse whitespace.

    Greenhouse escapes its HTML (`&lt;p&gt;`), so entities are decoded once to expose
    the tags, the tags are removed, and entities are decoded again for text like `&amp;`.
    """
    text = html.unescape(value or "")
    text = _TAG.sub(" ", text)
    text = html.unescape(text)
    return _SPACE.sub(" ", text.lower()).strip()


def phrase_pattern(phrase: str) -> re.Pattern:
    """Whole-word pattern for a phrase; words may be separated by any whitespace."""
    words = normalize(phrase).split()
    if not words:
        raise ValueError("empty phrase")
    body = r"\s+".join(re.escape(w) for w in words)
    return re.compile(rf"(?<![{_WORD}]){body}(?![{_WORD}])")


def find_phrase(phrase: str, normalized_text: str) -> Optional[re.Match]:
    """First whole-word match of `phrase` in already-normalized text, or None."""
    return phrase_pattern(phrase).search(normalized_text)


def find_substring(phrase: str, normalized_text: str) -> Optional[re.Match]:
    """Plain substring search. NOT the contract's matcher; used only by wrong version 2."""
    return re.compile(re.escape(normalize(phrase))).search(normalized_text)


def snippet(normalized_text: str, match: re.Match, width: int = 30) -> str:
    """A short window of the normalized text around a match (always a substring of it)."""
    start = max(0, match.start() - width)
    end = min(len(normalized_text), match.end() + width)
    return normalized_text[start:end].strip()
