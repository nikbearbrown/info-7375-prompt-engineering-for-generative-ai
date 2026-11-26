"""§6.2 skill check: which eligible résumé skills appear in a posting.

The eligible skills are the values under the seven §4 ``$.skills.*`` paths, in that
order; ``$.skills.familiar_with_not_shipped`` is never read. Each field (title,
``$.content``, each ``$.departments[i].name``) is cleaned with ``text.clean_html``
before matching, and a skill found in several fields is cited once, from the first
field in that order (PLAN A29).

Matching (§6.2): every special case is keyed by the exact résumé term.

* ``C#`` — exact and case-sensitive; no letter or digit before, and no letter, digit
  or ``#`` after (A6).
* ``Node.js`` / ``Next.js`` — ``Node.js``/``NodeJS`` and ``Next.js``/``NextJS``,
  case-insensitive.
* ``React`` — ``React``, ``React.js`` or ``ReactJS``, case-sensitive.
* ``Express`` — ``Express.js``, ``ExpressJS`` or ``Express framework``,
  case-sensitive.
* ``REST`` — ``REST API``, ``RESTful API`` or ``REST services``, case-sensitive; so
  the plurals ``REST APIs`` and ``RESTful APIs`` do not count (A7).
* Any other term — case-insensitive whole-word match (no letter or digit on either
  side); a multiword term's words must be consecutive, separated by one space after
  cleanup (which collapses whitespace runs).

Every special-case form also needs no letter or digit directly before or after it.

**Word boundaries are ASCII-only.** "No letter or digit" means no ``[A-Za-z0-9]``
character; a non-ASCII letter or digit (``é``, ``٣``) counts as a boundary, so
``éJava`` still matches ``Java``. This is deliberate and documented rather than
changed: the contract's golden tests pin the current matching.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from functools import cache
from types import MappingProxyType
from typing import Any, Final

from job_search_agent.errors import ConfigError
from job_search_agent.models import Posting, SkillEntry, SkillEvidence
from job_search_agent.text import clean_html

SKILL_PATHS: Final[tuple[str, ...]] = (
    "$.skills.languages",
    "$.skills.frontend",
    "$.skills.backend",
    "$.skills.data",
    "$.skills.messaging",
    "$.skills.cloud_devops",
    "$.skills.observability",
)
"""The §4 résumé skill arrays the rule counts, in contract order."""

MIN_DISTINCT_SKILLS: Final = 2
"""§6.5 condition 2: at least this many distinct eligible skills must match."""

_BEFORE: Final = r"(?<![A-Za-z0-9])"
_AFTER: Final = r"(?![A-Za-z0-9])"

_SPECIAL_CASES: Final[Mapping[str, re.Pattern[str]]] = MappingProxyType(
    {
        "C#": re.compile(rf"{_BEFORE}C#(?![A-Za-z0-9#])"),
        "Node.js": re.compile(rf"{_BEFORE}(?:node\.js|nodejs){_AFTER}", re.IGNORECASE),
        "Next.js": re.compile(rf"{_BEFORE}(?:next\.js|nextjs){_AFTER}", re.IGNORECASE),
        "React": re.compile(rf"{_BEFORE}(?:React\.js|ReactJS|React){_AFTER}"),
        "Express": re.compile(
            rf"{_BEFORE}(?:Express\.js|ExpressJS|Express framework){_AFTER}"
        ),
        "REST": re.compile(rf"{_BEFORE}(?:REST API|RESTful API|REST services){_AFTER}"),
    }
)
"""Résumé term -> its §6.2 special-case pattern (case-sensitive unless noted)."""


@cache
def _pattern(term: str) -> re.Pattern[str]:
    """Returns the matching pattern for one résumé term.

    Args:
        term: The exact résumé skill string.

    Returns:
        The special-case pattern, or a case-insensitive whole-word pattern.
    """
    special = _SPECIAL_CASES.get(term)
    if special is not None:
        return special
    return re.compile(rf"{_BEFORE}{re.escape(term)}{_AFTER}", re.IGNORECASE)


def term_in_text(term: str, cleaned_text: str) -> bool:
    """Returns True if a résumé term matches already-cleaned text under §6.2.

    Args:
        term: The exact résumé skill string, e.g. ``"C#"``.
        cleaned_text: Output of ``text.clean_html``.

    Returns:
        Whether the term's §6.2 form appears.
    """
    return _pattern(term).search(cleaned_text) is not None


def skill_entries_from_resume(resume_data: Mapping[str, Any]) -> tuple[SkillEntry, ...]:
    """Lists the countable résumé skills with their paths (§4), in path order.

    A term that appears under two paths is listed once, at its first path, because
    each distinct skill counts at most once (§6.2).

    Args:
        resume_data: The parsed résumé JSON.

    Returns:
        One ``SkillEntry`` per distinct term, e.g. ``("GraphQL",
        "$.skills.backend[4]")``.

    Raises:
        ConfigError: If a §4 skill path is missing, is not an array, or holds a value
            that is not a non-empty string.
    """
    skills = resume_data.get("skills")
    entries: dict[str, SkillEntry] = {}
    for path in SKILL_PATHS:
        group = path.removeprefix("$.skills.")
        values = skills.get(group) if isinstance(skills, Mapping) else None
        if not isinstance(values, list):
            raise ConfigError(f"résumé field {path} is missing or not an array")
        for index, value in enumerate(values):
            if not isinstance(value, str) or not value:
                raise ConfigError(f"résumé field {path}[{index}] is not a string")
            entries.setdefault(value, SkillEntry(value, f"{path}[{index}]"))
    return tuple(entries.values())


def searchable_fields(posting: Posting) -> tuple[tuple[str, str], ...]:
    """Returns ``(posting_path, cleaned_text)`` for every skill-search field.

    Order is ``$.title``, ``$.content``, then ``$.departments[i].name`` (A29). Empty
    fields are skipped, so a path is only ever cited when its raw value is a
    non-empty string.

    Args:
        posting: The normalised posting.

    Returns:
        The fields in citation order.
    """
    fields = [("$.title", posting.title), ("$.content", posting.content_raw)]
    fields += [
        (f"$.departments[{i}].name", name)
        for i, name in enumerate(posting.department_names)
    ]
    return tuple((path, clean_html(raw)) for path, raw in fields if raw)


def match_skills(posting: Posting, skills: Sequence[SkillEntry]) -> list[SkillEvidence]:
    """Finds every distinct eligible skill in the posting (§6.2).

    Args:
        posting: The normalised posting.
        skills: The countable résumé skills, from ``skill_entries_from_resume``.

    Returns:
        One evidence entry per distinct matched term, in ``skills`` order, each
        citing the first field that contains it.
    """
    fields = searchable_fields(posting)
    evidence: list[SkillEvidence] = []
    seen: set[str] = set()
    for skill in skills:
        if skill.term in seen:
            continue
        for path, cleaned in fields:
            if term_in_text(skill.term, cleaned):
                evidence.append(
                    SkillEvidence(
                        term=skill.term,
                        resume_path=skill.resume_path,
                        posting_path=path,
                    )
                )
                seen.add(skill.term)
                break
    return evidence
