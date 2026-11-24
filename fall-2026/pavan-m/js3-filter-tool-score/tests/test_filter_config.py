
from agent.filter import score_posting

FILLER = " ".join(["team"] * 60)


def post(title="Software Engineer", location="San Francisco, CA", content=""):
    return {"title": title, "location": location, "content": content + " " + FILLER}


# ---------- C1: years cutoff ----------

def test_c1_default_cutoff_is_still_8():
    r = score_posting(post(content="Java, Kafka, Docker, AWS. 5+ years of experience."))
    assert r["decision"] == "KEEP"


def test_c1_cutoff_5_rejects_five_plus_years():
    r = score_posting(
        post(content="Java, Kafka, Docker, AWS. 5+ years of experience."),
        config={"years_cutoff": 5}
    )
    assert r["decision"] == "REJECT"


def test_c1_cutoff_5_still_ignores_preferred_years():
    r = score_posting(
        post(content="Java, Kafka, Docker, AWS. 5+ years of experience preferred."),
        config={"years_cutoff": 5}
    )
    assert r["decision"] == "KEEP"


# ---------- C3: other US cities ----------

def test_c3_default_other_us_city_gets_0():
    r = score_posting(post(location="New York, NY", content="Java, Kafka, Docker."))
    # Title 4 + location 0 + 3 categories = 7
    assert r["score"] == 7
    assert r["decision"] == "REJECT"


def test_c3_other_us_city_gets_2_when_configured():
    r = score_posting(
        post(location="New York, NY", content="Java, Kafka, Docker."),
        config={"other_us_city_points": 2}
    )
    assert r["score"] == 9
    assert r["decision"] == "KEEP"


def test_c3_does_not_help_non_us():
    r = score_posting(
        post(location="London, United Kingdom", content="Java, Kafka, Docker."),
        config={"other_us_city_points": 2}
    )
    assert r["decision"] == "REJECT"
