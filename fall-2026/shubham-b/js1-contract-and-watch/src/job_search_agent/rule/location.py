"""§6.4 US-based location check, with the description rescue.

``$.location.name`` is read as one string (not cleaned or trimmed). Its signals:

* **US token** — ``US``, ``USA``, ``U.S.`` or ``United States``, case-sensitive, with
  no *letter* directly before or after (digits are allowed, PLAN A11).
* **State code** — ``", "`` followed by an uppercase code from ``STATE_CODES`` and no
  letter after it (A10). ``Toronto, CA`` therefore carries a US signal (A9).
* **US city** — a name from ``US_CITY_NAMES``, case-insensitive, whole word.
* **Non-US name** — a name from ``NON_US_NAMES``, case-insensitive, whole word.

"Whole word" means no letter or digit directly before or after (§6.2). The label is
``US_BASED`` with only US signals, ``NON_US`` with only non-US signals and
``NOT_ESTABLISHED`` with none or both. A location with no signal (or no
``$.location.name`` at all) is rescued to ``US_BASED`` only by one of
``RESCUE_PHRASES`` in the cleaned ``$.content``, matched case-insensitively with no
letter or digit on either side (A8). Nothing else is inferred.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Final

from job_search_agent.models import LocationCheck, LocationLabel

STATE_CODES: Final[tuple[str, ...]] = (
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
)
"""The 50 state codes plus DC, in contract order."""

US_TOKENS: Final[tuple[str, ...]] = ("US", "USA", "U.S.", "United States")
"""§6.4 signal 1, matched case-sensitively."""

US_CITY_NAMES: Final[tuple[str, ...]] = (
    "Atlanta",
    "Chicago",
    "New York",
    "New York City",
    "San Francisco",
    "South San Francisco",
    "Seattle",
    "Washington DC",
    "ATL",
    "CHI",
    "NYC",
    "SEA",
    "SF",
)
"""§6.4 signal 3, matched case-insensitively as whole words."""

NON_US_COUNTRIES: Final[tuple[str, ...]] = (
    "Australia",
    "Belgium",
    "Brazil",
    "Canada",
    "France",
    "Germany",
    "India",
    "Ireland",
    "Israel",
    "Japan",
    "Luxembourg",
    "Mexico",
    "New Zealand",
    "Poland",
    "Romania",
    "Singapore",
    "Spain",
    "Sweden",
    "Taiwan",
    "Thailand",
    "UK",
    "United Kingdom",
)
NON_US_CITIES: Final[tuple[str, ...]] = (
    "Amsterdam",
    "Auckland",
    "Bangalore",
    "Bangkok",
    "Barcelona",
    "Bengaluru",
    "Berlin",
    "Bucharest",
    "CDMX",
    "Dublin",
    "London",
    "Madrid",
    "Melbourne",
    "Munich",
    "Paris",
    "Sao Paulo",
    "Stockholm",
    "Sydney",
    "Taipei",
    "Tokyo",
    "Toronto",
    "Tor",
    "Toro",
    "Vancouver",
)
NON_US_NAMES: Final[tuple[str, ...]] = NON_US_COUNTRIES + NON_US_CITIES
"""Every §6.4 non-US signal, matched case-insensitively as whole words."""

RESCUE_PHRASES: Final[tuple[str, ...]] = (
    "must be based in the united states",
    "must be located in the united states",
    "united states only",
    "us only",
    "u.s. only",
    "usa only",
    "remote within the united states",
    "remote in the united states",
    "remote from the united states",
    "us-based only",
    "u.s.-based only",
    "usa-based only",
)
"""The §6.4 description phrases that rescue a location with no signal."""

LOCATION_PATH: Final = "$.location.name"
CONTENT_PATH: Final = "$.content"


def _alternation(words: Iterable[str]) -> str:
    """Escapes words into a regex alternation, longest first."""
    return "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True))


_WORD_BEFORE: Final = r"(?<![A-Za-z0-9])"
_WORD_AFTER: Final = r"(?![A-Za-z0-9])"

_US_TOKEN: Final = re.compile(
    rf"(?<![A-Za-z])(?:{_alternation(US_TOKENS)})(?![A-Za-z])"
)
_STATE_CODE: Final = re.compile(rf", (?:{_alternation(STATE_CODES)})(?![A-Za-z])")
_US_CITY: Final = re.compile(
    rf"{_WORD_BEFORE}(?:{_alternation(US_CITY_NAMES)}){_WORD_AFTER}", re.IGNORECASE
)
_NON_US: Final = re.compile(
    rf"{_WORD_BEFORE}(?:{_alternation(NON_US_NAMES)}){_WORD_AFTER}", re.IGNORECASE
)
_RESCUE: Final[tuple[tuple[str, re.Pattern[str]], ...]] = tuple(
    (
        phrase,
        re.compile(rf"{_WORD_BEFORE}{re.escape(phrase)}{_WORD_AFTER}", re.IGNORECASE),
    )
    for phrase in RESCUE_PHRASES
)


def location_signals(location_name: str) -> tuple[list[str], list[str]]:
    """Finds the §6.4 signals in a location string.

    Args:
        location_name: The raw ``$.location.name`` value.

    Returns:
        ``(us_signals, non_us_signals)``: the matched source text of each signal in
        order of appearance (a state code is reported with its ``", "``).
    """
    us = [
        (m.start(), m.group())
        for pattern in (_US_TOKEN, _STATE_CODE, _US_CITY)
        for m in pattern.finditer(location_name)
    ]
    non_us = [m.group() for m in _NON_US.finditer(location_name)]
    return [text for _, text in sorted(us)], non_us


def rescue_phrase(cleaned_content: str) -> str | None:
    """Returns the first §6.4 rescue phrase present in cleaned content, if any.

    Args:
        cleaned_content: ``text.clean_html`` of ``$.content``.

    Returns:
        The phrase (contract spelling), or ``None``.
    """
    for phrase, pattern in _RESCUE:
        if pattern.search(cleaned_content):
            return phrase
    return None


def _quoted(signals: Iterable[str]) -> str:
    return ", ".join(f"'{s}'" for s in signals)


def _no_signal_check(
    location_name: str | None, cleaned_content: str, fallback_path: str
) -> LocationCheck:
    """Labels a location with no signal of either kind (rescue or NOT_ESTABLISHED).

    Args:
        location_name: The raw value, or ``None`` when the path does not exist.
        cleaned_content: Cleaned ``$.content``.
        fallback_path: Evidence path used when ``location_name`` is ``None`` and no
            rescue phrase is present.

    Returns:
        The location check.
    """
    source = (
        "The posting has no $.location.name"
        if location_name is None
        else "The location has no US or non-US signal"
    )
    name_paths = [] if location_name is None else [LOCATION_PATH]
    phrase = rescue_phrase(cleaned_content)
    if phrase is not None:
        return LocationCheck(
            label=LocationLabel.US_BASED,
            evidence=[*name_paths, CONTENT_PATH],
            reason=f"{source}, and the description says '{phrase}'.",
        )
    return LocationCheck(
        label=LocationLabel.NOT_ESTABLISHED,
        evidence=name_paths or [fallback_path],
        reason=f"{source}, and no §6.4 rescue phrase appears in the description.",
    )


def classify_location(
    location_name: str | None,
    cleaned_content: str,
    *,
    fallback_path: str = CONTENT_PATH,
) -> LocationCheck:
    """Applies the §6.4 location check.

    Args:
        location_name: The raw ``$.location.name`` value, or ``None`` when that
            path does not exist in the posting (A30).
        cleaned_content: ``text.clean_html`` of ``$.content``, searched only for the
            rescue phrases.
        fallback_path: The evidence path for an absent location that is not
            rescued; the caller passes a path that exists (``$.content`` if the
            posting has one, otherwise ``$.id``). Reading A30: ``$.id`` is cited
            only so the evidence is always a real path; it holds neither a
            location nor content, and the provider records that as the
            ``MISSING_LOCATION`` data-quality issue's detail.

    Returns:
        The label, the source paths it rests on and a short reason.
    """
    us, non_us = location_signals(location_name or "")
    if us and non_us:
        return LocationCheck(
            label=LocationLabel.NOT_ESTABLISHED,
            evidence=[LOCATION_PATH],
            reason=(
                f"The location has US signal(s) {_quoted(us)} and non-US signal(s) "
                f"{_quoted(non_us)}, so it is not established as US-only."
            ),
        )
    if us:
        return LocationCheck(
            label=LocationLabel.US_BASED,
            evidence=[LOCATION_PATH],
            reason=f"The location has US signal(s) {_quoted(us)} and no non-US one.",
        )
    if non_us:
        return LocationCheck(
            label=LocationLabel.NON_US,
            evidence=[LOCATION_PATH],
            reason=(
                f"The location has non-US signal(s) {_quoted(non_us)} and no US one."
            ),
        )
    return _no_signal_check(location_name, cleaned_content, fallback_path)
