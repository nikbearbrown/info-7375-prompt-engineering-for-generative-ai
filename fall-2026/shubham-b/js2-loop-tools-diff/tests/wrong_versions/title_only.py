"""Wrong implementation A (CONTRACT §14): title-only matching.

It returns ``MATCH`` whenever the title passes the real §6.1 check. To look
plausible it still emits the real skill evidence and the real location check, but
it ignores the skill threshold, the exclusion phrases and the location label. Its
evidence validator is the real one; the bug is in ``evaluate`` alone.
"""

from __future__ import annotations

from job_search_agent.evidence_validator import validate_rule_evidence
from job_search_agent.models import (
    Gate,
    Posting,
    RuleVerdict,
    VerdictLabel,
    VerifiedResume,
)
from job_search_agent.rule.title import title_check
from job_search_agent.rule.verdict import evaluate as real_evaluate
from job_search_agent.rule.verdict import rule_inputs


def evaluate(posting: Posting, resume: VerifiedResume) -> RuleVerdict:
    """Labels a posting from its title alone (wrong on purpose)."""
    real = real_evaluate(posting, resume)
    title = title_check(posting.title, rule_inputs(resume.to_dict()).roles)
    if title.passed:
        return RuleVerdict(
            label=VerdictLabel.MATCH,
            location_check=real.location_check,
            evidence=real.evidence,
            reason="The title looks like a software engineering role.",
            failed_gates=[],
        )
    return RuleVerdict(
        label=VerdictLabel.NO_MATCH,
        location_check=real.location_check,
        evidence=real.evidence,
        reason=title.reason,
        failed_gates=[Gate.TITLE],
    )


__all__ = ["evaluate", "validate_rule_evidence"]
