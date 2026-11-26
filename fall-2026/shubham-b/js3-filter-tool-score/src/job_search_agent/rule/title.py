"""§6.1 title check: role-family phrases and seniority/internship markers.

The role families come from ``$.target.roles[*]`` (CONTRACT §4); this module only
holds the documented alias table that says which title words spell each family.
A title passes when it contains a family *phrase* and no excluded marker:

* **Family phrase (PLAN A2).** One of the role's family words, optionally followed by
  `` software``, followed by `` engineer``, with no letter or digit directly before or
  after the whole phrase. The title is lowercased, trimmed and its whitespace runs are
  collapsed to one space first. So ``Back-End Software Engineer`` and ``Full Stack
  Engineer`` pass, while ``Backend/API Engineer`` (a ``/`` between the words),
  ``Software Engineering`` and the plural ``Software Engineers`` (A4) do not. The
  Software Engineer role's only phrase is ``software engineer``.
* **Excluded markers (A5).** The §6.1 list as whole words (no letter or digit on
  either side) of the lowercased title. ``sr.`` is covered by ``sr``. ``SWE I`` and
  ``SWE II`` are "allowed" only in the sense that ``i`` and ``ii`` are not markers;
  a family phrase is still required (A3).

**Word boundaries are ASCII-only.** "No letter or digit" means no ``[a-z0-9]``
character (the title is lowercased first). A non-ASCII letter or digit is treated as
a boundary, so ``ébackend engineer`` would still contain the phrase. This is
deliberate and documented rather than changed: the contract's golden tests pin the
current matching, and the board's titles are ASCII.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Final

from job_search_agent.errors import ConfigError
from job_search_agent.models import TitleCheck

ROLE_ALIASES: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        "Software Engineer": ("software",),
        "Full-Stack Software Engineer": ("full-stack", "full stack", "fullstack"),
        "Backend Engineer": ("backend", "back-end", "back end"),
        "Frontend Engineer": ("frontend", "front-end", "front end"),
    }
)
"""Résumé role (exact ``$.target.roles`` string) -> lowercase family words (§6.1)."""

EXCLUDED_MARKERS: Final[tuple[str, ...]] = (
    "senior",
    "sr",
    "staff",
    "principal",
    "lead",
    "manager",
    "director",
    "intern",
    "internship",
    "iii",
    "iv",
    "l3",
    "l4",
)
"""§6.1 markers, lowercased, in contract order (``sr.`` is matched by ``sr``)."""

_BOUNDARY_BEFORE: Final = r"(?<![a-z0-9])"
_BOUNDARY_AFTER: Final = r"(?![a-z0-9])"
_WHITESPACE: Final = re.compile(r"\s+")


def _whole_word(words: str) -> re.Pattern[str]:
    """Compiles a lowercase pattern with no letter or digit on either side."""
    return re.compile(f"{_BOUNDARY_BEFORE}(?:{words}){_BOUNDARY_AFTER}")


def _family_pattern(role: str, aliases: Sequence[str]) -> re.Pattern[str]:
    """Compiles the family-phrase pattern of one role.

    Args:
        role: The résumé role.
        aliases: Its family words.

    Returns:
        ``software engineer`` for the Software Engineer role, otherwise
        ``(<alias>|...)( software)? engineer``, all whole-phrase.
    """
    if role == "Software Engineer":
        return _whole_word("software engineer")
    words = "|".join(re.escape(alias) for alias in aliases)
    return _whole_word(f"(?:{words})(?: software)? engineer")


_FAMILY_PATTERNS: Final[Mapping[str, re.Pattern[str]]] = MappingProxyType(
    {role: _family_pattern(role, aliases) for role, aliases in ROLE_ALIASES.items()}
)
_MARKER_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = tuple(
    (marker, _whole_word(re.escape(marker))) for marker in EXCLUDED_MARKERS
)


def normalize_title(title: str) -> str:
    """Lowercases, trims and collapses whitespace runs to a single space.

    Args:
        title: The raw ``$.title`` value.

    Returns:
        The normalised title.
    """
    return _WHITESPACE.sub(" ", title).strip().lower()


def validate_roles(roles: Sequence[str]) -> None:
    """Checks that every résumé role has a documented alias entry.

    Args:
        roles: The ``$.target.roles`` values.

    Raises:
        ConfigError: If a role is not a key of ``ROLE_ALIASES`` (exact string).
    """
    unknown = [role for role in roles if role not in ROLE_ALIASES]
    if unknown:
        raise ConfigError(
            f"$.target.roles has {len(unknown)} role(s) with no documented alias "
            f"entry; known roles: {sorted(ROLE_ALIASES)}"
        )


def _family_patterns(roles: Sequence[str]) -> list[tuple[str, re.Pattern[str]]]:
    """Selects the family patterns for the résumé's roles, in résumé order.

    Args:
        roles: The ``$.target.roles`` values.

    Returns:
        ``(role, pattern)`` pairs, duplicates removed.

    Raises:
        ConfigError: If a role has no documented alias entry.
    """
    validate_roles(roles)
    return [(role, _FAMILY_PATTERNS[role]) for role in dict.fromkeys(roles)]


def _reason(matched: Sequence[str], markers: Sequence[str]) -> str:
    """Builds the short human-readable reason for a title check."""
    if not matched:
        family = "The title contains no role-family phrase from $.target.roles"
    else:
        family = f"The title matches the role family {', '.join(matched)}"
    if markers:
        return f"{family}, and it contains excluded marker(s): {', '.join(markers)}."
    if matched:
        return f"{family} and contains no excluded marker."
    return f"{family}."


def title_check(title: str, roles: Sequence[str]) -> TitleCheck:
    """Applies the §6.1 title check.

    Args:
        title: The raw ``$.title`` value.
        roles: The résumé's ``$.target.roles`` values.

    Returns:
        Every matched role (résumé order) and every excluded marker found (contract
        order, each once). ``passed`` is true when a role matched and no marker did.

    Raises:
        ConfigError: If a role in ``roles`` has no documented alias entry.
    """
    normalized = normalize_title(title)
    matched = [
        role for role, pattern in _family_patterns(roles) if pattern.search(normalized)
    ]
    markers = [
        marker for marker, pattern in _MARKER_PATTERNS if pattern.search(normalized)
    ]
    return TitleCheck(
        matched_roles=matched,
        excluded_markers=markers,
        reason=_reason(matched, markers),
    )
