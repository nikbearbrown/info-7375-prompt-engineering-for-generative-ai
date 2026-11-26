"""Judging one posting: render, call, validate, retry once, log (PLAN §5.5).

* The call is made only when ``backend.availability()`` says so; otherwise the
  judgment is ``UNAVAILABLE`` and nothing is called or logged.
* A failed call (spawn, timeout, non-zero exit, bad envelope, ``is_error``) is
  ``ERROR`` and is **not** retried; the pipeline keeps the posting pending. A failure
  before any process started (``PRE_SPAWN_ERRORS``: executable gone, working
  directory not creatable) is ``UNAVAILABLE`` instead (CONTRACT §8), also pending.
* A reply that fails validation is retried **once** (when ``retry_once``) with the
  byte-identical prompt in a new process. Two invalid replies give
  ``INVALID_OUTPUT``. Experiments pass ``retry_once=False`` and score the first reply.
* Every attempt writes its own raw-reply log file. Only a ``ValidJudgment`` fills the
  record's structured fields; the record holds just pointers to the logs.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict

from job_search_agent.clock import format_run_id, to_eastern
from job_search_agent.config import ModelSettings
from job_search_agent.fsio import OutputRoot
from job_search_agent.judge.backend import (
    ADDED_ENV,
    STRIPPED_ENV,
    ClaudeCliBackend,
    MakeEmptyDir,
    UnavailableBackend,
)
from job_search_agent.judge.payload import (
    build_posting_payload,
    build_resume_payload,
    payload_sha256,
    render_json,
)
from job_search_agent.judge.prompt import PromptContract
from job_search_agent.judge.rawlog import (
    AttemptValidation,
    RawAttemptLog,
    RawReplyLog,
)
from job_search_agent.judge.validator import (
    Rejection,
    ValidationResult,
    ValidJudgment,
    validate_reply,
)
from job_search_agent.models import (
    PRE_SPAWN_ERRORS,
    AttemptSummary,
    BackendErrorKind,
    BackendReply,
    JudgmentDiagnostic,
    JudgmentOutcome,
    JudgmentStatus,
    ModelJudgment,
    Posting,
    VerifiedResume,
)
from job_search_agent.ports import Clock, CommandRunner, EventSink, ModelBackend
from job_search_agent.privacy import SensitiveValue, sensitive_values
from job_search_agent.resume import PERSONA_LABEL


@dataclass(frozen=True, slots=True)
class JudgeAttempt:
    """One model call made while judging a posting.

    Attributes:
        attempt: 1 or 2.
        reply: The backend's reply (failures included).
        validation: The validator result, or ``None`` when the call failed.
        raw_log_ref: Repo-relative path of this attempt's raw-reply log.
    """

    attempt: int
    reply: BackendReply
    validation: ValidationResult | None
    raw_log_ref: str


@dataclass(frozen=True, slots=True)
class JudgeRun:
    """Everything about one posting's judgment, for experiments and tests.

    Attributes:
        outcome: What the pipeline stores.
        attempts: The calls made, in order (empty when UNAVAILABLE).
        resume_payload: The résumé object sent (``None`` when UNAVAILABLE).
        posting_payload: The posting object sent (``None`` when UNAVAILABLE).
    """

    outcome: JudgmentOutcome
    attempts: tuple[JudgeAttempt, ...]
    resume_payload: Mapping[str, Any] | None
    posting_payload: Mapping[str, Any] | None


def _validation_log(result: ValidationResult | None) -> AttemptValidation:
    if result is None:
        return AttemptValidation(passed=None)
    if isinstance(result, ValidJudgment):
        return AttemptValidation(passed=True)
    return AttemptValidation(passed=False, codes=[c.value for c in result.codes])


def _summary(attempt: JudgeAttempt) -> AttemptSummary:
    result = attempt.validation
    return AttemptSummary(
        attempt=attempt.attempt,
        raw_log_ref=attempt.raw_log_ref,
        first_reply=attempt.attempt == 1,
        validation_passed=None if result is None else isinstance(result, ValidJudgment),
        validation_codes=(
            [c.value for c in result.codes] if isinstance(result, Rejection) else []
        ),
        session_id=attempt.reply.session_id,
        backend_error=attempt.reply.error,
    )


def echo_allow_list(resume_payload: Mapping[str, Any]) -> tuple[str, ...]:
    """Returns the strings a reply may always contain (review fix 5).

    Args:
        resume_payload: The résumé object as sent.

    Returns:
        The persona label and every skill and target phrase that was sent; CONTRACT
        §12 allows matched skill terms and the persona label in outputs.
    """
    allowed = [PERSONA_LABEL]
    for section in ("skills", "target"):
        arrays = resume_payload.get(section)
        if isinstance(arrays, Mapping):
            for items in arrays.values():
                if isinstance(items, list):
                    allowed += [item for item in items if isinstance(item, str)]
    return tuple(allowed)


def judge_posting_detailed(
    backend: ModelBackend,
    prompt: PromptContract,
    posting: Posting,
    resume: VerifiedResume,
    rawlog: RawReplyLog,
    *,
    log_dir: str,
    model_requested: str | None,
    retry_once: bool = True,
    seeded: bool | None = None,
) -> JudgeRun:
    """Judges one posting and returns the outcome plus every attempt.

    Args:
        backend: The model backend.
        prompt: The loaded prompt contract.
        posting: The posting to judge.
        resume: The verified résumé; nothing else is accepted.
        rawlog: Where raw replies are written.
        log_dir: Data-root-relative directory for this posting's attempt files.
        model_requested: The model ID asked for (recorded per call).
        retry_once: Retry once after a validation failure (pipeline); experiments
            pass ``False``.
        seeded: Copied into each raw log file when not ``None``.

    Returns:
        The run.

    Raises:
        TypeError: If ``resume`` is not a ``VerifiedResume``.
    """
    if not isinstance(resume, VerifiedResume):
        raise TypeError("the judge accepts only a VerifiedResume (CONTRACT §12)")
    availability = backend.availability()
    if not availability.available:
        return _unavailable_run(
            prompt, posting, model_requested, availability.reason or "unavailable"
        )
    resume_payload = build_resume_payload(resume)
    posting_payload = build_posting_payload(posting)
    call = _Call(
        text=prompt.render(render_json(resume_payload), render_json(posting_payload)),
        resume_payload=resume_payload,
        posting_payload=posting_payload,
        echo_values=sensitive_values(resume),
        echo_allow=echo_allow_list(resume_payload),
    )
    log = _LogContext(
        posting_id=posting.posting_id,
        prompt=prompt,
        payload_sha256=payload_sha256(resume_payload, posting_payload),
        model_requested=model_requested,
        claude_version=availability.version,
        seeded=seeded,
    )
    attempts = _attempt_calls(
        backend, call, log, rawlog, log_dir=log_dir, max_attempts=2 if retry_once else 1
    )
    diagnostic = JudgmentDiagnostic(
        prompt_id=prompt.prompt_id,
        prompt_sha256=prompt.sha256,
        model_requested=model_requested,
        attempts=[_summary(a) for a in attempts],
    )
    return JudgeRun(
        JudgmentOutcome(posting.posting_id, _final_judgment(attempts, diagnostic)),
        tuple(attempts),
        resume_payload,
        posting_payload,
    )


@dataclass(frozen=True, slots=True)
class _Call:
    """What every attempt sends and validates against (identical across retries)."""

    text: str
    resume_payload: Mapping[str, Any]
    posting_payload: Mapping[str, Any]
    echo_values: tuple[SensitiveValue, ...]
    echo_allow: tuple[str, ...]

    def validate(self, reply: BackendReply) -> ValidationResult | None:
        """Validates a successful reply; ``None`` when the call itself failed."""
        if not reply.ok or reply.result_text is None:
            return None
        return validate_reply(
            reply.result_text,
            self.resume_payload,
            self.posting_payload,
            echo_values=self.echo_values,
            echo_allow=self.echo_allow,
        )


@dataclass(frozen=True, slots=True)
class _LogContext:
    """The per-posting facts copied into every raw-reply log file."""

    posting_id: str
    prompt: PromptContract
    payload_sha256: str
    model_requested: str | None
    claude_version: str | None
    seeded: bool | None


def _attempt_log(
    ctx: _LogContext, number: int, reply: BackendReply, result: ValidationResult | None
) -> RawAttemptLog:
    """Builds the raw-reply log entry for one attempt."""
    return RawAttemptLog(
        posting_id=ctx.posting_id,
        attempt=number,
        first_reply=number == 1,
        prompt_id=ctx.prompt.prompt_id,
        prompt_sha256=ctx.prompt.sha256,
        payload_sha256=ctx.payload_sha256,
        model_requested=ctx.model_requested,
        model_served=list(reply.model_served),
        claude_version=ctx.claude_version,
        argv=list(reply.argv),
        started_at_utc=reply.started_at_utc,
        started_at_et=to_eastern(reply.started_at_utc),
        duration_ms=reply.duration_ms,
        exit_code=reply.exit_code,
        stdout_raw=reply.raw_stdout,
        stderr=reply.stderr,
        session_id=reply.session_id,
        is_error=reply.is_error,
        total_cost_usd=reply.total_cost_usd,
        backend_error=reply.error,
        validation=_validation_log(result),
        seeded=ctx.seeded,
    )


def _attempt_calls(
    backend: ModelBackend,
    call: _Call,
    log: _LogContext,
    rawlog: RawReplyLog,
    *,
    log_dir: str,
    max_attempts: int,
) -> list[JudgeAttempt]:
    """Calls the backend, logging each attempt; retries only a rejected reply."""
    attempts: list[JudgeAttempt] = []
    for number in range(1, max_attempts + 1):
        reply = backend.complete(call.text)
        result = call.validate(reply)
        ref = rawlog.write(log_dir, _attempt_log(log, number, reply, result))
        attempts.append(JudgeAttempt(number, reply, result, ref))
        if not isinstance(result, Rejection):
            break  # VALID, or a failed call (ERROR is never retried)
    return attempts


def _unavailable_run(
    prompt: PromptContract,
    posting: Posting,
    model_requested: str | None,
    reason: str,
) -> JudgeRun:
    """The run for a backend that reports itself unavailable (no call made)."""
    judgment = ModelJudgment(
        status=JudgmentStatus.UNAVAILABLE,
        diagnostic=JudgmentDiagnostic(
            prompt_id=prompt.prompt_id,
            prompt_sha256=prompt.sha256,
            model_requested=model_requested,
            unavailable_reason=reason,
        ),
    )
    return JudgeRun(JudgmentOutcome(posting.posting_id, judgment), (), None, None)


def _final_judgment(
    attempts: list[JudgeAttempt], diagnostic: JudgmentDiagnostic
) -> ModelJudgment:
    """Maps the last attempt to the stored judgment (VALID, INVALID_OUTPUT, ...)."""
    last = attempts[-1]
    final = last.validation
    if isinstance(final, ValidJudgment):
        reply = final.reply
        return ModelJudgment(
            status=JudgmentStatus.VALID,
            label=reply.label,
            summary=reply.summary,
            evidence=list(reply.evidence),
            uncertainties=list(reply.uncertainties),
            diagnostic=diagnostic,
        )
    if isinstance(final, Rejection):
        return ModelJudgment(
            status=JudgmentStatus.INVALID_OUTPUT, diagnostic=diagnostic
        )
    error = last.reply.error
    if error is not None and error in PRE_SPAWN_ERRORS:
        return ModelJudgment(
            status=JudgmentStatus.UNAVAILABLE,
            diagnostic=diagnostic.model_copy(
                update={"unavailable_reason": error.value.lower()}
            ),
        )
    return ModelJudgment(status=JudgmentStatus.ERROR, diagnostic=diagnostic)


class CliJudge:
    """``ports.Judge`` adapter used by the pipeline.

    Args:
        backend: The model backend (``ClaudeCliBackend`` or ``UnavailableBackend``).
        prompt: The prompt contract (``[model].prompt_version``).
        rawlog: Raw-reply log writer.
        model_requested: The pinned model ID, recorded per call.
        seeded: Written into every raw log file when not ``None`` (``True`` for
            replay runs, so the seeded label reaches every file).
    """

    def __init__(
        self,
        backend: ModelBackend,
        prompt: PromptContract,
        rawlog: RawReplyLog,
        *,
        model_requested: str | None,
        seeded: bool | None = None,
    ) -> None:
        self._backend = backend
        self._seeded = seeded
        self._prompt = prompt
        self._rawlog = rawlog
        self._model_requested = model_requested

    def judge(
        self, posting: Posting, resume: VerifiedResume, *, log_dir: str
    ) -> JudgmentOutcome:
        """Judges one posting, retrying once after a validation failure only.

        Args:
            posting: The posting.
            resume: The verified résumé.
            log_dir: Data-root-relative directory for raw-reply logs.

        Returns:
            The outcome.
        """
        return judge_posting_detailed(
            self._backend,
            self._prompt,
            posting,
            resume,
            self._rawlog,
            log_dir=log_dir,
            model_requested=self._model_requested,
            retry_once=True,
            seeded=self._seeded,
        ).outcome


def build_backend(
    settings: ModelSettings,
    *,
    runner: CommandRunner,
    make_empty_dir: MakeEmptyDir,
    clock: Clock,
    events: EventSink | None = None,
) -> ClaudeCliBackend | UnavailableBackend:
    """Builds the configured backend.

    Args:
        settings: ``[model]`` from ``config/agent.toml`` (after CLI overrides).
        runner: The command runner (``sysio.SubprocessRunner`` in production).
        make_empty_dir: ``OutputRoot.make_empty_dir``.
        clock: The clock.
        events: Receives backend events (``judge.workdir_cleanup_failed``).

    Returns:
        ``UnavailableBackend("backend_none")`` for ``backend = "none"``, else a
        ``ClaudeCliBackend``.
    """
    if settings.backend == "none":
        return UnavailableBackend("backend_none")
    return ClaudeCliBackend(
        executable=settings.executable,
        model_id=settings.model_id,
        timeout_s=settings.timeout_s,
        runner=runner,
        make_empty_dir=make_empty_dir,
        clock=clock,
        events=events,
    )


def build_judge(
    settings: ModelSettings,
    prompt: PromptContract,
    *,
    runner: CommandRunner,
    writer: OutputRoot,
    make_empty_dir: MakeEmptyDir,
    clock: Clock,
    repo_rel: Callable[[str], str],
    seeded: bool | None = None,
    events: EventSink | None = None,
) -> CliJudge:
    """Wires a ``CliJudge`` from configuration (convenience for the pipeline CLI).

    Args:
        settings: ``[model]`` settings.
        prompt: The loaded prompt for ``settings.prompt_version``.
        runner: The command runner.
        writer: ``OutputRoot`` (atomic JSON writes under the data dir).
        make_empty_dir: ``OutputRoot.make_empty_dir``.
        clock: The clock.
        repo_rel: ``AgentConfig.repo_rel``.
        seeded: Passed to ``CliJudge`` (``True`` for replay runs).
        events: The run's event log, for backend events.

    Returns:
        The judge.
    """
    backend = build_backend(
        settings,
        runner=runner,
        make_empty_dir=make_empty_dir,
        clock=clock,
        events=events,
    )
    return CliJudge(
        backend,
        prompt,
        RawReplyLog(writer, repo_rel=repo_rel),
        model_requested=settings.model_id if settings.backend != "none" else None,
        seeded=seeded,
    )


# --- doctor --probe-model -----------------------------------------------------

PROBE_PROMPT = "Reply with exactly the two letters OK and nothing else."
"""A tiny prompt with no résumé or posting content."""


class ProbeReport(BaseModel):
    """Facts from one ``jsa doctor --probe-model`` call (``data/doctor/<ts>.json``)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: Literal["probe-model"] = "probe-model"
    checked_at_utc: AwareDatetime
    checked_at_et: AwareDatetime
    available: bool
    unavailable_reason: str | None
    claude_version: str | None
    argv: list[str]
    prompt: str
    env_added: dict[str, str]
    env_removed: list[str]
    cwd_kind: Literal["fresh-empty"] = "fresh-empty"
    model_requested: str | None
    model_served: list[str]
    session_id: str | None
    exit_code: int | None
    duration_ms: int | None
    is_error: bool | None
    backend_error: BackendErrorKind | None
    result_text: str | None
    reply_is_ok: bool | None
    """Whether the reply was exactly ``OK`` after trimming whitespace."""
    total_cost_usd: float | None
    stdout_raw: str | None
    stderr: str | None


@dataclass(frozen=True, slots=True)
class ProbeResult:
    """A probe report and where it was written (if a writer was given)."""

    report: ProbeReport
    data_rel: str | None


def probe_model(
    backend: ModelBackend,
    *,
    model_requested: str | None,
    clock: Clock,
    writer: OutputRoot | None = None,
) -> ProbeResult:
    """Makes one tiny real call and records the facts (``jsa doctor --probe-model``).

    Args:
        backend: The backend to probe (normally a ``ClaudeCliBackend``).
        model_requested: The pinned model ID.
        clock: The clock.
        writer: If given, the report is written to ``doctor/<run-id>.json``.

    Returns:
        The report and its data-root-relative path.
    """
    checked: datetime = clock.now_utc()
    availability = backend.availability()
    argv: list[str] = list(getattr(backend, "display_argv", ()))
    common: dict[str, Any] = {
        "checked_at_utc": checked,
        "checked_at_et": to_eastern(checked),
        "claude_version": availability.version,
        "prompt": PROBE_PROMPT,
        "env_added": dict(ADDED_ENV),
        "env_removed": list(STRIPPED_ENV),
        "model_requested": model_requested,
    }
    if not availability.available:
        report = ProbeReport(
            available=False,
            unavailable_reason=availability.reason,
            argv=argv,
            model_served=[],
            session_id=None,
            exit_code=None,
            duration_ms=None,
            is_error=None,
            backend_error=None,
            result_text=None,
            reply_is_ok=None,
            total_cost_usd=None,
            stdout_raw=None,
            stderr=None,
            **common,
        )
    else:
        reply = backend.complete(PROBE_PROMPT)
        report = ProbeReport(
            available=True,
            unavailable_reason=None,
            argv=list(reply.argv),
            model_served=list(reply.model_served),
            session_id=reply.session_id,
            exit_code=reply.exit_code,
            duration_ms=reply.duration_ms,
            is_error=reply.is_error,
            backend_error=reply.error,
            result_text=reply.result_text,
            reply_is_ok=(
                reply.result_text.strip() == "OK"
                if reply.result_text is not None
                else None
            ),
            total_cost_usd=reply.total_cost_usd,
            stdout_raw=reply.raw_stdout,
            stderr=reply.stderr,
            **common,
        )
    data_rel: str | None = None
    if writer is not None:
        data_rel = f"doctor/{format_run_id(checked)}.json"
        writer.write_json_atomic(data_rel, report.model_dump(mode="json"))
    return ProbeResult(report, data_rel)


__all__ = [
    "PROBE_PROMPT",
    "CliJudge",
    "JudgeAttempt",
    "JudgeRun",
    "ProbeReport",
    "ProbeResult",
    "build_backend",
    "build_judge",
    "judge_posting_detailed",
    "probe_model",
]
