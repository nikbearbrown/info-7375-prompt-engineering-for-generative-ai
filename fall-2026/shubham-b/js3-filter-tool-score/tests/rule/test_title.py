"""§6.1 title check: role families from ``$.target.roles`` and exclusion markers."""

from __future__ import annotations

import pytest

from job_search_agent.errors import ConfigError
from job_search_agent.rule.title import ROLE_ALIASES, title_check

ROLES = (
    "Software Engineer",
    "Full-Stack Software Engineer",
    "Backend Engineer",
    "Frontend Engineer",
)


@pytest.mark.parametrize(
    ("title", "expected_role"),
    [
        ("Software Engineer", "Software Engineer"),
        ("Software Engineer, New Grad", "Software Engineer"),
        ("Full-Stack Software Engineer", "Full-Stack Software Engineer"),
        ("Full Stack Engineer, Revenue", "Full-Stack Software Engineer"),
        ("Fullstack Engineer", "Full-Stack Software Engineer"),
        ("Full-Stack Engineer", "Full-Stack Software Engineer"),
        ("Backend Engineer", "Backend Engineer"),
        ("Back-End Software Engineer", "Backend Engineer"),
        ("Back End Engineer", "Backend Engineer"),
        ("Frontend Engineer", "Frontend Engineer"),
        ("Front-End Software Engineer", "Frontend Engineer"),
        ("Front End Engineer", "Frontend Engineer"),
        ("Software Engineer I", "Software Engineer"),
        ("Software Engineer II", "Software Engineer"),
        ("\tSoftware Engineer ", "Software Engineer"),
        ("Software  Engineer", "Software Engineer"),
        ("SOFTWARE ENGINEER", "Software Engineer"),
        ("Software Engineer, Leadership Tools", "Software Engineer"),
        ("Software Engineer, Internal Tools", "Software Engineer"),
        ("Software Engineer, SRE", "Software Engineer"),
    ],
)
def test_title_passes(title: str, expected_role: str) -> None:
    check = title_check(title, ROLES)
    assert check.passed, check.reason
    assert expected_role in check.matched_roles
    assert check.excluded_markers == []


@pytest.mark.parametrize(
    "title",
    [
        "Backend Data Analyst",
        "Frontend Designer",
        "Software Engineering",
        "Software Engineering Manager",
        "Data Engineer",
        "Backend/API Engineer",
        "Backend / API Engineer, Radar",
        "SWE II",
        "Software Engineers",
        "Engineer, Software",
        "Infrastructure Engineer",
        "",
    ],
)
def test_title_fails_on_family(title: str) -> None:
    check = title_check(title, ROLES)
    assert not check.passed
    assert check.matched_roles == []


@pytest.mark.parametrize(
    ("title", "marker"),
    [
        ("Senior Software Engineer", "senior"),
        ("Sr. Software Engineer", "sr"),
        ("Sr Software Engineer", "sr"),
        ("Staff Software Engineer", "staff"),
        ("Principal Software Engineer", "principal"),
        ("Software Engineer, Tech Lead", "lead"),
        ("Software Engineer Manager", "manager"),
        ("Director, Software Engineer", "director"),
        ("Software Engineer Intern", "intern"),
        ("Software Engineer Internship", "internship"),
        ("Software Engineer III", "iii"),
        ("Software Engineer IV", "iv"),
        ("Software Engineer L3", "l3"),
        ("Software Engineer (L4)", "l4"),
    ],
)
def test_title_fails_on_exclusion(title: str, marker: str) -> None:
    check = title_check(title, ROLES)
    assert check.matched_roles, "the family phrase itself is present"
    assert not check.passed
    assert check.excluded_markers == [marker]


@pytest.mark.parametrize(
    "title", ["Engineering Manager", "Software Engineering Internship"]
)
def test_title_fails_on_family_and_exclusion(title: str) -> None:
    check = title_check(title, ROLES)
    assert not check.passed
    assert check.matched_roles == []
    assert check.excluded_markers


def test_title_records_every_excluded_marker() -> None:
    check = title_check("Senior Staff Software Engineer, Lead (L4) Intern", ROLES)
    assert check.excluded_markers == ["senior", "staff", "lead", "intern", "l4"]


def test_title_marker_recorded_once() -> None:
    check = title_check("Senior Software Engineer, Senior Tools", ROLES)
    assert check.excluded_markers == ["senior"]


def test_title_records_every_matched_role() -> None:
    check = title_check("Full Stack Software Engineer", ROLES)
    assert check.matched_roles == [
        "Software Engineer",
        "Full-Stack Software Engineer",
    ]


def test_title_families_derived_from_resume_roles() -> None:
    without_frontend = [r for r in ROLES if r != "Frontend Engineer"]
    assert not title_check("Frontend Engineer", without_frontend).passed
    assert title_check("Frontend Engineer", ROLES).passed
    assert not title_check("Software Engineer", ["Backend Engineer"]).passed


def test_unknown_role_in_resume_raises_config_error() -> None:
    with pytest.raises(ConfigError):
        title_check("Software Engineer", [*ROLES, "Data Scientist"])


def test_alias_table_covers_exactly_the_contract_roles() -> None:
    assert set(ROLE_ALIASES) == set(ROLES)


def test_reason_is_present() -> None:
    assert title_check("Software Engineer", ROLES).reason
    assert title_check("Senior Software Engineer", ROLES).reason
    assert title_check("Data Engineer", ROLES).reason
