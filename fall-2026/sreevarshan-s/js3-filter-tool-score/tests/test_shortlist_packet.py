import pytest

from js3 import build_shortlist_packet as bsp
from js3.sample_for_audit import OverwriteRefused


def greenhouse(title, location="San Francisco, California", company="Databricks"):
    return {
        "id": 1,
        "title": title,
        "company_name": company,
        "absolute_url": "https://example.test/job/1",
        "location": {"name": location},
        "metadata": [{"name": "Career Page Posting Category", "value": ["Engineering"]}],
    }


def lever(title, who="", additional="", country="US", commitment="Permanent"):
    return {
        "id": "abc",
        "text": title,
        "hostedUrl": "https://jobs.lever.co/x/abc",
        "descriptionPlain": "About the team.",
        "lists": [{"text": "Who You Are", "content": f"<li>{who}</li>"}],
        "additionalPlain": additional,
        "country": country,
        "categories": {"location": "New York, NY", "commitment": commitment},
    }


def claims(board, job):
    return bsp.label_claims(board, bsp._evidence(board, job))


# --- Never infer from company name or title alone ---------------------------

def test_greenhouse_ml_title_at_ml_company_does_not_establish_skills_or_visa():
    c = claims("databricks", greenhouse("Machine Learning Engineer"))
    assert c["role_type"]["proposed"] == "supported"          # the title says so
    for key in ("asks_python", "years_within_reach", "offers_sponsorship",
                "no_clearance", "masters_ok", "regular_role", "early_career_level"):
        assert c[key]["proposed"] == "insufficient", key


def test_missing_description_is_listed_as_missing():
    ev = bsp._evidence("stripe", greenhouse("Data Scientist", location="N/A"))
    assert any(m.startswith("content") for m in ev["missing_fields"])
    assert "location.name" in ev["missing_fields"]
    assert claims("stripe", greenhouse("Data Scientist", location="N/A"))["us_location"]["proposed"] == "insufficient"


def test_lever_silence_on_sponsorship_is_insufficient_not_supported():
    c = claims("spotify", lever("Machine Learning Engineer", who="Python and SQL."))
    assert c["offers_sponsorship"]["proposed"] == "insufficient"
    assert c["no_clearance"]["proposed"] == "insufficient"


# --- Supported / contradicted need the posting's own words -------------------

def test_explicit_no_sponsorship_is_contradicted_with_quote():
    c = claims("spotify", lever("Data Engineer", additional="We are unable to sponsor visas for this role."))
    assert c["offers_sponsorship"]["proposed"] == "contradicted"
    assert "unable to sponsor" in c["offers_sponsorship"]["quote"]


def test_clearance_requirement_is_contradicted():
    c = claims("spotify", lever("Data Engineer", who="An active Secret clearance is required."))
    assert c["no_clearance"]["proposed"] == "contradicted"


def test_years_requirement_quotes_the_span():
    c = claims("spotify", lever("Data Scientist", who="You have 5+ years of experience."))
    assert c["years_within_reach"]["proposed"] == "contradicted"
    assert "5+ years" in c["years_within_reach"]["quote"]


def test_python_listed_as_an_alternative_is_flagged():
    c = claims("spotify", lever("Data Scientist", who="Fluent in SQL and Python or R."))
    assert c["asks_python"]["proposed"] == "supported"
    assert "alternatives" in c["asks_python"]["note"]


def test_title_level_words():
    assert claims("stripe", greenhouse("Staff Machine Learning Engineer"))["early_career_level"]["proposed"] == "contradicted"
    phd = claims("stripe", greenhouse("PhD Machine Learning Engineer, Intern"))
    assert phd["masters_ok"]["proposed"] == "contradicted"
    assert phd["regular_role"]["proposed"] == "contradicted"


def test_function_word_blocks_role_type_support():
    c = claims("databricks", greenhouse("Specialist Solutions Architect - Data Engineering"))
    assert c["role_type"]["proposed"] == "insufficient"


def test_non_us_location_is_contradicted():
    assert claims("stripe", greenhouse("Data Scientist", location="Toronto"))["us_location"]["proposed"] == "contradicted"


# --- Packet build and overwrite guard ----------------------------------------

def test_build_uses_only_passed_postings():
    results = {
        "databricks": [
            {"id": 1, "passed": True, "reason": "title_match", "matched_words": {"role": ["machine learning"], "topic": [], "reject": []}},
            {"id": 2, "passed": False, "reason": "no_match", "matched_words": {"role": [], "topic": [], "reject": []}},
        ],
        "stripe": [], "spotify": [],
    }
    raw = {"databricks": [greenhouse("Machine Learning Engineer"), {**greenhouse("Recruiter"), "id": 2}],
           "stripe": [], "spotify": []}
    packet = bsp.build(results, raw)
    assert [p["id"] for p in packet["postings"]] == [1]
    assert all(lab["my_label"] == "" for lab in packet["postings"][0]["claims"].values())
    assert "pending human review" in packet["status"]


def test_edited_packet_is_not_overwritten(tmp_path):
    md = tmp_path / "shortlist_packet.md"
    md.write_text("| claim | supported | ... | | supported |\n")  # a reviewer's edits
    with pytest.raises(OverwriteRefused):
        bsp.write_outputs({md: "fresh packet"})
    assert "supported |" in md.read_text()
