"""CONTRACT §14 contract suite, run against ``--rule-impl`` (``real`` by default).

Only behaviour the contract states is tested here, through the two functions every
implementation exposes. Postings are constructed unless the test name says
``handcheck`` (the committed 2026-10-29 response).
"""

from __future__ import annotations

from typing import Any

import pytest

from job_search_agent.models import (
    Gate,
    LocationCheck,
    LocationLabel,
    Posting,
    RuleVerdict,
    SkillEvidence,
    VerdictLabel,
)
from tests.contract.impls import RuleImpl
from tests.tools.builders import (
    fixture_resume,
    fixture_resume_data,
    handcheck_posting,
    posting,
)

HANDCHECK = {
    "8249901": (VerdictLabel.MATCH, {"Java", "Python", "AWS"}),
    "7543868": (VerdictLabel.NO_MATCH, {"GraphQL", "AWS", "Docker", "Kubernetes"}),
    "8175099": (VerdictLabel.NO_MATCH, {"Java", "AWS", "GCP", "Kubernetes"}),
    "8127182": (VerdictLabel.NO_MATCH, {"Java"}),
    "8234357": (VerdictLabel.NO_MATCH, {"TypeScript", "React", "HTML", "CSS"}),
}


def _evaluate(impl: RuleImpl, item: Posting) -> RuleVerdict:
    return impl.evaluate(item, fixture_resume())


def _terms(verdict: RuleVerdict) -> list[str]:
    return [e.term for e in verdict.evidence]


def _check(
    impl: RuleImpl, verdict: RuleVerdict | dict[str, Any], item: Posting
) -> list[str]:
    """Runs the implementation's validator; only the error list reaches asserts."""
    return impl.validate_rule_evidence(verdict, item.raw, fixture_resume_data())


def _hand_built_match(item: Posting, *entries: tuple[str, str]) -> RuleVerdict:
    """A correct MATCH verdict written by hand, independent of any implementation."""
    return RuleVerdict(
        label=VerdictLabel.MATCH,
        location_check=LocationCheck(
            label=LocationLabel.US_BASED,
            evidence=["$.location.name"],
            reason="Seattle, WA is a US location.",
        ),
        evidence=[
            SkillEvidence(term=term, resume_path=path, posting_path="$.content")
            for term, path in entries
        ],
        reason="All four gates pass.",
        failed_gates=[],
    )


# --- wrong implementation A: the other three gates still apply ----------------


def test_contract_case4_one_skill_is_no_match(impl: RuleImpl) -> None:
    verdict = _evaluate(impl, handcheck_posting("8127182"))
    assert verdict.label is VerdictLabel.NO_MATCH
    assert Gate.SKILLS in verdict.failed_gates


def test_contract_case2_non_us_is_no_match(impl: RuleImpl) -> None:
    verdict = _evaluate(impl, handcheck_posting("7543868"))
    assert verdict.label is VerdictLabel.NO_MATCH
    assert verdict.location_check.label is LocationLabel.NON_US


def test_contract_na_location_is_no_match(impl: RuleImpl) -> None:
    verdict = _evaluate(impl, handcheck_posting("8234357"))
    assert verdict.label is VerdictLabel.NO_MATCH
    assert verdict.location_check.label is LocationLabel.NOT_ESTABLISHED


def test_contract_zero_skill_eligible_title_is_no_match(impl: RuleImpl) -> None:
    item = posting(content="We build payments infrastructure for the internet.")
    verdict = _evaluate(impl, item)
    assert verdict.label is VerdictLabel.NO_MATCH
    assert verdict.evidence == []


def test_contract_exclusion_phrase_is_no_match(impl: RuleImpl) -> None:
    item = posting(content="Java and Python. Must be a U.S. citizen.")
    verdict = _evaluate(impl, item)
    assert verdict.label is VerdictLabel.NO_MATCH
    assert Gate.EXCLUSION in verdict.failed_gates


# --- wrong implementation B: special cases, distinct counting, validator ------


def test_contract_csharp_vs_plain_c(impl: RuleImpl) -> None:
    plain = _evaluate(impl, posting(content="C and C++ experience, plus Python."))
    assert "C#" not in _terms(plain)
    exact = _evaluate(impl, posting(content="C# and Python services."))
    assert "C#" in _terms(exact)


def test_contract_rest_of_the_team_not_rest(impl: RuleImpl) -> None:
    verdict = _evaluate(impl, posting(content="Work with the rest of the team."))
    assert "REST" not in _terms(verdict)
    assert _terms(_evaluate(impl, posting(content="Design a REST API."))) == ["REST"]


def test_contract_repeated_mentions_count_once(impl: RuleImpl) -> None:
    two = _evaluate(impl, posting(content="Java, more Java, Java again; Python."))
    assert sorted(_terms(two)) == ["Java", "Python"]
    assert two.label is VerdictLabel.MATCH
    one = _evaluate(impl, posting(content="Java, more Java, and Java again."))
    assert _terms(one) == ["Java"]
    assert one.label is VerdictLabel.NO_MATCH


def test_contract_missing_evidence_path_rejected(impl: RuleImpl) -> None:
    item = posting(content="Java and Python")
    good = _hand_built_match(
        item, ("Java", "$.skills.languages[2]"), ("Python", "$.skills.languages[3]")
    )
    assert _check(impl, good, item) == []
    broken = good.model_dump(mode="json")
    broken["evidence"][0]["posting_path"] = "$.salary"
    assert _check(impl, broken, item) != []
    no_resume_key = good.model_dump(mode="json")
    no_resume_key["evidence"][1]["resume_path"] = "$.skills.go_lang[0]"
    assert _check(impl, no_resume_key, item) != []


def test_contract_wrong_resume_path_rejected(impl: RuleImpl) -> None:
    """GraphQL cited as ``$.skills.backend[3]``, whose value is REST."""
    item = posting(content="GraphQL and Java")
    good = _hand_built_match(
        item, ("GraphQL", "$.skills.backend[4]"), ("Java", "$.skills.languages[2]")
    )
    assert _check(impl, good, item) == []
    wrong = _hand_built_match(
        item, ("GraphQL", "$.skills.backend[3]"), ("Java", "$.skills.languages[2]")
    )
    assert _check(impl, wrong, item) != []


# --- §13 ----------------------------------------------------------------------


@pytest.mark.parametrize("posting_id", sorted(HANDCHECK))
def test_contract_handcheck_verdicts(impl: RuleImpl, posting_id: str) -> None:
    label, terms = HANDCHECK[posting_id]
    verdict = _evaluate(impl, handcheck_posting(posting_id))
    assert verdict.label is label
    assert sorted(_terms(verdict)) == sorted(terms)
