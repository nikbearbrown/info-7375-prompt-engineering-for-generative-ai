"""Maps a ``--rule-impl`` name to the rule implementation under test."""

from __future__ import annotations

import importlib
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from job_search_agent.models import Posting, RuleVerdict, VerifiedResume

Evaluate = Callable[[Posting, VerifiedResume], RuleVerdict]
Validate = Callable[
    [RuleVerdict | Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]],
    list[str],
]

_MODULES: Mapping[str, tuple[str, str]] = {
    "real": ("job_search_agent.rule.verdict", "job_search_agent.evidence_validator"),
    "wrong_a": ("tests.wrong_versions.title_only", "tests.wrong_versions.title_only"),
    "wrong_b": (
        "tests.wrong_versions.substring_count",
        "tests.wrong_versions.substring_count",
    ),
}


@dataclass(frozen=True)
class RuleImpl:
    """One implementation's ``evaluate`` and ``validate_rule_evidence``."""

    name: str
    evaluate: Evaluate
    validate_rule_evidence: Validate


def load_impl(name: str) -> RuleImpl:
    """Imports the named implementation (``real``, ``wrong_a`` or ``wrong_b``)."""
    evaluate_module, validator_module = _MODULES[name]
    evaluate: Evaluate = importlib.import_module(evaluate_module).evaluate
    validate: Validate = importlib.import_module(
        validator_module
    ).validate_rule_evidence
    return RuleImpl(name, evaluate, validate)
