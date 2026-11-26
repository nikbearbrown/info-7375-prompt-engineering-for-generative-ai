"""``jsonpath``: the tiny ``$ ( .key | [int] )*`` grammar used by evidence paths."""

from __future__ import annotations

from typing import Any

import pytest

from job_search_agent.jsonpath import (
    JsonPathSyntaxError,
    PathNotFoundError,
    exists,
    format_path,
    parse_path,
    resolve,
)

DOC: dict[str, Any] = {
    "skills": {"backend": ["Node.js", "Express", "Spring Boot", "REST", "GraphQL"]},
    "location": {"name": "Seattle, WA"},
    "departments": [{"name": "Payments"}],
    "content": "x",
    "_comment": "c",
}


@pytest.mark.parametrize(
    "path",
    [
        "$",
        "$.content",
        "$.skills.backend[4]",
        "$.departments[0].name",
        "$.location.name",
        "$._comment",
        "$.jobs[566]",
    ],
)
def test_round_trip(path: str) -> None:
    assert format_path(parse_path(path)) == path


def test_parse_parts() -> None:
    assert parse_path("$.skills.backend[4]") == ("skills", "backend", 4)
    assert parse_path("$") == ()


def test_resolve_values() -> None:
    assert resolve(DOC, "$.skills.backend[4]") == "GraphQL"
    assert resolve(DOC, "$.departments[0].name") == "Payments"
    assert resolve(DOC, "$") is DOC
    assert exists(DOC, "$.location.name")


def test_resolve_missing_key_raises() -> None:
    with pytest.raises(PathNotFoundError):
        resolve(DOC, "$.salary")
    with pytest.raises(PathNotFoundError):
        resolve(DOC, "$.content.name")
    assert not exists(DOC, "$.location.city")


def test_resolve_index_out_of_range_raises() -> None:
    with pytest.raises(PathNotFoundError):
        resolve(DOC, "$.skills.backend[5]")
    assert not exists(DOC, "$.departments[1].name")


def test_index_does_not_address_mapping_and_key_does_not_address_list() -> None:
    assert not exists({"a": {"0": "x"}}, "$.a[0]")
    assert not exists({"a": ["x"]}, "$.a.x")
    assert not exists({"a": "text"}, "$.a[0]")


@pytest.mark.parametrize(
    "path",
    [
        "",
        "content",
        "$.",
        "$..content",
        "$.skills.backend[*]",
        "$.skills[?(@.x)]",
        "$.skills.backend[-1]",
        "$.skills.backend[01]",
        "$.skills.backend[1",
        "$['content']",
        "$.a b",
        "$.1abc",
        " $.content",
        "$.content ",
    ],
)
def test_rejects_wildcards_filters_and_negative_index(path: str) -> None:
    with pytest.raises(JsonPathSyntaxError):
        parse_path(path)
    assert not exists(DOC, path)


@pytest.mark.parametrize("parts", [("a b",), (-1,), (True,), ("",)])
def test_format_rejects_bad_parts(parts: tuple[Any, ...]) -> None:
    with pytest.raises(JsonPathSyntaxError):
        format_path(parts)
