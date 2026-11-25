from js3.filter import Filter, load_postings


def lever(title, description="", lists=None):
    return {
        "id": "lever-1",
        "text": title,
        "descriptionPlain": description,
        "lists": lists or [],
    }


def greenhouse(title, metadata=None):
    return {"id": 1, "title": title, "location": {"name": "Remote"}, "metadata": metadata or []}


# --- Wrong version A: topic-only filter -------------------------------------

def test_ml_recruiter_with_topic_words_is_rejected():
    r = Filter.evaluate(lever("ML Recruiter", "You will hire Python, Spark and SQL engineers."))
    assert r["passed"] is False
    assert r["reason"] == "hard_reject"
    assert "recruiter" in r["matched_words"]["reject"]


def test_legal_ops_with_python_is_rejected():
    r = Filter.evaluate(lever("Legal Ops", "Python experience a plus."))
    assert r["passed"] is False
    assert r["reason"] == "hard_reject"


def test_topic_words_alone_do_not_pass_non_target_title():
    r = Filter.evaluate(lever("Marketing Coordinator", "Uses SQL and Python daily."))
    assert r["passed"] is False
    assert r["reason"] == "no_match"


# --- Wrong version B: case sensitivity --------------------------------------

def test_mixed_case_machine_learning_engineer_passes():
    r = Filter.evaluate(greenhouse("Machine Learning Engineer"))
    assert r["passed"] is True
    assert r["reason"] == "title_match"
    assert "machine learning" in r["matched_words"]["role"]


def test_upper_case_title_and_topic_words_match():
    r = Filter.evaluate(lever("SENIOR DATA ENGINEER", "PYTHON and AIRFLOW."))
    assert r["passed"] is True
    assert r["reason"] == "title_and_topic"
    assert set(r["matched_words"]["topic"]) == {"python", "airflow"}


# --- Hard rejects ------------------------------------------------------------

def test_hard_rejects_beat_role_words():
    for title in [
        "Machine Learning Manager",
        "Director, Data Platform",
        "VP of Machine Learning",
        "Head of Data Engineering",
        "Data Science Executive",
    ]:
        r = Filter.evaluate(greenhouse(title))
        assert r["passed"] is False, title
        assert r["reason"] == "hard_reject", title


def test_principal_rejected_unless_engineer_or_scientist():
    assert Filter.evaluate(greenhouse("Principal, ML Platform"))["reason"] == "hard_reject"
    assert Filter.evaluate(greenhouse("Principal ML Engineer"))["passed"] is True
    assert Filter.evaluate(greenhouse("Principal Data Scientist"))["passed"] is True


def test_vp_does_not_fire_inside_other_words():
    r = Filter.evaluate(greenhouse("Data Engineer, MVP Team"))
    assert r["passed"] is True


# --- Software engineer pairing ----------------------------------------------

def test_software_engineer_alone_fails():
    r = Filter.evaluate(lever("Software Engineer", "Build great products for listeners."))
    assert r["passed"] is False
    assert r["reason"] == "no_match"


def test_software_engineer_without_description_fails():
    r = Filter.evaluate(greenhouse("Software Engineer"))
    assert r["passed"] is False
    assert r["reason"] == "no_match"
    assert r["topic_evidence"] == "insufficient"


def test_software_engineer_with_python_in_description_passes():
    r = Filter.evaluate(lever("Software Engineer", "Our backend is written in Python."))
    assert r["passed"] is True
    assert r["reason"] == "title_and_topic"
    assert r["matched_words"]["topic"] == ["python"]


def test_software_engineer_with_topic_in_lists_passes():
    r = Filter.evaluate(lever(
        "Software Engineer",
        "Join us.",
        lists=[{"text": "What you'll do", "content": "<li>Run Kafka pipelines</li>"}],
    ))
    assert r["passed"] is True
    assert "kafka" in r["matched_words"]["topic"]


def test_software_engineer_with_topic_in_greenhouse_metadata_passes():
    r = Filter.evaluate(greenhouse(
        "Software Engineer",
        metadata=[{"id": 1, "name": "Team", "value": "Spark Runtime", "value_type": "short_text"}],
    ))
    assert r["passed"] is True
    assert r["matched_words"]["topic"] == ["spark"]


# --- Greenhouse title-only path ---------------------------------------------

def test_greenhouse_without_description_passes_on_title_alone():
    r = Filter.evaluate(greenhouse("Data Engineer"))
    assert r["passed"] is True
    assert r["reason"] == "title_match"
    assert r["description_available"] is False
    assert r["topic_evidence"] == "insufficient"


def test_role_word_matches_longer_word_form():
    assert Filter.evaluate(greenhouse("Data Engineering Intern"))["passed"] is True


def test_etl_does_not_fire_inside_other_words():
    r = Filter.evaluate(lever("Software Engineer", "Payments settlement and reconciliation."))
    assert r["passed"] is False
    assert r["matched_words"]["topic"] == []


# --- Missing fields ----------------------------------------------------------

def test_missing_title_does_not_crash():
    r = Filter.evaluate({"id": 7})
    assert r["passed"] is False
    assert r["reason"] == "no_match"
    assert r["title"] == ""


def test_null_and_odd_shaped_fields_do_not_crash():
    r = Filter.evaluate({"title": None, "lists": None, "metadata": [{"value": None}, "x"]})
    assert r["reason"] == "no_match"
    assert Filter.evaluate({"text": "Data Scientist", "lists": ["python"]})["passed"] is True


# --- Loaders -----------------------------------------------------------------

def test_load_greenhouse_format():
    raw = {"jobs": [greenhouse("Data Engineer"), greenhouse("Recruiter")], "meta": {"total": 2}}
    results = Filter.from_raw(raw).run()
    assert [r["passed"] for r in results] == [True, False]


def test_load_lever_format():
    raw = [lever("Data Scientist", "pytorch"), lever("Software Engineer")]
    results = Filter.from_raw(raw).run()
    assert [r["reason"] for r in results] == ["title_and_topic", "no_match"]


def test_load_empty_or_unknown_payload_returns_no_postings():
    assert load_postings({"jobs": []}) == []
    assert load_postings({"meta": {}}) == []
    assert load_postings(None) == []
