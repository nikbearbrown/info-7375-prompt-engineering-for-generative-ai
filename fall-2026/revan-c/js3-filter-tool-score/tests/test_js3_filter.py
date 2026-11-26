"""JS3 filter tests, written from FILTER.md v1 (0e15e65) before any JS3 implementation.

All postings are CONSTRUCTED fixtures (tests/js3_support.py), not board results.
Test names W1-W5 are the ones FILTER.md section 4 promises.
"""
import pytest

from jsfilter import filter as F
from js3_support import gh_body, gh_job, lever_body, lever_posting, resume


def score(job, board="klaviyo"):
    loaded = F.load_board(board, "greenhouse", gh_body(job), "fixture.body")
    assert loaded["status"] == "ok"
    return F.score_posting(resume(), loaded["postings"][0])


# ---- FILTER.md section 4, wrong versions -------------------------------------------------

def test_topic_cannot_bypass_role_title():
    """W1: topic words and skills in a non-target title never reach the shortlist."""
    # The title must fail R1 and nothing else, or another rule hides the bypass (found by the mutant check,
    # 2026-11-25: the first fixture said "Manager", so R2 rejected it and the W1 mutant survived).
    job = gh_job(1, title="Product Marketing Specialist, Platform",
                 content="<p>Platform, API, cloud, backend infrastructure. Python, SQL, AWS, Docker.</p>")
    row = score(job)
    assert row["failed_rules"] == ["R1"]
    assert row["fate"] == "hard_rule_reject"
    assert row["components"]["role"] == 0


def test_two_distinct_bounded_skills():
    """W2: Java is not JavaScript, SQL is not inside PostgreSQL, a repeat counts once."""
    only_false_friends = gh_job(2, content="<p>Backend work in JavaScript and PostgreSQL.</p>")
    row = score(only_false_friends)
    assert set(row["rules"]["R6"]["matched"]) == {"PostgreSQL"}
    assert row["rules"]["R6"]["passed"] is False

    repeated = gh_job(3, content="<p>Backend: Python. More Python. Python again.</p>")
    row = score(repeated)
    assert row["rules"]["R6"]["matched"] == ["Python"]
    assert row["components"]["skill"] == 1
    assert row["rules"]["R6"]["passed"] is False


def test_score_descending_and_stable_ties():
    """W3: kept postings sort by total descending, then board, then id ascending; never input order."""
    rows = [
        {"board": "patchmypc", "id": "b", "total": 7, "fate": "kept"},
        {"board": "klaviyo", "id": "9", "total": 6, "fate": "kept"},
        {"board": "klaviyo", "id": "10", "total": 7, "fate": "kept"},
        {"board": "duolingo", "id": "5", "total": 7, "fate": "kept"},
        {"board": "klaviyo", "id": "1", "total": 8, "fate": "below_threshold"},
    ]
    ranked = F.rank(rows)
    assert [(r["board"], r["id"]) for r in ranked] == [
        ("duolingo", "5"), ("klaviyo", "10"), ("patchmypc", "b"), ("klaviyo", "9")]
    assert F.rank(list(reversed(rows))) == ranked


def test_missing_board_is_unknown():
    """W4: an empty, malformed, or missing board is `unknown`, never zero relevant postings."""
    for raw in (b'{"jobs": []}', b"not json", None):
        loaded = F.load_board("klaviyo", "greenhouse", raw, "fixture.body")
        assert loaded["status"] == "unknown"
        assert loaded["error"]
        assert loaded["postings"] == []
    result = F.run_filter(resume(), [F.load_board("klaviyo", "greenhouse", b'{"jobs": []}', "x")])
    assert result["boards"]["klaviyo"]["status"] == "unknown"
    assert result["boards"]["klaviyo"]["kept"] == "unknown"
    assert result["boards"]["klaviyo"]["scored"] == "unknown"


def test_score_does_not_entail_claim():
    """W5: a kept posting's claims start `not reviewed`; nothing is published as fact without `supported`."""
    from jsfilter import shortlist as S
    job = gh_job(4, title="Backend Engineer",
                 content="<p>About us: our platform team once used Python, AWS and Docker. "
                         "This role builds backend APIs on our cloud infrastructure.</p>")
    row = score(job)
    assert row["fate"] == "kept"
    claims = S.draft_claims(row)
    assert claims, "a kept posting must get claims to review"
    assert all(c["label"] == "not reviewed" for c in claims)
    assert S.publishable(claims) == []
    assert S.render(row, claims).startswith("I cannot tell from this posting")
    claims[0]["label"] = "supported"
    claims[0]["reviewer"] = "Revan C."
    assert S.publishable(claims) == [claims[0]]


def test_location_claims_are_atomic():
    """A Boston location and Massachusetts remote eligibility need separate evidence labels."""
    from jsfilter import shortlist as S
    row = score(gh_job(40, title="Backend Engineer"))
    claims = S.draft_claims(row, "Backend APIs in Boston. Python and AWS.")
    location = [c for c in claims if c["kind"] == "location"]
    assert [c["claim"] for c in location] == [
        "The posting names Boston as a job location.",
        "A Boston resident may work fully remotely in this role.",
    ]
    assert all(c["label"] == "not reviewed" for c in location)


def test_remote_eligibility_quote_includes_full_state_list():
    from jsfilter import shortlist as S
    text = "To be eligible for consideration, candidates for fully remote positions must reside in one of the following U.S. states: AL, NY, WY."
    assert S._remote_eligibility_passage(text) == text


def test_years_quote_stays_on_the_requirement_line():
    from jsfilter import shortlist as S
    text = ("Design and develop AI agents across the portfolio\n"
            "Bachelor's degree in Computer Science or equivalent experience\n"
            "5+ years of professional software development with C# and the .NET ecosystem\n"
            "Familiarity with an AI agent framework")
    assert S._years_passage(text) == "5+ years of professional software development with C# and the .NET ecosystem"


# ---- Rules R1-R6 -------------------------------------------------------------------------

def test_role_phrase_is_whole_words_and_weighted():
    assert score(gh_job(5, title="Backend Engineer"))["components"]["role"] == 3
    assert score(gh_job(6, title="Platform Engineer II"))["components"]["role"] == 3
    assert score(gh_job(7, title="Software Engineer, Payments"))["components"]["role"] == 2
    assert score(gh_job(8, title="Site Reliability Engineer"))["components"]["role"] == 2
    # Highest match wins.
    assert score(gh_job(9, title="Software Engineer - Backend Engineer track"))["components"]["role"] == 3
    # "devops engineering" does not contain the complete phrase "devops engineer".
    assert score(gh_job(10, title="DevOps Engineering Lead"))["rules"]["R1"]["passed"] is False


def test_seniority_and_role_type_exclusions_are_whole_words():
    for title in ("Senior Software Engineer", "Sr. Software Engineer", "Staff Backend Engineer",
                  "Software Engineer, Engineering Manager track", "Lead Platform Engineer"):
        row = score(gh_job(11, title=title))
        assert row["rules"]["R2"]["passed"] is False, title
        assert row["fate"] == "hard_rule_reject"
    for title in ("Software Engineer, Frontend", "Software Engineer - Front End",
                  "Software Engineer II, Mobile", "iOS Software Engineer", "Android Software Engineer"):
        assert score(gh_job(12, title=title))["rules"]["R3"]["passed"] is False, title
    # Whole words only: "leader" is not "lead", "Staffing" is not "staff".
    assert score(gh_job(13, title="Software Engineer, Staffing Platform Leaders"))["rules"]["R2"]["passed"] is True


def test_location_boston_or_explicit_remote():
    assert score(gh_job(14, location="Boston, MA; Denver, CO"))["rules"]["R4"]["passed"] is True
    assert score(gh_job(15, location="Remote - US"))["rules"]["R4"]["passed"] is True
    for loc in ("United States", "Eastern Timezone", "New York, NY", "Bostonia, CA"):
        assert score(gh_job(16, location=loc))["rules"]["R4"]["passed"] is False, loc


def test_lever_remote_from_workplace_type_and_all_description_fields():
    body = lever_body(
        lever_posting("lev-1", location="United States", workplace_type="remote",
                      description="<div>Backend APIs.</div>", lists=["<li>Python</li>"],
                      additional="<p>Kubernetes</p>"),
        lever_posting("lev-2", location="United States", workplace_type="onsite"),
    )
    loaded = F.load_board("patchmypc", "lever", body, "fixture.body")
    rows = {p["id"]: F.score_posting(resume(), p) for p in loaded["postings"]}
    assert rows["lev-1"]["rules"]["R4"]["passed"] is True
    assert set(rows["lev-1"]["rules"]["R6"]["matched"]) == {"Python", "Kubernetes"}
    assert rows["lev-2"]["rules"]["R4"]["passed"] is False


def test_topic_fit_counts_distinct_phrases_capped_at_two():
    assert score(gh_job(17, content="<p>Python and SQL.</p>"))["components"]["topic"] == 0
    assert score(gh_job(18, content="<p>Our API. Python and SQL. API again.</p>"))["components"]["topic"] == 1
    row = score(gh_job(19, content="<p>Backend, back end, API, cloud. Python and SQL.</p>"))
    assert row["components"]["topic"] == 2
    assert set(row["rules"]["R5"]["matched"]) == {"backend", "back end", "api", "cloud"}


def test_skill_fit_capped_at_three_and_familiar_not_counted():
    row = score(gh_job(20, content="<p>Backend: Python, SQL, AWS, Docker, Redis, Rust, Terraform.</p>"))
    assert row["components"]["skill"] == 3
    assert "Rust" not in row["rules"]["R6"]["matched"]
    assert "Terraform" not in row["rules"]["R6"]["matched"]


def test_threshold_six_and_fates():
    # role 2 + topic 1 + skill 2 = 5: every hard rule passes, total below 6.
    five = score(gh_job(21, title="Software Engineer", content="<p>API work. Python and SQL.</p>"))
    assert five["total"] == 5 and five["fate"] == "below_threshold"
    assert five["failed_rules"] == []
    # role 3 + topic 1 + skill 2 = 6: kept.
    six = score(gh_job(22, title="Backend Engineer", content="<p>API work. Python and SQL.</p>"))
    assert six["total"] == 6 and six["fate"] == "kept"
    # A high total does not override a hard rule.
    senior = score(gh_job(23, title="Senior Backend Engineer",
                          content="<p>Backend API cloud. Python, SQL, AWS.</p>"))
    assert senior["total"] == 8 and senior["fate"] == "hard_rule_reject"
    assert senior["failed_rules"] == ["R2"]


def test_missing_field_is_unscorable_not_zero():
    job = gh_job(24, url=False)
    loaded = F.load_board("klaviyo", "greenhouse", gh_body(job, gh_job(25)), "fixture.body")
    rows = {p["id"]: F.score_posting(resume(), p) for p in loaded["postings"]}
    assert rows["24"]["fate"] == "unscorable"
    assert rows["24"]["missing"] == ["url"]
    assert rows["24"]["total"] is None
    assert rows["25"]["fate"] != "unscorable"


def test_closest_calls_follow_filter_md():
    rows = [
        {"board": "k", "id": "a", "total": 5, "failed_rules": [], "fate": "below_threshold"},
        {"board": "k", "id": "b", "total": 6, "failed_rules": ["R2"], "fate": "hard_rule_reject"},
        {"board": "k", "id": "c", "total": 7, "failed_rules": ["R2", "R4"], "fate": "hard_rule_reject"},
        {"board": "k", "id": "d", "total": 4, "failed_rules": [], "fate": "below_threshold"},
        {"board": "k", "id": "e", "total": 5, "failed_rules": ["R4"], "fate": "hard_rule_reject"},
        {"board": "k", "id": "f", "total": None, "failed_rules": [], "fate": "unscorable"},
    ]
    assert [r["id"] for r in F.closest_calls(rows)] == ["a", "b"]


def test_key_is_board_and_id():
    a = F.load_board("klaviyo", "greenhouse", gh_body(gh_job(77, title="Backend Engineer")), "a")
    b = F.load_board("duolingo", "greenhouse", gh_body(gh_job(77, title="Accountant")), "b")
    result = F.run_filter(resume(), [a, b])
    keys = {(r["board"], r["id"]) for r in result["rows"]}
    assert keys == {("klaviyo", "77"), ("duolingo", "77")}


def test_audit_view_has_one_row_per_posting_with_source_and_fate():
    jobs = [gh_job(i, title=t) for i, t in enumerate(
        ["Backend Engineer", "Accountant", "Senior Software Engineer", "Software Engineer"], start=100)]
    result = F.run_filter(resume(), [F.load_board("klaviyo", "greenhouse", gh_body(*jobs), "src.body")])
    assert len(result["rows"]) == 4
    for row in result["rows"]:
        assert row["source_path"] == "src.body"
        assert row["fate"] in {"kept", "below_threshold", "hard_rule_reject", "unscorable"}
        assert set(row["rules"]) == {"R1", "R2", "R3", "R4", "R5", "R6"}
        assert "zero_topic" in row and "zero_skill" in row


def test_reject_sample_is_seeded_distinct_and_rejects_only():
    rows = [{"board": "k", "id": str(i), "fate": "hard_rule_reject" if i % 3 else "kept"} for i in range(90)]
    first = F.sample_rejects(rows, 30, seed="s")
    assert first == F.sample_rejects(rows, 30, seed="s")
    assert len({(r["board"], r["id"]) for r in first}) == 30
    assert all(r["fate"] in {"hard_rule_reject", "below_threshold"} for r in first)
    assert first != F.sample_rejects(rows, 30, seed="other")
    with pytest.raises(ValueError):
        F.sample_rejects(rows[:3], 30, seed="s")
