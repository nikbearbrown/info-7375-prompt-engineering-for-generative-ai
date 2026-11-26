"""An independent §6.4 location classifier, deliberately built differently.

The production classifier (``job_search_agent.rule.location``) uses hand-typed lists
and regular expressions. This oracle:

* reads the signal lists **directly from the text of CONTRACT.md §6.4** (the
  backticked items on the relevant lines), so a transcription slip in the production
  lists shows up as a disagreement; and
* matches **without ``re``**: names are compared against runs of letters/digits
  ("word tokens") joined by single spaces, and the case-sensitive US tokens and the
  ``", XX"`` state codes are found by scanning with ``str.find`` and checking the
  neighbouring characters by hand.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path

CONTRACT_PATH = Path(__file__).resolve().parents[2] / "CONTRACT.md"


@dataclass(frozen=True)
class ContractLists:
    """The §6.4 lists exactly as written in CONTRACT.md."""

    us_tokens: tuple[str, ...]
    state_codes: tuple[str, ...]
    us_cities: tuple[str, ...]
    non_us_countries: tuple[str, ...]
    non_us_cities: tuple[str, ...]
    rescue_phrases: tuple[str, ...]


def _backticked(text: str) -> list[str]:
    parts = text.split("`")
    return [parts[i] for i in range(1, len(parts), 2)]


def _line_starting(lines: list[str], prefix: str) -> str:
    (line,) = [line for line in lines if line.startswith(prefix)]
    return line


@cache
def contract_lists() -> ContractLists:
    """Parses the §6.4 lists out of CONTRACT.md."""
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    section = text.split("### 6.4", 1)[1].split("### 6.5", 1)[0]
    lines = section.splitlines()
    codes_line = _line_starting(lines, "2. A comma")
    (codes,) = [
        item for item in _backticked(codes_line) if " " in item and "," not in item
    ]
    rescue_line = _line_starting(lines, "**Rescue from the description.**")
    rescue_part = rescue_line.split("case-insensitively:", 1)[1].split(
        "If one is present", 1
    )[0]
    token_line = _line_starting(lines, "1. The token").split(", matched", 1)[0]
    return ContractLists(
        us_tokens=tuple(_backticked(token_line)),
        state_codes=tuple(codes.split(" ")),
        us_cities=tuple(_backticked(_line_starting(lines, "3. One of these city"))),
        non_us_countries=tuple(_backticked(_line_starting(lines, "- Countries:"))),
        non_us_cities=tuple(_backticked(_line_starting(lines, "- Cities:"))),
        rescue_phrases=tuple(_backticked(rescue_part)),
    )


def _tokens(text: str) -> list[tuple[int, int]]:
    """Returns ``(start, end)`` of every maximal run of ASCII letters/digits."""
    spans: list[tuple[int, int]] = []
    start = None
    for i, ch in enumerate(text + "\0"):
        alnum = ch.isascii() and ch.isalnum()
        if alnum and start is None:
            start = i
        elif not alnum and start is not None:
            spans.append((start, i))
            start = None
    return spans


def _has_name(text: str, name: str) -> bool:
    """Case-insensitive whole-word match of a (possibly multiword) name."""
    words = name.lower().split(" ")
    spans = _tokens(text)
    lowered = [text[a:b].lower() for a, b in spans]
    for i in range(len(spans) - len(words) + 1):
        if lowered[i : i + len(words)] != words:
            continue
        gaps_ok = all(
            text[spans[i + k][1] : spans[i + k + 1][0]] == " "
            for k in range(len(words) - 1)
        )
        if gaps_ok:
            return True
    return False


def _is_letter(ch: str) -> bool:
    return ch.isascii() and ch.isalpha()


def _has_us_token(text: str, token: str) -> bool:
    """Case-sensitive token with no letter directly before or after it."""
    pos = text.find(token)
    while pos != -1:
        before = text[pos - 1] if pos > 0 else ""
        after = text[pos + len(token)] if pos + len(token) < len(text) else ""
        if not _is_letter(before) and not _is_letter(after):
            return True
        pos = text.find(token, pos + 1)
    return False


def _has_state_code(text: str, codes: tuple[str, ...]) -> bool:
    """``", "`` + an uppercase state code with no letter after it."""
    pos = text.find(", ")
    while pos != -1:
        code = text[pos + 2 : pos + 4]
        after = text[pos + 4] if pos + 4 < len(text) else ""
        if code in codes and not _is_letter(after):
            return True
        pos = text.find(", ", pos + 1)
    return False


def oracle_label(location_name: str, cleaned_content: str = "") -> str:
    """Labels a location string under §6.4.

    Args:
        location_name: The raw ``$.location.name``.
        cleaned_content: Cleaned description text, used only for the rescue.

    Returns:
        ``"US_BASED"``, ``"NON_US"`` or ``"NOT_ESTABLISHED"``.
    """
    lists = contract_lists()
    us = (
        any(_has_us_token(location_name, t) for t in lists.us_tokens)
        or _has_state_code(location_name, lists.state_codes)
        or any(_has_name(location_name, c) for c in lists.us_cities)
    )
    non_us = any(
        _has_name(location_name, n)
        for n in lists.non_us_countries + lists.non_us_cities
    )
    if us and not non_us:
        return "US_BASED"
    if non_us and not us:
        return "NON_US"
    if not us and not non_us:
        lowered = cleaned_content.lower()
        for phrase in lists.rescue_phrases:
            pos = lowered.find(phrase)
            while pos != -1:
                before = lowered[pos - 1] if pos > 0 else ""
                end = pos + len(phrase)
                after = lowered[end] if end < len(lowered) else ""
                if not (before.isascii() and before.isalnum()) and not (
                    after.isascii() and after.isalnum()
                ):
                    return "US_BASED"
                pos = lowered.find(phrase, pos + 1)
    return "NOT_ESTABLISHED"
