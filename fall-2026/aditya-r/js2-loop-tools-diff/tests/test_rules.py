"""The written rule (CONTRACT.md §4, R1, R2), including the contract's own worked examples."""
import copy

from agent.rules import evaluate, html_to_text, normalize, resume_fields_with_skill
from tests.fixtures import NEAR_MISS, NOT_RELEVANT, PERSONA, RELEVANT, posting


def verdict(title, desc, persona=PERSONA):
    return evaluate(posting(1, title, desc), persona)


def test_contract_examples_for_title_matching():
    assert verdict("Software Engineer II", "<p>Python and SQL</p>")["verdict"] == "relevant"
    r = verdict("Software Engineering Manager", "<p>Python and SQL</p>")
    assert not r["checks"]["A_role_phrase"]["pass"]
    assert verdict("Machine-Learning Engineer", "<p>Python, SQL</p>")["checks"]["A_role_phrase"]["matched"] == ["machine learning engineer"]
    r = verdict("Sr. Data Engineer", "<p>Python, SQL</p>")
    assert r["checks"]["B_no_excluded_term"]["found"] == ["sr"] and r["verdict"] == "not_relevant"


def test_exclusions_apply_to_title_only():
    r = verdict("Data Engineer", "<p>Work with a senior staff manager. Python and SQL.</p>")
    assert r["checks"]["B_no_excluded_term"]["pass"] and r["verdict"] == "relevant"


def test_no_synonyms_or_substrings():
    r = verdict("Data Engineer", "<p>PySpark, PostgreSQL, NoSQL, Pythonic code</p>")
    assert r["checks"]["C_shared_skills"]["shared"] == []
    assert r["verdict"] == "not_relevant"


def test_repeated_mentions_count_once_and_threshold_is_two():
    r = verdict("Data Engineer", "<p>Python. Python. Python. Python. Python.</p>")
    assert len(r["checks"]["C_shared_skills"]["shared"]) == 1 and r["verdict"] == "not_relevant"


def test_spark_never_counts_for_persona_without_spark():
    r = verdict("Data Engineer", "<p>Spark and Python</p>")
    assert [s["skill"] for s in r["checks"]["C_shared_skills"]["shared"]] == ["python"]
    assert "absent from the four résumé skill arrays" in r["checks"]["C_shared_skills"]["not_shared"]["spark"]


def test_missing_title_or_description_is_not_relevant_with_reason():
    r = evaluate({"id": 9, "title": "Data Engineer", "content": ""}, PERSONA)
    assert r["verdict"] == "not_relevant" and r["missing"] == ["posting.description"]
    assert "posting.description" in r["explanation"]
    r = evaluate({"id": 9, "title": "データエンジニア", "content": "&lt;p&gt;Python SQL&lt;/p&gt;"}, PERSONA)
    assert r["missing"] == ["posting.title"] and r["verdict"] == "not_relevant"


def test_html_entities_and_script_style_removed():
    raw = "&lt;p&gt;Python&amp;nbsp;&lt;/p&gt;&lt;script&gt;sql()&lt;/script&gt;&lt;style&gt;.sql{}&lt;/style&gt;"
    text = normalize(html_to_text(raw))
    assert text == "python"


def test_resume_matching_is_whole_word_within_one_entry_R1():
    persona = copy.deepcopy(PERSONA)
    persona["skills"]["languages"] = ["MySQL", "Python"]
    persona["skills"]["data_bi"] = ["Databricks SQL"]
    assert resume_fields_with_skill(persona, "sql") == ["skills.data_bi"]  # not MySQL
    persona["skills"]["data_bi"] = ["Data", "bricks"]
    persona["skills"]["database_cloud"] = []
    assert resume_fields_with_skill(persona, "databricks") == []  # entries never joined


def test_other_resume_fields_do_not_change_the_rule():
    persona = copy.deepcopy(PERSONA)
    persona["skills"]["familiar_with_not_shipped"] = ["Spark"]
    persona["education"] = [{"degree": "PhD"}]
    assert evaluate(NEAR_MISS, persona) == evaluate(NEAR_MISS, PERSONA)


def test_fixture_outcomes_and_explanations_cite_fields():
    assert evaluate(RELEVANT, PERSONA)["verdict"] == "relevant"
    assert evaluate(NOT_RELEVANT, PERSONA)["verdict"] == "not_relevant"
    r = evaluate(NEAR_MISS, PERSONA)
    assert r["verdict"] == "not_relevant" and "senior" in r["explanation"]
    rel = evaluate(RELEVANT, PERSONA)["explanation"]
    assert "posting.title" in rel and "skills.languages" in rel and "posting.description" in rel
