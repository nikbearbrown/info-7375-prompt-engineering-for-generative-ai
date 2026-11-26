"""FILTER.md §1: the filter block, each rule, and the threshold."""

from __future__ import annotations

import pytest

from job_search_agent.errors import ConfigError
from job_search_agent.js3.filter import load_filter, parse_filter
from tests.conftest import REPO_ROOT
from tests.js3.helpers import FILLER, posting, scored, spec


def test_filter_md_is_the_frozen_v03() -> None:
    assert spec().version == "0.3"
    assert load_filter(REPO_ROOT / "experiments/js3/filters/FILTER.v0.3.md") == spec()


def test_v01_has_api_and_no_blockers() -> None:
    v01 = load_filter(REPO_ROOT / "experiments/js3/filters/FILTER.v0.1.md")
    assert {"api", "apis"} <= set(v01.topic_words) and v01.generic_blockers == ()
    assert {"api", "apis"}.isdisjoint(spec().topic_words)


def test_exactly_one_block_required() -> None:
    text = (REPO_ROOT / "FILTER.md").read_text(encoding="utf-8")
    with pytest.raises(ConfigError):
        parse_filter(text + text)
    with pytest.raises(ConfigError):
        parse_filter("no block")


def test_contract_bar_is_exactly_the_threshold() -> None:
    s = scored(posting("Software Engineer", "We use Java and PostgreSQL." + FILLER))
    assert s.points["R1"] == 4 and s.points["R4"] == 2 and s.points["R6"] == 1
    assert s.total == 7 and s.kept


def test_skill_cap_and_topic_once() -> None:
    s = scored(
        posting(
            "Backend Engineer",
            "Java, Python, SQL, AWS, Docker, Kafka. "
            "backend, microservices, distributed systems." + FILLER,
        )
    )
    assert s.points["R4"] == 3 and s.points["R5"] == 1 and s.total == 9


def test_generic_word_scores_two_and_blocker_removes_it() -> None:
    text = "Java, Python and SQL on distributed systems." + FILLER
    assert scored(posting("Product Engineer", text)).points["R2"] == 2
    blocked = scored(posting("Security Engineer", text))
    assert (
        blocked.points["R2"] == 0
        and blocked.generic_blocker == "security"
        and not blocked.kept
    )


def test_blocker_never_touches_a_role_phrase() -> None:
    s = scored(
        posting(
            "Software Engineer, Security, Stablecoin", "Java, Python, SQL." + FILLER
        )
    )
    assert s.points["R1"] == 4 and s.generic_blocker is None


def test_api_is_not_a_topic_word_in_v03() -> None:
    s = scored(
        posting(
            "Account Executive",
            "Experience selling API-based products at an API-first company." + FILLER,
        )
    )
    assert s.points["R5"] == 0


@pytest.mark.parametrize(
    ("title", "location", "content", "rule"),
    [
        ("Senior Software Engineer", "Seattle, WA", "Java Python SQL", "R3"),
        ("Software Engineer", "London", "Java Python SQL", "R6"),
        (
            "Software Engineer",
            "Seattle, WA",
            "Java Python SQL. Must be a U.S. citizen.",
            "R7",
        ),
    ],
)
def test_vetoes_cannot_be_outscored(
    title: str, location: str, content: str, rule: str
) -> None:
    s = scored(posting(title, content + FILLER, location=location))
    assert s.points[rule] == -10 and not s.kept


def test_unknown_location_is_zero_not_a_veto() -> None:
    s = scored(
        posting(
            "Software Engineer", "Java, Python, SQL. backend." + FILLER, location=None
        )
    )
    assert s.points["R6"] == 0 and s.total == 8 and s.kept
