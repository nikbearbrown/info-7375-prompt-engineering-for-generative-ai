"""Hermetic test doubles for the ``job_search_agent.ports`` Protocols.

Every fake records how it was called so tests can assert on it (for example that the
backend was called zero times on a baseline, or that an allow-list rejection never
reached the inner transport).
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx

from job_search_agent.models import (
    Availability,
    BackendErrorKind,
    BackendReply,
    CompletedCommand,
)

__all__ = [
    "FAKE_MODEL_LABEL",
    "FakeBackend",
    "FakeGit",
    "FakeRunner",
    "FixedClock",
    "RecordingTransport",
    "Reply",
    "RunCall",
    "mock_transport",
]

FAKE_MODEL_LABEL = "claude-sonnet-5-5"
_FAKE_STARTED = datetime(2026, 10, 30, 2, 11, 7, tzinfo=UTC)


# --- clock ----------------------------------------------------------------


def _aware_utc(instant: datetime) -> datetime:
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware")
    return instant.astimezone(UTC)


class FixedClock:
    """A deterministic clock for tests and reproducible runs.

    Each call to ``now_utc`` returns the current instant and then advances it by
    ``step``, so a run's start and finish times differ predictably.

    Args:
        start: First instant returned; must be timezone-aware.
        step: Amount to advance after each call (default: never advance).

    Raises:
        ValueError: If ``start`` is naive or ``step`` is negative.
    """

    def __init__(self, start: datetime, *, step: timedelta = timedelta(0)) -> None:
        if step < timedelta(0):
            raise ValueError("step must not be negative")
        self._next = _aware_utc(start)
        self._step = step

    def now_utc(self) -> datetime:
        """Returns the current fixed instant (UTC), then advances by ``step``."""
        current = self._next
        self._next = current + self._step
        return current


# --- model backend ----------------------------------------------------------


class FakeBackend:
    """Scripted ``ModelBackend``.

    Each script item is consumed by one ``complete`` call: a ``str`` is returned as
    Claude's reply text inside a well-formed CLI envelope; a ``BackendErrorKind``
    produces a failed call of that kind; a ``BackendReply`` is returned as is.
    Calling ``complete`` past the end of the script, or while unavailable, fails the
    test.
    """

    def __init__(
        self,
        script: Iterable[str | BackendErrorKind | BackendReply] = (),
        *,
        available: bool = True,
        unavailable_reason: str = "backend_none",
    ) -> None:
        self._script = list(script)
        self._available = available
        self._unavailable_reason = unavailable_reason
        self.prompts: list[str] = []

    @property
    def calls(self) -> int:
        """Number of ``complete`` calls made so far."""
        return len(self.prompts)

    def availability(self) -> Availability:
        if self._available:
            return Availability(available=True, version="fake 0.0.0")
        return Availability(available=False, reason=self._unavailable_reason)

    def complete(self, prompt: str) -> BackendReply:
        if not self._available:
            raise AssertionError("complete() called on an unavailable backend")
        if not self._script:
            raise AssertionError("FakeBackend script exhausted")
        self.prompts.append(prompt)
        item = self._script.pop(0)
        if isinstance(item, BackendReply):
            return item
        session_id = f"fake-session-{len(self.prompts)}"
        if isinstance(item, BackendErrorKind):
            return _error_reply(item, session_id)
        return _ok_reply(item, session_id)


def _ok_reply(text: str, session_id: str) -> BackendReply:
    envelope = {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "result": text,
        "session_id": session_id,
        "total_cost_usd": 0.0,
        "modelUsage": {FAKE_MODEL_LABEL: {}},
    }
    return BackendReply(
        argv=("claude", "-p"),
        started_at_utc=_FAKE_STARTED,
        duration_ms=1,
        exit_code=0,
        raw_stdout=json.dumps(envelope),
        stderr="",
        result_text=text,
        is_error=False,
        session_id=session_id,
        model_served=(FAKE_MODEL_LABEL,),
        total_cost_usd=0.0,
        error=None,
    )


def _error_reply(kind: BackendErrorKind, session_id: str) -> BackendReply:
    is_error = kind is BackendErrorKind.IS_ERROR
    return BackendReply(
        argv=("claude", "-p"),
        started_at_utc=_FAKE_STARTED,
        duration_ms=1,
        exit_code=None if kind is BackendErrorKind.TIMEOUT else 1,
        raw_stdout=json.dumps({"is_error": True}) if is_error else "",
        stderr="fake failure",
        result_text=None,
        is_error=is_error,
        session_id=session_id if is_error else None,
        model_served=(),
        total_cost_usd=None,
        error=kind,
    )


# --- command runner ---------------------------------------------------------


@dataclass(frozen=True)
class RunCall:
    """One recorded ``FakeRunner.run`` call."""

    argv: tuple[str, ...]
    cwd: Path
    env: Mapping[str, str]
    stdin: str
    timeout_s: float


class FakeRunner:
    """Scripted ``CommandRunner``; records every call and never starts a process.

    Script items are ``CompletedCommand`` results (their ``argv`` is replaced by the
    real call's argv) or an ``OSError`` instance to raise, as when the program cannot
    be started.
    """

    def __init__(self, script: Iterable[CompletedCommand | OSError] = ()) -> None:
        self._script = list(script)
        self.calls: list[RunCall] = []

    def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str],
        stdin: str,
        timeout_s: float,
    ) -> CompletedCommand:
        call = RunCall(tuple(argv), cwd, dict(env), stdin, timeout_s)
        self.calls.append(call)
        if not self._script:
            raise AssertionError("FakeRunner script exhausted")
        item = self._script.pop(0)
        if isinstance(item, OSError):
            raise item
        return CompletedCommand(
            argv=call.argv,
            returncode=item.returncode,
            stdout=item.stdout,
            stderr=item.stderr,
            timed_out=item.timed_out,
            duration_ms=item.duration_ms,
        )


# --- git --------------------------------------------------------------------


@dataclass
class FakeGit:
    """Configurable ``GitInspector``.

    Attributes:
        head_commit: Value returned by ``head``.
        dirty: Value returned by ``is_dirty``.
        clean_tracked: Repo-relative paths (POSIX) reported as tracked and clean.
    """

    head_commit: str = "0" * 40
    dirty: bool = False
    clean_tracked: set[str] = field(default_factory=set)

    def head(self) -> str:
        return self.head_commit

    def is_dirty(self) -> bool:
        return self.dirty

    def is_tracked_and_clean(self, path: Path) -> bool:
        return path.as_posix() in self.clean_tracked


# --- http -------------------------------------------------------------------


@dataclass(frozen=True)
class Reply:
    """A canned HTTP response; a fresh ``httpx.Response`` is built for every request."""

    status: int = 200
    body: bytes = b""
    headers: Mapping[str, str] = field(default_factory=dict)


Route = Reply | Callable[[httpx.Request], httpx.Response]


class RecordingTransport(httpx.MockTransport):
    """``httpx.MockTransport`` that records every request it receives."""

    def __init__(self, handler: Callable[[httpx.Request], httpx.Response]) -> None:
        self.requests: list[httpx.Request] = []

        def recording(request: httpx.Request) -> httpx.Response:
            self.requests.append(request)
            return handler(request)

        super().__init__(recording)


def mock_transport(
    routes: Mapping[str, Route] | Callable[[httpx.Request], httpx.Response],
) -> RecordingTransport:
    """Builds a recording mock transport.

    Args:
        routes: Either a handler function, or a mapping from exact URL string (as
            ``str(request.url)``) to a ``Reply`` or a handler. A request to an
            unlisted URL fails the test.

    Returns:
        The transport; inspect ``.requests`` afterwards.
    """
    if callable(routes):
        return RecordingTransport(routes)
    table = dict(routes)

    def handler(request: httpx.Request) -> httpx.Response:
        route = table.get(str(request.url))
        if route is None:
            raise AssertionError(f"unexpected request to {request.url.host!r}")
        if isinstance(route, Reply):
            return httpx.Response(
                route.status, headers=dict(route.headers), content=route.body
            )
        return route(request)

    return RecordingTransport(handler)
