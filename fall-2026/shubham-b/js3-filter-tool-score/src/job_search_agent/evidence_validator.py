"""CONTRACT §7 rule-evidence validator.

It re-checks a rule verdict against the actual input objects instead of trusting the
rule that produced it:

* **Shape.** A mapping (e.g. a record read back from disk) must validate as a
  ``RuleVerdict``: every evidence entry has exactly ``term``, ``resume_path`` and
  ``posting_path``, and ``location_check`` has at least one path.
* **Skill evidence.** Each ``resume_path`` is an element of one of the seven §4 skill
  arrays, exists in the résumé and holds exactly ``term``. Each ``posting_path`` is
  ``$.title``, ``$.content`` or ``$.departments[i].name``, exists in the raw posting,
  is a string, and its ``text.clean_html`` cleanup supports ``term`` under the §6.2
  matching rules. No term appears twice.
* **Location evidence.** Every ``location_check.evidence`` path is ``$.location.name``,
  ``$.content`` or ``$.id`` and exists in the raw posting.
* **Consistency.** ``MATCH`` needs ``US_BASED`` and no failed gate; ``NO_MATCH``
  needs at least one; ``failed_gates`` is unique and in contract order; ``SKILLS`` is
  recorded exactly when fewer than two skills are cited and ``LOCATION`` exactly when
  the label is not ``US_BASED``.

Error strings name the field and the problem only; they never echo posting text.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, Final

from pydantic import ValidationError

from job_search_agent import jsonpath
from job_search_agent.models import (
    Gate,
    LocationLabel,
    RuleVerdict,
    SkillEvidence,
    VerdictLabel,
)
from job_search_agent.rule.skills import (
    MIN_DISTINCT_SKILLS,
    SKILL_PATHS,
    term_in_text,
)
from job_search_agent.text import clean_html

_SKILL_PATH: Final = re.compile(
    "(?:" + "|".join(re.escape(p) for p in SKILL_PATHS) + r")\[(?:0|[1-9][0-9]*)\]"
)
_POSTING_PATH: Final = re.compile(
    r"\$\.title|\$\.content|\$\.departments\[(?:0|[1-9][0-9]*)\]\.name"
)
_LOCATION_PATHS: Final = frozenset({"$.location.name", "$.content", "$.id"})
"""Paths a location check may cite. ``$.id`` is allowed only for reading A30: when a
posting has neither ``$.location.name`` nor ``$.content``, the evidence must still be
a real path, so it cites ``$.id`` (which holds no location or content; the provider's
``MISSING_LOCATION`` data-quality issue records that)."""


def _resolve(document: Mapping[str, Any], path: str) -> tuple[bool, Any]:
    """Resolves a path, returning ``(found, value)``."""
    try:
        return True, jsonpath.resolve(document, path)
    except (jsonpath.JsonPathSyntaxError, jsonpath.PathNotFoundError):
        return False, None


def _resume_path_errors(
    entry: SkillEvidence, resume_data: Mapping[str, Any], where: str
) -> list[str]:
    """Checks that the résumé path is an eligible skill holding exactly the term."""
    if not _SKILL_PATH.fullmatch(entry.resume_path):
        return [f"{where}.resume_path: not an element of a §4 skill array"]
    found, value = _resolve(resume_data, entry.resume_path)
    if not found:
        return [f"{where}.resume_path: path does not exist in the résumé"]
    if value != entry.term:
        return [f"{where}.resume_path: value is not the term"]
    return []


def _posting_path_errors(
    entry: SkillEvidence, raw_posting: Mapping[str, Any], where: str
) -> list[str]:
    """Checks that the posting path is a searched field whose text supports the term."""
    if not _POSTING_PATH.fullmatch(entry.posting_path):
        return [f"{where}.posting_path: not a title, content or department name path"]
    found, value = _resolve(raw_posting, entry.posting_path)
    if not found:
        return [f"{where}.posting_path: path does not exist in the posting"]
    if not isinstance(value, str):
        return [f"{where}.posting_path: value is not a string"]
    if not term_in_text(entry.term, clean_html(value)):
        return [f"{where}.posting_path: term not found in the field"]
    return []


def _skill_errors(
    evidence: Sequence[SkillEvidence],
    raw_posting: Mapping[str, Any],
    resume_data: Mapping[str, Any],
) -> list[str]:
    """Checks every skill evidence entry and term uniqueness."""
    errors: list[str] = []
    first_index: dict[str, int] = {}
    for i, entry in enumerate(evidence):
        where = f"evidence[{i}]"
        if entry.term in first_index:
            errors.append(
                f"{where}.term: duplicate of evidence[{first_index[entry.term]}]"
            )
        first_index.setdefault(entry.term, i)
        errors += _resume_path_errors(entry, resume_data, where)
        errors += _posting_path_errors(entry, raw_posting, where)
    return errors


def _location_errors(verdict: RuleVerdict, raw_posting: Mapping[str, Any]) -> list[str]:
    """Checks that every location evidence path is allowed and exists."""
    errors: list[str] = []
    for i, path in enumerate(verdict.location_check.evidence):
        where = f"location_check.evidence[{i}]"
        if path not in _LOCATION_PATHS:
            errors.append(f"{where}: not a location, content or id path")
        elif not _resolve(raw_posting, path)[0]:
            errors.append(f"{where}: path does not exist in the posting")
    return errors


def _consistency_errors(verdict: RuleVerdict) -> list[str]:
    """Checks label, failed gates, skill count and location label agree."""
    errors: list[str] = []
    gates = verdict.failed_gates
    us_based = verdict.location_check.label is LocationLabel.US_BASED
    if verdict.label is VerdictLabel.MATCH:
        if not us_based:
            errors.append("label: MATCH requires location_check.label US_BASED")
        if gates:
            errors.append("label: MATCH requires no failed gate")
    elif not gates:
        errors.append("label: NO_MATCH requires at least one failed gate")
    if gates != [gate for gate in Gate if gate in gates]:
        errors.append("failed_gates: not unique and in contract order")
    few_skills = len(verdict.evidence) < MIN_DISTINCT_SKILLS
    if few_skills and Gate.SKILLS not in gates:
        errors.append("failed_gates: SKILLS must be recorded below 2 distinct skills")
    if not few_skills and Gate.SKILLS in gates:
        errors.append("failed_gates: SKILLS recorded with 2 or more distinct skills")
    if not us_based and Gate.LOCATION not in gates:
        errors.append("failed_gates: LOCATION must be recorded unless US_BASED")
    if us_based and Gate.LOCATION in gates:
        errors.append("failed_gates: LOCATION recorded although US_BASED")
    return errors


def _shape_errors(exc: ValidationError) -> list[str]:
    """Formats pydantic errors as ``shape:`` lines without echoing input values."""
    return [
        f"shape: {'.'.join(str(p) for p in err['loc']) or '<root>'}: {err['type']}"
        for err in exc.errors()
    ]


def validate_rule_evidence(
    verdict: RuleVerdict | Mapping[str, Any],
    raw_posting: Mapping[str, Any],
    resume_data: Mapping[str, Any],
) -> list[str]:
    """Validates a rule verdict against the raw posting and the résumé (§7).

    Args:
        verdict: A verdict, or its JSON form (e.g. read back from a record).
        raw_posting: The posting object exactly as in the raw response; posting
            paths are relative to it.
        resume_data: The parsed résumé JSON.

    Returns:
        Every problem found, as short ``field: problem`` strings; empty means valid.
        A shape problem is reported alone, because the other checks need the shape.
    """
    if not isinstance(verdict, RuleVerdict):
        try:
            verdict = RuleVerdict.model_validate(verdict)
        except ValidationError as exc:
            return _shape_errors(exc)
    return [
        *_skill_errors(verdict.evidence, raw_posting, resume_data),
        *_location_errors(verdict, raw_posting),
        *_consistency_errors(verdict),
    ]
