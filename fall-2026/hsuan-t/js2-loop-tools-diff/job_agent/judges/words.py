"""The one place that turns text into words, phrases, years and salaries for every rule check.

CONTRACT Wrong version 4: if each check lowercased and split on its own, one of them would drift
(forget "/" or tabs) and its verdicts would be wrong in a way that still looks plausible. Every
check imports from here instead, so the test for this module covers all six checks at once.
"""

import html
import re

# \W is "not a letter, digit or underscore" in Unicode, so "Zürich" stays one word; the underscore
# is added because the CONTRACT splits at everything that is not a letter or a digit.
_SPLIT = re.compile(r"[\W_]+")
_TAG = re.compile(r"<[^>]+>")
# A range counts as its first number ("2–12+ years" -> 2), per CONTRACT "Numbers".
_YEARS = re.compile(r"(\d+)\s*\+?\s*(?:[-–—]\s*\d+\s*\+?\s*)?(?:years?|yrs)\b")
# Only comma-grouped dollar amounts ("$156,800"); "$5" or "$1M" are deliberately not salaries (Known limits).
_SALARY = re.compile(r"\$(\d{1,3}(?:,\d{3})+)")


def words(text: str) -> list[str]:
    """Lowercase, then split at every non-letter/non-digit; empty pieces dropped (CONTRACT "How words are matched")."""
    return [w for w in _SPLIT.split(text.lower()) if w]


def strip_html(content: str) -> str:
    """Greenhouse escapes its HTML once (&lt;p&gt;), so unescape, drop tags, then unescape the text's own entities (&amp;)."""
    return html.unescape(_TAG.sub(" ", html.unescape(content)))


def has_all_words(phrase: str, text_words: set[str]) -> bool:
    """Order-free match: every word of the phrase is somewhere in the text. Used by checks 1a, 1b, 2, 3."""
    phrase_words = words(phrase)
    return bool(phrase_words) and all(w in text_words for w in phrase_words)


def has_phrase(phrase: str, text_words: list[str]) -> bool:
    """Whole-phrase match (check 5 only): the words must be adjacent and in order, otherwise
    "No degree required. Visa sponsorship is available." would fail on "no sponsorship" (Wrong version 6)."""
    p = words(phrase)
    n = len(p)
    return n > 0 and any(text_words[i:i + n] == p for i in range(len(text_words) - n + 1))


def years_in(text: str) -> list[int]:
    return [int(n) for n in _YEARS.findall(text.lower())]


def salaries_in(text: str) -> list[int]:
    return [int(n.replace(",", "")) for n in _SALARY.findall(text)]
