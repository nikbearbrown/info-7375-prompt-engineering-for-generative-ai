"""The shared models."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from job_search_agent import resume as resume_module
from job_search_agent.models import (
    AbandonedJudgment,
    AttemptSummary,
    DataQualityCode,
    DataQualityIssue,
    ExitCode,
    FetchErrorKind,
    FetchResult,
    Gate,
    JudgmentDiagnostic,
    JudgmentOutcome,
    JudgmentReply,
    JudgmentStatus,
    LocationCheck,
    LocationLabel,
    ModelEvidence,
    ModelJudgment,
    OutputRecord,
    ParsedBoard,
    PendingJudgment,
    Posting,
    RawRef,
    RuleVerdict,
    RunMode,
    RunReport,
    RunStatus,
    SeenState,
    Severity,
    SkillEvidence,
    VerdictLabel,
    VerifiedResume,
    exit_code_for_status,
)

SHA = "a" * 64
RUN = "2026-10-30T02-11-07Z"
T0 = datetime(2026, 10, 30, 2, 11, 7, tzinfo=UTC)


def _values(enum: Any) -> list[str]:
    return [member.value for member in enum]


# --- enums ------------------------------------------------------------------


def test_run_status_has_exactly_the_seven_contract_statuses() -> None:
    assert _values(RunStatus) == [
        "BASELINE",
        "SUCCESS_WITH_NEW",
        "SUCCESS_NO_NEW",
        "FETCH_FAILED",
        "EMPTY_RESPONSE",
        "INVALID_RESPONSE",
        "PARTIAL_FAILURE",
    ]


def test_location_label_values() -> None:
    assert _values(LocationLabel) == ["US_BASED", "NON_US", "NOT_ESTABLISHED"]


def test_judgment_status_values() -> None:
    assert _values(JudgmentStatus) == [
        "VALID",
        "INVALID_OUTPUT",
        "ERROR",
        "UNAVAILABLE",
    ]


def test_verdict_and_gate_values() -> None:
    assert _values(VerdictLabel) == ["MATCH", "NO_MATCH"]
    assert _values(Gate) == ["TITLE", "SKILLS", "EXCLUSION", "LOCATION"]


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (RunStatus.BASELINE, 0),
        (RunStatus.SUCCESS_WITH_NEW, 0),
        (RunStatus.SUCCESS_NO_NEW, 0),
        (RunStatus.PARTIAL_FAILURE, 1),
        (RunStatus.FETCH_FAILED, 2),
        (RunStatus.EMPTY_RESPONSE, 2),
        (RunStatus.INVALID_RESPONSE, 2),
    ],
)
def test_exit_code_for_status(status: RunStatus, code: int) -> None:
    assert exit_code_for_status(status) == code


def test_exit_codes_for_aborts() -> None:
    assert (ExitCode.RESUME_REFUSED, ExitCode.STATE_CORRUPT, ExitCode.CONFIG_ERROR) == (
        3,
        4,
        5,
    )


# --- builders ---------------------------------------------------------------


def _rule_verdict() -> RuleVerdict:
    return RuleVerdict(
        label=VerdictLabel.MATCH,
        location_check=LocationCheck(
            label=LocationLabel.US_BASED,
            evidence=["$.location.name"],
            reason="Seattle, WA is a US location.",
        ),
        evidence=[
            SkillEvidence(
                term="Java",
                resume_path="$.skills.languages[2]",
                posting_path="$.content",
            ),
            SkillEvidence(
                term="AWS",
                resume_path="$.skills.cloud_devops[0]",
                posting_path="$.content",
            ),
        ],
        reason="All four gates pass.",
        failed_gates=[],
    )


def _valid_judgment() -> ModelJudgment:
    return ModelJudgment(
        status=JudgmentStatus.VALID,
        label="RELEVANT",
        summary="Worth considering.",
        evidence=[
            ModelEvidence(
                resume_path="$.skills.languages[2]",
                posting_path="$.content",
                reason="Java appears in both.",
            )
        ],
        uncertainties=["Sponsorship is not stated."],
        diagnostic=JudgmentDiagnostic(
            prompt_id="judge.v1",
            prompt_sha256=SHA,
            model_requested="claude-sonnet-5-5",
            attempts=[
                AttemptSummary(
                    attempt=1,
                    raw_log_ref=f"data/live/runs/{RUN}/model/8249901/attempt-1.json",
                    first_reply=True,
                    validation_passed=True,
                    session_id="s1",
                )
            ],
        ),
    )


def _record() -> OutputRecord:
    return OutputRecord(
        posting_id="8249901",
        title="Software Engineer",
        location="Seattle, WA",
        updated_at=None,
        rule_verdict=_rule_verdict(),
        model_judgment=_valid_judgment(),
    )


def _state(**overrides: Any) -> SeenState:
    fields: dict[str, Any] = {
        "schema_version": 1,
        "provider": "greenhouse",
        "board": "stripe",
        "seeded": False,
        "seen_ids": ["8249901", "7543868"],
        "last_successful_fetch_utc": T0,
        "last_successful_run_id": RUN,
        "run_started_at_utc": T0,
        "pending": [
            PendingJudgment(
                posting_id="7543868",
                last_status=JudgmentStatus.ERROR,
                queued_run_id=RUN,
                last_attempt_run_id=RUN,
                attempts=1,
                source=RawRef(path="data/live/raw.json", sha256=SHA, index=575),
            )
        ],
    }
    fields.update(overrides)
    return SeenState.model_validate(fields)


def _report() -> RunReport:
    return RunReport(
        run_id=RUN,
        mode=RunMode.LIVE,
        seeded=False,
        provider="greenhouse",
        board="stripe",
        code_commit="0" * 40,
        code_dirty=False,
        started_at_utc=T0,
        started_at_et=T0,
        finished_at_utc=T0,
        finished_at_et=T0,
        status=RunStatus.SUCCESS_WITH_NEW,
        fetched_count=734,
        unique_valid_ids=734,
        new_count=1,
        new_ids=["8249901"],
        judgment_counts={JudgmentStatus.VALID: 1},
        data_quality_issues=[
            DataQualityIssue(
                code=DataQualityCode.TOTAL_MISMATCH, severity=Severity.WARNING
            )
        ],
        records_saved=True,
        state_saved=True,
        raw_evidence=RawRef(path="data/live/raw.json", sha256=SHA),
        model_backend="claude-cli",
    )


# --- round trips ------------------------------------------------------------


@pytest.mark.parametrize(
    "build", [_rule_verdict, _valid_judgment, _record, _state, _report]
)
def test_models_round_trip_through_json(build: Any) -> None:
    model: BaseModel = build()
    again = type(model).model_validate_json(model.model_dump_json())
    assert again == model


def test_record_keys_follow_contract_order() -> None:
    dumped = json.loads(_record().model_dump_json())
    assert list(dumped)[:6] == [
        "posting_id",
        "title",
        "location",
        "updated_at",
        "rule_verdict",
        "model_judgment",
    ]
    assert list(dumped["rule_verdict"])[:4] == [
        "label",
        "location_check",
        "evidence",
        "reason",
    ]
    assert dumped["rule_verdict"]["label"] == "MATCH"


def test_models_reject_unknown_keys() -> None:
    data = json.loads(_record().model_dump_json())
    data["surprise"] = 1
    with pytest.raises(ValidationError):
        OutputRecord.model_validate(data)


def test_skill_evidence_is_strict() -> None:
    with pytest.raises(ValidationError):
        SkillEvidence.model_validate(
            {"term": "Java", "resume_path": 1, "posting_path": "$.content"}
        )


def test_judgment_reply_strict_matches_contract_schema() -> None:
    reply = {
        "label": "RELEVANT",
        "summary": "s",
        "evidence": [{"resume_path": "$.a", "posting_path": "$.b", "reason": "r"}],
        "uncertainties": [],
    }
    assert JudgmentReply.model_validate(reply, strict=True).label == "RELEVANT"
    for broken in (
        {**reply, "label": "MATCH"},
        {**reply, "extra": 1},
        {**reply, "evidence": []},
        {k: v for k, v in reply.items() if k != "uncertainties"},
    ):
        with pytest.raises(ValidationError):
            JudgmentReply.model_validate(broken, strict=True)


# --- invariants -------------------------------------------------------------


def test_non_valid_judgment_cannot_carry_label() -> None:
    with pytest.raises(ValidationError):
        ModelJudgment(status=JudgmentStatus.INVALID_OUTPUT, label="RELEVANT")
    assert ModelJudgment(status=JudgmentStatus.UNAVAILABLE).label is None


def test_valid_judgment_needs_label_summary_and_evidence() -> None:
    with pytest.raises(ValidationError):
        ModelJudgment(status=JudgmentStatus.VALID, label="RELEVANT", summary="s")


def test_judgment_outcome_validity() -> None:
    outcome = JudgmentOutcome("8249901", _valid_judgment())
    assert outcome.is_valid
    assert outcome.status is JudgmentStatus.VALID
    assert not JudgmentOutcome("1", ModelJudgment(status=JudgmentStatus.ERROR)).is_valid


@pytest.mark.parametrize(
    "overrides",
    [
        {"seen_ids": ["1", "1"]},
        {"seen_ids": ["0123"]},
        {"seen_ids": ["8249901"]},  # pending 7543868 no longer in seen_ids
        {"schema_version": 2},
        {"last_successful_fetch_utc": datetime(2026, 10, 30)},  # naive
        {"last_successful_run_id": "2026-10-30 02:11:07"},
    ],
)
def test_state_integrity_violations_rejected(overrides: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        _state(**overrides)


def test_state_rejects_id_both_pending_and_abandoned() -> None:
    abandoned = AbandonedJudgment(
        posting_id="7543868",
        last_status=JudgmentStatus.ERROR,
        queued_run_id=RUN,
        dropped_at_utc=T0,
        reason="CLI unavailable for a week",
    )
    with pytest.raises(ValidationError):
        _state(abandoned=[abandoned])


def test_pending_cannot_be_valid_and_needs_index() -> None:
    base: dict[str, Any] = {
        "posting_id": "1",
        "last_status": JudgmentStatus.ERROR,
        "queued_run_id": RUN,
        "last_attempt_run_id": RUN,
        "attempts": 1,
        "source": RawRef(path="data/x.json", sha256=SHA, index=0),
    }
    PendingJudgment.model_validate(base)
    with pytest.raises(ValidationError):
        PendingJudgment.model_validate({**base, "last_status": JudgmentStatus.VALID})
    with pytest.raises(ValidationError):
        PendingJudgment.model_validate(
            {**base, "source": RawRef(path="data/x.json", sha256=SHA)}
        )


def test_abandoned_reason_must_not_be_blank() -> None:
    with pytest.raises(ValidationError):
        AbandonedJudgment(
            posting_id="1",
            last_status=JudgmentStatus.ERROR,
            queued_run_id=RUN,
            dropped_at_utc=T0,
            reason="   ",
        )


@pytest.mark.parametrize(
    "path",
    [
        "/Users/x/data/raw.json",
        "../raw.json",
        "data/../../x",
        "",
        "C:/x",
        "a\\b",
        "./a",
    ],
)
def test_raw_ref_rejects_non_repo_relative_paths(path: str) -> None:
    with pytest.raises(ValidationError):
        RawRef(path=path, sha256=SHA)


def test_report_new_count_must_match_ids() -> None:
    data = json.loads(_report().model_dump_json())
    data["new_count"] = 2
    with pytest.raises(ValidationError):
        RunReport.model_validate(data)


# --- port values ------------------------------------------------------------


def test_verified_resume_is_opaque_and_copies(
    verified_resume: VerifiedResume,
) -> None:
    assert "example.com" not in repr(verified_resume)
    copy_ = verified_resume.to_dict()
    first = copy_["skills"]["languages"][0]
    copy_["skills"]["languages"].insert(0, "Go-not-in-fixture")
    assert verified_resume.to_dict()["skills"]["languages"][0] == first


def test_verified_resume_cannot_be_constructed_directly() -> None:
    data: dict[str, Any] = {"skills": {"x": ["Java"]}}
    with pytest.raises(TypeError, match="load_verified_resume"):
        VerifiedResume(data, sha256=SHA, source_path="persona/x.json")
    with pytest.raises(TypeError, match="load_verified_resume"):
        VerifiedResume(data, sha256=SHA, source_path="persona/x.json", token=object())


def test_verified_resume_still_validates_digest_and_path() -> None:
    token = resume_module._GATE_TOKEN  # noqa: SLF001 - the gate's own token
    data: dict[str, Any] = {"skills": {"x": ["Java"]}}
    with pytest.raises(ValueError, match="sha256"):
        VerifiedResume(data, sha256="ABC", source_path="persona/x.json", token=token)
    with pytest.raises(ValueError, match="relative"):
        VerifiedResume(data, sha256=SHA, source_path="/abs/x.json", token=token)


def _posting(**overrides: Any) -> Posting:
    fields: dict[str, Any] = {
        "posting_id": "8249901",
        "index": 566,
        "raw": {"id": 8249901, "title": "Software Engineer"},
        "title": "Software Engineer",
        "location_name": None,
        "updated_at": None,
        "content_raw": "",
        "department_names": ("Engineering",),
    }
    fields.update(overrides)
    return Posting(**fields)


def test_posting_is_hashable_and_hides_raw_from_repr() -> None:
    posting = _posting(content_raw="&lt;p&gt;secret-ish&lt;/p&gt;")
    assert hash(posting) == hash(
        _posting(raw={}, content_raw="&lt;p&gt;secret-ish&lt;/p&gt;")
    )
    assert "secret-ish" not in repr(posting)


def test_parsed_board_helpers() -> None:
    issue = DataQualityIssue(
        code=DataQualityCode.MISSING_ID, severity=Severity.ERROR, index=3
    )
    board = ParsedBoard(
        postings=(_posting(),), fetched_count=2, meta_total=2, data_quality=(issue,)
    )
    assert board.valid_ids == ("8249901",)
    assert board.error_count == 1
    assert not board.is_empty
    assert ParsedBoard(postings=(), fetched_count=0, meta_total=0).is_empty


def test_fetch_result_ok_requires_body_and_no_error() -> None:
    ok = FetchResult("u", "u", (), 200, {}, b"{}", None)
    http_error = FetchResult("u", "u", (), 404, {}, b"nope", FetchErrorKind.HTTP_STATUS)
    no_body = FetchResult("u", None, (), None, {}, None, FetchErrorKind.TRANSPORT)
    assert ok.ok
    assert not http_error.ok
    assert http_error.body == b"nope"  # body kept so the raw file can still be saved
    assert not no_body.ok
