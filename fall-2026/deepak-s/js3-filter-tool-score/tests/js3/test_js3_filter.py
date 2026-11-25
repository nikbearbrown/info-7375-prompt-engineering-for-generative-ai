"""Filter v1 (FILTER.md sections 1 to 4): every rule, precedence, abstention, and the wrong
versions F01-F04 and F06-F09 of section 6 (F05 concerns the shortlist, section 4 rule 3, and is
tested with the shortlist in Phase 4).

Written by Claude Code (claude-opus-5-5), 2026-11-25. All postings SEEDED (hand-built).
"""
import dataclasses

import js3kit  # noqa: F401

import pytest

import filter_checks as C
from filter_checks import ev, line, rules_hit
from jobwatch import filter as flt

PY = ("<p>We use Python.</p>",)


# --- the checks pass on v1 ---------------------------------------------------------------------
@pytest.mark.parametrize("check", [C.check_F01_whole_words, C.check_F02_boilerplate_not_counted,
                                   C.check_F03_topic_counted_once, C.check_F04_missing_location_not_a_match,
                                   C.check_F06_ties_not_by_fetch_order, C.check_F07_preferred_years_skipped,
                                   C.check_F08_bare_remote_is_not_us, C.check_F09_primary_location_only])
def test_check_passes_on_v1(check):
    check()


# --- each wrong version is caught --------------------------------------------------------------
def caught(check):
    with pytest.raises(AssertionError):
        check()


def test_F01_substring_matching_is_caught(monkeypatch):
    def substring(term, spans):
        text = " ".join(t for t, _, _ in spans)
        return (0, 1) if term.lower() in text else None
    monkeypatch.setattr(flt, "find_term", substring)
    caught(C.check_F01_whole_words)


def test_F02_topic_words_in_boilerplate_is_caught(monkeypatch):
    monkeypatch.setattr(flt, "body_sentences", lambda ln: [(s["start"], ln["text"][s["start"]:s["end"]]) for s in ln["sentences"]])
    caught(C.check_F02_boilerplate_not_counted)


def test_F03_topic_counted_every_time_is_caught(monkeypatch):
    def every_time(ln, rules):
        out = []
        for off, sent in flt.body_sentences(ln):
            spans = flt.token_spans(sent)
            for rid, term in rules.topics:
                t = flt.js1_tokens(term)
                out += [{"rule": rid} for i in range(len(spans)) if [s[0] for s in spans[i:i + len(t)]] == t]
        return out
    monkeypatch.setattr(flt, "topic_matches", every_time)
    caught(C.check_F03_topic_counted_once)


def test_F04_missing_location_as_match_is_caught(monkeypatch):
    real = flt.location_status
    monkeypatch.setattr(flt, "location_status", lambda ln, r: ("match", None) if not ln.get("location") else real(ln, r))
    caught(C.check_F04_missing_location_not_a_match)


def test_F06_ties_by_fetch_order_is_caught(monkeypatch):
    monkeypatch.setattr(flt, "rank", lambda outs: sorted(outs, key=lambda o: -(o["score"] or 0)))
    caught(C.check_F06_ties_not_by_fetch_order)


def test_F07_years_in_preferred_sentences_is_caught(monkeypatch):
    monkeypatch.setitem(flt.VERSIONS, "v1", dataclasses.replace(flt.V1, skip_words=()))
    caught(C.check_F07_preferred_years_skipped)


def test_F08_bare_remote_as_us_is_caught(monkeypatch):
    monkeypatch.setitem(flt.VERSIONS, "v1", dataclasses.replace(flt.V1, us_tokens=("remote",)))
    caught(C.check_F08_bare_remote_is_not_us)


def test_F09_secondary_locations_is_caught(monkeypatch):
    monkeypatch.setattr(flt, "primary_location",
                        lambda ln: " / ".join([ln.get("location") or ""] + ln.get("secondary_locations", [])))
    caught(C.check_F09_primary_location_only)


# --- every rule ----------------------------------------------------------------------------------
@pytest.mark.parametrize("rid,title", [("X01", "Senior Staff ML Engineer"), ("X02", "Staff ML Engineer"),
                                       ("X03", "Principal ML Engineer"), ("X04", "Director, ML Engineer"),
                                       ("X05", "ML Engineer Intern"), ("X06", "ML Engineer Manager"),
                                       ("X07", "Lead ML Engineer"), ("X08", "Head of ML, ML Engineer")])
def test_exclusion_terms_reject_whatever_else_matches(rid, title):
    o = ev(line(title=title, body=PY))
    assert o["decision"] == "reject" and o["score"] is None and rid in rules_hit(o)


@pytest.mark.parametrize("rid,title", [("R01", "Machine Learning Engineer"), ("R02", "ML Engineer"), ("R03", "AI Engineer"),
                                       ("R04", "Applied Scientist"), ("R05", "Data Scientist"), ("R06", "Research Engineer"),
                                       ("R07", "Research Scientist"), ("R08", "Machine Learning Scientist"),
                                       ("R09", "LLM Engineer"), ("R10", "Applied AI Engineer")])
def test_each_role_word_passes_the_role_gate(rid, title):
    o = ev(line(title=title, body=PY))
    assert rid in rules_hit(o) and o["decision"] == "keep" and o["score"] == 8


def test_no_role_word_rejects():
    o = ev(line(title="Software Engineer", body=PY))
    assert o["decision"] == "reject" and o["reasons"] == ["no role word R01-R10 in the title"]


def test_role_weight_counts_once_however_many_role_words_match():
    assert ev(line(title="Applied AI Engineer / AI Engineer", body=PY))["score"] == 8


@pytest.mark.parametrize("rid,loc", [("L01", "Boston, MA"), ("L02", "New York City"), ("L03", "NYC"), ("L04", "Seattle, WA"),
                                     ("L05", "Remote - US"), ("L05", "Remote (USA)"), ("L05", "Remote, United States"),
                                     ("L05", "U.S. Remote")])
def test_each_location_rule_qualifies(rid, loc):
    o = ev(line(location=loc, body=PY))
    assert rid in rules_hit(o) and o["decision"] == "keep"


def test_known_nonmatching_location_rejects_even_another_us_city():
    o = ev(line(location="San Francisco, CA", body=PY))
    assert o["decision"] == "reject" and o["score"] is None


@pytest.mark.parametrize("rid,word", [("T01", "Python"), ("T02", "PyTorch"), ("T03", "TensorFlow"), ("T04", "Keras"),
                                      ("T05", "scikit-learn"), ("T06", "machine learning"), ("T07", "deep learning"),
                                      ("T08", "LLM"), ("T09", "NLP"), ("T10", "model training"), ("T11", "model evaluation"),
                                      ("T12", "inference"), ("T13", "fine-tuning"), ("T14", "RAG"), ("T15", "embeddings"),
                                      ("T16", "transformers"), ("T17", "MLOps"), ("T18", "computer vision")])
def test_each_topic_word_adds_one_with_its_span(rid, word):
    o = ev(line(body=(f"<p>Work with {word} daily.</p>",)))
    (m,) = [m for m in o["matched"] if m["rule"] == rid]
    assert o["score"] == 8 and o["topics"] == 1
    assert m["field"] == "text" and m["quote"].lower() == word.lower()


def test_spans_point_into_the_field_they_quote():
    ln = line(title="Senior ML Engineer", location="New York, NY",
              body=("<p>Intro.</p>", "<li>3 years of experience with PyTorch.</li>"))
    o = ev(ln)
    for m in o["matched"]:
        src = {"title": ln["title"], "location": ln["location"], "text": ln["text"]}[m["field"]]
        assert src[m["start"]:m["end"]] == m["quote"]


def test_threshold_seven_rejects_with_a_score_and_eight_keeps():
    o = ev(line())
    assert (o["decision"], o["score"]) == ("reject", 7)
    assert (ev(line(body=PY))["decision"], ev(line(body=PY))["score"]) == ("keep", 8)


# --- E01 ---------------------------------------------------------------------------------------
@pytest.mark.parametrize("sentence,years", [
    ("6 years of experience in ML.", 6), ("6+ years of experience.", 6), ("6 or more years of experience.", 6),
    ("6-9 years of experience.", 6), ("6–9 years of experience.", 6), ("6—9 years of experience.", 6),
    ("6 to 9 years of experience.", 6), ("Experienced engineer with 7 years in Python.", 7),
    ("3.5 years of experience.", None), ("6 years building things.", None), ("Years of experience: 6", None),
])
def test_E01_reads_the_number_of_years(sentence, years):
    assert ev(line(body=(f"<p>{sentence}</p>",)))["years"] == years


@pytest.mark.parametrize("skip", ["preferred", "nice to have", "bonus", "ideally", "plus"])
def test_E01_skips_sentences_with_each_skip_word(skip):
    o = ev(line(body=(f"<p>9 years of experience {skip}.</p><p>We use Python.</p>",)))
    assert o["years"] is None and o["decision"] == "keep"


def test_E01_largest_remaining_n_and_more_than_five_rejects():
    o = ev(line(body=("<li>2+ years of experience with Python.</li><li>6+ years of experience in software.</li>",)))
    assert o["years"] == 6 and o["decision"] == "reject" and "E01" in o["reasons"][0]


def test_E01_five_years_passes():
    assert ev(line(body=("<li>5+ years of experience with Python.</li>",)))["decision"] == "keep"


def test_E01_ignores_boilerplate_sentences():
    b = "We value 10 years of experience in our culture."
    assert ev(line(body=(f"<p>{b}</p><p>Python.</p>",), boilerplate=(b,)))["years"] is None


def test_senior_with_five_or_less_passes_more_rejects_none_abstains_or_rejects():
    assert ev(line(title="Senior ML Engineer", body=("<li>4 years of experience with Python.</li>",)))["decision"] == "keep"
    assert ev(line(title="Senior ML Engineer", body=("<li>7 years of experience with Python.</li>",)))["decision"] == "reject"
    o = ev(line(title="Senior ML Engineer", body=PY))
    assert o["decision"] == "abstain" and "Senior title and E01 found no experience requirement" in o["reasons"][0]
    o = ev(line(title="Senior ML Engineer"))
    assert o["decision"] == "reject" and o["score"] is None and "at most 7" in o["reasons"][0]


# --- precedence and abstention (section 2 precedence bullet, section 4) -------------------------
def test_hard_rejection_beats_abstention():
    assert ev(line(title="Staff ML Engineer", location=None, body=PY))["decision"] == "reject"
    assert ev(line(location="Remote", body=("<li>8 years of experience with Python.</li>",)))["decision"] == "reject"
    assert ev(line(title="Intern", location=None, body=()))["decision"] == "reject"


def test_missing_description_gives_i_cannot_tell():
    o = ev(line(body=()))
    assert o["decision"] == "abstain" and o["reasons"] == ["I cannot tell: description missing or empty"]
    o = ev(line(location=None, body=("<p>   </p>",)))
    assert o["decision"] == "abstain" and "description missing or empty" in o["reasons"][0]


def test_bare_remote_with_no_topic_rejects_by_the_score_bound():
    o = ev(line(location="Remote"))
    assert o["decision"] == "reject" and o["score"] is None


def test_failed_board_abstains_once_per_board_not_per_posting():
    outs = flt.run([line(body=PY)], {"failed_boards": ["greenhouse:stripe-js2-nonexistent"]})
    boards = [o for o in outs if o.get("scope") == "board"]
    assert len(outs) == 2 and len(boards) == 1
    assert boards[0]["decision"] == "abstain" and boards[0]["reasons"] == ["I cannot tell: board failed in this run"]
