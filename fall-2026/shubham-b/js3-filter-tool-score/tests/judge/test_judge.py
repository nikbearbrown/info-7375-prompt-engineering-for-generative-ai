"""``judge_posting_detailed``: retry once, and the raw-reply log (PLAN §5.5)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from job_search_agent.config import ModelSettings
from job_search_agent.judge.backend import ClaudeCliBackend
from job_search_agent.judge.judge import (
    PROBE_PROMPT,
    CliJudge,
    JudgeRun,
    build_backend,
    build_judge,
    judge_posting_detailed,
    probe_model,
)
from job_search_agent.judge.prompt import load_prompt
from job_search_agent.judge.rawlog import RawReplyLog
from job_search_agent.models import (
    BackendErrorKind,
    CompletedCommand,
    JudgmentStatus,
)
from job_search_agent.ports import Judge
from tests.conftest import REPO_ROOT
from tests.fakes import FakeBackend, FakeRunner, FixedClock
from tests.judge.doubles import MemoryWriter, valid_reply
from tests.tools.builders import fixture_resume, small_posting

LOG_DIR = "live/runs/2026-10-30T02-11-07Z/model/1234"
VALID = json.dumps(valid_reply())
INVALID = "```json\n" + VALID + "\n```"
PROMPT = load_prompt(REPO_ROOT, "v1")


def _run(
    backend: FakeBackend, tmp_path: Path, *, retry_once: bool = True
) -> tuple[JudgeRun, MemoryWriter]:
    writer = MemoryWriter(tmp_path)
    run = judge_posting_detailed(
        backend,
        PROMPT,
        small_posting(),
        fixture_resume(),
        RawReplyLog(writer),
        log_dir=LOG_DIR,
        model_requested="claude-sonnet-5-5",
        retry_once=retry_once,
    )
    return run, writer


def _log(writer: MemoryWriter, attempt: int) -> dict[str, Any]:
    log: dict[str, Any] = writer.json[f"{LOG_DIR}/attempt-{attempt}.json"]
    return log


def test_first_valid_no_retry(tmp_path: Path) -> None:
    backend = FakeBackend([VALID])
    run, writer = _run(backend, tmp_path)
    judgment = run.outcome.judgment
    assert judgment.status is JudgmentStatus.VALID
    assert judgment.label == "RELEVANT"
    assert judgment.evidence[0].resume_path == "$.skills.languages[2]"
    assert backend.calls == 1
    assert list(writer.json) == [f"{LOG_DIR}/attempt-1.json"]
    (attempt,) = judgment.diagnostic.attempts
    assert attempt.raw_log_ref == f"data/{LOG_DIR}/attempt-1.json"
    assert attempt.validation_passed is True
    assert judgment.diagnostic.prompt_sha256 == PROMPT.sha256


def test_invalid_then_valid_both_attempts_logged_first_flagged(tmp_path: Path) -> None:
    backend = FakeBackend([INVALID, VALID])
    run, writer = _run(backend, tmp_path)
    judgment = run.outcome.judgment
    assert judgment.status is JudgmentStatus.VALID
    first, second = judgment.diagnostic.attempts
    assert first.first_reply and not second.first_reply
    assert first.validation_passed is False and "CODE_FENCE" in first.validation_codes
    assert second.validation_passed is True
    log1, log2 = _log(writer, 1), _log(writer, 2)
    assert log1["first_reply"] is True and log2["first_reply"] is False
    assert log1["validation"] == {"passed": False, "codes": ["CODE_FENCE"]}
    assert log2["validation"] == {"passed": True, "codes": []}
    assert json.loads(log1["stdout_raw"])["result"] == INVALID


def test_invalid_twice_INVALID_OUTPUT(tmp_path: Path) -> None:  # noqa: N802
    backend = FakeBackend([INVALID, "Not JSON at all"])
    run, writer = _run(backend, tmp_path)
    judgment = run.outcome.judgment
    assert judgment.status is JudgmentStatus.INVALID_OUTPUT
    assert judgment.label is None and judgment.summary is None
    assert judgment.evidence == [] and judgment.uncertainties == []
    assert len(judgment.diagnostic.attempts) == 2
    assert len(writer.json) == 2
    assert not run.outcome.is_valid


def test_retry_prompt_identical(tmp_path: Path) -> None:
    backend = FakeBackend([INVALID, VALID])
    _, writer = _run(backend, tmp_path)
    assert backend.prompts[0].encode() == backend.prompts[1].encode()
    assert _log(writer, 1)["payload_sha256"] == _log(writer, 2)["payload_sha256"]
    assert _log(writer, 1)["session_id"] != _log(writer, 2)["session_id"]
    # A second, independent judgment of the same posting renders the same bytes.
    again = FakeBackend([VALID])
    judge_posting_detailed(
        again,
        PROMPT,
        small_posting(),
        fixture_resume(),
        RawReplyLog(MemoryWriter(tmp_path / "again")),
        log_dir=LOG_DIR,
        model_requested=None,
    )
    assert again.prompts[0] == backend.prompts[0]


def test_no_retry_when_retry_once_false(tmp_path: Path) -> None:
    backend = FakeBackend([INVALID])
    run, writer = _run(backend, tmp_path, retry_once=False)
    assert backend.calls == 1
    assert run.outcome.status is JudgmentStatus.INVALID_OUTPUT
    assert len(run.attempts) == 1 and len(writer.json) == 1


def test_backend_error_is_ERROR_no_retry(tmp_path: Path) -> None:  # noqa: N802
    backend = FakeBackend([BackendErrorKind.NONZERO_EXIT, VALID])
    run, writer = _run(backend, tmp_path)
    judgment = run.outcome.judgment
    assert judgment.status is JudgmentStatus.ERROR
    assert backend.calls == 1
    attempt = judgment.diagnostic.attempts[0]
    assert attempt.validation_passed is None
    assert attempt.backend_error is BackendErrorKind.NONZERO_EXIT
    assert _log(writer, 1)["validation"] == {"passed": None, "codes": []}


def test_error_on_retry_is_ERROR(tmp_path: Path) -> None:  # noqa: N802
    backend = FakeBackend([INVALID, BackendErrorKind.TIMEOUT])
    run, _ = _run(backend, tmp_path)
    assert run.outcome.status is JudgmentStatus.ERROR
    assert backend.calls == 2


def test_timeout_is_ERROR(tmp_path: Path) -> None:  # noqa: N802
    run, writer = _run(FakeBackend([BackendErrorKind.TIMEOUT]), tmp_path)
    assert run.outcome.status is JudgmentStatus.ERROR
    assert _log(writer, 1)["exit_code"] is None
    assert _log(writer, 1)["backend_error"] == "TIMEOUT"


def test_is_error_envelope_is_ERROR(tmp_path: Path) -> None:  # noqa: N802
    run, writer = _run(FakeBackend([BackendErrorKind.IS_ERROR]), tmp_path)
    assert run.outcome.status is JudgmentStatus.ERROR
    assert _log(writer, 1)["is_error"] is True


def test_unavailable_makes_no_call(tmp_path: Path) -> None:
    backend = FakeBackend(available=False, unavailable_reason="cli_not_found")
    run, writer = _run(backend, tmp_path)
    judgment = run.outcome.judgment
    assert judgment.status is JudgmentStatus.UNAVAILABLE
    assert judgment.diagnostic.unavailable_reason == "cli_not_found"
    assert backend.calls == 0 and writer.json == {} and run.attempts == ()


def test_raw_reply_never_overwrites_structured_fields(tmp_path: Path) -> None:
    sneaky = json.dumps(valid_reply(label="relevant", summary="RAW SUMMARY"))
    run, writer = _run(FakeBackend([sneaky, sneaky]), tmp_path)
    judgment = run.outcome.judgment
    dumped = judgment.model_dump_json()
    assert "RAW SUMMARY" not in dumped
    assert judgment.label is None and judgment.summary is None
    assert "RAW SUMMARY" in _log(writer, 1)["stdout_raw"]


def test_raw_log_fields(tmp_path: Path) -> None:
    _, writer = _run(FakeBackend([VALID]), tmp_path)
    log = _log(writer, 1)
    for key in (
        "prompt_id",
        "prompt_sha256",
        "payload_sha256",
        "model_requested",
        "model_served",
        "claude_version",
        "argv",
        "cwd_kind",
        "started_at_utc",
        "started_at_et",
        "duration_ms",
        "exit_code",
        "stdout_raw",
        "stderr",
        "session_id",
        "is_error",
        "total_cost_usd",
        "validation",
    ):
        assert key in log, key
    assert log["prompt_id"] == "judge.v1"
    assert log["cwd_kind"] == "fresh-empty"
    assert log["started_at_et"].endswith("-04:00") or log["started_at_et"].endswith(
        "-05:00"
    )
    assert log["claude_version"] == "fake 0.0.0"


def test_unverified_resume_refused(tmp_path: Path) -> None:
    with pytest.raises(TypeError):
        judge_posting_detailed(
            FakeBackend([VALID]),
            PROMPT,
            small_posting(),
            fixture_resume().to_dict(),  # type: ignore[arg-type]
            RawReplyLog(MemoryWriter(tmp_path)),
            log_dir=LOG_DIR,
            model_requested=None,
        )


def test_cli_judge_implements_port(tmp_path: Path) -> None:
    backend = FakeBackend([INVALID, VALID])
    judge: Judge = CliJudge(
        backend,
        PROMPT,
        RawReplyLog(MemoryWriter(tmp_path)),
        model_requested="claude-sonnet-5-5",
    )
    outcome = judge.judge(small_posting(), fixture_resume(), log_dir=LOG_DIR)
    assert outcome.is_valid and backend.calls == 2  # the pipeline retries once


def _settings(backend: str = "claude-cli") -> ModelSettings:
    return ModelSettings(
        backend=backend,  # type: ignore[arg-type]
        executable="claude",
        model_id="claude-sonnet-5-5",
        timeout_s=180.0,
        prompt_version="v1",
    )


def test_build_backend_none_is_unavailable(tmp_path: Path) -> None:
    clock = FixedClock(datetime(2026, 10, 30, tzinfo=UTC))
    writer = MemoryWriter(tmp_path)
    backend = build_backend(
        _settings("none"),
        runner=FakeRunner(),
        make_empty_dir=writer.make_empty_dir,
        clock=clock,
    )
    assert backend.availability().reason == "backend_none"
    cli = build_backend(
        _settings(),
        runner=FakeRunner(),
        make_empty_dir=writer.make_empty_dir,
        clock=clock,
    )
    assert isinstance(cli, ClaudeCliBackend) and cli.model_id == "claude-sonnet-5-5"
    judge = build_judge(
        _settings("none"),
        PROMPT,
        runner=FakeRunner(),
        writer=writer,
        make_empty_dir=writer.make_empty_dir,
        clock=clock,
        repo_rel=lambda rel: f"data/{rel}",
    )
    outcome = judge.judge(small_posting(), fixture_resume(), log_dir=LOG_DIR)
    assert outcome.status is JudgmentStatus.UNAVAILABLE


def test_probe_model_records_facts(tmp_path: Path) -> None:
    clock = FixedClock(datetime(2026, 10, 30, 0, 5, tzinfo=UTC))
    writer = MemoryWriter(tmp_path)
    envelope = json.dumps(
        {
            "is_error": False,
            "result": "OK",
            "session_id": "s-probe",
            "modelUsage": {"claude-sonnet-5-5": {}},
        }
    )
    runner = FakeRunner(
        [
            CompletedCommand((), 0, "2.1.312 (Claude Code)", "", False, 5),
            CompletedCommand((), 0, envelope, "", False, 900),
        ]
    )
    backend = ClaudeCliBackend(
        executable="claude",
        model_id="claude-sonnet-5-5",
        timeout_s=180.0,
        runner=runner,
        make_empty_dir=writer.make_empty_dir,
        clock=clock,
        which=lambda name: "/x/claude",
        base_env={"PATH": "/bin", "ANTHROPIC_API_KEY": "sk-ant-zzz"},
    )
    result = probe_model(
        backend, model_requested="claude-sonnet-5-5", clock=clock, writer=writer
    )
    report = result.report
    assert result.data_rel == "doctor/2026-10-30T00-05-00Z.json"
    assert report.available and report.reply_is_ok
    assert report.session_id == "s-probe"
    assert report.model_served == ["claude-sonnet-5-5"]
    assert report.claude_version == "2.1.312 (Claude Code)"
    assert report.argv[0] == "claude" and "--safe-mode" in report.argv
    assert "ANTHROPIC_API_KEY" in report.env_removed
    assert runner.calls[1].stdin == PROBE_PROMPT
    assert "sk-ant-zzz" not in json.dumps(writer.json)


def test_probe_model_unavailable(tmp_path: Path) -> None:
    clock = FixedClock(datetime(2026, 10, 30, tzinfo=UTC))
    backend = FakeBackend(available=False, unavailable_reason="cli_not_found")
    result = probe_model(backend, model_requested="m", clock=clock)
    assert not result.report.available
    assert result.report.unavailable_reason == "cli_not_found"
    assert result.data_rel is None and backend.calls == 0


def test_cli_judge_marks_seeded_logs(tmp_path: Path) -> None:
    writer = MemoryWriter(tmp_path)
    judge = CliJudge(
        FakeBackend([VALID]),
        PROMPT,
        RawReplyLog(writer),
        model_requested="claude-sonnet-5-5",
        seeded=True,
    )
    judge.judge(small_posting(), fixture_resume(), log_dir=LOG_DIR)
    assert _log(writer, 1)["seeded"] is True


# --- review fix 5: résumé values echoed in free text are rejected -----------------


def _resume_doc() -> dict[str, Any]:
    return fixture_resume().to_dict()


@pytest.mark.parametrize("where", ["summary", "reason", "uncertainty"])
def test_resume_value_echo_is_invalid_after_retry(tmp_path: Path, where: str) -> None:
    doc = _resume_doc()
    leaks = {
        "summary": f"{doc['personal']['name']} fits this role.",
        "reason": f"Matches work at {doc['experience'][0]['company']}.",
        "uncertainty": f"Unclear: {doc['projects'][0]['bullets'][0]}",
    }
    reply = valid_reply()
    if where == "summary":
        reply["summary"] = leaks["summary"]
    elif where == "reason":
        reply["evidence"][0]["reason"] = leaks["reason"]
    else:
        reply["uncertainties"] = ["ok", leaks["uncertainty"]]
    text = json.dumps(reply)
    backend = FakeBackend([text, text])
    run, writer = _run(backend, tmp_path)
    judgment = run.outcome.judgment
    assert judgment.status is JudgmentStatus.INVALID_OUTPUT
    assert backend.calls == 2  # stricter validation flows through retry-once
    for attempt in judgment.diagnostic.attempts:
        assert attempt.validation_codes == ["RESUME_VALUE_ECHO"]
    assert judgment.summary is None and judgment.uncertainties == []
    assert _log(writer, 1)["validation"]["codes"] == ["RESUME_VALUE_ECHO"]


def test_skill_terms_and_persona_label_are_not_an_echo(tmp_path: Path) -> None:
    doc = _resume_doc()
    terms = [
        t
        for key in ("languages", "backend", "cloud_devops")
        for t in doc["skills"][key]
    ]
    reply = valid_reply(
        summary="kiran-joshi (fictional) lists " + ", ".join(terms) + ".",
        uncertainties=[f"Whether {doc['target']['roles'][0]} covers this level."],
    )
    reply["evidence"][0]["reason"] = f"{terms[0]} and {terms[-1]} both appear."
    backend = FakeBackend([json.dumps(reply)])
    run, _ = _run(backend, tmp_path)
    assert run.outcome.judgment.status is JudgmentStatus.VALID
    assert backend.calls == 1


# --- review fix 7: no process started means UNAVAILABLE (CONTRACT §8) -------------


@pytest.mark.parametrize(
    ("kind", "reason"),
    [
        (BackendErrorKind.CLI_NOT_FOUND, "cli_not_found"),
        (BackendErrorKind.WORKDIR_FAILED, "workdir_failed"),
    ],
)
def test_failure_before_spawn_is_unavailable_not_error(
    tmp_path: Path, kind: BackendErrorKind, reason: str
) -> None:
    backend = FakeBackend([kind])
    run, _ = _run(backend, tmp_path)
    judgment = run.outcome.judgment
    assert judgment.status is JudgmentStatus.UNAVAILABLE
    assert judgment.diagnostic.unavailable_reason == reason
    assert backend.calls == 1  # never retried
    assert judgment.diagnostic.attempts[0].backend_error is kind


def test_failure_after_spawn_is_still_error(tmp_path: Path) -> None:
    backend = FakeBackend([BackendErrorKind.SPAWN_FAILED])
    run, _ = _run(backend, tmp_path)
    assert run.outcome.judgment.status is JudgmentStatus.ERROR
