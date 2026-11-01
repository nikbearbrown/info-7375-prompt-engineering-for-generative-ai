"""§6.2 skill check: eligible résumé skills and the special matching cases.

Postings are constructed unless the test name says otherwise.
"""

from __future__ import annotations

import pytest

from job_search_agent.models import SkillEntry, SkillEvidence
from job_search_agent.rule.skills import (
    SKILL_PATHS,
    match_skills,
    skill_entries_from_resume,
    term_in_text,
)
from tests.tools.builders import fixture_resume_data, handcheck_posting, posting

SKILLS = skill_entries_from_resume(fixture_resume_data())


def _terms(content: str, *, title: str = "Software Engineer") -> set[str]:
    found = match_skills(posting(title=title, content=content), SKILLS)
    return {e.term for e in found}


# --- the eligible skill set ---------------------------------------------------


def test_skill_paths_are_the_contract_paths_in_order() -> None:
    assert SKILL_PATHS == (
        "$.skills.languages",
        "$.skills.frontend",
        "$.skills.backend",
        "$.skills.data",
        "$.skills.messaging",
        "$.skills.cloud_devops",
        "$.skills.observability",
    )


def test_each_resume_path_points_to_its_term() -> None:
    data = fixture_resume_data()
    assert len(SKILLS) == 29
    for entry in SKILLS:
        group, index = entry.resume_path.removeprefix("$.skills.").split("[")
        assert data["skills"][group][int(index.rstrip("]"))] == entry.term
    assert SKILLS[0] == SkillEntry("TypeScript", "$.skills.languages[0]")
    assert SkillEntry("GraphQL", "$.skills.backend[4]") in SKILLS
    assert SkillEntry("REST", "$.skills.backend[3]") in SKILLS


def test_familiar_with_not_shipped_never_counted() -> None:
    assert {"Go", "Terraform"}.isdisjoint(e.term for e in SKILLS)
    assert _terms("We use Go and Terraform. Go Go Go.") == set()


def test_non_list_skill_group_rejected() -> None:
    from job_search_agent.errors import ConfigError

    data = fixture_resume_data()
    data["skills"]["data"] = "PostgreSQL"
    with pytest.raises(ConfigError):
        skill_entries_from_resume(data)


# --- C# -----------------------------------------------------------------------


def test_csharp_matches_exact_token() -> None:
    assert _terms("Experience with C#, .NET") == {"C#"}
    assert _terms("&lt;li&gt;C#&lt;/li&gt;") == {"C#"}
    assert _terms("(C#)") == {"C#"}


def test_plain_c_does_not_match_csharp() -> None:
    assert _terms("C and C++ experience; c is fine") == set()
    assert _terms("ABC# notation") == set()
    assert _terms("C## twice") == set()


def test_lowercase_csharp_does_not_match() -> None:
    """A6: ``C#`` is matched exactly, so ``c#`` does not count."""
    assert _terms("c# experience") == set()


def test_real_csharp_posting_7396679() -> None:
    """Real data: the only posting on the 2026-10-29 board that mentions C#."""
    found = match_skills(handcheck_posting("7396679"), SKILLS)
    assert (
        SkillEvidence(
            term="C#", resume_path="$.skills.languages[5]", posting_path="$.content"
        )
        in found
    )


# --- REST ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "content",
    ["a REST API for payments", "RESTful API design", "build REST services"],
)
def test_rest_phrases_count(content: str) -> None:
    assert _terms(content) == {"REST"}


def test_rest_of_the_team_does_not_count() -> None:
    assert _terms("Work with the rest of the team. Rest well.") == set()
    assert _terms("rest api in lowercase") == set()


def test_restful_apis_plural_does_not_count() -> None:
    """A7: the §6.2 phrases need a boundary on both sides; plurals do not count."""
    assert _terms("design RESTful APIs and REST APIs") == set()
    assert _terms("bare REST alone") == set()


# --- React --------------------------------------------------------------------


@pytest.mark.parametrize("content", ["React", "React.js apps", "ReactJS, too"])
def test_react_forms_case_sensitive(content: str) -> None:
    assert _terms(content) == {"React"}


def test_lowercase_react_does_not_count() -> None:
    assert _terms("we react to incidents; REACT; reactjs; Reactive") == set()


def test_sentence_initial_react_counts_known_limitation() -> None:
    """Known limitation (§6.2): a capitalised English verb is a false positive."""
    assert _terms("React quickly to incidents.") == {"React"}


def test_react_native_counts_known_limitation() -> None:
    """``React Native`` contains the ``React`` form, so it counts (as written)."""
    assert _terms("Mobile apps in React Native") == {"React"}


# --- Express ------------------------------------------------------------------


@pytest.mark.parametrize(
    "content", ["Express.js", "ExpressJS services", "the Express framework"]
)
def test_express_forms(content: str) -> None:
    assert _terms(content) == {"Express"}


def test_express_interest_does_not_count() -> None:
    assert _terms("Please express interest by applying.") == set()
    assert _terms("Express interest early; express.js lowercase") == set()


def test_bare_express_does_not_count() -> None:
    assert _terms("Stripe Express accounts") == set()


# --- other skills ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("content", "term"),
    [
        ("Node.js", "Node.js"),
        ("NodeJS", "Node.js"),
        ("node.js", "Node.js"),
        ("NODEJS", "Node.js"),
        ("Next.js", "Next.js"),
        ("NextJS", "Next.js"),
        ("nextjs", "Next.js"),
    ],
)
def test_node_next_variants_case_insensitive(content: str, term: str) -> None:
    assert _terms(content) == {term}


def test_node_without_js_does_not_count() -> None:
    assert _terms("a node in the graph; next steps") == set()


def test_java_not_inside_javascript() -> None:
    assert _terms("JavaScript") == {"JavaScript"}
    assert _terms("java") == {"Java"}


def test_sql_not_inside_postgresql() -> None:
    assert _terms("PostgreSQL") == {"PostgreSQL"}
    assert _terms("NoSQL and MySQL") == set()


def test_digit_adjacent_is_not_whole_word() -> None:
    assert _terms("HTML5 and CSS3") == set()


def test_multiword_skills_consecutive() -> None:
    assert _terms("Spring Boot and GitHub Actions") == {"Spring Boot", "GitHub Actions"}
    assert _terms("spring  boot") == {"Spring Boot"}
    assert _terms("Spring and Boot; GitHub, Actions") == set()


def test_repeated_mentions_count_once() -> None:
    found = match_skills(posting(content="Java, Java and more Java"), SKILLS)
    assert found == [
        SkillEvidence(
            term="Java", resume_path="$.skills.languages[2]", posting_path="$.content"
        )
    ]


def test_skills_searched_in_title_content_departments_and_first_field_cited() -> None:
    """A29: one entry per skill, citing the first field in title → content → depts."""
    item = posting(
        title="Backend Engineer, Kafka",
        content="Kafka and Python",
        departments=[{"name": "Risk"}, {"name": "Python Platform"}, {"name": "AWS"}],
    )
    found = {e.term: e.posting_path for e in match_skills(item, SKILLS)}
    assert found == {
        "Python": "$.content",
        "Kafka": "$.title",
        "AWS": "$.departments[2].name",
    }


def test_evidence_follows_resume_order() -> None:
    found = match_skills(posting(content="Grafana, AWS, TypeScript"), SKILLS)
    assert [e.term for e in found] == ["TypeScript", "AWS", "Grafana"]


def test_frontend_word_is_not_a_skill() -> None:
    assert _terms("Frontend, front-end and Front End work") == set()


def test_html_is_cleaned_before_matching() -> None:
    assert _terms("&lt;li&gt;Java&lt;/li&gt;&lt;li&gt;Python&lt;/li&gt;") == {
        "Java",
        "Python",
    }
    assert _terms("&lt;p&gt;Py&lt;/p&gt;thon") == set()


def test_term_in_text_unknown_term_uses_whole_word_rule() -> None:
    assert term_in_text("Rust", "We write Rust.")
    assert not term_in_text("Rust", "Trusty")
