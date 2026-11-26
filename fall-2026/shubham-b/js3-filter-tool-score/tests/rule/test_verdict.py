"""§6.5 verdict: all four gates, every failed gate recorded (constructed postings)."""

from __future__ import annotations

import itertools

import pytest

from job_search_agent.errors import ConfigError
from job_search_agent.models import Gate, LocationLabel, VerdictLabel
from job_search_agent.rule.verdict import evaluate, rule_inputs
from tests.tools.builders import (
    fixture_resume,
    fixture_resume_data,
    handcheck_verdicts,
    job,
    posting,
    posting_from_job,
)

RESUME = fixture_resume()


def _gate_posting(
    *, title_ok: bool, skills_ok: bool, exclusion_ok: bool, location_ok: bool
) -> dict[str, object]:
    content = "Java and Python" if skills_ok else "Java only"
    if not exclusion_ok:
        content += ". This is an unpaid role."
    return {
        "title": "Software Engineer" if title_ok else "Senior Software Engineer",
        "content": content,
        "location": {"name": "Seattle, WA" if location_ok else "London"},
    }


@pytest.mark.parametrize(
    ("title_ok", "skills_ok", "exclusion_ok", "location_ok"),
    list(itertools.product([True, False], repeat=4)),
)
def test_match_requires_all_four_gates(
    title_ok: bool, skills_ok: bool, exclusion_ok: bool, location_ok: bool
) -> None:
    fields = _gate_posting(
        title_ok=title_ok,
        skills_ok=skills_ok,
        exclusion_ok=exclusion_ok,
        location_ok=location_ok,
    )
    verdict = evaluate(posting(**fields), RESUME)
    expected_failed = [
        gate
        for gate, ok in zip(
            Gate, (title_ok, skills_ok, exclusion_ok, location_ok), strict=True
        )
        if not ok
    ]
    assert verdict.failed_gates == expected_failed
    all_ok = title_ok and skills_ok and exclusion_ok and location_ok
    assert (verdict.label is VerdictLabel.MATCH) is all_ok


def test_all_failed_gates_recorded() -> None:
    fields = _gate_posting(
        title_ok=False, skills_ok=False, exclusion_ok=False, location_ok=False
    )
    verdict = evaluate(posting(**fields), RESUME)
    assert verdict.label is VerdictLabel.NO_MATCH
    assert verdict.failed_gates == [
        Gate.TITLE,
        Gate.SKILLS,
        Gate.EXCLUSION,
        Gate.LOCATION,
    ]
    for word in ("senior", "1 distinct", "unpaid role", "London"):
        assert word in verdict.reason


def test_match_reason_states_every_gate() -> None:
    verdict = evaluate(posting(content="Java and Python"), RESUME)
    assert verdict.label is VerdictLabel.MATCH
    assert verdict.failed_gates == []
    assert "US-based" in verdict.reason


def test_match_implies_us_based() -> None:
    """Real data: every MATCH on the committed board has a US_BASED location."""
    verdicts = [verdict for _, verdict in handcheck_verdicts()]
    matches = [v for v in verdicts if v.label is VerdictLabel.MATCH]
    assert matches
    assert all(v.location_check.label is LocationLabel.US_BASED for v in matches)
    assert all(v.failed_gates == [] for v in matches)
    assert all(v.failed_gates for v in verdicts if v.label is VerdictLabel.NO_MATCH)


def test_no_match_still_lists_matched_skills() -> None:
    verdict = evaluate(
        posting(location={"name": "London"}, content="Java, Python, AWS"), RESUME
    )
    assert verdict.label is VerdictLabel.NO_MATCH
    assert [e.term for e in verdict.evidence] == ["Java", "Python", "AWS"]


def test_rule_has_no_sponsorship_gate() -> None:
    assert [g.value for g in Gate] == ["TITLE", "SKILLS", "EXCLUSION", "LOCATION"]
    content = "Java and Python. We do not sponsor work visas for this role."
    assert evaluate(posting(content=content), RESUME).label is VerdictLabel.MATCH


def test_rule_ignores_personal_fields() -> None:
    item = posting(content="Java, Python and React")
    baseline = evaluate(item, RESUME)
    data = fixture_resume_data()
    # The gate only admits the approved persona name; every other personal value
    # (and every section the rule does not read) is changed or emptied.
    data["personal"] = {
        "name": data["personal"]["name"],
        "email": "someone.else@example.com",
        "phone": "555-0199",
    }
    data["education"] = []
    data["experience"] = []
    data["projects"] = []
    data["work_authorization"] = {}
    assert evaluate(item, fixture_resume(data)) == baseline


def test_missing_location_cites_content_or_id() -> None:
    raw = job(content="Java and Python")
    del raw["location"]
    verdict = evaluate(posting_from_job(raw), RESUME)
    assert verdict.location_check.label is LocationLabel.NOT_ESTABLISHED
    assert verdict.location_check.evidence == ["$.content"]
    del raw["content"]
    no_content = evaluate(posting_from_job(raw), RESUME)
    assert no_content.location_check.evidence == ["$.id"]


def test_rescued_location_can_match() -> None:
    item = posting(
        location={"name": "Remote"},
        content="Java and Python. Remote within the United States.",
    )
    verdict = evaluate(item, RESUME)
    assert verdict.label is VerdictLabel.MATCH
    assert verdict.location_check.evidence == ["$.location.name", "$.content"]


def test_rule_inputs_reads_roles_and_skills() -> None:
    inputs = rule_inputs(fixture_resume_data())
    assert inputs.roles == (
        "Software Engineer",
        "Full-Stack Software Engineer",
        "Backend Engineer",
        "Frontend Engineer",
    )
    assert len(inputs.skills) == 29


@pytest.mark.parametrize(
    "roles", [["Software Engineer", "Data Scientist"], "Software Engineer", [3]]
)
def test_bad_roles_raise_config_error(roles: object) -> None:
    data = fixture_resume_data()
    data["target"]["roles"] = roles
    with pytest.raises(ConfigError):
        rule_inputs(data)
