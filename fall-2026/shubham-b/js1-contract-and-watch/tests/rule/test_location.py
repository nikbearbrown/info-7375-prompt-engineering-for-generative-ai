"""§6.4 US-based location check and the description rescue (constructed inputs)."""

from __future__ import annotations

import pytest

from job_search_agent.models import LocationLabel
from job_search_agent.rule.location import (
    NON_US_NAMES,
    RESCUE_PHRASES,
    STATE_CODES,
    US_CITY_NAMES,
    classify_location,
    location_signals,
)

US = LocationLabel.US_BASED
NON = LocationLabel.NON_US
NOT = LocationLabel.NOT_ESTABLISHED


def _label(name: str | None, content: str = "") -> LocationLabel:
    return classify_location(name, content).label


@pytest.mark.parametrize(
    ("name", "label"),
    [
        ("Seattle, WA", US),
        ("US-Remote", US),
        ("US - Remote", US),
        ("NYC-Privy", US),
        ("South San Francisco, CA", US),
        ("San Francisco, New York City, Seattle, Chicago, US-Remote", US),
        ("United States", US),
        ("USA", US),
        ("U.S.", US),
        ("Remote in the US", US),
        ("Washington DC", US),
        ("Bengaluru, India", NON),
        ("London", NON),
        ("Dublin, Ireland", NON),
        ("N/A", NOT),
        ("na", NOT),
        ("LOCATION", NOT),
        ("AMER", NOT),
        ("Remote", NOT),
        ("Remote ", NOT),
        ("", NOT),
        ("Chicago, Toronto", NOT),
        ("US, Canada", NOT),
        ("Toronto, CA", NOT),
        ("NYC, Sea, SF, Tor", NOT),
    ],
)
def test_contract_examples(name: str, label: LocationLabel) -> None:
    assert _label(name) is label


def test_toronto_ca_reads_ca_as_a_state_code() -> None:
    """A9: taken literally, ``, CA`` is a US signal, so the label is mixed."""
    us, non_us = location_signals("Toronto, CA")
    assert us == [", CA"]
    assert non_us == ["Toronto"]


def test_lowercase_in_or_never_states() -> None:
    assert _label("Remote in or near Portland") is NOT
    assert _label("Remote, in") is NOT


def test_state_code_requires_comma_space() -> None:
    assert _label("Bellevue WA") is NOT
    assert _label("Bellevue,WA") is NOT
    assert _label("Bellevue,  WA") is NOT
    assert _label("Bellevue, wa") is NOT


def test_state_code_requires_right_boundary() -> None:
    """A10: no letter may follow the state code."""
    assert _label("Remote, CAN") is NOT
    assert _label("Remote, CA-2") is US


def test_lowercase_us_pronoun_not_signal() -> None:
    assert _label("Join us remotely") is NOT
    assert _label("Us") is NOT


def test_us_token_letter_boundary_only() -> None:
    """A11: only a letter blocks the token; digits next to it are allowed."""
    assert _label("US2") is US
    assert _label("2US") is US
    assert _label("USB hub") is NOT
    assert _label("BUS depot") is NOT
    assert _label("US-Remote") is US


def test_city_names_case_insensitive_whole_word() -> None:
    assert _label("seattle") is US
    assert _label("chi") is US
    assert _label("Chicagoland") is NOT
    assert _label("Seattle2") is NOT
    assert _label("Indiana") is NOT
    assert _label("india") is NON


def test_signal_lists_are_the_contract_lists() -> None:
    assert len(STATE_CODES) == 51
    assert "DC" in STATE_CODES
    assert len(US_CITY_NAMES) == 13
    assert len(NON_US_NAMES) == 22 + 24
    assert len(RESCUE_PHRASES) == 12


def test_reason_and_evidence_present() -> None:
    check = classify_location("Seattle, WA", "")
    assert check.evidence == ["$.location.name"]
    assert check.reason


# --- rescue -------------------------------------------------------------------


@pytest.mark.parametrize("phrase", RESCUE_PHRASES)
def test_each_rescue_phrase(phrase: str) -> None:
    content = f"This role is {phrase.upper()}, full stop."
    assert _label("Remote", content) is US


def test_rescue_cites_content() -> None:
    check = classify_location("N/A", "Remote within the United States.")
    assert check.label is US
    assert "$.content" in check.evidence
    assert "$.location.name" in check.evidence


def test_rescue_not_applied_to_mixed() -> None:
    assert _label("US, Canada", "Must be based in the United States.") is NOT


def test_rescue_not_applied_to_non_us() -> None:
    assert _label("London", "US only") is NON


def test_other_wording_does_not_rescue() -> None:
    content = "US preferred. Americas. Based in North America. Work from the US."
    assert _label("Remote", content) is NOT


def test_rescue_requires_word_boundary() -> None:
    """A8: ``status only`` must not read as ``us only``."""
    assert _label("Remote", "Report your status only once.") is NOT
    assert _label("Remote", "a bonus only on weekends") is NOT


def test_missing_location_field_not_established_with_valid_path() -> None:
    """A30: an absent ``$.location.name`` is NOT_ESTABLISHED; evidence is real."""
    check = classify_location(None, "", fallback_path="$.id")
    assert check.label is NOT
    assert check.evidence == ["$.id"]
    content_check = classify_location(None, "nothing here")
    assert content_check.evidence == ["$.content"]


def test_missing_location_field_can_be_rescued() -> None:
    check = classify_location(None, "Must be located in the United States.")
    assert check.label is US
    assert check.evidence == ["$.content"]
