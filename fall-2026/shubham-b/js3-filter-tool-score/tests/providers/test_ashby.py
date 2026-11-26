"""Ashby provider: URL, shape, UUID IDs and the GATE §9 field mapping.

Every board here is constructed in memory, in the shape of the real response seen on
2026-11-09 (``{"jobs": [...], "apiVersion": "1"}``).
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from job_search_agent.errors import ConfigError, InvalidResponse
from job_search_agent.models import DataQualityCode
from job_search_agent.providers import get_provider
from job_search_agent.providers.ashby import AshbyProvider

UUID_A = "34413f8d-26bf-4bbc-8ade-eb309a0e2245"
UUID_B = "8fb1615c-34bf-47c4-a1d1-b7b2f836bbd3"


def _job(**fields: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": UUID_A,
        "title": "Software Engineer, Backend",
        "department": "Engineering",
        "team": "Backend",
        "location": "New York, NY (HQ)",
        "publishedAt": "2026-04-07T17:12:35.753+00:00",
        "descriptionHtml": "<p>We use TypeScript &amp; PostgreSQL.</p>",
        "descriptionPlain": "We use TypeScript & PostgreSQL.",
    }
    base.update(fields)
    return base


def _body(jobs: list[Any]) -> bytes:
    return json.dumps({"jobs": jobs, "apiVersion": "1"}).encode()


def test_registry_builds_ashby() -> None:
    assert get_provider("ashby").name == "ashby"


def test_jobs_url() -> None:
    url = AshbyProvider().jobs_url("ramp")
    assert url == "https://api.ashbyhq.com/posting-api/job-board/ramp"


@pytest.mark.parametrize("token", ["", "Ramp", "ramp/../x", "ramp?x=1", "a b"])
def test_jobs_url_rejects_unsafe_token(token: str) -> None:
    with pytest.raises(ConfigError):
        AshbyProvider().jobs_url(token)


def test_fields_are_mapped_to_rule_paths() -> None:
    board = AshbyProvider().parse(_body([_job()]))
    (posting,) = board.postings
    assert posting.posting_id == UUID_A
    assert posting.title == "Software Engineer, Backend"
    assert posting.location_name == "New York, NY (HQ)"
    assert posting.department_names == ("Engineering", "Backend")
    assert posting.updated_at == "2026-04-07T17:12:35.753+00:00"
    assert posting.content_raw == "<p>We use TypeScript &amp; PostgreSQL.</p>"
    assert posting.raw["location"] == {"name": "New York, NY (HQ)"}
    assert board.meta_total == board.fetched_count == 1
    assert board.data_quality == ()


def test_empty_board_is_empty_not_invalid() -> None:
    board = AshbyProvider().parse(b'{"jobs":[],"apiVersion":"1"}')
    assert board.is_empty
    assert board.postings == ()


@pytest.mark.parametrize(
    ("body", "code"),
    [
        (b"Not Found", "not_json"),
        (b"[]", "not_object"),
        (b'{"jobs": {}}', "jobs_not_list"),
        (b'{"apiVersion": "1"}', "jobs_not_list"),
    ],
)
def test_invalid_shapes(body: bytes, code: str) -> None:
    with pytest.raises(InvalidResponse) as info:
        AshbyProvider().parse(body)
    assert info.value.code == code


@pytest.mark.parametrize("bad_id", [123, UUID_A.upper(), "not-a-uuid", None])
def test_bad_ids_are_reported_not_invented(bad_id: object) -> None:
    board = AshbyProvider().parse(_body([_job(id=bad_id), _job(id=UUID_B)]))
    assert [p.posting_id for p in board.postings] == [UUID_B]
    assert [i.code for i in board.data_quality] == [DataQualityCode.INVALID_ID]


def test_missing_id_and_duplicates() -> None:
    no_id = _job()
    del no_id["id"]
    board = AshbyProvider().parse(_body([no_id, _job(), _job()]))
    assert [p.posting_id for p in board.postings] == [UUID_A]
    assert [i.code for i in board.data_quality] == [
        DataQualityCode.MISSING_ID,
        DataQualityCode.DUPLICATE_ID,
    ]


def test_no_valid_ids_is_invalid() -> None:
    with pytest.raises(InvalidResponse) as info:
        AshbyProvider().parse(_body([_job(id=1)]))
    assert info.value.code == "no_valid_ids"


def test_absent_location_is_a_warning_not_a_value() -> None:
    job = _job()
    del job["location"]
    (posting,) = AshbyProvider().parse(_body([job])).postings
    assert posting.location_name is None
    assert "location" not in posting.raw
