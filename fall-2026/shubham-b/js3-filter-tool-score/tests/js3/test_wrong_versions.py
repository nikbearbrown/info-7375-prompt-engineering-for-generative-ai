"""FILTER.md §4: the real code passes every check.

Each wrong version fails its named check.

Each implementation is three callables: ``kept(posting)``, ``skills(posting)`` (credited
résumé terms) and ``labels(posting)`` (claim id -> label for C3 and C5).
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from typing import Any

import pytest

from job_search_agent.js3.claims import INSUFFICIENT, SUPPORTED, justify
from job_search_agent.models import Posting
from job_search_agent.text import clean_html
from tests.js3.helpers import FILLER, inputs, posting, scored, spec

Impl = dict[str, Callable[[Posting], Any]]


def _labels(p: Posting) -> dict[str, str]:
    return {
        c.claim_id: c.label
        for c in justify(scored(p)).claims
        if c.claim_id in ("C3", "C5")
    }


REAL: Impl = {
    "kept": lambda p: scored(p).kept,
    "skills": lambda p: {k.term for k in scored(p).skills},
    "labels": _labels,
}


def _wv1_kept(p: Posting) -> bool:  # role words read from title or content
    return scored(
        dataclasses.replace(p, title=p.title + " " + clean_html(p.content_raw))
    ).kept


def _wv2_kept(p: Posting) -> bool:  # rank by skill count, no cap, no veto
    return len(scored(p).skills) >= 2


def _wv3_labels(p: Posting) -> dict[str, str]:  # silence is support
    return {k: SUPPORTED if v == INSUFFICIENT else v for k, v in _labels(p).items()}


def _wv4_skills(p: Posting) -> set[str]:  # substring match
    text = (p.title + " " + clean_html(p.content_raw)).lower()
    return {s.term for s in inputs().skills if s.term.lower() in text}


def _wv5_kept(p: Posting) -> bool:  # > instead of >=
    return scored(p).total > spec().threshold


WRONG: dict[str, Impl] = {
    "WV1": {**REAL, "kept": _wv1_kept},
    "WV2": {**REAL, "kept": _wv2_kept},
    "WV3": {**REAL, "labels": _wv3_labels},
    "WV4": {**REAL, "skills": _wv4_skills},
    "WV5": {**REAL, "kept": _wv5_kept},
}


def check_role_words_read_title_only(impl: Impl) -> None:
    p = posting(
        "Account Executive",
        "You will partner with our software engineer and backend engineer teams. "
        "Java, Python, SQL, distributed systems." + FILLER,
    )
    assert not impl["kept"](p)


def check_seniority_vetoes_any_skill_count(impl: Impl) -> None:
    many = (
        "TypeScript JavaScript Java Python SQL GraphQL PostgreSQL Redis Kafka AWS "
        "Docker Kubernetes"
    )
    assert not impl["kept"](posting("Staff Software Engineer", many + FILLER))


def check_silence_is_insufficient(impl: Impl) -> None:
    labels = impl["labels"](
        posting("Software Engineer", "Java and SQL." + FILLER, location="Remote")
    )
    assert labels == {"C3": INSUFFICIENT, "C5": INSUFFICIENT}


def check_skills_are_whole_words(impl: Impl) -> None:
    got = impl["skills"](
        posting(
            "Software Engineer",
            "JavaScript on a NoSQL store with reactive streams." + FILLER,
        )
    )
    assert got == {"JavaScript"}


def check_threshold_is_inclusive(impl: Impl) -> None:
    p = posting("Software Engineer", "Java and PostgreSQL." + FILLER)
    assert scored(p).total == spec().threshold and impl["kept"](p)


CHECKS = {
    "WV1": check_role_words_read_title_only,
    "WV2": check_seniority_vetoes_any_skill_count,
    "WV3": check_silence_is_insufficient,
    "WV4": check_skills_are_whole_words,
    "WV5": check_threshold_is_inclusive,
}


@pytest.mark.parametrize("check", CHECKS.values(), ids=CHECKS.keys())
def test_real_code_passes(check: Callable[[Impl], None]) -> None:
    check(REAL)


@pytest.mark.parametrize("name", WRONG)
def test_wrong_version_is_caught_by_its_check(name: str) -> None:
    with pytest.raises(AssertionError):
        CHECKS[name](WRONG[name])
