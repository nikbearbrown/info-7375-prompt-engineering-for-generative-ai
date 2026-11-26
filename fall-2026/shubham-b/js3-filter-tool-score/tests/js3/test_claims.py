"""FILTER.md §2: claim labels, "I cannot tell", and the documented limits."""

from __future__ import annotations

import pytest

from job_search_agent.js3.claims import (
    CONTRADICTED,
    INSUFFICIENT,
    SUPPORTED,
    justify,
    stated_minimum_years,
)
from tests.js3.helpers import FILLER, posting, scored


def _labels(
    title: str, content: str, location: str | None = "Seattle, WA"
) -> dict[str, str]:
    return {
        c.claim_id: c.label
        for c in justify(scored(posting(title, content + FILLER, location))).claims
        if c.claim_id != "C2"
    }


def test_all_supported_says_it_fits() -> None:
    j = justify(
        scored(
            posting(
                "Software Engineer",
                "3+ years of experience with Java and SQL. "
                "Visa sponsorship is available." + FILLER,
            )
        )
    )
    assert {c.label for c in j.claims} == {SUPPORTED} and not j.abstained


def test_years_above_kiran_contradict_and_come_first() -> None:
    j = justify(
        scored(
            posting(
                "Software Engineer",
                "5+ years of experience with Java and SQL." + FILLER,
            )
        )
    )
    assert j.claims[0].claim_id == "C4" and j.claims[0].label == CONTRADICTED
    assert j.answer.startswith(
        "Matches the filter, but the posting's text contradicts C4"
    )


def test_silence_on_sponsorship_abstains() -> None:
    j = justify(
        scored(
            posting(
                "Software Engineer",
                "2+ years of experience with Java and SQL." + FILLER,
            )
        )
    )
    assert "I cannot tell whether it fits on: C5" in j.answer and j.abstained


def test_no_sponsorship_contradicts() -> None:
    assert (
        _labels(
            "Software Engineer",
            "Java and SQL. We are unable to sponsor visas for this role.",
        )["C5"]
        == CONTRADICTED
    )


def test_both_ways_is_insufficient() -> None:
    text = (
        "Java and SQL. We will sponsor H-1B transfers. "
        "We cannot sponsor new OPT candidates."
    )
    assert _labels("Software Engineer", text)["C5"] == INSUFFICIENT


def test_generic_title_is_insufficient_for_c1() -> None:
    assert (
        _labels("Product Engineer", "Java, Python and SQL on distributed systems.")[
            "C1"
        ]
        == INSUFFICIENT
    )


def test_short_text_abstains_on_everything_but_the_title() -> None:
    j = justify(scored(posting("Software Engineer", "", "Seattle, WA")))
    assert j.abstained and all(
        c.label == INSUFFICIENT for c in j.claims if c.claim_id != "C1"
    )


def test_years_range_takes_the_lower_bound() -> None:
    assert stated_minimum_years("<li>2–12+ years of industry experience</li>")[0] == 2


def test_years_outside_an_experience_sentence_are_ignored() -> None:
    assert (
        stated_minimum_years("<p>Founded 15 years ago.</p><p>Experience with Java.</p>")
        is None
    )


# Documented limits (docs/js3/SHORTLIST_NOTES.md): pinned so a fix is a visible change.


def test_limit_a_ceiling_is_invisible() -> None:
    # Stripe "Software Engineer, New Grad": Kiran's 4 years exceed this cap,
    # yet C4 abstains.
    assert (
        stated_minimum_years(
            "<li>New grad candidates should have no more than 18 months "
            "of professional experience</li>"
        )
        is None
    )


def test_limit_spelled_number_with_parenthesis() -> None:
    assert (
        stated_minimum_years(
            "<p>plus three (3) years of software engineering or related experience.</p>"
        )
        is None
    )


# Review fixes (2026-11-25): two real false "supported" labels (Ramp),
# and two missed refusals.


@pytest.mark.parametrize(
    "text",
    [
        "We sponsored Neal Shipley while he was still an amateur golfer.",
        "We will sponsor you for relocation.",
    ],
)
def test_sponsor_without_visa_context_is_not_support(text: str) -> None:
    assert _labels("Software Engineer", "Java and SQL. " + text)["C5"] == INSUFFICIENT


@pytest.mark.parametrize(
    "text",
    [
        "We do not currently sponsor visas.",
        "Sponsorship is not available for this position.",
    ],
)
def test_more_refusals_contradict(text: str) -> None:
    assert _labels("Software Engineer", "Java and SQL. " + text)["C5"] == CONTRADICTED


def test_visa_sponsorship_offer_is_support() -> None:
    text = "Java and SQL. We will sponsor H-1B visas for this role."
    assert _labels("Software Engineer", text)["C5"] == SUPPORTED
