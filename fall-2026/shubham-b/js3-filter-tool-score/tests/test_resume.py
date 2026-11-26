"""Tests for the résumé gate (CONTRACT §12, PLAN §3.3, A12, A13)."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from job_search_agent.config import load_config
from job_search_agent.errors import ConfigError, ResumeRefused
from job_search_agent.models import RefusalCode, SkillEntry, VerifiedResume
from job_search_agent.resume import (
    PERSONA_LABEL,
    default_project_root,
    load_verified_resume,
)
from job_search_agent.rule.skills import skill_entries_from_resume
from tests.conftest import PINNED_RESUME_SHA256, REPO_ROOT, RESUME_FIXTURE_REL

# The independent pin: typed here by hand from the committed bytes, never computed.
PIN_LITERAL = "562a9d607213564c5291520f375ba69a7d407894c5803a995bad5b2d8f810532"
FIXTURE = REPO_ROOT / RESUME_FIXTURE_REL


def _fixture_doc() -> dict[str, Any]:
    doc: dict[str, Any] = json.loads(FIXTURE.read_bytes())
    return doc


def _reader(data: bytes) -> Callable[[Path], bytes]:
    return lambda _path: data


def _codes(
    doc_or_bytes: dict[str, Any] | bytes, *, pin_to_content: bool = True
) -> frozenset[RefusalCode]:
    """Refusal codes for mutated content; by default the pin matches the bytes, so
    only the content checks can fail."""
    data = (
        doc_or_bytes
        if isinstance(doc_or_bytes, bytes)
        else json.dumps(doc_or_bytes).encode()
    )
    pin = hashlib.sha256(data).hexdigest() if pin_to_content else PIN_LITERAL
    with pytest.raises(ResumeRefused) as info:
        load_verified_resume(FIXTURE, pin, read_bytes=_reader(data))
    return info.value.codes


def test_committed_fixture_verifies(verified_resume: VerifiedResume) -> None:
    assert isinstance(verified_resume, VerifiedResume)
    assert verified_resume.sha256 == PIN_LITERAL
    assert verified_resume.source_path == RESUME_FIXTURE_REL


def test_pinned_digest_literal_matches_config() -> None:
    config = load_config(REPO_ROOT / "config" / "agent.toml")
    assert config.resume.pinned_sha256 == PIN_LITERAL
    assert PINNED_RESUME_SHA256 == PIN_LITERAL


def test_source_path_is_repo_relative_with_explicit_root() -> None:
    resume = load_verified_resume(
        Path(RESUME_FIXTURE_REL), PIN_LITERAL, project_root=REPO_ROOT
    )
    assert resume.source_path == RESUME_FIXTURE_REL
    assert default_project_root() == REPO_ROOT.resolve()


def test_path_outside_project_root_is_config_error(tmp_path: Path) -> None:
    outside = tmp_path / "kiran.resume.example.json"
    outside.write_bytes(FIXTURE.read_bytes())
    with pytest.raises(ConfigError):
        load_verified_resume(outside, PIN_LITERAL)


@pytest.mark.parametrize("pin", [None, "", "not-a-digest", PIN_LITERAL.upper()])
def test_pin_not_set_refuses(pin: str | None) -> None:
    with pytest.raises(ResumeRefused) as info:
        load_verified_resume(FIXTURE, pin)
    assert info.value.codes == {RefusalCode.PIN_NOT_SET}


def test_digest_mismatch_refuses() -> None:
    data = bytearray(FIXTURE.read_bytes())
    index = data.index(b"Boston")
    data[index] ^= 0x01  # one byte flipped inside a string; still valid JSON
    assert _codes(bytes(data), pin_to_content=False) == {RefusalCode.DIGEST_MISMATCH}


def test_digest_checked_before_parse() -> None:
    calls: list[Path] = []

    def spy(path: Path) -> bytes:
        calls.append(path)
        return b"\xff not json"

    with pytest.raises(ResumeRefused) as info:
        load_verified_resume(FIXTURE, PIN_LITERAL, read_bytes=spy)
    # One read: the digest is taken over exactly the bytes that are then parsed.
    assert len(calls) == 1
    assert RefusalCode.DIGEST_MISMATCH in info.value.codes
    assert info.value.codes == {RefusalCode.DIGEST_MISMATCH, RefusalCode.NOT_JSON}


def test_unreadable_refuses() -> None:
    def broken(_path: Path) -> bytes:
        raise PermissionError("denied")

    with pytest.raises(ResumeRefused) as info:
        load_verified_resume(FIXTURE, PIN_LITERAL, read_bytes=broken)
    assert info.value.codes == {RefusalCode.UNREADABLE}


def test_duplicate_keys_are_not_json() -> None:
    data = b'{"fictional": false, "fictional": true}'
    assert RefusalCode.NOT_JSON in _codes(data)


def test_notexample_com_refused() -> None:
    doc = _fixture_doc()
    doc["personal"]["email"] = "kiran.joshi@notexample.com"
    assert _codes(doc, pin_to_content=False) >= {
        RefusalCode.EMAIL_DOMAIN,
        RefusalCode.DIGEST_MISMATCH,
    }
    assert _codes(doc) == {RefusalCode.EMAIL_DOMAIN}


@pytest.mark.parametrize(
    "email",
    [
        "kiran.joshi@mail.example.com",
        "kiran.joshi@example.com.evil",
        "kiran.joshi@EXAMPLE.COM",
        "@example.com",
        " kiran.joshi@example.com",
    ],
)
def test_subdomain_example_com_refused(email: str) -> None:
    doc = _fixture_doc()
    doc["personal"]["email"] = email
    assert _codes(doc) == {RefusalCode.EMAIL_DOMAIN}


def test_two_at_signs_refused() -> None:
    doc = _fixture_doc()
    doc["personal"]["email"] = "kiran@evil.org@example.com"
    assert _codes(doc) == {RefusalCode.EMAIL_DOMAIN}


@pytest.mark.parametrize(
    "phone", ["(617) 555-0243", "(617) 556-0143", "555-0143x", "617 555 0143"]
)
def test_non_555_phone_refused(phone: str) -> None:
    doc = _fixture_doc()
    doc["personal"]["phone"] = phone
    assert _codes(doc) == {RefusalCode.PHONE_PATTERN}


@pytest.mark.parametrize(
    "phone", ["(617) 555-0143", " 555-0199 ", "+1 617-555-0100", "617.555-0142"]
)
def test_fictional_phone_variants_accepted(phone: str) -> None:
    doc = _fixture_doc()
    doc["personal"]["phone"] = phone
    data = json.dumps(doc).encode()
    pin = hashlib.sha256(data).hexdigest()
    assert load_verified_resume(FIXTURE, pin, read_bytes=_reader(data)).sha256 == pin


def test_fictional_false_refused() -> None:
    doc = _fixture_doc()
    doc["fictional"] = False
    assert _codes(doc) == {RefusalCode.NOT_FICTIONAL}


@pytest.mark.parametrize("value", ["true", 1, "True", None])
def test_fictional_string_true_refused(value: object) -> None:
    doc = _fixture_doc()
    doc["fictional"] = value
    assert _codes(doc) == {RefusalCode.NOT_FICTIONAL}


def test_fictional_missing_refused() -> None:
    doc = _fixture_doc()
    del doc["fictional"]
    assert _codes(doc) == {RefusalCode.NOT_FICTIONAL}


def _drop(doc: dict[str, Any], dotted: str) -> None:
    *parents, last = dotted.split(".")
    node: Any = doc
    for part in parents:
        node = node[int(part)] if isinstance(node, list) else node[part]
    del node[last]


@pytest.mark.parametrize(
    "dotted",
    [
        "personal.name",
        "personal.email",
        "personal.phone",
        "target.roles",
        "target.levels",
        "target.locations",
        "target.excluded",
        "skills.languages",
        "skills.observability",
        "skills.familiar_with_not_shipped",
        "experience.0.bullets",
        "projects.1.bullets",
        "personal",
        "skills",
        "experience",
    ],
)
def test_missing_required_field_refused(dotted: str) -> None:
    doc = _fixture_doc()
    _drop(doc, dotted)
    assert RefusalCode.MISSING_FIELD in _codes(doc)


def test_wrong_type_field_refused() -> None:
    doc = _fixture_doc()
    doc["skills"]["backend"] = ["Node.js", 7]
    assert _codes(doc) == {RefusalCode.MISSING_FIELD}


def test_other_persona_refused() -> None:
    doc = _fixture_doc()
    doc["personal"]["name"] = "Somebody Else"
    assert _codes(doc) == {RefusalCode.PERSONA_MISMATCH}


def test_non_object_root_refused() -> None:
    assert _codes(b"[1, 2]") == {RefusalCode.NOT_FICTIONAL, RefusalCode.MISSING_FIELD}


def test_all_failures_collected() -> None:
    doc = _fixture_doc()
    doc["fictional"] = False
    doc["personal"]["email"] = "x@notexample.com"
    doc["personal"]["phone"] = "(617) 867-5309"
    del doc["target"]["roles"]
    assert _codes(doc, pin_to_content=False) == {
        RefusalCode.DIGEST_MISMATCH,
        RefusalCode.NOT_FICTIONAL,
        RefusalCode.EMAIL_DOMAIN,
        RefusalCode.PHONE_PATTERN,
        RefusalCode.MISSING_FIELD,
    }


def test_refusal_message_contains_no_resume_values() -> None:
    doc = _fixture_doc()
    doc["fictional"] = False
    doc["personal"]["email"] = "kiran.joshi@notexample.com"
    doc["personal"]["phone"] = "(617) 867-5309"
    data = json.dumps(doc).encode()
    with pytest.raises(ResumeRefused) as info:
        load_verified_resume(FIXTURE, PIN_LITERAL, read_bytes=_reader(data))
    text = str(info.value) + repr(info.value)
    for secret in ("kiran", "Kiran", "notexample", "867", "617", "Fernleaf"):
        assert secret not in text
    assert info.value.__cause__ is None or "kiran" not in str(info.value.__cause__)


def test_skill_entries_order_and_exclusion(verified_resume: VerifiedResume) -> None:
    entries = skill_entries_from_resume(verified_resume.to_dict())
    assert entries[0] == SkillEntry("TypeScript", "$.skills.languages[0]")
    assert SkillEntry("C#", "$.skills.languages[5]") in entries
    assert SkillEntry("GraphQL", "$.skills.backend[4]") in entries
    assert entries[-1] == SkillEntry("Grafana", "$.skills.observability[2]")
    terms = {entry.term for entry in entries}
    assert "Go" not in terms
    assert "Terraform" not in terms
    assert len(entries) == 29
    categories = [entry.resume_path.split("[")[0] for entry in entries]
    assert list(dict.fromkeys(categories)) == [
        "$.skills.languages",
        "$.skills.frontend",
        "$.skills.backend",
        "$.skills.data",
        "$.skills.messaging",
        "$.skills.cloud_devops",
        "$.skills.observability",
    ]


def test_persona_label_has_no_name() -> None:
    assert "Kiran Joshi" not in PERSONA_LABEL
