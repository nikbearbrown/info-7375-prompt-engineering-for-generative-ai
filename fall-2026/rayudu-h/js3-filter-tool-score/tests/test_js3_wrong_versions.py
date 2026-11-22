"""FILTER.md section 5: the wrong versions W1-W6. These tests were committed before any js3 code.

Every posting here is CONSTRUCTED for the test (see conftest.posting).
"""
import pytest

from conftest import posting
from js3 import claims, filterdoc, sample, score

FILLER = ("<p>You will work with a small team on internal tools, write design notes, review code, "
          "and help other teams adopt what you build. We value clear writing and steady delivery. "
          "This paragraph is filler so the text is long enough to be judged at all.</p>")   # > 200 chars


def test_filler_alone_is_long_enough():
    assert len(posting("f", "x", FILLER)["text"]) >= 200


@pytest.fixture(scope="module")
def flt():
    return filterdoc.load()


# ---- W1: substring matching ------------------------------------------------------------------
def test_w1_aws_inside_laws_is_not_a_skill(flt):
    p = posting("w1a", "AI Engineer", FILLER + "<p>You will comply with employment Laws. Python is required.</p>")
    r = score.score(p, flt)
    assert r["skills"] == ["Python"]          # not AWS (inside "Laws")


def test_w1_ai_inside_email_is_not_a_role_word(flt):
    p = posting("w1b", "Email Operations Specialist", FILLER + "<p>Python and SQL.</p>")
    r = score.score(p, flt)
    assert r["role_words"] == []              # "AI" inside "Email" does not count


# ---- W2: ranking by raw match count -------------------------------------------------------------
def test_w2_distinct_skills_outrank_repeated_word(flt):
    a = posting("w2a", "Data Engineer", FILLER + "<p>" + "Python " * 20 + "</p>")
    b = posting("w2b", "Data Engineer", FILLER + "<p>Python, SQL and AWS.</p>")
    ra, rb = score.score(a, flt), score.score(b, flt)
    assert ra["skills"] == ["Python"]         # counted once, however often it appears
    assert [r["key"] for r in score.rank([ra, rb])] == [rb["key"], ra["key"]]


# ---- W3: missing text silently rejected ----------------------------------------------------------
def test_w3_empty_text_is_cannot_tell_not_rejected(flt):
    p = posting("w3a", "AI Engineer", "")
    assert score.score(p, flt)["decision"] == "cannot tell"


def test_w3_short_text_is_cannot_tell(flt):
    p = posting("w3b", "AI Engineer", "<p>Python.</p>")     # under min_text_chars (200)
    assert score.score(p, flt)["decision"] == "cannot tell"


def test_w3_empty_title_is_cannot_tell(flt):
    p = posting("w3c", "", FILLER + "<p>Python and SQL.</p>")
    assert score.score(p, flt)["decision"] == "cannot tell"


# ---- W4: a quote from the neighbouring posting (shifted pairing) --------------------------------
def test_w4_quote_must_come_from_this_posting():
    a = posting("w4a", "AI Engineer", FILLER + "<p>We build agents in Python.</p>")
    b = posting("w4b", "Data Engineer", FILLER + "<p>We use Delta Lake daily.</p>")
    assert claims.quote_in_posting("We use Delta Lake daily", b)
    assert not claims.quote_in_posting("We use Delta Lake daily", a)


def test_w4_whitespace_is_normalized_but_words_are_not():
    b = posting("w4c", "Data Engineer", FILLER + "<p>We use   Delta\nLake daily.</p>")
    assert claims.quote_in_posting("We use Delta Lake daily", b)
    assert not claims.quote_in_posting("We use Delta Lakes daily", b)


def test_w4_supported_label_without_a_grounded_quote_is_rejected():
    a = posting("w4d", "AI Engineer", FILLER + "<p>We build agents in Python.</p>")
    errors = claims.validate_label({"claim": "C2", "label": "supported", "quote": "We use Delta Lake daily"}, a)
    assert errors and "not found" in errors[0]


# ---- W5: held-out labels leaking into tuning -----------------------------------------------------
def _fake_results(n_kept=60, n_rej=200):
    rs = []
    for i in range(n_kept):
        rs.append({"key": f"k{i}", "decision": "kept", "score": 4.5 + (i % 5), "margin": 1.5 + (i % 5)})
    for i in range(n_rej):
        rs.append({"key": f"r{i}", "decision": "rejected", "score": 2.5 - (i % 4), "margin": -0.5 - (i % 4),
                   "excluded_by": []})
    return rs


def test_w5_samples_are_disjoint():
    s = sample.draw(_fake_results(), seed=1)
    sets = [set(s[name]) for name in ("heldout", "audit_random_rejects", "audit_closest", "audit_kept")]
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            assert not (sets[i] & sets[j])
    assert len(s["audit_random_rejects"]) >= 30


def test_w5_threshold_fit_refuses_heldout_ids():
    s = sample.draw(_fake_results(), seed=1)
    leaked = {s["heldout"][0]: "relevant"}
    with pytest.raises(ValueError):
        sample.fit_threshold(leaked, {r["key"]: r for r in _fake_results()}, heldout=set(s["heldout"]))


# ---- W6: an exclusion applied after the score ----------------------------------------------------
def test_w6_excluded_title_is_rejected_whatever_the_score(flt):
    p = posting("w6", "Engineering Manager, Machine Learning", FILLER + "<p>Python and AWS every day.</p>")
    r = score.score(p, flt)
    assert r["score"] == 5.5                  # 3 role + 2 skills + 0.5 any-skill
    assert r["decision"] == "rejected"
    assert r["excluded_by"] == ["Manager"]
    assert score.shortlist([r], latest_keys={r["key"]}, n=10) == []


# ---- the rest of R1-R14, checked on constructed postings ------------------------------------------
def test_seniority_word_subtracts_two(flt):
    p = posting("s1", "Staff Data Engineer", FILLER + "<p>Python required.</p>")
    r = score.score(p, flt)
    assert r["score"] == 2.5 and r["decision"] == "rejected" and r["seniority"] == ["Staff"]


def test_no_skill_is_never_kept_even_above_threshold(flt):
    p = posting("s2", "AI Engineer", FILLER + "<p>An MS is a plus.</p>")
    r = score.score(p, flt)
    assert r["score"] == 3.5 and r["decision"] == "rejected"


def test_unshipped_skills_do_not_satisfy_the_skill_rule(flt):
    p = posting("s3", "ML Engineer", FILLER + "<p>Ray and Kubeflow.</p>")
    r = score.score(p, flt)
    assert r["skills"] == [] and r["skills_unshipped"] == ["Ray", "Kubeflow"] and r["decision"] == "rejected"


def test_security_clearance_excludes(flt):
    p = posting("s4", "AI Engineer", FILLER + "<p>Python. An active security clearance is required.</p>")
    r = score.score(p, flt)
    assert r["decision"] == "rejected" and r["excluded_by"] == ["security clearance"]


def test_location_never_decides(flt):
    boston = score.score(posting("s5", "AI Engineer", FILLER + "<p>Python.</p>", location="Boston, MA"), flt)
    tokyo = score.score(posting("s6", "AI Engineer", FILLER + "<p>Python.</p>", location="Tokyo"), flt)
    assert boston["score"] == tokyo["score"] == 4.5 and boston["decision"] == tokyo["decision"] == "kept"


def test_every_result_records_the_filter_version_and_hash(flt):
    r = score.score(posting("s7", "AI Engineer", FILLER + "<p>Python.</p>"), flt)
    assert r["filter_version"] == flt["filter_version"] and len(r["filter_sha256"]) == 64
