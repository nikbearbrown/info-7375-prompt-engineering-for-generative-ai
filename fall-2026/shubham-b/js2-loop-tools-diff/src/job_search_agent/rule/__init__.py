"""The deterministic CONTRACT §6 rule: pure functions, no I/O.

``evaluate`` applies all four gates to one posting; the gate modules are
``title`` (§6.1), ``skills`` (§6.2), ``exclusions`` (§6.3) and ``location`` (§6.4).
"""

from __future__ import annotations

from job_search_agent.rule.exclusions import find_exclusions
from job_search_agent.rule.location import classify_location
from job_search_agent.rule.skills import match_skills, skill_entries_from_resume
from job_search_agent.rule.title import title_check
from job_search_agent.rule.verdict import (
    RuleInputs,
    evaluate,
    evaluate_with,
    rule_inputs,
)

__all__ = [
    "RuleInputs",
    "classify_location",
    "evaluate",
    "evaluate_with",
    "find_exclusions",
    "match_skills",
    "rule_inputs",
    "skill_entries_from_resume",
    "title_check",
]
