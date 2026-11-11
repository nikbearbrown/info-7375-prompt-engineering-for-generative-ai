"""Injected boundaries (changes are additive only).

The pure core never touches the clock, network, filesystem, subprocesses or git
directly; it receives these Protocols. Real implementations live in ``clock``,
``http``, ``sources``, ``providers``, ``judge.backend`` and the CLI wiring; test fakes
live in ``tests/fakes.py``. Expected failures are returned as values
(``FetchResult.error``, ``BackendReply.error``) so callers handle them explicitly;
exceptions are reserved for policy violations and corrupt inputs (``errors``).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Protocol

from job_search_agent.models import (
    Availability,
    BackendReply,
    CompletedCommand,
    FetchResult,
    JudgmentOutcome,
    ParsedBoard,
    Posting,
    SourceResult,
    VerifiedResume,
)

JsonScalar = str | int | float | bool | None
"""A JSON scalar value."""

type JsonValue = JsonScalar | Sequence[JsonValue] | Mapping[str, JsonValue]
"""Any JSON-serialisable value (recursive)."""


class Clock(Protocol):
    """Source of the current time."""

    def now_utc(self) -> datetime:
        """Returns the current instant as a timezone-aware UTC datetime."""
        ...


class EventSink(Protocol):
    """Receives one structured event per observation (``events.jsonl``, JS2 trace seam).

    Implemented by ``events.EventLog``; used by ``http.build_fetcher`` and
    the pipeline. Events must never carry résumé values, credentials or absolute paths.
    """

    def emit(self, event: str, fields: Mapping[str, JsonValue]) -> None:
        """Records one event.

        Args:
            event: Dotted event name, e.g. ``"http.request"``, ``"http.response"``.
            fields: JSON-serialisable details.
        """
        ...


class HttpFetcher(Protocol):
    """Allow-listed HTTPS GET client (``http.build_fetcher``)."""

    def get(self, url: str) -> FetchResult:
        """Performs one GET, following only allow-listed redirects.

        Args:
            url: Absolute HTTPS URL on an allow-listed host.

        Returns:
            The result; every network, status, redirect, size or allow-list failure is
            reported through ``FetchResult.error`` rather than raised.
        """
        ...


class RawSource(Protocol):
    """Provides the raw board response: live (network) or replay (saved file)."""

    def obtain(self) -> SourceResult:
        """Obtains the raw response once.

        Returns:
            The bytes and their provenance, or an error value.
        """
        ...


class BoardProvider(Protocol):
    """One applicant-tracking system's public board API (JS2 seam: more providers)."""

    @property
    def name(self) -> str:
        """Registry name, e.g. ``"greenhouse"``; written as ``provider`` in state."""
        ...

    def jobs_url(self, board_token: str) -> str:
        """Returns the exact jobs URL for a board.

        Args:
            board_token: Board identifier, e.g. ``"stripe"``.

        Returns:
            The URL, e.g.
            ``"https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"``.
        """
        ...

    def parse(self, body: bytes) -> ParsedBoard:
        """Validates the response shape and normalises postings.

        Args:
            body: Raw response bytes.

        Returns:
            The parsed board; ``is_empty`` when the jobs array is empty.

        Raises:
            InvalidResponse: Not JSON, wrong shape, or zero valid IDs in a non-empty
                jobs array.
        """
        ...


class ModelBackend(Protocol):
    """Something that can answer a prompt: the ``claude`` CLI, or nothing."""

    def availability(self) -> Availability:
        """Reports, without making a model call, whether calls are possible."""
        ...

    def complete(self, prompt: str) -> BackendReply:
        """Makes one fresh, stateless call.

        Only called after ``availability().available`` is true.

        Args:
            prompt: The full rendered prompt (sent on stdin, never in argv).

        Returns:
            The reply; failures are reported through ``BackendReply.error``.
        """
        ...


class CommandRunner(Protocol):
    """Runs a child process (wraps ``subprocess.run``)."""

    def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str],
        stdin: str,
        timeout_s: float,
    ) -> CompletedCommand:
        """Runs ``argv`` to completion or timeout, never through a shell.

        Args:
            argv: Program and arguments.
            cwd: Working directory.
            env: The complete child environment (not merged with ``os.environ``).
            stdin: Text written to the child's stdin.
            timeout_s: Seconds before the child is killed.

        Returns:
            The captured result; a timeout sets ``timed_out``.

        Raises:
            OSError: If the program cannot be started.
        """
        ...


class GitInspector(Protocol):
    """Read-only repository questions (``code_commit``, experiment ordering gates)."""

    def head(self) -> str:
        """Returns the full commit hash of ``HEAD``."""
        ...

    def is_dirty(self) -> bool:
        """Returns True if tracked files differ from ``HEAD`` (``code_dirty``)."""
        ...

    def is_tracked_and_clean(self, path: Path) -> bool:
        """Returns True if ``path`` is tracked and identical to its committed version.

        Args:
            path: Repo-relative path.
        """
        ...


class Judge(Protocol):
    """Produces Claude's judgment for one posting (``judge.judge.CliJudge``).

    Implementations must not raise: every failure (no backend, a failed call, an
    invalid reply, a log or work-directory write that fails) is reported through the
    returned ``JudgmentOutcome``'s status. The pipeline still guards the call, and
    turns an ``AgentError``, ``OSError`` or ``ValueError`` that escapes into an
    ``ERROR`` judgment so the posting stays pending (review fix 1).
    """

    def judge(
        self, posting: Posting, resume: VerifiedResume, *, log_dir: str
    ) -> JudgmentOutcome:
        """Judges one posting, retrying once after a validation failure only.

        Args:
            posting: The posting to judge.
            resume: The verified résumé; nothing else is accepted.
            log_dir: Data-root-relative directory (an ``OutputRoot`` rel) for
                raw-reply logs, e.g. ``"live/runs/<run_id>/model/<posting_id>"``.

        Returns:
            The outcome; ``UNAVAILABLE`` without any call when the backend is
            unavailable.

        Raises:
            Nothing by contract; see the class docstring.
        """
        ...
