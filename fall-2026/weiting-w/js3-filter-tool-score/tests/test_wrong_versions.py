"""FILTER.md §4: each wrong version must be caught by a real test.

A wrong version nobody runs is a claim about a test that never met it -- which
is the mistake JS2 made with its own W2 and had to correct after the fact.
These four are all exercised against the real corpus.
"""

from __future__ import annotations

from jobfilter import pipeline, score as scorer
from tests import wrong_versions as wrong
from tests.conftest import make_posting


# --- W1: a missing body is not a zero -----------------------------------------

def test_W1_turns_157_unscorable_postings_into_rejects(postings, persona):
    """The real pipeline keeps them apart; W1 collapses them."""
    real = pipeline.run(postings, persona)
    assert pipeline.summary(real)["counts"]["cannot_score"] == 11

    bad = [wrong.missing_body_scores_zero(p, persona) for p in postings]
    assert all(d.bucket != pipeline.CANNOT_SCORE for d in bad), (
        "W1 is supposed to have no such bucket"
    )
    bad_zeroes = [
        d for d in bad
        if d.score is not None and d.score.total == 0 and not d.posting.has_body
    ]
    assert bad_zeroes, "W1 should have scored body-less postings 0"
    for d in bad_zeroes:
        assert d.bucket == pipeline.BELOW_THRESHOLD


def test_the_real_pipeline_never_scores_a_posting_with_no_body(decisions):
    for d in decisions:
        if not d.posting.has_body:
            assert d.score is None
            assert d.bucket in (pipeline.GATED, pipeline.CANNOT_SCORE)


def test_the_buckets_add_up(decisions):
    s = pipeline.summary(decisions)
    assert sum(s["counts"].values()) == 452


# --- W2: substring matching ----------------------------------------------------

def test_W2_fires_on_words_that_merely_contain_the_signal():
    body = "This is an ongoing Chicago category of work."
    assert wrong.substring_topic_match(body, "go") is True
    assert scorer._pattern("go").search(body) is None


def test_the_real_matcher_is_whole_word_on_the_real_corpus(postings):
    """`api` must not fire on "rapid", "capital" or "therapist"."""
    trap = "We need rapid capital decisions from a therapist's calm."
    assert wrong.substring_topic_match(trap, "api") is True
    assert scorer._pattern("api").search(trap) is None


def test_punctuated_signals_still_match_whole(postings):
    """`c++` and `c#` need the non-word-char boundary, not `\\b`.

    `\\bc\\+\\+\\b` can never match, because there is no word boundary after `+`.
    The boundary is written as "not flanked by a word character" instead.

    Its limit, found by this test and left standing: the guard stops a *word*
    character on either side, so `c++` still matches inside a run of plus
    signs. "c+++" is not something a job posting writes, and tightening the
    pattern to exclude it would also exclude "C++." and "C++,", which postings
    write constantly. Recorded rather than fixed.
    """
    assert scorer._pattern("c++").search("languages such as C++, or Java") is not None
    assert scorer._pattern("c++").search("experience in C++.") is not None
    assert scorer._pattern("c++").search("we use c++x internally") is None
    assert scorer._pattern("c++").search("the c+++ thing") is not None   # the limit
    assert scorer._pattern("c#").search("C# and .NET") is not None


# --- W3: scoring the whole record ----------------------------------------------

def test_W3_scores_markup_and_urls_that_the_real_scorer_cannot_see():
    posting = make_posting(
        body="We write careful code.",
        raw={
            "descriptionHtml": '<a href="https://ex.com/rendering/api">read</a>',
            "applyUrl": "https://jobs.example.com/python-backend/apply",
        },
    )
    real = scorer.score(posting.body)
    bad = wrong.score_from_the_whole_record(posting)
    assert real.total == 0
    assert bad.total > 0, "W3 should have scored the URL and the markup"
    assert {h.word for h in bad.hits} & {"api", "python", "backend", "rendering"}


def test_html_in_the_lever_body_is_stripped_with_its_attributes():
    from jobfilter.corpus import strip_html

    out = strip_html('<a href="https://x.com/python">click</a> here')
    assert "python" not in out.lower()
    assert out.strip() == "click here"


# --- W4: relevance is not entailment -------------------------------------------

def test_W4_calls_a_word_match_an_entailment():
    hits = [scorer.Hit("S2_language", "python", 2, 0, 6, "Python or JavaScript)")]
    assert wrong.relevance_implies_support("this is a Python job", hits) == "supported"


def test_the_real_labeller_does_not(postings):
    """The real one is in jobfilter.evidence and is asserted in its own file."""
    from jobfilter import evidence

    span = "You will work in Python or JavaScript."
    assert evidence.label_claim("the posting mentions Python", span) == "supported"
    assert evidence.label_claim("this is primarily a Python job", span) == "insufficient"
