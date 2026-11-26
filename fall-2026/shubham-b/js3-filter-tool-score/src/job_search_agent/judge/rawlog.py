"""Raw-reply log: one JSON file per model call attempt (PLAN §5.5, CONTRACT §8).

The raw CLI envelope is kept here, verbatim, and nowhere else. Records refer to these
files by repo-relative path (``AttemptSummary.raw_log_ref``); the raw text can never
reach a record's structured fields.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from job_search_agent.fsio import OutputRoot
from job_search_agent.models import BackendErrorKind


class AttemptValidation(BaseModel):
    """Validator outcome for one attempt (``None`` when there was no reply)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    passed: bool | None
    codes: list[str] = Field(default_factory=list)


class RawAttemptLog(BaseModel):
    """Contents of ``attempt-<n>.json`` (PLAN §5.5 fields plus identification)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    posting_id: str
    attempt: int = Field(ge=1, le=2)
    first_reply: bool
    prompt_id: str
    prompt_sha256: str
    payload_sha256: str
    model_requested: str | None
    model_served: list[str]
    claude_version: str | None
    argv: list[str]
    """The command line without the prompt (the prompt went on stdin)."""
    cwd_kind: Literal["fresh-empty"] = "fresh-empty"
    started_at_utc: AwareDatetime
    started_at_et: AwareDatetime
    duration_ms: int
    exit_code: int | None
    stdout_raw: str
    """The verbatim CLI envelope."""
    stderr: str
    """Sanitised stderr, or ``"[withheld: credential pattern]"``."""
    session_id: str | None
    is_error: bool
    total_cost_usd: float | None
    backend_error: BackendErrorKind | None
    validation: AttemptValidation
    seeded: bool | None = None
    """Set by callers that need the seeded label in every file (replay runs)."""


def default_repo_rel(data_rel: str) -> str:
    """Maps a data-root-relative path to a repo-relative one for ``data/``.

    Args:
        data_rel: E.g. ``"live/runs/x/model/1/attempt-1.json"``.

    Returns:
        E.g. ``"data/live/runs/x/model/1/attempt-1.json"``.
    """
    return f"data/{data_rel}"


class RawReplyLog:
    """Writes one file per attempt under a caller-chosen directory.

    Args:
        writer: Atomic JSON writer rooted at the data directory.
        repo_rel: Converts a data-root-relative path to a repo-relative one
            (``AgentConfig.repo_rel``).
    """

    def __init__(
        self,
        writer: OutputRoot,
        *,
        repo_rel: Callable[[str], str] = default_repo_rel,
    ) -> None:
        self._writer = writer
        self._repo_rel = repo_rel

    @staticmethod
    def attempt_rel(log_dir: str, attempt: int) -> str:
        """Returns the data-root-relative path of one attempt file."""
        return f"{log_dir.rstrip('/')}/attempt-{attempt}.json"

    def write(self, log_dir: str, entry: RawAttemptLog) -> str:
        """Writes one attempt.

        Args:
            log_dir: Data-root-relative directory, e.g.
                ``"live/runs/<run_id>/model/<posting_id>"``.
            entry: The attempt's facts.

        Returns:
            The repo-relative path of the written file.
        """
        rel = self.attempt_rel(log_dir, entry.attempt)
        self._writer.write_json_atomic(rel, entry.model_dump(mode="json"))
        return self._repo_rel(rel)
