"""CONTRACT §8 validator (PLAN §3.5, §5.4)."""

from __future__ import annotations

import json
from typing import Any

import pytest

from job_search_agent.judge.payload import build_posting_payload, build_resume_payload
from job_search_agent.judge.validator import (
    Rejection,
    RejectionCode,
    ValidJudgment,
    evidence_path_findings,
    validate_reply,
)
from job_search_agent.privacy import sensitive_values
from job_search_agent.resume import PERSONA_LABEL
from tests.judge.doubles import valid_reply
from tests.tools.builders import fixture_resume, small_posting

RESUME = build_resume_payload(fixture_resume())
POSTING = build_posting_payload(small_posting())


def _check(text: str) -> ValidJudgment | Rejection:
    return validate_reply(text, RESUME, POSTING)


def _rejected(text: str, *codes: RejectionCode) -> Rejection:
    result = _check(text)
    assert isinstance(result, Rejection), result
    for code in codes:
        assert code in result.codes, (code, result.codes)
    assert result.original_text == text
    return result


def _dump(obj: Any) -> str:
    return json.dumps(obj)


# --- accepted ---------------------------------------------------------------


def test_valid_reply_accepted() -> None:
    result = _check(_dump(valid_reply()))
    assert isinstance(result, ValidJudgment)
    assert result.reply.label == "RELEVANT"
    assert result.reply.evidence[0].resume_path == "$.skills.languages[2]"


def test_surrounding_whitespace_accepted() -> None:
    assert isinstance(_check("\n \t" + _dump(valid_reply()) + "\r\n "), ValidJudgment)


def test_non_json_whitespace_around_object_rejected() -> None:
    _rejected(" " + _dump(valid_reply()), RejectionCode.TEXT_OUTSIDE_OBJECT)


def test_not_relevant_and_empty_uncertainties_accepted() -> None:
    reply = valid_reply(label="NOT_RELEVANT", uncertainties=[])
    assert isinstance(_check(_dump(reply)), ValidJudgment)


def test_non_leaf_path_accepted() -> None:
    entry = {
        "resume_path": "$.skills.backend",
        "posting_path": "$.location",
        "reason": "r",
    }
    assert isinstance(_check(_dump(valid_reply(evidence=[entry]))), ValidJudgment)


# --- framing ----------------------------------------------------------------


def test_not_json() -> None:
    _rejected("{label: RELEVANT}", RejectionCode.NOT_JSON)
    _rejected("RELEVANT", RejectionCode.NOT_JSON)


def test_empty_text() -> None:
    _rejected("  \n", RejectionCode.EMPTY)


def test_prose_before() -> None:
    _rejected(
        "Here is my answer: " + _dump(valid_reply()), RejectionCode.TEXT_OUTSIDE_OBJECT
    )


def test_prose_after() -> None:
    _rejected(
        _dump(valid_reply()) + "\nHope this helps.", RejectionCode.TEXT_OUTSIDE_OBJECT
    )


def test_json_fence() -> None:
    _rejected("```json\n" + _dump(valid_reply()) + "\n```", RejectionCode.CODE_FENCE)


def test_bare_fence() -> None:
    _rejected("```\n" + _dump(valid_reply()) + "\n```", RejectionCode.CODE_FENCE)


def test_top_level_array() -> None:
    _rejected(_dump([valid_reply()]), RejectionCode.TOP_LEVEL_NOT_OBJECT)


def test_duplicate_keys() -> None:
    text = _dump(valid_reply())[:-1] + ', "label": "NOT_RELEVANT"}'
    _rejected(text, RejectionCode.DUPLICATE_KEY)


def test_duplicate_keys_nested() -> None:
    text = _dump(valid_reply()).replace(
        '"reason": "Java appears in the posting."',
        '"reason": "a", "reason": "b"',
    )
    _rejected(text, RejectionCode.DUPLICATE_KEY)


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_nan_constant(constant: str) -> None:
    text = _dump(valid_reply(extra_marker=0)).replace(
        '"extra_marker": 0', f'"extra_marker": {constant}'
    )
    _rejected(text, RejectionCode.NON_FINITE_NUMBER)


# --- keys -------------------------------------------------------------------


@pytest.mark.parametrize("key", ["label", "summary", "evidence", "uncertainties"])
def test_missing_key(key: str) -> None:
    reply = valid_reply()
    del reply[key]
    _rejected(_dump(reply), RejectionCode.MISSING_KEY)


def test_extra_top_key() -> None:
    _rejected(_dump(valid_reply(confidence=0.9)), RejectionCode.EXTRA_KEY)


def test_extra_evidence_key() -> None:
    entry = dict(valid_reply()["evidence"][0], weight=1)
    _rejected(_dump(valid_reply(evidence=[entry])), RejectionCode.EXTRA_KEY)


def test_missing_evidence_key() -> None:
    entry = dict(valid_reply()["evidence"][0])
    del entry["reason"]
    _rejected(_dump(valid_reply(evidence=[entry])), RejectionCode.MISSING_KEY)


# --- labels -----------------------------------------------------------------


def test_label_lowercase() -> None:
    _rejected(_dump(valid_reply(label="relevant")), RejectionCode.BAD_LABEL)


def test_label_MATCH() -> None:  # noqa: N802 - name fixed by PLAN §3.5
    _rejected(_dump(valid_reply(label="MATCH")), RejectionCode.BAD_LABEL)


def test_label_non_string() -> None:
    _rejected(_dump(valid_reply(label=1)), RejectionCode.BAD_LABEL)


# --- types ------------------------------------------------------------------


def test_summary_non_string() -> None:
    _rejected(_dump(valid_reply(summary=["a"])), RejectionCode.WRONG_TYPE)


def test_uncertainties_null() -> None:
    _rejected(_dump(valid_reply(uncertainties=None)), RejectionCode.WRONG_TYPE)


def test_uncertainties_with_int() -> None:
    _rejected(_dump(valid_reply(uncertainties=["x", 3])), RejectionCode.WRONG_TYPE)


def test_evidence_not_list() -> None:
    entry = valid_reply()["evidence"][0]
    _rejected(_dump(valid_reply(evidence=entry)), RejectionCode.WRONG_TYPE)


def test_evidence_item_not_object() -> None:
    _rejected(
        _dump(valid_reply(evidence=["$.skills.languages[2]"])), RejectionCode.WRONG_TYPE
    )


def test_evidence_empty() -> None:
    _rejected(_dump(valid_reply(evidence=[])), RejectionCode.EMPTY_EVIDENCE)


def test_reason_empty() -> None:
    entry = dict(valid_reply()["evidence"][0], reason="")
    _rejected(_dump(valid_reply(evidence=[entry])), RejectionCode.EMPTY_REASON)


def test_path_non_string() -> None:
    entry = dict(valid_reply()["evidence"][0], resume_path=["$.skills"])
    _rejected(_dump(valid_reply(evidence=[entry])), RejectionCode.WRONG_TYPE)


# --- paths ------------------------------------------------------------------


def _with_paths(resume_path: str, posting_path: str) -> str:
    entry = {"resume_path": resume_path, "posting_path": posting_path, "reason": "r"}
    return _dump(valid_reply(evidence=[entry]))


def test_resume_path_nonexistent() -> None:
    _rejected(
        _with_paths("$.skills.backend[9]", "$.content"),
        RejectionCode.RESUME_PATH_NOT_FOUND,
    )


def test_posting_path_nonexistent() -> None:
    _rejected(
        _with_paths("$.skills.backend[0]", "$.salary"),
        RejectionCode.POSTING_PATH_NOT_FOUND,
    )


@pytest.mark.parametrize(
    "path",
    [
        "skills.backend[0]",
        "$.skills.backend[-1]",
        "$.skills.*",
        "$['skills']",
        "$.skills.backend[01]",
        "$..x",
        "",
    ],
)
def test_path_bad_syntax(path: str) -> None:
    _rejected(_with_paths(path, "$.content"), RejectionCode.PATH_SYNTAX)


def test_path_to_field_not_sent() -> None:
    # The fixture has $.personal.email, but the payload never contains it (A18).
    _rejected(
        _with_paths("$.personal.email", "$.content"),
        RejectionCode.RESUME_PATH_NOT_FOUND,
    )
    _rejected(
        _with_paths("$.experience[0].company", "$.content"),
        RejectionCode.RESUME_PATH_NOT_FOUND,
    )
    _rejected(
        _with_paths("$.skills.backend[0]", "$.absolute_url"),
        RejectionCode.POSTING_PATH_NOT_FOUND,
    )


def test_root_path_rejected() -> None:
    _rejected(_with_paths("$", "$.content"), RejectionCode.PATH_IS_ROOT)
    _rejected(_with_paths("$.skills.backend[0]", "$"), RejectionCode.PATH_IS_ROOT)


def test_index_into_string_rejected() -> None:
    _rejected(
        _with_paths("$.skills.backend[0]", "$.content[0]"),
        RejectionCode.POSTING_PATH_NOT_FOUND,
    )


def test_every_bad_entry_reported() -> None:
    good = valid_reply()["evidence"][0]
    bad = {"resume_path": "$.nope", "posting_path": "$.nope", "reason": "r"}
    result = _rejected(_dump(valid_reply(evidence=[good, bad])))
    assert set(result.codes) == {
        RejectionCode.RESUME_PATH_NOT_FOUND,
        RejectionCode.POSTING_PATH_NOT_FOUND,
    }
    assert result.details == ("evidence.1.resume_path", "evidence.1.posting_path")


def test_validator_never_repairs() -> None:
    for text in (
        "```json\n" + _dump(valid_reply()) + "\n```",
        "Sure! " + _dump(valid_reply()),
        _dump(valid_reply(label="relevant")),
    ):
        result = _check(text)
        assert isinstance(result, Rejection)
        assert result.original_text is text


# --- path findings (experiment metric) ---------------------------------------


def test_path_findings_counts_parseable_reply_even_if_schema_fails() -> None:
    bad = {"resume_path": "$.nope", "posting_path": "$.content", "reason": "r"}
    good = valid_reply()["evidence"][0]
    text = _dump(valid_reply(label="maybe", evidence=[good, bad, "junk"]))
    findings = evidence_path_findings(text, RESUME, POSTING)
    assert findings is not None
    assert (findings.entries, findings.valid_entries) == (2, 1)


def test_path_findings_none_for_unparseable() -> None:
    assert evidence_path_findings("```json\n{}\n```", RESUME, POSTING) is None
    assert evidence_path_findings("{}", RESUME, POSTING) is None


# --- review fix 5: RESUME_VALUE_ECHO ----------------------------------------------


def test_echo_check_runs_only_when_values_are_given() -> None:
    resume = fixture_resume()
    name = resume.to_dict()["personal"]["name"]
    text = _dump(valid_reply(summary=f"{name} is a fit."))
    assert isinstance(_check(text), ValidJudgment)  # no values: structural only
    result = validate_reply(
        text,
        build_resume_payload(resume),
        build_posting_payload(small_posting()),
        echo_values=sensitive_values(resume),
        echo_allow=(PERSONA_LABEL,),
    )
    assert isinstance(result, Rejection)
    assert result.codes == (RejectionCode.RESUME_VALUE_ECHO,)
    assert result.details == ("summary",)
    assert name not in " ".join(result.details)
    assert result.original_text == text
