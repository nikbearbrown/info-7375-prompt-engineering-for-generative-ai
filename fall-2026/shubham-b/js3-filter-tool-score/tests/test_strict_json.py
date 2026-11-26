"""Strict-JSON hooks shared by the résumé gate, the provider and the judge validator."""

from __future__ import annotations

import json

import pytest

from job_search_agent.strict_json import (
    DuplicateKeyError,
    NonStandardConstantError,
    reject_constant,
    reject_duplicate_keys,
)


def _loads(text: str) -> object:
    return json.loads(
        text, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_constant
    )


def test_plain_json_parses() -> None:
    assert _loads('{"a": [1, {"b": 2.5}], "c": null}') == {
        "a": [1, {"b": 2.5}],
        "c": None,
    }


@pytest.mark.parametrize("text", ['{"a": 1, "a": 2}', '{"x": {"k": 1, "k": 1}}'])
def test_duplicate_keys_refused_at_any_depth(text: str) -> None:
    with pytest.raises(DuplicateKeyError):
        _loads(text)


@pytest.mark.parametrize("text", ["NaN", '{"a": Infinity}', "[-Infinity]"])
def test_non_standard_constants_refused(text: str) -> None:
    with pytest.raises(NonStandardConstantError):
        _loads(text)


def test_errors_are_value_errors() -> None:
    assert issubclass(DuplicateKeyError, ValueError)
    assert issubclass(NonStandardConstantError, ValueError)
