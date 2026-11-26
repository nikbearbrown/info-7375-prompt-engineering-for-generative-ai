"""CONTRACT §13 golden test: the five hand checks on the committed raw response."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import pytest

from job_search_agent import jsonpath
from job_search_agent.evidence_validator import validate_rule_evidence
from job_search_agent.models import Gate, LocationLabel, RuleVerdict, VerdictLabel
from job_search_agent.rule.verdict import evaluate
from tests.conftest import RawHandcheck
from tests.tools.builders import (
    fixture_resume,
    fixture_resume_data,
    handcheck_board,
    handcheck_verdicts,
)

CONTRACT_SHA256_PREFIX = "74e20e05ef226186"
LANG = "$.skills.languages"
FRONT = "$.skills.frontend"
BACK = "$.skills.backend"
CLOUD = "$.skills.cloud_devops"
CONTENT = "$.content"


@dataclass(frozen=True)
class HandCheck:
    index: int
    posting_id: str
    title: str
    location: str
    verdict: VerdictLabel
    evidence: frozenset[tuple[str, str, str]]
    location_label: LocationLabel
    failed_gates: tuple[Gate, ...]


def _ev(*items: tuple[str, str]) -> frozenset[tuple[str, str, str]]:
    return frozenset((term, path, CONTENT) for term, path in items)


CASES = (
    HandCheck(
        566,
        "8249901",
        "Software Engineer",
        "Seattle, WA",
        VerdictLabel.MATCH,
        _ev(("Java", f"{LANG}[2]"), ("Python", f"{LANG}[3]"), ("AWS", f"{CLOUD}[0]")),
        LocationLabel.US_BASED,
        (),
    ),
    HandCheck(
        575,
        "7543868",
        "Software Engineer, Financial Business Insights",
        "Bengaluru, India",
        VerdictLabel.NO_MATCH,
        _ev(
            ("GraphQL", f"{BACK}[4]"),
            ("AWS", f"{CLOUD}[0]"),
            ("Docker", f"{CLOUD}[2]"),
            ("Kubernetes", f"{CLOUD}[3]"),
        ),
        LocationLabel.NON_US,
        (Gate.LOCATION,),
    ),
    HandCheck(
        556,
        "8175099",
        "Senior Software Engineer",
        "South San Francisco, CA",
        VerdictLabel.NO_MATCH,
        _ev(
            ("Java", f"{LANG}[2]"),
            ("AWS", f"{CLOUD}[0]"),
            ("GCP", f"{CLOUD}[1]"),
            ("Kubernetes", f"{CLOUD}[3]"),
        ),
        LocationLabel.US_BASED,
        (Gate.TITLE,),
    ),
    HandCheck(
        604,
        "8127182",
        "Software Engineer, Revenue and Financial Automation",
        "San Francisco, New York City, Seattle, Chicago, US-Remote",
        VerdictLabel.NO_MATCH,
        _ev(("Java", f"{LANG}[2]")),
        LocationLabel.US_BASED,
        (Gate.SKILLS,),
    ),
    HandCheck(
        273,
        "8234357",
        "Full Stack Engineer, Revenue",
        "N/A",
        VerdictLabel.NO_MATCH,
        _ev(
            ("TypeScript", f"{LANG}[0]"),
            ("React", f"{FRONT}[0]"),
            ("HTML", f"{FRONT}[2]"),
            ("CSS", f"{FRONT}[3]"),
        ),
        LocationLabel.NOT_ESTABLISHED,
        (Gate.LOCATION,),
    ),
)
IDS = [f"{c.index}-{c.posting_id}" for c in CASES]


def _verdict(case: HandCheck) -> RuleVerdict:
    return evaluate(handcheck_board().postings[case.index], fixture_resume())


def test_raw_digest_matches_meta_and_contract_prefix(
    raw_handcheck: RawHandcheck,
) -> None:
    digest = hashlib.sha256(raw_handcheck.body).hexdigest()
    assert digest == raw_handcheck.meta["sha256"]
    assert digest.startswith(CONTRACT_SHA256_PREFIX)
    assert raw_handcheck.meta["http_status"] == 200
    assert len(raw_handcheck.body) == raw_handcheck.meta["bytes"]


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_handcheck_index_and_id(case: HandCheck, raw_handcheck: RawHandcheck) -> None:
    raw = raw_handcheck.data["jobs"][case.index]
    assert str(raw["id"]) == case.posting_id
    assert raw["title"] == case.title
    assert raw["location"]["name"] == case.location
    parsed = handcheck_board().postings[case.index]
    assert parsed.index == case.index
    assert parsed.posting_id == case.posting_id


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_posting_paths_relative_to_posting(
    case: HandCheck, raw_handcheck: RawHandcheck
) -> None:
    """§5: record paths resolve against the posting; hand checks add ``$.jobs[i]``."""
    posting_obj = jsonpath.resolve(raw_handcheck.data, f"$.jobs[{case.index}]")
    for entry in _verdict(case).evidence:
        assert jsonpath.exists(posting_obj, entry.posting_path)
        assert not jsonpath.exists(raw_handcheck.data, entry.posting_path)


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_handcheck_verdict(case: HandCheck) -> None:
    assert _verdict(case).label is case.verdict


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_handcheck_skill_evidence_exact(case: HandCheck) -> None:
    evidence = _verdict(case).evidence
    found = {(e.term, e.resume_path, e.posting_path) for e in evidence}
    assert found == case.evidence
    assert len(evidence) == len(case.evidence)


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_handcheck_location_label(case: HandCheck) -> None:
    check = _verdict(case).location_check
    assert check.label is case.location_label
    assert check.evidence == ["$.location.name"]


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_handcheck_failed_gates(case: HandCheck) -> None:
    assert tuple(_verdict(case).failed_gates) == case.failed_gates


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_handcheck_records_pass_evidence_validator(case: HandCheck) -> None:
    raw = handcheck_board().postings[case.index].raw
    assert validate_rule_evidence(_verdict(case), raw, fixture_resume_data()) == []


def test_every_board_verdict_passes_evidence_validator() -> None:
    """All 2026-10-29 postings: the rule's own records always validate."""
    data = fixture_resume_data()
    failures = {
        p.posting_id: errors
        for p, verdict in handcheck_verdicts()
        if (errors := validate_rule_evidence(verdict, p.raw, data))
    }
    assert failures == {}
