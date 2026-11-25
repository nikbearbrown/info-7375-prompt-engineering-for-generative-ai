"""Tests for the FILTER.md v1.0 score, written before js3/filter.py existed.

Every posting here is CONSTRUCTED test data, not an observed posting.
Each expected number is computed by hand from FILTER.md §1 in the comment beside it.
"""
import pytest

from js3.filter import load_filter, score_posting

V1 = load_filter("v1.0")


def P(title, text, board="figma", provider="greenhouse", pid="t1", location="Boston, MA"):
    return {"key": f"{provider}:{board}:{pid}", "provider": provider, "board": board, "id": pid,
            "title": title, "text": text, "location": location, "departments": []}


def test_hand_example_core_role_keep():
    # R: "machine learning engineer" core +4; S 0; T: python, llm, agents, ml (from title) = 4 (cap 4);
    # E 0; Y: "1+ years" -> N=1 -> 0. Total 8 -> keep.
    r = score_posting(P("Machine Learning Engineer", "You will build LLM agents in Python. 1+ years of experience."), V1)
    assert (r["parts"]["R"]["points"], r["parts"]["S"]["points"], r["parts"]["T"]["points"],
            r["parts"]["E"]["points"], r["parts"]["Y"]["points"]) == (4, 0, 4, 0, 0)
    assert r["score"] == 8 and r["verdict"] == "keep"


def test_threshold_boundary_6_keeps_5_rejects():
    # Software engineer +2; python, sql, aws, machine learning = 4 groups -> 6 -> keep.
    keep = score_posting(P("Software Engineer", "Python and SQL on AWS for machine learning."), V1)
    assert keep["score"] == 6 and keep["verdict"] == "keep"
    # Drop one group (aws): 2 + 3 = 5 -> reject.
    rej = score_posting(P("Software Engineer", "Python and SQL for machine learning."), V1)
    assert rej["score"] == 5 and rej["verdict"] == "reject"


def test_highest_role_tier_only():
    # "ml engineer" (+4) and "data engineer" (+2) both match; take the highest, not the sum.
    r = score_posting(P("ML Engineer / Data Engineer", "Nothing else."), V1)
    assert r["parts"]["R"]["points"] == 4


def test_no_role_phrase_cannot_reach_threshold():
    # R 0 + T capped 4 + E 1 = 5 < 6.
    r = score_posting(P("Solutions Consultant", "New grad welcome. Python SQL LLM agents AWS machine learning."), V1)
    assert r["score"] == 5 and r["verdict"] == "reject"


# W1 — substring matching
def test_w1_whole_word_only():
    r = score_posting(P("HTML Email Developer, Leading Edge",
                        "PostgreSQL and NoSQL. Maintain pythonic code. Managers welcome. Agentless."), V1)
    assert r["parts"]["R"]["points"] == 0
    assert r["parts"]["S"]["points"] == 0          # "leading" is not "lead"
    assert r["parts"]["T"]["points"] == 0          # no ml / sql / python / agent whole words


# W2 — employer name as topic
def test_w2_employer_word_ignored_on_own_board():
    text = "Python on Databricks."
    on_db = score_posting(P("Software Engineer", text, board="databricks"), V1)
    on_fg = score_posting(P("Software Engineer", text, board="figma"), V1)
    assert on_fg["parts"]["T"]["points"] == 2      # python + data platform
    assert on_db["parts"]["T"]["points"] == 1      # python only; "databricks" ignored on its own board


# W3 — raw mention count instead of distinct, capped groups
def test_w3_distinct_groups_and_cap():
    many = score_posting(P("Software Engineer", "python " * 20), V1)
    assert many["parts"]["T"]["points"] == 1
    all_groups = score_posting(P("Software Engineer",
                                 "python sql llm agents machine learning evaluation delta lake aws"), V1)
    assert all_groups["parts"]["T"]["uncapped"] == 8
    assert all_groups["parts"]["T"]["points"] == 4


# W4 — missing description becomes a reject
@pytest.mark.parametrize("text", ["", "   ", None, "<p></p>", "!!! ---"])
def test_w4_missing_description_is_cannot_tell(text):
    r = score_posting(P("AI Engineer", text), V1)
    assert r["verdict"] == "cannot_tell"
    assert "posting.description" in r["missing"]


def test_missing_title_is_cannot_tell_without_score():
    r = score_posting(P("", "Python LLM"), V1)
    assert r["verdict"] == "cannot_tell" and r["score"] is None


# W5 — seniority read from the description
def test_w5_level_from_title_only():
    r = score_posting(P("AI Engineer", "Work with senior engineers and a staff architect. Python, LLM."), V1)
    assert r["parts"]["S"]["points"] == 0
    assert r["score"] == 6 and r["verdict"] == "keep"


def test_level_and_intern_penalties():
    assert score_posting(P("Sr. AI Engineer", "Python LLM"), V1)["parts"]["S"]["points"] == -6
    assert score_posting(P("AI Engineer Intern", "Python LLM"), V1)["parts"]["S"]["points"] == -6


@pytest.mark.parametrize("text,n,points", [
    ("5+ years of experience", 5, -3),
    ("3-5 years of experience", 3, -1),
    ("4 yrs building systems", 4, -1),
    ("2 years of experience; 7+ years preferred", 2, 0),
    ("no stated requirement", None, 0),
    ("We were founded 2015 and have 1000 employees", None, 0),
])
def test_years_rule(text, n, points):
    r = score_posting(P("AI Engineer", text), V1)
    assert r["parts"]["Y"]["N"] == n
    assert r["parts"]["Y"]["points"] == points


def test_early_career_signal():
    assert score_posting(P("AI Engineer", "New grad role."), V1)["parts"]["E"]["points"] == 1
    assert score_posting(P("AI Engineer", "Entry-level role."), V1)["parts"]["E"]["points"] == 1


def test_every_match_carries_field_and_quote():
    r = score_posting(P("AI Engineer", "Ship Python services. Evaluate LLM quality."), V1)
    for g in r["parts"]["T"]["groups"]:
        assert g["field"] in ("posting.title", "posting.description")
        assert g["phrase"] in g["quote"].lower().replace("-", " ")
