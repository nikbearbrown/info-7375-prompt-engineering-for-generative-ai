"""§6.4 over every distinct ``location.name`` of the committed 2026-10-29 response."""

from __future__ import annotations

from typing import Any

import pytest

from job_search_agent.models import LocationLabel
from job_search_agent.rule import location as impl
from job_search_agent.rule.location import classify_location, location_signals
from tests.conftest import RawHandcheck
from tests.oracles.location_oracle import contract_lists, oracle_label

NO_SIGNAL = {"N/A", "na", "LOCATION", "AMER", "Remote", "Remote "}


def distinct_locations(raw: dict[str, Any]) -> list[str]:
    """Returns every distinct ``$.jobs[*].location.name`` string, sorted."""
    names = {
        job["location"]["name"]
        for job in raw["jobs"]
        if isinstance(job.get("location"), dict)
        and isinstance(job["location"].get("name"), str)
    }
    return sorted(names)


@pytest.fixture(scope="module")
def names(raw_handcheck: RawHandcheck) -> list[str]:
    return distinct_locations(raw_handcheck.data)


def test_raw_has_294_distinct_location_strings(names: list[str]) -> None:
    assert len(names) == 294


def test_only_documented_strings_have_no_signal(names: list[str]) -> None:
    assert {n for n in names if location_signals(n) == ([], [])} == NO_SIGNAL
    for name in NO_SIGNAL:
        assert classify_location(name, "").label is LocationLabel.NOT_ESTABLISHED


def test_both_signal_strings_are_not_established(names: list[str]) -> None:
    both = [n for n in names if all(location_signals(n))]
    assert len(both) == 25
    assert "Toronto, CA" in both
    for name in both:
        assert classify_location(name, "").label is LocationLabel.NOT_ESTABLISHED


def test_differential_against_token_oracle(names: list[str]) -> None:
    disagreements = {
        name: (classify_location(name, "").label.value, oracle_label(name))
        for name in names
        if classify_location(name, "").label.value != oracle_label(name)
    }
    assert disagreements == {}


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("Remote within the United States only.", "US_BASED"),
        ("the status only matters", "NOT_ESTABLISHED"),
        ("US preferred", "NOT_ESTABLISHED"),
    ],
)
def test_differential_rescue_against_oracle(content: str, expected: str) -> None:
    assert classify_location("Remote", content).label.value == expected
    assert oracle_label("Remote", content) == expected


def test_lists_match_contract_text() -> None:
    """The production lists equal the backticked §6.4 lists in CONTRACT.md."""
    lists = contract_lists()
    assert lists.us_tokens == impl.US_TOKENS
    assert lists.state_codes == impl.STATE_CODES
    assert lists.us_cities == impl.US_CITY_NAMES
    assert lists.non_us_countries == impl.NON_US_COUNTRIES
    assert lists.non_us_cities == impl.NON_US_CITIES
    assert lists.rescue_phrases == impl.RESCUE_PHRASES
