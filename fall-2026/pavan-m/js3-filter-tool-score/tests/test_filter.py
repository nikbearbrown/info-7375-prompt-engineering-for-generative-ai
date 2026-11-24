from agent.filter import score_posting

# 60 neutral words, so descriptions pass the 50-word rule (FILTER.md §2.6)
FILLER = " ".join(["team"] * 60)


def post(title="Software Engineer", location="San Francisco, CA", content=""):
    return {"title": title, "location": location, "content": content + " " + FILLER}


# ---------- Wrong versions (FILTER.md §5) ----------

def test_wv1_java_does_not_match_javascript():
    r = score_posting(post(content="We build with JavaScript and TypeScript."))
    assert "Programming" not in r["categories"]


def test_wv2_title_alone_does_not_qualify():
    r = score_posting(post(content="Frontend work with React and CSS."))
    assert r["decision"] == "REJECT"


def test_wv3_repetition_does_not_raise_score():
    once = score_posting(post(content="Java"))
    many = score_posting(post(content=" ".join(["Java"] * 30)))
    assert many["score"] == once["score"]
    assert many["categories"] == ["Programming"]


def test_wv4_missing_description_is_cannot_tell_not_reject():
    r = score_posting({"title": "Software Engineer", "location": "San Francisco, CA", "content": ""})
    assert r["decision"] == "CANNOT TELL"
    assert r["score"] is None


def test_wv5_matching_is_case_insensitive():
    for word in ("kafka", "KAFKA", "Kafka"):
        r = score_posting(post(content=f"{word} pipelines"))
        assert "Messaging" in r["categories"]


# ---------- Key rules ----------

def test_strong_match_is_kept_with_the_expected_score():
    r = score_posting(post(content="Java, Kafka, Docker and AWS."))
    # Title 4 + location 2 + 4 categories = 10
    assert r["decision"] == "KEEP" and r["score"] == 10


def test_eight_plus_years_is_rejected():
    r = score_posting(post(content="Java, Kafka, Docker, AWS. Minimum of 8 years of experience."))
    assert r["decision"] == "REJECT"


def test_five_years_is_not_rejected_by_the_years_rule():
    r = score_posting(post(content="Java, Kafka, Docker, AWS. 5+ years of experience."))
    assert r["decision"] == "KEEP"


def test_engineering_manager_is_rejected():
    r = score_posting(post(title="Engineering Manager", content="Java, Kafka, Docker, AWS."))
    assert r["decision"] == "REJECT"


def test_senior_title_is_flagged_not_rejected():
    r = score_posting(post(title="Senior Software Engineer", content="Java, Kafka, Docker, AWS."))
    assert r["decision"] == "KEEP"
    assert "review: senior/lead" in r["flags"]


def test_plain_remote_is_cannot_tell():
    r = score_posting(post(location="Remote", content="Java, Kafka, Docker, AWS."))
    assert r["decision"] == "CANNOT TELL"


def test_non_us_only_is_rejected():
    r = score_posting(post(location="London, United Kingdom", content="Java, Kafka, Docker, AWS."))
    assert r["decision"] == "REJECT"


def test_short_description_is_cannot_tell():
    r = score_posting({
        "title": "Software Engineer",
        "location": "San Francisco, CA",
        "content": "Java and Kafka role."
    })
    assert r["decision"] == "CANNOT TELL"


def test_spring_alone_is_not_spring_boot():
    r = score_posting(post(content="Spring 2027 internship cohort."))
    assert "Frameworks" not in r["categories"]


def test_html_entities_decoded_before_matching():
    r = score_posting(post(content="&lt;li&gt;Kafka&lt;/li&gt;&lt;li&gt;Docker&lt;/li&gt;"))
    assert "Messaging" in r["categories"] and "Containers" in r["categories"]
