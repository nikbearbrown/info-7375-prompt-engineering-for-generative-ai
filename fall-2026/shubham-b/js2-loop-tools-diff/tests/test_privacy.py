"""Tests for the privacy audit (CONTRACT §12, PLAN §3.3, A24)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from job_search_agent.models import VerifiedResume
from job_search_agent.privacy import (
    FindingKind,
    SensitiveValue,
    scan_text,
    scan_tree,
    sensitive_values,
)
from job_search_agent.resume import PERSONA_LABEL
from job_search_agent.rule.skills import skill_entries_from_resume


def _by_path(resume: VerifiedResume) -> dict[str, SensitiveValue]:
    return {value.resume_path: value for value in sensitive_values(resume)}


def test_sensitive_values_cover_contacts_bullets_institutions_employers(
    verified_resume: VerifiedResume,
) -> None:
    values = _by_path(verified_resume)
    doc = verified_resume.to_dict()
    for key in ("email", "phone", "linkedin", "github"):
        assert values[f"$.personal.{key}"].category == "contact"
    assert values["$.personal.name"].category == "name"
    assert values["$.education[1].institution"].category == "institution"
    assert values["$.experience[0].company"].category == "employer"
    assert values["$.work_authorization.status"].category == "work_authorization"
    bullet_paths = [
        f"$.{section}[{i}].bullets[{j}]"
        for section in ("experience", "projects")
        for i, item in enumerate(doc[section])
        for j, _ in enumerate(item["bullets"])
    ]
    assert len(bullet_paths) == 10
    for path in bullet_paths:
        assert values[path].category == "bullet"
    skill_terms = {
        entry.term for entry in skill_entries_from_resume(verified_resume.to_dict())
    }
    assert not skill_terms & {value.value for value in values.values()}


def test_sensitive_value_repr_hides_value(verified_resume: VerifiedResume) -> None:
    for value in sensitive_values(verified_resume):
        assert value.value not in repr(value)


def test_scan_reports_location_not_value(verified_resume: VerifiedResume) -> None:
    doc = verified_resume.to_dict()
    bullet = doc["experience"][0]["bullets"][1]
    email = doc["personal"]["email"]
    text = f"ok line\nsummary: {bullet}\ncontact {email.upper()}\n"
    findings = scan_text(text, sensitive_values(verified_resume), location="r.md")
    labels = [(f.kind, f.label, f.line, f.column) for f in findings]
    assert labels == [
        (FindingKind.RESUME_VALUE, "$.experience[0].bullets[1]", 2, 10),
        (FindingKind.RESUME_VALUE, "$.personal.email", 3, 9),
    ]
    for finding in findings:
        rendered = finding.describe() + repr(finding) + str(finding)
        assert bullet not in rendered
        assert email not in rendered
        assert email.split("@")[0] not in rendered
    assert findings[0].describe().startswith("r.md:2:10 RESUME_VALUE")


def test_skill_terms_and_persona_label_allowed(
    verified_resume: VerifiedResume,
) -> None:
    entries = skill_entries_from_resume(verified_resume.to_dict())
    text = "\n".join(
        [f"persona: {PERSONA_LABEL}", "location: Boston, MA"]
        + [f"matched {e.term} at {e.resume_path}" for e in entries]
    )
    values = sensitive_values(verified_resume)
    assert scan_text(text, values, allow=[PERSONA_LABEL]) == []
    assert scan_text(text, values) == []


def test_allow_list_masks_overlapping_value(verified_resume: VerifiedResume) -> None:
    values = sensitive_values(verified_resume)
    text = "fixture: Kiran Joshi"
    assert [f.label for f in scan_text(text, values)] == ["$.personal.name"]
    assert scan_text(text, values, allow=["fixture: kiran joshi"]) == []


def test_json_escaped_and_suffix_forms_found(verified_resume: VerifiedResume) -> None:
    doc = verified_resume.to_dict()
    record = {"summary": doc["projects"][0]["bullets"][0], "x": "Fernleaf Health"}
    text = json.dumps(record)
    labels = {f.label for f in scan_text(text, sensitive_values(verified_resume))}
    assert labels == {"$.projects[0].bullets[0]", "$.experience[0].company"}


def test_phone_tail_found(verified_resume: VerifiedResume) -> None:
    findings = scan_text("call 555-0143", sensitive_values(verified_resume))
    assert [f.label for f in findings] == ["$.personal.phone"]


@pytest.mark.parametrize(
    ("text", "kind", "label"),
    [
        ("path /Users/someone/x.json", FindingKind.ABSOLUTE_PATH, "home_dir_macos"),
        ("cwd=/home/dev/repo", FindingKind.ABSOLUTE_PATH, "home_dir_linux"),
        ("key sk-ant-api03-abcdefghijkl", FindingKind.CREDENTIAL, "anthropic_key"),
        (
            '"ANTHROPIC_API_KEY": "abcd1234efgh"',
            FindingKind.CREDENTIAL,
            "credential_assignment",
        ),
        (
            "Authorization: Bearer abc.def.ghijkl",
            FindingKind.CREDENTIAL,
            "bearer_token",
        ),
    ],
)
def test_patterns_found_without_echo(text: str, kind: FindingKind, label: str) -> None:
    findings = scan_text(text, ())
    assert [(f.kind, f.label) for f in findings] == [(kind, label)]
    assert text.split()[-1] not in findings[0].describe()


def test_env_var_names_alone_not_flagged() -> None:
    text = "removed from env: ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN"
    assert scan_text(text, ()) == []
    assert scan_text("data/live/runs/x/report.json", ()) == []


def test_scan_tree_reports_relative_locations(
    tmp_path: Path, verified_resume: VerifiedResume
) -> None:
    doc = verified_resume.to_dict()
    root = tmp_path / "data"
    (root / "live" / "runs").mkdir(parents=True)
    (root / "live" / "runs" / "clean.json").write_text('{"ok": true}')
    (root / "live" / "runs" / "leak.md").write_text(
        "line\n" + doc["personal"]["github"] + "\n"
    )
    (root / "bin.dat").write_bytes(b"\xff\xfe /Users/me/x")
    outside = tmp_path / "outside.txt"
    outside.write_text(doc["personal"]["email"])
    (root / "link.txt").symlink_to(outside)
    findings = scan_tree(root, sensitive_values(verified_resume))
    assert [(f.location, f.line, f.label) for f in findings] == [
        ("bin.dat", 1, "home_dir_macos"),
        ("live/runs/leak.md", 2, "$.personal.github"),
    ]
    single = scan_tree(
        root / "live" / "runs" / "leak.md", sensitive_values(verified_resume)
    )
    assert [f.location for f in single] == ["leak.md"]


def test_allow_never_hides_a_longer_value_that_contains_it(
    verified_resume: VerifiedResume,
) -> None:
    bullet = verified_resume.to_dict()["projects"][0]["bullets"][0]
    word = max(bullet.split(), key=len)
    findings = scan_text(
        f"note: {bullet}", sensitive_values(verified_resume), allow=[word]
    )
    assert [f.label for f in findings] == ["$.projects[0].bullets[0]"]
