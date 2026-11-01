"""The rule in CONTRACT.md, case by case. All postings are CONSTRUCTED."""
from conftest import posting
from jsagent import rule


def v(resume, title, content="<p>Python</p>"):
    return rule.judge(posting(1, title, content), resume)["verdict"]


def test_relevant_when_all_three_tests_pass(resume):
    r = rule.judge(posting(1, "Applied AI Engineer", "<p>Python, SQL and AWS</p>", "London, UK"), resume)
    assert r["verdict"] == rule.RELEVANT
    assert '"AI"' in r["justification"] and '"Engineer"' in r["justification"]
    assert "content matched skills: Python, SQL, AWS" in r["justification"]
    assert "location: London, UK (not used)" in r["justification"]


def test_worked_example_shape(resume):
    """Same shape as the hand-worked example: 'Engineering Manager, ...' with no skill in the content."""
    r = rule.judge(posting(1, "Engineering Manager, Claude Platform", "<p>Lead a team. Go and TypeScript.</p>"), resume)
    assert r["verdict"] == rule.NOT_RELEVANT
    assert r["tests"] == {"title": True, "skills": False, "not_management": False}
    assert "failed: skills test, management test" in r["justification"]


def test_title_words_come_from_experience_title_minus_coop(resume):
    assert rule.title_terms(resume) == ["AI", "Engineer", "Engineering"]
    assert v(resume, "Co-op Program Coordinator") == rule.NOT_RELEVANT


def test_engineering_counts(resume):
    assert v(resume, "Engineering Lead, Infrastructure") == rule.RELEVANT


def test_whole_words_ignoring_case(resume):
    assert v(resume, "Digital Campaigns, Policy Advocacy") == rule.NOT_RELEVANT   # "ai" inside a word
    assert v(resume, "applied ai ENGINEER") == rule.RELEVANT                        # case ignored
    assert v(resume, "AI Engineer", "<p>PostgreSQL and laws</p>") == rule.NOT_RELEVANT


def test_multiword_skills_and_familiar_list_excluded(resume):
    assert v(resume, "AI Engineer", "<p>We run Delta   Lake.</p>") == rule.RELEVANT
    assert v(resume, "AI Engineer", "<p>Ray and Kubeflow only.</p>") == rule.NOT_RELEVANT


def test_management_words_exclude_but_senior_staff_do_not(resume):
    for t in ["Manager, Applied AI Engineering", "Director of AI", "Head of AI Engineering"]:
        assert v(resume, t) == rule.NOT_RELEVANT, t
    for t in ["Senior AI Engineer", "Staff Software Engineer", "Principal Engineer", "Lead AI Engineer"]:
        assert v(resume, t) == rule.RELEVANT, t


def test_missing_fields_cannot_judge(resume):
    r = rule.judge(posting(1, "AI Engineer", ""), resume)
    assert r["verdict"] == rule.CANNOT_JUDGE and "missing field: content" in r["justification"]
    r = rule.judge({"id": 2, "content": "x"}, resume)
    assert r["verdict"] == rule.CANNOT_JUDGE and "title" in r["justification"]


def test_location_never_decides(resume):
    a = rule.judge(posting(1, "AI Engineer", location="Tokyo, Japan"), resume)["verdict"]
    b = rule.judge(posting(1, "AI Engineer", location="Boston, MA"), resume)["verdict"]
    assert a == b == rule.RELEVANT


def test_greenhouse_double_escaped_html():
    assert rule.plain_text("&lt;p&gt;Python &amp;amp; SQL&lt;/p&gt;") == "Python & SQL"
