"""§6.5 final verdict: MATCH if and only if all four gates pass.

Every failed gate is recorded in ``Gate`` order, and a ``NO_MATCH`` still lists all
matched skill evidence (§7). There is no sponsorship gate: the rule never guesses
whether an employer sponsors a visa (§6.5).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from job_search_agent.errors import ConfigError
from job_search_agent.models import (
    Gate,
    LocationCheck,
    LocationLabel,
    Posting,
    RuleVerdict,
    SkillEntry,
    SkillEvidence,
    TitleCheck,
    VerdictLabel,
    VerifiedResume,
)
from job_search_agent.rule.exclusions import find_exclusions
from job_search_agent.rule.location import CONTENT_PATH, classify_location
from job_search_agent.rule.skills import (
    MIN_DISTINCT_SKILLS,
    match_skills,
    skill_entries_from_resume,
)
from job_search_agent.rule.title import title_check, validate_roles
from job_search_agent.text import clean_html


@dataclass(frozen=True, slots=True)
class RuleInputs:
    """The résumé values the rule reads (§4), and nothing else.

    Attributes:
        roles: ``$.target.roles[*]``, in résumé order.
        skills: The countable skills of the seven §4 skill paths.
    """

    roles: tuple[str, ...]
    skills: tuple[SkillEntry, ...]


def rule_inputs(resume_data: Mapping[str, Any]) -> RuleInputs:
    """Extracts the rule's inputs from parsed résumé JSON.

    Args:
        resume_data: The parsed résumé (e.g. ``VerifiedResume.to_dict()``).

    Returns:
        The roles and countable skills.

    Raises:
        ConfigError: If ``$.target.roles`` is not an array of strings, names a role
            with no documented alias entry, or a §4 skill path is malformed.
    """
    target = resume_data.get("target")
    roles = target.get("roles") if isinstance(target, Mapping) else None
    if not isinstance(roles, list) or not all(isinstance(r, str) for r in roles):
        raise ConfigError("résumé field $.target.roles is not an array of strings")
    validate_roles(roles)
    return RuleInputs(tuple(roles), skill_entries_from_resume(resume_data))


def _failed_gates(
    title: TitleCheck,
    evidence: Sequence[SkillEvidence],
    exclusions: Sequence[str],
    location: LocationCheck,
) -> list[Gate]:
    """Lists every failed §6.5 condition in ``Gate`` order."""
    passed = {
        Gate.TITLE: title.passed,
        Gate.SKILLS: len(evidence) >= MIN_DISTINCT_SKILLS,
        Gate.EXCLUSION: not exclusions,
        Gate.LOCATION: location.label is LocationLabel.US_BASED,
    }
    return [gate for gate in Gate if not passed[gate]]


def _reason(
    failed: Sequence[Gate],
    title: TitleCheck,
    evidence: Sequence[SkillEvidence],
    exclusions: Sequence[str],
    location: LocationCheck,
) -> str:
    """Explains the verdict, naming every failed gate."""
    if not failed:
        return (
            f"The title passes the role check, {len(evidence)} distinct résumé "
            "skills appear in the posting, no exclusion phrase appears, and the "
            "location is US-based."
        )
    explanations = {
        Gate.TITLE: title.reason,
        Gate.SKILLS: (
            f"{len(evidence)} distinct résumé skill(s) appear in the posting; at "
            f"least {MIN_DISTINCT_SKILLS} are required."
        ),
        Gate.EXCLUSION: (
            f"The posting contains exclusion phrase(s): {', '.join(exclusions)}."
        ),
        Gate.LOCATION: f"Location {location.label.value}: {location.reason}",
    }
    names = ", ".join(gate.value for gate in failed)
    details = " ".join(explanations[gate] for gate in failed)
    return f"Failed gate(s): {names}. {details}"


def evaluate_with(posting: Posting, inputs: RuleInputs) -> RuleVerdict:
    """Applies the §6 rule to one posting, given the extracted résumé inputs.

    Args:
        posting: The normalised posting.
        inputs: From ``rule_inputs``.

    Returns:
        The verdict, with skill evidence, the location check and every failed gate.

    Raises:
        ConfigError: If a role has no documented alias entry.
    """
    title = title_check(posting.title, inputs.roles)
    evidence = match_skills(posting, inputs.skills)
    exclusions = find_exclusions(posting)
    # A30: the location evidence must be a real path. With neither $.location.name
    # nor $.content, $.id is the only one left; it carries no location or content,
    # and the provider's MISSING_LOCATION issue says so.
    fallback = CONTENT_PATH if "content" in posting.raw else "$.id"
    location = classify_location(
        posting.location_name,
        clean_html(posting.content_raw),
        fallback_path=fallback,
    )
    failed = _failed_gates(title, evidence, exclusions, location)
    return RuleVerdict(
        label=VerdictLabel.NO_MATCH if failed else VerdictLabel.MATCH,
        location_check=location,
        evidence=evidence,
        reason=_reason(failed, title, evidence, exclusions, location),
        failed_gates=failed,
    )


def evaluate(posting: Posting, resume: VerifiedResume) -> RuleVerdict:
    """Applies the §6 rule to one posting.

    Only the §4 résumé fields are read; names, contacts, schools, employers and
    dates never influence the verdict.

    Args:
        posting: The normalised posting.
        resume: The verified résumé.

    Returns:
        The verdict.

    Raises:
        ConfigError: If the résumé's roles or skill arrays are unusable.
    """
    return evaluate_with(posting, rule_inputs(resume.to_dict()))
