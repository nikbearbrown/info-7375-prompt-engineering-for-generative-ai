"""§6.3 explicit exclusion phrases (citizenship, clearance, unpaid work).

The phrases are a fixed reading of ``$.target.excluded[*]``; that résumé field is
never parsed at runtime. Each phrase is matched case-insensitively in the cleaned
title and the cleaned ``$.content`` (not department names, PLAN A27), searched as
separate fields, with no letter or digit directly before or after it (A8). Nothing
is inferred from silence or from other wording.
"""

from __future__ import annotations

import re
from typing import Final

from job_search_agent.models import Posting
from job_search_agent.text import clean_html

EXCLUSION_PHRASES: Final[tuple[str, ...]] = (
    "must be a U.S. citizen",
    "U.S. citizens only",
    "United States citizens only",
    "citizenship required",
    "security clearance required",
    "active clearance required",
    "must hold a clearance",
    "unpaid position",
    "unpaid role",
    "unpaid internship",
    "this is an unpaid opportunity",
)
"""The §6.3 phrases, in contract order."""

_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = tuple(
    (
        phrase,
        re.compile(
            rf"(?<![A-Za-z0-9]){re.escape(phrase)}(?![A-Za-z0-9])", re.IGNORECASE
        ),
    )
    for phrase in EXCLUSION_PHRASES
)


def phrases_in_text(cleaned_text: str) -> list[str]:
    """Returns every §6.3 phrase present in already-cleaned text.

    Args:
        cleaned_text: Output of ``text.clean_html``.

    Returns:
        The phrases found, in contract order.
    """
    return [phrase for phrase, pattern in _PATTERNS if pattern.search(cleaned_text)]


def find_exclusions(posting: Posting) -> list[str]:
    """Applies the §6.3 check to a posting's cleaned title and content.

    Args:
        posting: The normalised posting.

    Returns:
        Every phrase found in either field, once each, in contract order; empty
        when the check passes.
    """
    found = set(phrases_in_text(clean_html(posting.title)))
    found.update(phrases_in_text(clean_html(posting.content_raw)))
    return [phrase for phrase in EXCLUSION_PHRASES if phrase in found]
