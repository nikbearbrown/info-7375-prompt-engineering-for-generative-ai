"""Prompt contract files (PLAN §5.3)."""

from __future__ import annotations

import hashlib

import pytest

from job_search_agent.judge.prompt import (
    POSTING_PLACEHOLDER,
    REQUIRED_SECTIONS,
    RESUME_PLACEHOLDER,
    PromptError,
    changed_sections,
    contract_from_bytes,
    load_prompt,
)
from tests.conftest import REPO_ROOT

V1_LABEL_DEFINITION = (
    "RELEVANT if, based only on the supplied text, the posting is worth Kiran "
    "considering given the résumé's target roles, levels, locations, exclusions and "
    "skills; otherwise NOT_RELEVANT."
)


def _v1_text() -> str:
    return (REPO_ROOT / "prompts/judge.v1.md").read_text(encoding="utf-8")


def test_placeholders_once_each() -> None:
    text = _v1_text()
    assert text.count(RESUME_PLACEHOLDER) == 1
    assert text.count(POSTING_PLACEHOLDER) == 1
    contract = load_prompt(REPO_ROOT, "v1")
    rendered = contract.render('{"r": 1}', '{"p": "{{RESUME_JSON}}"}')
    assert '{"r": 1}' in rendered
    assert '{"p": "{{RESUME_JSON}}"}' in rendered  # payload text is not re-scanned
    assert rendered.count("{{") == 1


def test_prompt_sha_recorded() -> None:
    contract = load_prompt(REPO_ROOT, "v1")
    raw = (REPO_ROOT / "prompts/judge.v1.md").read_bytes()
    assert contract.sha256 == hashlib.sha256(raw).hexdigest()
    assert contract.prompt_id == "judge.v1"
    assert contract.repo_path == "prompts/judge.v1.md"


def test_v1_sections_in_order_and_label_definition_is_general() -> None:
    contract = load_prompt(REPO_ROOT, "v1")
    assert tuple(contract.sections) == REQUIRED_SECTIONS
    assert contract.sections["label_definition"] == V1_LABEL_DEFINITION


def test_v1_header_records_claude_draft_and_is_not_sent() -> None:
    text = _v1_text()
    header = text.split("<!-- section:role -->", 1)[0]
    assert "Drafted by Claude" in header and "2026-10-29" in header
    rendered = load_prompt(REPO_ROOT, "v1").render("{}", "{}")
    assert "Drafted by Claude" not in rendered
    assert "<!--" not in rendered


def test_v1_output_schema_forbids_fences_and_prose() -> None:
    schema = load_prompt(REPO_ROOT, "v1").sections["output_schema"]
    assert "Output only the JSON object, no code fences, no other text." in schema


def test_render_is_byte_identical() -> None:
    contract = load_prompt(REPO_ROOT, "v1")
    assert contract.render("{}", "[]") == contract.render("{}", "[]")


def _make(sections: dict[str, str]) -> bytes:
    parts = ["header\n"]
    for name, body in sections.items():
        parts.append(f"<!-- section:{name} -->\n{body}\n<!-- /section -->\n")
    return "\n".join(parts).encode("utf-8")


def _base() -> dict[str, str]:
    sections = {name: f"body of {name}" for name in REQUIRED_SECTIONS}
    sections["inputs"] = f"{RESUME_PLACEHOLDER}\n{POSTING_PLACEHOLDER}"
    return sections


def test_missing_or_reordered_section_rejected() -> None:
    sections = _base()
    del sections["task"]
    with pytest.raises(PromptError):
        contract_from_bytes(_make(sections), version="v9", repo_path="p")
    reordered = dict(reversed(list(_base().items())))
    with pytest.raises(PromptError):
        contract_from_bytes(_make(reordered), version="v9", repo_path="p")


def test_placeholder_outside_inputs_rejected() -> None:
    sections = _base()
    sections["task"] = f"see {RESUME_PLACEHOLDER}"
    with pytest.raises(PromptError):
        contract_from_bytes(_make(sections), version="v9", repo_path="p")


def test_unbalanced_marker_rejected() -> None:
    raw = _make(_base()) + b"<!-- /section -->\n"
    with pytest.raises(PromptError):
        contract_from_bytes(raw, version="v9", repo_path="p")


def test_changed_sections_lists_only_changed() -> None:
    v1 = contract_from_bytes(_make(_base()), version="v1", repo_path="a")
    changed = _base()
    changed["label_definition"] = "different"
    v2 = contract_from_bytes(_make(changed), version="v2", repo_path="b")
    assert changed_sections(v1, v2) == ["label_definition"]
    changed["output_schema"] = "also different"
    v2b = contract_from_bytes(_make(changed), version="v2", repo_path="b")
    assert changed_sections(v1, v2b) == ["label_definition", "output_schema"]


def test_v2_differs_from_v1_in_exactly_one_section() -> None:
    if not (REPO_ROOT / "prompts/judge.v2.md").exists():
        pytest.skip("judge.v2.md is written by the student after the v1 dev run")
    v1 = load_prompt(REPO_ROOT, "v1")
    v2 = load_prompt(REPO_ROOT, "v2")
    assert len(changed_sections(v1, v2)) == 1


def test_bad_version_rejected() -> None:
    with pytest.raises(PromptError):
        load_prompt(REPO_ROOT, "../x")
    with pytest.raises(PromptError):
        load_prompt(REPO_ROOT, "v99")
