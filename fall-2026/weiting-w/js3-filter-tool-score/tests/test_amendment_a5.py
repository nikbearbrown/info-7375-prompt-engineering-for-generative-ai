"""FILTER.md §7 A5: `infrastructure` reinstated once A4 made it safe."""

from __future__ import annotations

from jobfilter import pipeline, score as scorer, sections


def test_the_scorer_is_s_v5():
    assert scorer.SCORER_VERSION == "S-v5"


def test_infrastructure_is_back_in_s1():
    assert "infrastructure" in scorer.SIGNALS["S1_core"][0]


def test_twenty_of_its_twenty_one_firings_earn_nothing(decisions):
    """The measurement A5 rests on, kept runnable."""
    company, elsewhere = 0, 0
    for d in decisions:
        if d.score is None:
            continue
        for h in d.score.hits:
            if h.word != "infrastructure":
                continue
            if h.section == sections.COMPANY:
                assert h.points == 0
                company += 1
            else:
                assert h.points == 2
                elsewhere += 1
    assert (company, elsewhere) == (20, 1)


def test_the_shortlist_did_not_change(decisions):
    assert pipeline.summary(decisions)["counts"]["shortlisted"] == 4


def test_the_one_real_match_is_in_a_section_about_the_job(decisions):
    d = next(x for x in decisions if x.posting.title.strip() == "Full Stack Engineer - Music")
    hit = next(h for h in d.score.hits if h.word == "infrastructure")
    assert hit.section != sections.COMPANY
    assert hit.points == 2
    assert d.score.total == 8
    assert "serving infrastructure" in hit.sentence


def test_the_other_two_a2_cuts_stay_cut():
    """A4 does not rescue them: their wrong matches are in real sections."""
    assert "go" not in scorer.SIGNALS["S2_language"][0]
    assert "1-2 years" not in scorer.SIGNALS["S5_newgrad"][0]
    assert "0-2 years" not in scorer.SIGNALS["S5_newgrad"][0]


def test_gos_wrong_matches_would_still_count(postings):
    """The reason `go` stays cut, asserted rather than asserted-in-prose."""
    import re

    pattern = re.compile(r"(?<!\w)go(?!\w)", re.IGNORECASE)
    in_real_sections = 0
    for p in postings:
        if not p.has_body:
            continue
        spans = sections.heading_spans(p.body)
        for m in pattern.finditer(p.body):
            if sections.kind_at(p.body, m.start(), spans) in (
                sections.DUTIES, sections.REQUIRED, sections.UNLABELLED
            ):
                in_real_sections += 1
                break
    assert in_real_sections >= 30, (
        "if A4 had moved these into `company`, `go` would be worth revisiting"
    )
