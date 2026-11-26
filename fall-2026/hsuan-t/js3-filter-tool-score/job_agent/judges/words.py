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
# FILTER v2 (B2): the number may sit in brackets, "six (6) years" -> 6; v1 stopped at the ")" and
# read no years at all in 7 Stripe US-PERM postings (reports/filter_v2_measure/result.md).
_YEARS = re.compile(r"\(?(\d+)\+?\)?\s*\+?\s*(?:[-–—]\s*\d+\s*\+?\s*)?(?:years?|yrs)\b")
# FILTER v2 (A): ceilings a new-grad JD sets, "no more than 18 months", "0-1 years" (upper end).
_CAP_NO_MORE = re.compile(r"no more than (\d+)\s*(months?|years?)\b")
_CAP_RANGE = re.compile(r"\b(\d+)\s*[-–—]\s*(\d+)\s*\+?\s*(?:years?|yrs)\b")
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


def year_ceilings(text: str) -> list[float]:
    """Upper limits on experience, in years (months / 12). Rule 4 needs them because "0-1 years"
    reads as a requirement of 0 (a pass) while it means the role is for people with at most 1 year."""
    t = text.lower()
    caps = [int(n) / (12 if unit.startswith("month") else 1) for n, unit in _CAP_NO_MORE.findall(t)]
    return caps + [float(hi) for _, hi in _CAP_RANGE.findall(t)]


def salaries_in(text: str) -> list[int]:
    return [int(n.replace(",", "")) for n in _SALARY.findall(text)]
