"""Listing-response parsing (GATE F3, "Board failure policy"). Synthetic inputs only."""

import json

import pytest

from agent.errors import MalformedResponse
from agent.providers import parse_ids
from support import ASHBY_SMALL, GREENHOUSE_SMALL


def body(obj) -> bytes:
    return json.dumps(obj).encode()


def test_fixtures_are_labeled_synthetic():
    """Rule: test fixtures are synthetic, never real postings (build-step instructions)."""
    for path in (GREENHOUSE_SMALL, ASHBY_SMALL):
        assert json.loads(path.read_text())["_synthetic"] is True


def test_greenhouse_fixture_parses_integer_ids():
    """F3: Greenhouse IDs are integers excluding booleans; count unique IDs."""
    parsed = parse_ids("greenhouse", GREENHOUSE_SMALL.read_bytes())
    assert parsed.ids == (9000001, 9000002, 9000003)
    assert parsed.jobs_in_response == 3 and parsed.duplicates_removed == 0


def test_ashby_fixture_parses_string_ids():
    """F3: Ashby IDs are non-empty strings."""
    parsed = parse_ids("ashby", ASHBY_SMALL.read_bytes())
    assert parsed.ids == ("00000000-0000-4000-8000-000000000001", "00000000-0000-4000-8000-000000000002")
    assert parsed.duplicates_removed == 0


@pytest.mark.parametrize("provider", ["greenhouse", "ashby"])
def test_empty_jobs_list_is_zero_not_failure(provider):
    """Board failure policy: a valid empty `jobs` list means zero fetched."""
    parsed = parse_ids(provider, body({"jobs": []}))
    assert parsed.ids == () and parsed.jobs_in_response == 0 and parsed.duplicates_removed == 0


@pytest.mark.parametrize("raw", [b"", b"{not json", b"\xff\xfe\x00", b"null"])
def test_bad_or_empty_body_is_malformed(raw):
    """F3 + Board failure policy: an empty body or invalid JSON is a failure, not zero."""
    with pytest.raises(MalformedResponse):
        parse_ids("greenhouse", raw)


@pytest.mark.parametrize("obj", [[], [{"id": 1}], "jobs", 3])
def test_top_level_not_object_is_malformed(obj):
    """F3: a top level that isn't an object is malformed."""
    with pytest.raises(MalformedResponse, match="not an object"):
        parse_ids("greenhouse", body(obj))


@pytest.mark.parametrize("obj", [{}, {"postings": []}, {"jobs": None}, {"jobs": {"id": 1}}, {"jobs": "[]"}])
def test_missing_or_non_list_jobs_is_malformed(obj):
    """F3: `jobs` missing or not a list is malformed."""
    with pytest.raises(MalformedResponse, match="'jobs'"):
        parse_ids("ashby", body(obj))


@pytest.mark.parametrize("bad_id", [True, False])
def test_bool_id_is_malformed_for_greenhouse(bad_id):
    """F3: Greenhouse IDs are integers excluding booleans."""
    with pytest.raises(MalformedResponse):
        parse_ids("greenhouse", body({"jobs": [{"id": 1}, {"id": bad_id}]}))


@pytest.mark.parametrize("bad_id", ["123", 1.5, None, [1]])
def test_non_integer_id_is_malformed_for_greenhouse(bad_id):
    """F3 + GATE: keep Greenhouse IDs as integers; a string or float ID is invalid."""
    with pytest.raises(MalformedResponse):
        parse_ids("greenhouse", body({"jobs": [{"id": bad_id}]}))


def test_empty_string_id_is_malformed_for_ashby():
    """F3: Ashby IDs are non-empty strings."""
    with pytest.raises(MalformedResponse):
        parse_ids("ashby", body({"jobs": [{"id": "a"}, {"id": ""}]}))


@pytest.mark.parametrize("bad_id", [123, True, None])
def test_non_string_id_is_malformed_for_ashby(bad_id):
    """F3 + GATE: keep Ashby IDs as strings."""
    with pytest.raises(MalformedResponse):
        parse_ids("ashby", body({"jobs": [{"id": bad_id}]}))


@pytest.mark.parametrize("job", [{"title": "no id"}, "not-an-object", None])
def test_job_without_id_is_malformed(job):
    """F3: any job that lacks a valid `id` makes the response malformed."""
    with pytest.raises(MalformedResponse):
        parse_ids("greenhouse", body({"jobs": [{"id": 1}, job]}))


def test_duplicates_are_counted_and_removed():
    """F3: count and compare unique IDs, and log how many duplicates were removed."""
    parsed = parse_ids("greenhouse", body({"jobs": [{"id": 3}, {"id": 1}, {"id": 3}, {"id": 2}, {"id": 1}]}))
    assert parsed.ids == (3, 1, 2)
    assert parsed.jobs_in_response == 5 and parsed.duplicates_removed == 2
