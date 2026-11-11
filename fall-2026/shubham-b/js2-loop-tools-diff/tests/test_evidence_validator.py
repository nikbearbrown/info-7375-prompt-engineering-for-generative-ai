"""§7 rule-evidence validator: paths exist, terms are supported, labels consistent.

The verdicts are produced by the real rule on constructed postings and then edited.
"""

from __future__ import annotations

from typing import Any

import pytest

from job_search_agent.evidence_validator import validate_rule_evidence
from job_search_agent.models import Gate, LocationLabel, RuleVerdict, VerdictLabel
from job_search_agent.rule.verdict import evaluate
from tests.tools.builders import fixture_resume, fixture_resume_data, posting

RESUME_DATA = fixture_resume_data()
POSTING = posting(
    title="Backend Engineer",
    content="&lt;p&gt;GraphQL, Java and AWS&lt;/p&gt;",
    departments=[{"name": "Payments"}, {"name": "Kafka Platform"}],
)
VERDICT = evaluate(POSTING, fixture_resume())


def _edit(**changes: Any) -> dict[str, Any]:
    data = VERDICT.model_dump(mode="json")
    data.update(changes)
    return data


def _with_entry(index: int, **changes: str) -> dict[str, Any]:
    data = VERDICT.model_dump(mode="json")
    data["evidence"][index].update(changes)
    return data


def _errors(verdict: RuleVerdict | dict[str, Any]) -> list[str]:
    return validate_rule_evidence(verdict, POSTING.raw, RESUME_DATA)


def _entry_index(term: str) -> int:
    return [e.term for e in VERDICT.evidence].index(term)


def test_valid_record_passes() -> None:
    assert VERDICT.label is VerdictLabel.MATCH
    assert {e.term for e in VERDICT.evidence} == {"Java", "GraphQL", "AWS", "Kafka"}
    assert _errors(VERDICT) == []
    assert _errors(VERDICT.model_dump(mode="json")) == []


def test_valid_no_match_passes() -> None:
    item = posting(title="Senior Software Engineer", location={"name": "London"})
    verdict = evaluate(item, fixture_resume())
    assert verdict.failed_gates == [Gate.TITLE, Gate.SKILLS, Gate.LOCATION]
    assert validate_rule_evidence(verdict, item.raw, RESUME_DATA) == []


@pytest.mark.parametrize("bad_path", ["$.salary", "$.departments[5].name", "$.x[0]"])
def test_missing_posting_path_rejected(bad_path: str) -> None:
    errors = _errors(_with_entry(0, posting_path=bad_path))
    assert any("evidence[0].posting_path" in e for e in errors)


def test_posting_path_outside_searched_fields_rejected() -> None:
    errors = _errors(_with_entry(0, posting_path="$.location.name"))
    assert any("evidence[0].posting_path" in e for e in errors)


def test_malformed_path_rejected() -> None:
    errors = _errors(_with_entry(0, resume_path="$.skills.languages[*]"))
    assert any("evidence[0].resume_path" in e for e in errors)


def test_nonexistent_resume_path_rejected() -> None:
    errors = _errors(_with_entry(0, resume_path="$.skills.backend[9]"))
    assert any("evidence[0].resume_path" in e for e in errors)


def test_graphql_cited_as_backend_3_rejected() -> None:
    """§14: ``$.skills.backend[3]`` is REST, so it cannot support GraphQL."""
    index = _entry_index("GraphQL")
    errors = _errors(_with_entry(index, resume_path="$.skills.backend[3]"))
    assert errors == [f"evidence[{index}].resume_path: value is not the term"]


def test_familiar_with_not_shipped_path_rejected() -> None:
    index = _entry_index("Java")
    errors = _errors(
        _with_entry(
            index, term="Go", resume_path="$.skills.familiar_with_not_shipped[0]"
        )
    )
    assert any(f"evidence[{index}].resume_path" in e for e in errors)


def test_term_not_supported_by_cited_field_rejected() -> None:
    index = _entry_index("Kafka")
    errors = _errors(_with_entry(index, posting_path="$.content"))
    assert errors == [f"evidence[{index}].posting_path: term not found in the field"]
    wrong_dept = _errors(_with_entry(index, posting_path="$.departments[0].name"))
    assert wrong_dept == [
        f"evidence[{index}].posting_path: term not found in the field"
    ]


def test_term_and_resume_path_both_wrong_reported() -> None:
    index = _entry_index("Java")
    errors = _errors(
        _with_entry(index, term="Python", resume_path="$.skills.languages[3]")
    )
    assert errors == [f"evidence[{index}].posting_path: term not found in the field"]


def test_duplicate_term_entries_rejected() -> None:
    data = VERDICT.model_dump(mode="json")
    data["evidence"].append(dict(data["evidence"][0]))
    errors = _errors(data)
    assert any("duplicate" in e for e in errors)


@pytest.mark.parametrize("change", ["missing", "extra"])
def test_entry_missing_or_extra_key_rejected(change: str) -> None:
    data = VERDICT.model_dump(mode="json")
    if change == "missing":
        del data["evidence"][0]["posting_path"]
    else:
        data["evidence"][0]["note"] = "x"
    errors = _errors(data)
    assert errors
    assert all(e.startswith("shape:") for e in errors)


def test_match_without_us_based_rejected() -> None:
    location = {
        "label": "NOT_ESTABLISHED",
        "evidence": ["$.location.name"],
        "reason": "r",
    }
    errors = _errors(_edit(location_check=location))
    assert "label: MATCH requires location_check.label US_BASED" in errors


def test_location_check_without_valid_path_rejected() -> None:
    for paths in (["$.location.city"], ["$.title"], ["$.content", "$.nope"]):
        location = {"label": "US_BASED", "evidence": paths, "reason": "r"}
        errors = _errors(_edit(location_check=location))
        assert any(e.startswith("location_check.evidence") for e in errors), paths


def test_location_check_with_no_path_rejected() -> None:
    location = {"label": "US_BASED", "evidence": [], "reason": "r"}
    assert all(e.startswith("shape:") for e in _errors(_edit(location_check=location)))


def test_match_with_failed_gates_rejected() -> None:
    errors = _errors(_edit(failed_gates=["TITLE"]))
    assert "label: MATCH requires no failed gate" in errors


def test_no_match_without_failed_gates_rejected() -> None:
    errors = _errors(_edit(label="NO_MATCH"))
    assert "label: NO_MATCH requires at least one failed gate" in errors


def test_skill_gate_must_agree_with_evidence_count() -> None:
    data = _edit(evidence=VERDICT.model_dump(mode="json")["evidence"][:1])
    assert "failed_gates: SKILLS must be recorded below 2 distinct skills" in _errors(
        data
    )
    extra = _edit(label="NO_MATCH", failed_gates=["SKILLS"])
    assert "failed_gates: SKILLS recorded with 2 or more distinct skills" in _errors(
        extra
    )


def test_location_gate_must_agree_with_label() -> None:
    location = {"label": "NON_US", "evidence": ["$.location.name"], "reason": "r"}
    data = _edit(label="NO_MATCH", failed_gates=[], location_check=location)
    errors = _errors(data)
    assert "failed_gates: LOCATION must be recorded unless US_BASED" in errors
    us_failed = _edit(label="NO_MATCH", failed_gates=["LOCATION"])
    assert "failed_gates: LOCATION recorded although US_BASED" in _errors(us_failed)


def test_failed_gates_order_and_uniqueness() -> None:
    data = _edit(label="NO_MATCH", failed_gates=["TITLE", "TITLE"])
    assert "failed_gates: not unique and in contract order" in _errors(data)


def test_errors_do_not_echo_posting_content() -> None:
    errors = _errors(_with_entry(0, posting_path="$.content", term="Rust"))
    assert errors
    assert all("GraphQL, Java" not in e for e in errors)


def test_location_label_values_cover_enum() -> None:
    assert {label.value for label in LocationLabel} == {
        "US_BASED",
        "NON_US",
        "NOT_ESTABLISHED",
    }
