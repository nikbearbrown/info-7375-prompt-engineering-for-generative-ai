"""FILTER.md v0.1: one test per "Wrong versions" row (rows 1–5), G1–G5 pass/fail/unknown
cases, the score and verdicts, persona loading, normalization, and the CLI.

Every posting here is tiny and synthetic. Row 6 (claim labeling) is not built in step 1.
"""

import json

import pytest

from agent import filter as flt
from agent.postings import RunError, load_run, normalize_ashby, normalize_greenhouse

FILLER = " Our team builds products." * 10  # pads text past the 200-character minimum
PERSONA = {"skills": ["Python", "Java", "TypeScript", "SQL", "PostgreSQL", "Spring Boot", "React", "Docker", "AWS"],
           "target_titles": ["Software Engineer", "AI Engineer", "Backend Engineer"],
           "years_experience": 0, "needs_sponsorship": True, "work_country": "US"}


def posting(title="Software Engineer", locations=("San Francisco, CA",),
            text="You will build backend APIs and platform services in Python and Java. 2+ years of experience." + FILLER,
            board="greenhouse/stripe", pid=1):
    return {"board": board, "id": pid, "title": title,
            "locations": list(locations) if locations is not None else None,
            "text": text, "date": "2026-11-20", "url": "https://example.com/job"}


def verdict(**kw):
    return flt.evaluate(posting(**kw), PERSONA)


# ---------- FILTER.md "Wrong versions" ----------

def test_wrong_version_1_substring_matching():
    """Whole-word matching. "Engineering Manager" fails G1, and the seniority word also fails G2."""
    result = verdict(title="Engineering Manager")
    assert result["gates"]["G1"]["result"] == "fail"
    assert result["gates"]["G2"]["result"] == "fail" and result["gates"]["G2"]["matched"] == ["Manager"]
    assert result["verdict"] == "reject"
    # "AI Engineer" must not match inside "Dubai Engineer"; "AI" is not a word inside "maintain".
    assert flt.check_g1("Dubai Engineer")["result"] == "fail"
    assert flt._found("We maintain systems", ["AI"]) == []
    # "Software Engineering" is not "Software Engineer"; "Java" is not in "JavaScript".
    assert flt.check_g1("Software Engineering Generalist")["result"] == "fail"
    assert flt.score("JavaScript only. " + FILLER, ["Java"])["skills"]["matched"] == []


def test_wrong_version_2_exclusions_win():
    """G2 rejects "Senior Software Engineer" whatever G1 says, even with a top score."""
    result = verdict(title="Senior Software Engineer",
                     text="backend API platform infrastructure Python Java SQL AWS 1+ years" + FILLER)
    assert result["gates"]["G1"]["result"] == "pass"
    assert result["gates"]["G2"]["result"] == "fail"
    assert result["verdict"] == "reject" and result["first_failing_gate"] == "G2"
    assert result["score"] is None


@pytest.mark.parametrize("text", [None, "x" * 199], ids=["no-text", "199-chars"])
def test_wrong_version_3_missing_text_is_cannot_tell(text):
    """No-text postings are cannot_tell, counted separately."""
    result = verdict(text=text)
    assert result["verdict"] == "cannot_tell"
    assert result["text_status"] == ("missing" if text is None else "short")
    assert result["gates"]["G4"]["result"] == "unknown" and result["gates"]["G5"]["result"] == "unknown"
    summary = flt.summarize([result, verdict()], [], "run", "persona")
    assert summary["by_verdict"]["cannot_tell"] == 1 and summary["by_verdict"]["reject"] == 0
    assert summary["text_status"] == {result["text_status"]: 1, "ok": 1}


def test_wrong_version_3_text_boundary_and_title_rejects():
    """200 characters is enough text; a title gate (or G3, as confirmed 2026-11-21) still rejects."""
    assert verdict(text="2+ years of Python and backend work. ".ljust(200, "x"))["text_status"] == "ok"
    assert verdict(title="Account Executive", text=None)["verdict"] == "reject"
    assert verdict(title="Staff Software Engineer", text=None)["verdict"] == "reject"
    assert verdict(locations=["Dublin, Ireland"], text=None)["verdict"] == "reject"


@pytest.mark.parametrize("location", ["Remote", "Remote ", "remote", "N/A", "LOCATION", "na", "Remote/Hybrid"])
def test_wrong_version_4_bare_remote_is_cannot_tell(location):
    """A bare "Remote" (or placeholder) is cannot_tell, never a pass or a reject."""
    result = verdict(locations=[location])
    assert result["gates"]["G3"]["result"] == "unknown"
    assert result["verdict"] == "cannot_tell"


def test_wrong_version_5_length_bias_capped():
    """Each score term is capped at 3, so a long posting can't outscore a short one on length."""
    long_text = ("backend API distributed systems infrastructure platform full-stack LLM machine learning "
                 "Python Java TypeScript SQL PostgreSQL Spring Boot React Docker AWS 1+ years " * 20)
    short_text = "backend API platform Python Java SQL 1+ years" + FILLER
    long_score = flt.score(long_text, PERSONA["skills"])
    short_score = flt.score(short_text, PERSONA["skills"])
    assert len(long_score["topic"]["matched"]) == 8 and len(long_score["skills"]["matched"]) == 9
    assert long_score["topic"]["points"] == 3 and long_score["skills"]["points"] == 3
    assert long_score["total"] == short_score["total"] == 6


# ---------- G1 ----------

@pytest.mark.parametrize("title", ["Software Engineer", "Backend Engineer, Payments", "Back-End Engineer",
                                   "Full-Stack Engineer", "Full Stack Engineer", "software developer",
                                   "Machine Learning Engineer", "ML Engineer", "AI Engineer"])
def test_g1_pass(title):
    assert flt.check_g1(title)["result"] == "pass"


@pytest.mark.parametrize("title", ["Security Engineer", "Solutions Engineer", "Software Engineering Manager",
                                   "Sales Engineer", "Data Scientist"])
def test_g1_fail(title):
    assert flt.check_g1(title)["result"] == "fail"


def test_g1_g2_missing_title_unknown():
    assert flt.check_g1(None)["result"] == "unknown" and flt.check_g2(None)["result"] == "unknown"


# ---------- G2 ----------

@pytest.mark.parametrize("title", ["Sr. Software Engineer", "Staff Software Engineer", "Software Engineer, Intern",
                                   "Head of Engineering", "VP Engineering", "Lead Backend Engineer",
                                   "Principal ML Engineer", "Director, Software"])
def test_g2_fail(title):
    assert flt.check_g2(title)["result"] == "fail"


@pytest.mark.parametrize("title", ["Software Engineer, Internal Tools", "Software Engineer, Leadership Tools",
                                   "Backend Engineer, Headless Commerce", "Software Engineer"])
def test_g2_pass_whole_word(title):
    """"Internal", "Leadership" and "Headless" don't contain the whole words Intern, Lead, Head."""
    assert flt.check_g2(title)["result"] == "pass"


# ---------- G3 ----------

@pytest.mark.parametrize("locations", [["US-Remote"], ["San Francisco, California"], ["Remote in the US"],
                                       ["Dublin, Ireland", "New York, New York"], ["Chicago, Remote"],
                                       ["Seattle, WA"], ["Atlanta, Georgia"]])
def test_g3_pass(locations):
    assert flt.check_g3(locations)["result"] == "pass"


@pytest.mark.parametrize("locations", [["Dublin, Ireland"], ["Toronto, CA"], ["CA-Toronto; CA-Remote"],
                                       ["London OR Dublin"], ["Sweden (Remote)"], ["Europe"],
                                       ["IN-Bengaluru"]])
def test_g3_fail(locations):
    assert flt.check_g3(locations)["result"] == "fail"


@pytest.mark.parametrize("locations", [None, [], ["Remote"], ["North America"], ["AMER"],
                                       ["North America", "Europe"], ["Dublin, Ireland", "Remote"]])
def test_g3_unknown(locations):
    """Missing field, bare Remote, or a region that contains the US without naming it
    (confirmed reading, 2026-11-21) is unknown."""
    assert flt.check_g3(locations)["result"] == "unknown"


# ---------- G4 ----------

@pytest.mark.parametrize("text,expected,largest", [
    ("Requires 2+ years of experience.", "pass", 2),
    ("Requires 3+ years.", "pass", 3),
    ("Requires 4+ years.", "fail", 4),
    ("3–5 years of experience in backend work.", "pass", 3),   # a range is its minimum, not "5 years of"
    ("3-5 years of experience.", "pass", 3),
    ("At least 4 years in industry.", "fail", 4),
    ("4 years of experience with Go.", "fail", 4),
    ("1+ years with Python; 5+ years preferred for senior folks.", "fail", 5),  # the largest minimum
    ("No experience required.", "unknown", None),
    ("Two (2) years of experience.", "unknown", None),          # spelled-out numbers aren't a FILTER form
])
def test_g4(text, expected, largest):
    gate = flt.check_g4(text)
    assert gate["result"] == expected
    if largest is not None:
        assert max(n for _, n in flt.g4_minimums(text)) == largest


# ---------- G5 ----------

def test_g5_fail_pass_and_not_applicable():
    refusal = "We are unable to sponsor visas for this role." + FILLER
    assert flt.check_g5(refusal, True)["result"] == "fail"
    assert flt.check_g5("Without sponsorship, candidates must be authorized.", True)["result"] == "fail"
    assert flt.check_g5("Nothing about visas." + FILLER, True)["result"] == "pass"       # silence is not a no
    assert flt.check_g5("You will be the executive sponsor for key accounts.", True)["result"] == "pass"
    assert flt.check_g5(refusal, False)["result"] == "pass"                               # not applicable
    assert verdict(text=refusal + " 2+ years")["verdict"] == "reject"


# ---------- score and verdicts ----------

def test_keep_threshold_boundary():
    two = verdict(text="Python and AWS. 2+ years." + FILLER)                 # 0 topic + 2 skills = 2
    one = verdict(text="Python only. 2+ years." + FILLER)                    # 1
    zero = verdict(text="Spreadsheets. 2+ years." + FILLER)                  # 0
    assert two["score"]["total"] == 2 and two["verdict"] == "keep" and two["near_threshold"]
    assert one["score"]["total"] == 1 and one["verdict"] == "reject" and one["near_threshold"]
    assert one["first_failing_gate"] is None
    assert zero["score"]["total"] == 0 and zero["verdict"] == "reject" and not zero["near_threshold"]
    high = verdict(text="backend API platform Python Java SQL 2+ years" + FILLER)
    assert high["score"]["total"] == 6 and high["verdict"] == "keep" and not high["near_threshold"]


def test_unknown_gate_beats_score_and_fail_beats_unknown():
    assert verdict(locations=["Remote"], text="backend API platform Python Java SQL 2+ years" + FILLER)["verdict"] == "cannot_tell"
    result = verdict(title="Staff Software Engineer", locations=["Remote"])
    assert result["verdict"] == "reject" and result["first_failing_gate"] == "G2"


def test_result_records_every_gate_and_term():
    result = verdict()
    assert set(result["gates"]) == {"G1", "G2", "G3", "G4", "G5"}
    assert all(set(g) == {"result", "matched", "detail"} for g in result["gates"].values())
    assert result["gates"]["G1"]["matched"] == ["Software Engineer"]
    assert result["gates"]["G4"]["matched"] == ["2+ years"]
    assert result["score"]["topic"]["matched"] == ["backend", "platform"]  # "APIs" is not the word "API"
    assert result["score"]["skills"]["matched"] == ["Python", "Java"]


# ---------- persona ----------

def write_persona(tmp_path, **overrides):
    data = {"personal": {"name": "Fictional"}, "skills": ["Rust"],
            "job_search": {"target_titles": ["Software Engineer"], "years_experience": 0,
                           "needs_sponsorship": True, "work_country": "US"}}
    for dotted, value in overrides.items():
        node = data
        *parents, leaf = dotted.split("__")
        for part in parents:
            node = node[part]
        if value is ...:
            del node[leaf]
        else:
            node[leaf] = value
    path = tmp_path / "persona.json"
    path.write_text(json.dumps(data))
    return path


@pytest.mark.parametrize("field", ["skills", "job_search__target_titles", "job_search__years_experience",
                                   "job_search__needs_sponsorship", "job_search__work_country"])
def test_missing_persona_field_is_an_error(tmp_path, field):
    with pytest.raises(flt.PersonaError):
        flt.load_persona(write_persona(tmp_path, **{field: ...}))


@pytest.mark.parametrize("overrides", [{"skills": []}, {"job_search__years_experience": True},
                                       {"job_search__needs_sponsorship": "yes"}, {"job_search__work_country": "CA"},
                                       {"job_search__years_experience": 5},
                                       {"job_search__target_titles": ["Data Scientist"]}])
def test_persona_values_outside_filter_are_errors(tmp_path, overrides):
    with pytest.raises(flt.PersonaError):
        flt.load_persona(write_persona(tmp_path, **overrides))


def test_skills_come_from_the_persona_file(tmp_path):
    persona = flt.load_persona(write_persona(tmp_path))
    assert persona["skills"] == ["Rust"]
    result = flt.evaluate(posting(text="Rust and Python services. 2+ years." + FILLER), persona)
    assert result["score"]["skills"]["matched"] == ["Rust"]


def test_needs_sponsorship_false_makes_g5_not_applicable(tmp_path):
    persona = flt.load_persona(write_persona(tmp_path, job_search__needs_sponsorship=False))
    result = flt.evaluate(posting(text="Python. We will not sponsor. 2+ years." + FILLER), persona)
    assert result["gates"]["G5"]["result"] == "pass"


# ---------- normalization ----------

def test_greenhouse_normalization_unescapes_then_strips():
    job = {"id": 7, "title": " Software Engineer ", "location": {"name": "US-Remote"},
           "content": "&lt;p&gt;Python &amp;amp; Go&lt;/p&gt;&lt;ul&gt;&lt;li&gt;AWS&lt;/li&gt;&lt;li&gt;SQL&lt;/li&gt;&lt;/ul&gt;",
           "first_published": "", "updated_at": "2026-11-01T00:00:00-04:00", "absolute_url": "https://x/7"}
    p = normalize_greenhouse("greenhouse/stripe", job)
    assert p == {"board": "greenhouse/stripe", "id": 7, "title": "Software Engineer", "locations": ["US-Remote"],
                 "text": "Python & Go AWS SQL", "date": "2026-11-01T00:00:00-04:00", "url": "https://x/7"}


def test_missing_fields_become_null_never_empty():
    g = normalize_greenhouse("greenhouse/stripe", {"id": 1, "title": "", "location": {"name": "  "}, "content": ""})
    a = normalize_ashby("ashby/notion", {"id": "a", "descriptionPlain": "   ", "secondaryLocations": None})
    for p in (g, a):
        assert all(p[f] is None for f in ("title", "locations", "text", "date", "url"))


def test_ashby_locations_and_fields():
    job = {"id": "x1", "title": "Backend Engineer", "location": "Dublin, Ireland",
           "secondaryLocations": [{"location": "New York, New York"}, {"location": ""}],
           "descriptionPlain": "Build\n\nAPIs   in Python.", "publishedAt": "2026-11-02T10:00:00+00:00",
           "jobUrl": "https://jobs.ashbyhq.com/x1", "isRemote": True, "workplaceType": "Hybrid"}
    p = normalize_ashby("ashby/notion", job)
    assert p["locations"] == ["Dublin, Ireland", "New York, New York"]
    assert p["text"] == "Build APIs in Python."
    assert p["date"] == "2026-11-02T10:00:00+00:00" and p["url"] == "https://jobs.ashbyhq.com/x1"
    assert set(p) == {"board", "id", "title", "locations", "text", "date", "url"}


# ---------- run folder and CLI ----------

def make_run(tmp_path, *, fail_ashby=False):
    run_id = "run-test-1"
    run = tmp_path / "run"
    (run / "raw" / "greenhouse" / "stripe").mkdir(parents=True)
    gh = {"jobs": [
        {"id": 1, "title": "Software Engineer", "location": {"name": "SF"},
         "content": "&lt;p&gt;" + "Python AWS backend. 2+ years." + FILLER + "&lt;/p&gt;", "first_published": "2026-11-20"},
        {"id": 2, "title": "Account Executive", "location": {"name": "Dublin"}, "content": "&lt;p&gt;Sales&lt;/p&gt;"},
    ]}
    (run / "raw" / "greenhouse" / "stripe" / "attempt-1.raw").write_text(json.dumps(gh))
    boards = [{"board": "greenhouse/stripe", "provider": "greenhouse", "token": "stripe", "status": "succeeded",
               "raw_paths": [f"runs/{run_id}/raw/greenhouse/stripe/attempt-1.raw"]}]
    if fail_ashby:
        boards.append({"board": "ashby/linear", "provider": "ashby", "token": "linear", "status": "failed",
                       "raw_paths": [], "failure": {"kind": "http-403"}})
    (run / "summary.json").write_text(json.dumps({"run_id": run_id, "boards": boards}))
    return run


def test_failed_board_is_a_failure_not_zero_postings(tmp_path):
    postings, failures = load_run(make_run(tmp_path, fail_ashby=True))
    assert {p["board"] for p in postings} == {"greenhouse/stripe"}
    assert failures == [{"board": "ashby/linear", "status": "failed", "failure": {"kind": "http-403"}}]


def test_raw_path_cannot_leave_run_folder(tmp_path):
    run = make_run(tmp_path)
    summary = json.loads((run / "summary.json").read_text())
    summary["boards"][0]["raw_paths"] = ["runs/run-test-1/../../outside.raw"]
    (run / "summary.json").write_text(json.dumps(summary))
    with pytest.raises(RunError):
        load_run(run)


def test_cli_writes_results_and_summary(tmp_path):
    run, out = make_run(tmp_path, fail_ashby=True), tmp_path / "out"
    code = flt.main(["--run", str(run), "--out", str(out), "--persona", str(write_persona(tmp_path, skills=["Python", "AWS"]))])
    assert code == 0
    results = [json.loads(line) for line in (out / "results.jsonl").read_text().splitlines()]
    assert [(r["id"], r["verdict"]) for r in results] == [(1, "keep"), (2, "reject")]
    summary = json.loads((out / "summary.json").read_text())
    assert summary["by_verdict"] == {"keep": 1, "reject": 1, "cannot_tell": 0}
    assert summary["by_board"]["greenhouse/stripe"] == {"keep": 1, "reject": 1, "cannot_tell": 0, "total": 2}
    assert summary["by_first_failing_gate"]["G1"] == 1
    assert summary["board_failures"][0]["board"] == "ashby/linear"


def test_cli_missing_persona_field_exits_2_and_writes_nothing(tmp_path):
    out = tmp_path / "out"
    code = flt.main(["--run", str(make_run(tmp_path)), "--out", str(out),
                     "--persona", str(write_persona(tmp_path, skills=...))])
    assert code == 2 and not out.exists()
