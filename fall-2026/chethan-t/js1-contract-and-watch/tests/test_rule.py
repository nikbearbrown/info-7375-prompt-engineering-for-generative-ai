from agent import rule


def verdict(postings, resume, case):
    return rule.judge(postings[case], resume)["verdict"]


# Role, seniority, experience

def test_01_software_engineer_boston_is_relevant(postings, resume):
    assert verdict(postings, resume, "swe_boston_plain") == "relevant"


def test_02_staff_title_is_not_relevant(postings, resume):
    assert verdict(postings, resume, "staff_swe_boston") == "not_relevant"


def test_03_senior_needing_5_years_is_not_relevant(postings, resume):
    assert verdict(postings, resume, "senior_swe_boston_5_years") == "not_relevant"


def test_04_senior_uses_smallest_years_found_is_relevant(postings, resume):
    # "6+ years" and "2+ years ... with Angular": the smallest number (2) decides.
    assert verdict(postings, resume, "senior_frontend_boston_6_and_2_years") == "relevant"


def test_05_senior_with_no_years_stated_is_not_relevant(postings, resume):
    assert verdict(postings, resume, "senior_swe_boston_no_years") == "not_relevant"


def test_06_non_engineering_title_is_not_relevant(postings, resume):
    assert verdict(postings, resume, "product_designer_boston") == "not_relevant"


# Location

def test_07_london_only_is_not_relevant(postings, resume):
    assert verdict(postings, resume, "swe_london") == "not_relevant"


def test_08_one_us_location_among_several_is_relevant(postings, resume):
    assert verdict(postings, resume, "swe_boston_and_london") == "relevant"


def test_08b_us_with_periods_is_relevant(postings, resume):
    # Contract v2.1: periods are ignored, so "U.S." counts as "US".
    assert verdict(postings, resume, "swe_remote_us_periods") == "relevant"


# Work authorization

def test_09_unable_to_sponsor_is_not_relevant(postings, resume):
    assert verdict(postings, resume, "swe_boston_unable_to_sponsor") == "not_relevant"


def test_10_us_citizen_required_in_escaped_html_is_not_relevant(postings, resume):
    assert verdict(postings, resume, "swe_boston_us_citizen_escaped") == "not_relevant"


# Wrong versions

def test_11_citizenship_status_footer_is_relevant(postings, resume):
    # Wrong version 1: "citizenship" matched as a single word.
    assert verdict(postings, resume, "swe_boston_citizenship_status_footer") == "relevant"


def test_12_brussels_is_not_relevant(postings, resume):
    # Wrong version 2: "US" matched as a substring of "Brussels".
    assert verdict(postings, resume, "swe_brussels") == "not_relevant"


# Wrong version 3: justification cites exactly the fields of the checks applied.

def test_13a_non_senior_cites_role_seniority_location_auth_fields(postings, resume):
    result = rule.judge(postings["swe_boston_plain"], resume)
    assert set(result["posting_fields"]) == {"title", "location.name", "content"}
    assert set(result["resume_fields"]) == {"target.roles", "target.locations", "work_authorization"}


def test_13b_senior_also_cites_experience_fields(postings, resume):
    result = rule.judge(postings["senior_frontend_boston_6_and_2_years"], resume)
    assert set(result["posting_fields"]) == {"title", "location.name", "content"}
    assert set(result["resume_fields"]) == {
        "target.roles", "experience", "target.locations", "work_authorization",
    }
