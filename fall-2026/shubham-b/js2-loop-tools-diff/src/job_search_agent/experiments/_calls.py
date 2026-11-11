"""One scored experiment call: first reply only, never retried (PLAN §0.8)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from pydantic import AwareDatetime, BaseModel, ConfigDict

from job_search_agent.clock import to_eastern
from job_search_agent.judge.judge import judge_posting_detailed
from job_search_agent.judge.prompt import PromptContract
from job_search_agent.judge.rawlog import RawReplyLog
from job_search_agent.judge.validator import (
    Rejection,
    ValidJudgment,
    evidence_path_findings,
)
from job_search_agent.models import (
    JudgmentStatus,
    ModelLabel,
    Posting,
    VerifiedResume,
)
from job_search_agent.ports import ModelBackend


class CallRecord(BaseModel):
    """Structured facts of one experiment call (the raw reply stays in its log)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    posting_id: str
    status: JudgmentStatus
    first_reply_valid: bool
    validation_codes: list[str]
    label: ModelLabel | None
    evidence_paths: list[list[str]]
    """``[resume_path, posting_path]`` pairs of a valid reply, in reply order."""
    parseable: bool
    path_entries: int
    path_entries_valid: int
    session_id: str | None
    model_served: list[str]
    raw_log_ref: str | None
    started_at_utc: AwareDatetime | None
    started_at_et: AwareDatetime | None
    prompt_id: str
    prompt_sha256: str


JudgeCall = Callable[[Posting, PromptContract, str], CallRecord]
"""``judge_call(posting, prompt, log_dir) -> CallRecord`` (data-root-relative dir)."""


@dataclass(frozen=True)
class FirstReplyJudge:
    """Builds ``CallRecord``s with ``retry_once=False``.

    Attributes:
        backend: The model backend.
        resume: The verified résumé.
        rawlog: Raw-reply log writer.
        model_requested: The pinned model ID.
    """

    backend: ModelBackend
    resume: VerifiedResume
    rawlog: RawReplyLog
    model_requested: str | None

    def __call__(
        self, posting: Posting, prompt: PromptContract, log_dir: str
    ) -> CallRecord:
        """Makes one call and scores its first (only) reply.

        Args:
            posting: The posting.
            prompt: The prompt contract.
            log_dir: Data-root-relative directory for the attempt file.

        Returns:
            The call record.
        """
        run = judge_posting_detailed(
            self.backend,
            prompt,
            posting,
            self.resume,
            self.rawlog,
            log_dir=log_dir,
            model_requested=self.model_requested,
            retry_once=False,
        )
        if not run.attempts:
            return CallRecord(
                posting_id=posting.posting_id,
                status=run.outcome.status,
                first_reply_valid=False,
                validation_codes=[],
                label=None,
                evidence_paths=[],
                parseable=False,
                path_entries=0,
                path_entries_valid=0,
                session_id=None,
                model_served=[],
                raw_log_ref=None,
                started_at_utc=None,
                started_at_et=None,
                prompt_id=prompt.prompt_id,
                prompt_sha256=prompt.sha256,
            )
        first = run.attempts[0]
        result = first.validation
        text = first.reply.result_text
        findings = None
        if text is not None and run.resume_payload and run.posting_payload:
            findings = evidence_path_findings(
                text, run.resume_payload, run.posting_payload
            )
        valid = isinstance(result, ValidJudgment)
        return CallRecord(
            posting_id=posting.posting_id,
            status=run.outcome.status,
            first_reply_valid=valid,
            validation_codes=(
                [c.value for c in result.codes] if isinstance(result, Rejection) else []
            ),
            label=result.reply.label if isinstance(result, ValidJudgment) else None,
            evidence_paths=(
                [[e.resume_path, e.posting_path] for e in result.reply.evidence]
                if isinstance(result, ValidJudgment)
                else []
            ),
            parseable=findings is not None,
            path_entries=findings.entries if findings else 0,
            path_entries_valid=findings.valid_entries if findings else 0,
            session_id=first.reply.session_id,
            model_served=list(first.reply.model_served),
            raw_log_ref=first.raw_log_ref,
            started_at_utc=first.reply.started_at_utc,
            started_at_et=to_eastern(first.reply.started_at_utc),
            prompt_id=prompt.prompt_id,
            prompt_sha256=prompt.sha256,
        )
