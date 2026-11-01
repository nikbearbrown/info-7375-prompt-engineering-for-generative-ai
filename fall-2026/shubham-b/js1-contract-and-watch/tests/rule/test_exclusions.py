"""§6.3 explicit exclusion phrases. All texts are constructed except the board test."""

from __future__ import annotations

import pytest

from job_search_agent.rule.exclusions import EXCLUSION_PHRASES, find_exclusions
from tests.tools.builders import handcheck_board, posting

PHRASES = (
    "must be a U.S. citizen",
    "U.S. citizens only",
    "United States citizens only",
    "citizenship required",
    "security clearance required",
    "active clearance required",
    "must hold a clearance",
    "unpaid position",
    "unpaid role",
    "unpaid internship",
    "this is an unpaid opportunity",
)


def test_phrase_list_is_the_contract_list() -> None:
    assert EXCLUSION_PHRASES == PHRASES


@pytest.mark.parametrize("phrase", PHRASES)
def test_each_phrase_excludes(phrase: str) -> None:
    content = f"&lt;p&gt;Note: {phrase}.&lt;/p&gt;"
    assert find_exclusions(posting(content=content)) == [phrase]


def test_case_insensitive() -> None:
    found = find_exclusions(posting(content="CITIZENSHIP REQUIRED; Unpaid Role"))
    assert found == ["citizenship required", "unpaid role"]


def test_whitespace_and_tags_normalised() -> None:
    content = "security\n  clearance&nbsp;<b>required</b>"
    assert find_exclusions(posting(content=content)) == ["security clearance required"]


def test_phrase_in_title_excludes() -> None:
    item = posting(title="Software Engineer (unpaid position)")
    assert find_exclusions(item) == ["unpaid position"]


def test_ambiguous_wording_not_excluded() -> None:
    content = (
        "Citizenship preferred. Clearance a plus. Some roles are unpaid. "
        "Applicants must be U.S. citizens or residents."
    )
    assert find_exclusions(posting(content=content)) == []


def test_phrase_needs_word_boundaries() -> None:
    """A8: a phrase embedded in a longer word does not count."""
    content = "noncitizenship requiredness; unpaid roles"
    assert find_exclusions(posting(content=content)) == []


def test_department_text_not_searched() -> None:
    """A27: §6.3 searches the cleaned title and content, not department names."""
    item = posting(departments=[{"name": "unpaid internship"}])
    assert find_exclusions(item) == []


def test_every_phrase_recorded() -> None:
    content = "unpaid role. must hold a clearance. citizenship required."
    assert find_exclusions(posting(content=content)) == [
        "citizenship required",
        "must hold a clearance",
        "unpaid role",
    ]


def test_board_2026_10_29_has_no_exclusion_phrases() -> None:
    """Real-data fact: no §6.3 phrase appears anywhere on the committed board."""
    hits = {p.posting_id: find_exclusions(p) for p in handcheck_board().postings}
    assert {pid: found for pid, found in hits.items() if found} == {}
