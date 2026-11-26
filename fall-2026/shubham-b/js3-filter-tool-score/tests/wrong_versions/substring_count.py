"""Wrong implementation B (CONTRACT §14): raw substring counting.

Skills: after HTML cleanup it lowercases the text and the skill names and strips
punctuation from both (``C#`` becomes ``c``, ``Node.js`` becomes ``nodejs``), then
counts ``text.count(skill)`` with no word boundaries and no special cases. It emits
one evidence entry per occurrence and counts occurrences toward the threshold. The
title, exclusion and location gates are the real ones.

Validator: it only checks that cited paths resolve, with a naive resolver, and it
treats a ``KeyError`` (a missing key) as valid; it never checks that the cited
value supports the term.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from job_search_agent.models import (
    Gate,
    LocationLabel,
    Posting,
    RuleVerdict,
    SkillEvidence,
    VerdictLabel,
    VerifiedResume,
)
from job_search_agent.rule.exclusions import find_exclusions
from job_search_agent.rule.location import classify_location
from job_search_agent.rule.skills import searchable_fields
from job_search_agent.rule.title import title_check
from job_search_agent.rule.verdict import rule_inputs
from job_search_agent.text import clean_html

_PUNCTUATION = re.compile(r"[^\w\s]")


def _strip(text: str) -> str:
    return _PUNCTUATION.sub("", text.lower())


def _count_skills(posting: Posting, resume: VerifiedResume) -> list[SkillEvidence]:
    evidence: list[SkillEvidence] = []
    fields = searchable_fields(posting)
    for skill in rule_inputs(resume.to_dict()).skills:
        needle = _strip(skill.term)
        for path, cleaned in fields:
            occurrences = _strip(cleaned).count(needle)
            evidence += [
                SkillEvidence(
                    term=skill.term, resume_path=skill.resume_path, posting_path=path
                )
            ] * occurrences
    return evidence


def evaluate(posting: Posting, resume: VerifiedResume) -> RuleVerdict:
    """Applies the rule with substring skill counting (wrong on purpose)."""
    roles = rule_inputs(resume.to_dict()).roles
    title = title_check(posting.title, roles)
    evidence = _count_skills(posting, resume)
    exclusions = find_exclusions(posting)
    location = classify_location(posting.location_name, clean_html(posting.content_raw))
    passed = {
        Gate.TITLE: title.passed,
        Gate.SKILLS: len(evidence) >= 2,
        Gate.EXCLUSION: not exclusions,
        Gate.LOCATION: location.label is LocationLabel.US_BASED,
    }
    failed = [gate for gate in Gate if not passed[gate]]
    return RuleVerdict(
        label=VerdictLabel.NO_MATCH if failed else VerdictLabel.MATCH,
        location_check=location,
        evidence=evidence,
        reason=f"{len(evidence)} skill mention(s) counted.",
        failed_gates=failed,
    )


def _naive_resolve(document: Any, path: str) -> Any:  # noqa: ANN401
    node = document
    for part in re.findall(r"\.(\w+)|\[(\d+)\]", path):
        key, index = part
        node = node[key] if key else node[int(index)]
    return node


def validate_rule_evidence(
    verdict: RuleVerdict | Mapping[str, Any],
    raw_posting: Mapping[str, Any],
    resume_data: Mapping[str, Any],
) -> list[str]:
    """Checks only that paths resolve; a missing key passes (wrong on purpose)."""
    parsed = (
        verdict
        if isinstance(verdict, RuleVerdict)
        else RuleVerdict.model_validate(verdict)
    )
    errors: list[str] = []
    for i, entry in enumerate(parsed.evidence):
        for document, path in (
            (resume_data, entry.resume_path),
            (raw_posting, entry.posting_path),
        ):
            try:
                _naive_resolve(document, path)
            except KeyError:
                continue
            except (IndexError, TypeError):
                errors.append(f"evidence[{i}]: {path} does not resolve")
    return errors
