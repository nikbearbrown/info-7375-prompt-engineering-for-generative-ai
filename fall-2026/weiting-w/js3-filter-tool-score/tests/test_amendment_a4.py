"""FILTER.md §7 A4: a span is weighted by the section it sits in."""

from __future__ import annotations

import pytest

from jobfilter import pipeline, score as scorer, sections


def test_the_predicted_table(decisions):
    """A4 predicted shortlist 6 -> 4 and it is still 4 after A5, which moved a
    score without moving a bucket. Current versions: tests/test_versions.py."""
    s = pipeline.summary(decisions)
    assert s["counts"]["shortlisted"] == 4
    assert s["counts"]["below_threshold"] == 20
    assert s["scored"] == 24


def test_every_posting_with_text_has_a_recognised_heading(postings):
    """The measurement that turned 'a subsystem' into 'a table'."""
    missing = [
        p.identity for p in postings
        if p.has_body and not sections.heading_spans(p.body)
    ]
    assert missing == [], f"{len(missing)} postings with no recognised heading"


@pytest.mark.parametrize("heading,kind", [
    ("WHAT YOU NEED", sections.REQUIRED),
    ("What You Need", sections.REQUIRED),
    ("Who You Are", sections.REQUIRED),
    ("WHAT YOU'LL DO", sections.DUTIES),
    ("What You’ll Do", sections.DUTIES),
    ("ABOUT THE ROLE", sections.DUTIES),
    ("NICE TO HAVES", sections.OPTIONAL),
    ("NICE-TO-HAVES", sections.OPTIONAL),
    ("ABOUT RAMP", sections.COMPANY),
    ("OTHER NOTICES", sections.COMPANY),
])
def test_the_heading_table_reads_the_variants_the_corpus_uses(heading, kind):
    assert sections.HEADINGS[sections.normalise(heading)] == kind


def test_about_the_role_is_duties_not_company():
    """The bug the prediction caught before any code was written.

    "ABOUT THE ROLE" is the section that says "In this role, you will build
    core machine learning models". Classifying it as company boilerplate
    showed up as an implausible +28 in the predicted effect.
    """
    assert sections.HEADINGS[sections.normalise("ABOUT THE ROLE")] == sections.DUTIES


def test_nothing_on_the_shortlist_scores_from_an_optional_or_company_section(
    decisions,
):
    """The defect A4 exists to fix, asserted gone."""
    for d in decisions:
        if d.bucket != pipeline.SHORTLISTED:
            continue
        for h in d.score.hits:
            if h.points > 0:
                assert h.section in (
                    sections.REQUIRED, sections.DUTIES, sections.UNLABELLED
                ), f"{d.posting.title}: {h.word} scored from {h.section}"


def test_the_two_nice_to_haves_postings_dropped(decisions):
    for fragment in ("Software Engineer, iOS", "Software Engineer, Android"):
        d = next(x for x in decisions if x.posting.title.strip() == fragment)
        assert d.score.total == 3
        assert d.bucket == pipeline.BELOW_THRESHOLD
        optional = [h for h in d.score.hits if h.section == sections.OPTIONAL]
        assert len(optional) == 3
        assert all(h.raw_points == 2 and h.points == 1 for h in optional)
        # A5 added an `infrastructure` hit in the company blurb, worth 0
        assert all(
            h.points == 0 for h in d.score.hits if h.section == sections.COMPANY
        )


def test_a_penalty_is_never_scaled_by_its_section():
    """A rule that can be evaded by moving a sentence is not a rule."""
    body = (
        "ABOUT US\nWe are a company.\n\n"
        "NICE TO HAVES\n- 8+ years of experience would be lovely\n"
    )
    result = scorer.score(body)
    wall = next(h for h in result.hits if h.signal == "S6_experience_wall")
    assert wall.points == -6
    assert wall.section == sections.OPTIONAL


def test_a_hit_in_the_company_blurb_scores_nothing():
    body = (
        "ABOUT RAMP\nRamp is a company built on Python and a public API.\n\n"
        "WHAT YOU NEED\n- A pulse\n"
    )
    result = scorer.score(body)
    company_hits = [h for h in result.hits if h.section == sections.COMPANY]
    assert company_hits, [h.word for h in result.hits]
    assert all(h.points == 0 for h in company_hits)
    assert all(h.raw_points == 2 for h in company_hits)
    assert result.total == 0


def test_an_unknown_heading_does_not_cost_a_posting_its_points():
    """Weighting the unknown down would punish a board for its formatting."""
    body = "SOMETHING NOBODY ELSE WRITES\n- We build a backend API in Python.\n"
    result = scorer.score(body)
    assert result.total == 6
    assert all(h.section == sections.UNLABELLED for h in result.hits)


def test_api_does_not_match_the_plural_the_corpus_actually_writes(postings):
    """Found by getting this file's own fixture wrong.

    The first version of the test above said "We build APIs in Python" and
    scored 2 instead of 4, because `api` is matched whole-word and "APIs" is a
    different word. Across the corpus `api` matches 29 postings and misses
    **42** that write only "APIs", 10 of them among the 24 that get scored.

    Recorded here rather than fixed in A4: it is a word-list change, A4 is a
    section-weighting change, and one change per amendment is what has made
    every amendment in FILTER.md checkable. FILTER.md §7 lists it as next.
    """
    import re

    missed = [
        p for p in postings
        if p.has_body
        and not scorer._pattern("api").search(p.body)
        and re.search(r"(?<!\w)apis(?!\w)", p.body, re.IGNORECASE)
    ]
    assert len(missed) == 42
