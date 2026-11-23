"""reports/shortlist.md's numbers and its two worked cases, as tests."""

from __future__ import annotations

from jobfilter import evidence, pipeline


def shortlisted(decisions):
    return [d for d in decisions if d.bucket == pipeline.SHORTLISTED]


def test_the_shortlist_is_seven_entries(decisions):
    assert len(shortlisted(decisions)) == 7


def test_the_claim_totals_are_22_supported_0_contradicted_7_insufficient(decisions):
    agg = {"supported": 0, "contradicted": 0, "insufficient": 0}
    for d in shortlisted(decisions):
        for k, v in evidence.summarise(evidence.claims_for(d)).items():
            agg[k] += v
    assert agg == {"supported": 22, "contradicted": 0, "insufficient": 7}


def test_every_insufficient_is_the_same_unanswerable_claim(decisions):
    for d in shortlisted(decisions):
        for c in evidence.claims_for(d):
            if c.label == evidence.INSUFFICIENT:
                assert c.kind == "OPEN_TO_NEW_GRADS"


def test_every_supported_claim_quotes_a_span_containing_its_word(decisions):
    """E1: if the characters cannot be pointed at, the label is insufficient."""
    for d in shortlisted(decisions):
        for c in evidence.claims_for(d):
            if c.label == evidence.SUPPORTED:
                assert c.span, c.text
                assert str(c.arg).lower() in c.span.lower()


# --- the two worked cases -----------------------------------------------------

def _find(decisions, title_fragment):
    for d in decisions:
        if title_fragment in d.posting.title:
            return d
    raise AssertionError(f"no posting titled like {title_fragment!r}")


def test_relevance_is_not_entailment_the_inference_accounting_case(decisions):
    """shortlist.md §2: the ML signal fired on an invoicing term."""
    d = _find(decisions, "AI Spend Management")
    hit = next(h for h in d.score.hits if h.word == "inference")
    assert hit.signal == "S4_ml" and hit.points == 2
    assert "inference accounting" in hit.sentence.lower()

    # the mention is supported; the claim about the job is not
    mention = evidence.judge(evidence.Claim(
        kind="MENTIONS", text="the posting mentions inference",
        span=hit.sentence, arg="inference"))
    assert mention.label == evidence.SUPPORTED
    assert evidence.label_claim("this is a machine-learning job", hit.sentence) \
        == evidence.INSUFFICIENT


def test_the_plus_two_and_the_minus_six_come_from_one_sentence(decisions):
    """shortlist.md §2: a word match carries no sign."""
    d = _find(decisions, "Backend, Growth")
    sents = {h.word: h.sentence for h in d.score.hits}
    assert sents["python"] == sents["5+ years"]
    assert d.score.total == -2


def test_four_scored_postings_say_senior_in_the_body_not_the_title(decisions, postings):
    from jobfilter import score as scorer

    pattern = scorer._pattern("senior")
    found = [
        d for d in decisions
        if d.score is not None and d.posting.body
        and pattern.search(d.posting.body)
        and "senior" not in d.posting.title.lower()
    ]
    assert len(found) == 4


def test_the_abstention_counterexample_abstains(decisions):
    """shortlist.md §4: the body says 'Senior Backend Engineer'; E-v1 abstains."""
    d = _find(decisions, "Backend, Accounting")
    assert "senior backend engineer" in d.posting.body.lower()
    claim = next(c for c in evidence.claims_for(d) if c.kind == "OPEN_TO_NEW_GRADS")
    assert claim.label == evidence.INSUFFICIENT, (
        "E-v1's contradiction trigger is a years number; this posting said it "
        "in a word. The limit is recorded, not repaired."
    )


def test_the_obvious_repair_would_break_this_one(decisions):
    """'senior' here describes the colleagues, not the role."""
    d = _find(decisions, "Machine Learning Engineer - Subscriptions")
    body = d.posting.body.lower()
    assert "senior and staff ml engineers" in body
    assert d.bucket == pipeline.SHORTLISTED
