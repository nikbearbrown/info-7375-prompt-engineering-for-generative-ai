"""Greenhouse provider: URL, shape validation, ID canonicalisation, data quality.

Every board below except the committed hand-check file is **constructed** in memory.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from job_search_agent.errors import ConfigError, InvalidResponse
from job_search_agent.models import DataQualityCode, ParsedBoard, Severity
from job_search_agent.providers import get_provider
from job_search_agent.providers.greenhouse import GreenhouseProvider
from tests.conftest import REPO_ROOT, RawHandcheck


def _job(**fields: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": 1,
        "title": "Software Engineer",
        "location": {"name": "Seattle, WA"},
        "updated_at": "2026-10-29T10:42:09-04:00",
        "content": "&lt;p&gt;Java&lt;/p&gt;",
        "departments": [{"name": "Engineering"}],
    }
    base.update(fields)
    return base


def _board(jobs: list[Any], total: int | None = None) -> bytes:
    meta_total = len(jobs) if total is None else total
    return json.dumps({"jobs": jobs, "meta": {"total": meta_total}}).encode()


def _parse(body: bytes) -> ParsedBoard:
    return GreenhouseProvider().parse(body)


def _codes(board: ParsedBoard) -> list[DataQualityCode]:
    return [issue.code for issue in board.data_quality]


def test_parse_handcheck_raw_734(raw_handcheck: RawHandcheck) -> None:
    board = _parse(raw_handcheck.body)
    expected = len(raw_handcheck.data["jobs"])
    assert board.fetched_count == expected
    assert board.meta_total == raw_handcheck.data["meta"]["total"]
    assert len(board.postings) == expected
    assert board.data_quality == ()
    assert [p.index for p in board.postings] == list(range(expected))
    case1 = board.postings[566]
    assert case1.posting_id == "8249901"
    assert case1.title == "Software Engineer"
    assert case1.location_name == "Seattle, WA"
    assert case1.department_names == ("Global Operations",)
    assert case1.raw == raw_handcheck.data["jobs"][566]


def test_ids_canonicalised_to_decimal_strings() -> None:
    board = _parse(_board([_job(id=42), _job(id=8249901)]))
    assert board.valid_ids == ("42", "8249901")


def test_missing_id_reported_not_invented() -> None:
    job = _job()
    del job["id"]
    board = _parse(_board([job, _job(id=7)]))
    assert board.valid_ids == ("7",)
    (issue,) = board.data_quality
    assert issue.code is DataQualityCode.MISSING_ID
    assert issue.severity is Severity.ERROR
    assert issue.index == 0
    assert issue.posting_id is None


@pytest.mark.parametrize("bad_id", [True, False])
def test_bool_id_invalid(bad_id: bool) -> None:
    board = _parse(_board([_job(id=bad_id), _job(id=7)]))
    assert board.valid_ids == ("7",)
    assert _codes(board) == [DataQualityCode.INVALID_ID]
    assert board.data_quality[0].posting_id is None


@pytest.mark.parametrize("bad_id", ["8249901", "abc", 1.5, 0, -3, None, [1]])
def test_string_id_invalid(bad_id: Any) -> None:
    """A31: only a positive JSON integer is a valid ID; strings are rejected too."""
    board = _parse(_board([_job(id=bad_id), _job(id=7)]))
    assert board.valid_ids == ("7",)
    assert _codes(board) == [DataQualityCode.INVALID_ID]
    assert board.data_quality[0].severity is Severity.ERROR


def test_duplicate_id_reported() -> None:
    board = _parse(_board([_job(id=5, title="A"), _job(id=5, title="B")]))
    assert board.valid_ids == ("5",)
    assert board.postings[0].title == "A"
    (issue,) = board.data_quality
    assert issue.code is DataQualityCode.DUPLICATE_ID
    assert issue.severity is Severity.ERROR
    assert issue.index == 1
    assert issue.posting_id == "5"


def test_non_object_job_reported() -> None:
    board = _parse(_board(["not a job", _job(id=7)]))
    assert board.valid_ids == ("7",)
    assert _codes(board) == [DataQualityCode.NOT_AN_OBJECT]
    assert board.fetched_count == 2


def test_missing_optional_fields_become_empty() -> None:
    board = _parse(_board([{"id": 9}]))
    (posting,) = board.postings
    assert posting.title == ""
    assert posting.location_name is None
    assert posting.updated_at is None
    assert posting.content_raw == ""
    assert posting.department_names == ()
    assert _codes(board) == [DataQualityCode.MISSING_LOCATION]
    assert board.data_quality[0].severity is Severity.WARNING
    assert board.data_quality[0].posting_id == "9"


def test_wrong_field_types_become_empty_with_warnings() -> None:
    job = _job(
        title=3,
        location={"name": None},
        updated_at=5,
        content=["x"],
        departments=[{"name": 1}, {"name": "Payments"}],
    )
    board = _parse(_board([job]))
    (posting,) = board.postings
    assert posting.title == ""
    assert posting.location_name is None
    assert posting.updated_at is None
    assert posting.content_raw == ""
    assert posting.department_names == ("", "Payments")
    codes = _codes(board)
    assert codes.count(DataQualityCode.WRONG_FIELD_TYPE) == 5
    assert all(i.severity is Severity.WARNING for i in board.data_quality)


def test_null_updated_at_is_not_a_data_quality_issue() -> None:
    board = _parse(_board([_job(updated_at=None)]))
    assert board.postings[0].updated_at is None
    assert board.data_quality == ()


def test_total_mismatch_is_warning_only() -> None:
    board = _parse(_board([_job(id=1), _job(id=2)], total=5))
    assert board.valid_ids == ("1", "2")
    assert board.meta_total == 5
    assert _codes(board) == [DataQualityCode.TOTAL_MISMATCH]
    assert board.data_quality[0].severity is Severity.WARNING


@pytest.mark.parametrize(
    "body",
    [b"", b"not json", b"\xff\xfe", b'{"jobs": [], "meta": {"total": NaN}}'],
)
def test_not_json_invalid(body: bytes) -> None:
    with pytest.raises(InvalidResponse) as info:
        _parse(body)
    assert info.value.code == "not_json"


def test_top_level_array_invalid() -> None:
    with pytest.raises(InvalidResponse) as info:
        _parse(b"[]")
    assert info.value.code == "not_object"


@pytest.mark.parametrize("jobs", [None, {}, "jobs", 3])
def test_jobs_not_list_invalid(jobs: Any) -> None:
    body = json.dumps({"jobs": jobs, "meta": {"total": 0}}).encode()
    with pytest.raises(InvalidResponse) as info:
        _parse(body)
    assert info.value.code == "jobs_not_list"


def test_missing_jobs_key_invalid() -> None:
    with pytest.raises(InvalidResponse) as info:
        _parse(b'{"meta": {"total": 0}}')
    assert info.value.code == "jobs_not_list"


@pytest.mark.parametrize(
    "meta",
    [None, {}, {"total": "3"}, {"total": True}, {"total": 1.0}, [], "meta"],
)
def test_missing_meta_total_invalid(meta: Any) -> None:
    """A21: an integer ``meta.total`` is part of the required shape."""
    body = json.dumps({"jobs": [_job()], "meta": meta}).encode()
    with pytest.raises(InvalidResponse) as info:
        _parse(body)
    assert info.value.code == "meta_total"


def test_missing_meta_key_invalid() -> None:
    body = json.dumps({"jobs": [_job()]}).encode()
    with pytest.raises(InvalidResponse) as info:
        _parse(body)
    assert info.value.code == "meta_total"


def test_empty_jobs_is_empty() -> None:
    board = _parse(_board([]))
    assert board.is_empty
    assert board.postings == ()
    assert board.data_quality == ()


def test_all_ids_invalid_is_invalid_response() -> None:
    with pytest.raises(InvalidResponse) as info:
        _parse(_board([_job(id="1"), {"title": "x"}, "junk"]))
    assert info.value.code == "no_valid_ids"


def test_jobs_url_exact() -> None:
    assert (
        GreenhouseProvider().jobs_url("stripe")
        == "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"
    )


@pytest.mark.parametrize(
    "token", ["", "stripe/../x", "stripe?x=1", "a b", "stripe#", "Stripe@evil"]
)
def test_jobs_url_rejects_unsafe_token(token: str) -> None:
    with pytest.raises(ConfigError):
        GreenhouseProvider().jobs_url(token)


def test_provider_name_and_registry() -> None:
    provider = get_provider("greenhouse")
    assert provider.name == "greenhouse"
    assert isinstance(provider, GreenhouseProvider)


def test_unknown_provider_raises_config_error() -> None:
    with pytest.raises(ConfigError):
        get_provider("lever")


def test_no_count_constant() -> None:
    """§2: the posting count is read from the response, never hard-coded."""
    offenders = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / "src").rglob("*.py")
        if "734" in path.read_text(encoding="utf-8")
    ]
    assert offenders == []


def test_missing_location_and_content_explains_id_evidence() -> None:
    """A30: the rule then cites ``$.id``; the data-quality issue says why."""
    board = _parse(_board([{"id": 9}, {"id": 10, "content": "x"}]))
    no_content, with_content = board.data_quality
    assert no_content.code is with_content.code is DataQualityCode.MISSING_LOCATION
    assert "$.content" in no_content.detail and "$.id" in no_content.detail
    assert with_content.detail == "$.location.name is absent"
