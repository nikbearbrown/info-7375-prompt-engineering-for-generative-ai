"""Model backends: the ``claude`` CLI subprocess, and nothing (PLAN §5.1, R1).

The only real backend runs the subscription-authenticated ``claude`` executable once
per call with exactly the argv and environment of PLAN amendment R1::

    env: CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 CLAUDE_CODE_DISABLE_CLAUDE_MDS=1
         ENABLE_CLAUDEAI_MCP_SERVERS=false
         (ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, ANTHROPIC_BASE_URL,
          CLAUDE_CODE_USE_BEDROCK, CLAUDE_CODE_USE_VERTEX removed)

Since PLAN amendment R9 the environment is built from an allowlist (``ALLOWED_ENV``
plus ``LC_*``) rather than by removing the R1 names, so the removal above holds for
any variable nobody has thought of yet.
    claude -p --no-session-persistence --tools "" --disallowedTools "mcp__*"
           --strict-mcp-config --setting-sources project --safe-mode
           --output-format json --model <model_id>

The prompt goes on stdin, never in argv. Each call runs in a fresh, empty working
directory (``data/tmp/claude-<uuid>/`` via the injected maker, which is
``OutputRoot.make_empty_dir`` in production) that is removed afterwards. Removal is
best effort: a failure emits ``judge.workdir_cleanup_failed`` and never replaces the
reply. A failure before any process starts (the executable gone from ``PATH`` at
call time, or the working directory not creatable) is ``CLI_NOT_FOUND`` or
``WORKDIR_FAILED``, which the judge records as ``UNAVAILABLE`` (CONTRACT §8).

``--bare`` is never used: it skips OAuth and needs an API key, which §11 forbids.
Removing the API key variables means the CLI cannot quietly fall back to API-key
billing.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Any

from job_search_agent.errors import PathRejected
from job_search_agent.models import (
    Availability,
    BackendErrorKind,
    BackendReply,
    CompletedCommand,
)
from job_search_agent.ports import Clock, CommandRunner, EventSink

ADDED_ENV: Mapping[str, str] = {
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1",
    "ENABLE_CLAUDEAI_MCP_SERVERS": "false",
}
"""Variables set in the child environment (R1)."""

ALLOWED_ENV: frozenset[str] = frozenset(
    {
        "PATH",
        "HOME",
        "USER",
        "LOGNAME",
        "SHELL",
        "LANG",
        "TERM",
        "TMPDIR",
        "__CF_USER_TEXT_ENCODING",  # macOS text encoding for the child
    }
)
"""Parent variables copied into the child environment (PLAN R9); nothing else is."""

ALLOWED_ENV_PREFIXES: tuple[str, ...] = ("LC_",)
"""Parent variable-name prefixes also copied (locale settings, PLAN R9)."""

STRIPPED_ENV: tuple[str, ...] = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_BASE_URL",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
)
"""The R1 credential and provider switches, kept as documentation and for the probe
report (``env_removed``). Since R9 the child environment is an allowlist, so these
(and every other variable not in ``ALLOWED_ENV``) are never passed through."""

WITHHELD_STDERR = "[withheld: credential pattern]"

_CREDENTIAL = re.compile(
    r"sk-ant-|sk-[A-Za-z0-9_-]{16,}|bearer\s+\S|api[_-]?key|auth[_-]?token|"
    r"access[_-]?token|refresh[_-]?token|oauth|password|secret",
    re.IGNORECASE,
)

TMP_DIR_PREFIX = "tmp/claude-"
"""Data-root-relative prefix of the per-call working directories."""

VERSION_TIMEOUT_S = 30.0

MakeEmptyDir = Callable[[str], Path]
"""``make_empty_dir(rel) -> absolute path`` (``fsio.OutputRoot.make_empty_dir``)."""

RemoveDir = Callable[[Path], None]


def judge_argv(executable: str, model_id: str) -> tuple[str, ...]:
    """Returns the exact R1 argv for one judge call (the prompt is not included).

    Args:
        executable: Program to run (``"claude"`` or a resolved path).
        model_id: The pinned model ID, e.g. ``"claude-sonnet-5-5"``.

    Returns:
        The argv tuple.
    """
    return (
        executable,
        "-p",
        "--no-session-persistence",
        "--tools",
        "",
        "--disallowedTools",
        "mcp__*",
        "--strict-mcp-config",
        "--setting-sources",
        "project",
        "--safe-mode",
        "--output-format",
        "json",
        "--model",
        model_id,
    )


def child_env(base: Mapping[str, str]) -> dict[str, str]:
    """Builds the child environment from an allowlist, plus ``ADDED_ENV`` (PLAN R9).

    Only ``ALLOWED_ENV`` names and ``LC_*`` locale variables are copied from
    ``base``; everything else (an unknown ``ANTHROPIC_*`` or ``CLAUDE_CODE_USE_*``
    switch, cloud credentials, proxy settings) is dropped, so a new variable fails
    closed. The three R1 variables are then set, overriding any parent value.

    Args:
        base: The parent environment (normally ``os.environ``).

    Returns:
        A new mapping; ``base`` is not modified.
    """
    env = {
        k: v
        for k, v in base.items()
        if k in ALLOWED_ENV or k.startswith(ALLOWED_ENV_PREFIXES)
    }
    env.update(ADDED_ENV)
    return env


def sanitize_stderr(stderr: str, *, home: str | None = None) -> str:
    """Makes CLI stderr safe to store in a log.

    Args:
        stderr: Raw stderr text.
        home: The home directory to replace with ``~`` (defaults to the real one).

    Returns:
        ``WITHHELD_STDERR`` if the text looks like it contains a credential, otherwise
        the text with the home directory prefix replaced by ``~``.
    """
    if _CREDENTIAL.search(stderr):
        return WITHHELD_STDERR
    home_dir = home if home is not None else str(Path.home())
    if home_dir and home_dir != "/":
        stderr = stderr.replace(home_dir, "~")
    return stderr


def _served_models(envelope: Mapping[str, Any]) -> tuple[str, ...]:
    usage = envelope.get("modelUsage")
    if isinstance(usage, Mapping):
        return tuple(sorted(str(key) for key in usage))
    return ()


@dataclass(frozen=True, slots=True)
class Envelope:
    """What was read from the CLI's ``--output-format json`` stdout.

    Attributes:
        error: Why the call failed, or ``None`` when ``result_text`` is usable.
        result_text: The envelope's ``result`` string (only when ``error`` is None).
        is_error: The envelope's ``is_error`` flag (False if absent).
        session_id: The envelope's ``session_id``.
        model_served: Keys of ``modelUsage``, sorted.
        total_cost_usd: The envelope's ``total_cost_usd``.
    """

    error: BackendErrorKind | None
    result_text: str | None = None
    is_error: bool = False
    session_id: str | None = None
    model_served: tuple[str, ...] = ()
    total_cost_usd: float | None = None


def parse_envelope(completed: CompletedCommand) -> Envelope:
    """Interprets the CLI's ``--output-format json`` envelope.

    Args:
        completed: The finished process.

    Returns:
        The envelope facts. ``error`` is ``None`` only for exit status 0, a JSON
        object envelope, ``is_error`` exactly false and a string ``result``.
    """
    if completed.timed_out:
        return Envelope(BackendErrorKind.TIMEOUT)
    try:
        envelope: Any = json.loads(completed.stdout)
    except (json.JSONDecodeError, RecursionError):
        envelope = None
    if not isinstance(envelope, dict):
        if completed.returncode != 0:
            return Envelope(BackendErrorKind.NONZERO_EXIT)
        return Envelope(BackendErrorKind.ENVELOPE_NOT_JSON)
    session = envelope.get("session_id")
    cost = envelope.get("total_cost_usd")
    total_cost: float | None = None
    if isinstance(cost, int | float) and not isinstance(cost, bool):
        total_cost = float(cost)
    facts = Envelope(
        error=None,
        is_error=envelope.get("is_error") is True,
        session_id=session if isinstance(session, str) else None,
        model_served=_served_models(envelope),
        total_cost_usd=total_cost,
    )
    result = envelope.get("result")
    if completed.returncode != 0:
        if facts.is_error:
            return replace(facts, error=BackendErrorKind.IS_ERROR)
        return replace(facts, error=BackendErrorKind.NONZERO_EXIT)
    if facts.is_error:
        return replace(facts, error=BackendErrorKind.IS_ERROR)
    if not isinstance(envelope.get("is_error"), bool) or not isinstance(result, str):
        return replace(facts, error=BackendErrorKind.ENVELOPE_SHAPE)
    return replace(facts, result_text=result)


class ClaudeCliBackend:
    """``ModelBackend`` that runs the ``claude`` CLI once per call (R1).

    Args:
        executable: Configured program name (``[model].executable``), e.g.
            ``"claude"``. It is resolved with ``which``; logs show this name, never
            the resolved absolute path.
        model_id: Pinned model ID (``[model].model_id``).
        timeout_s: Per-call timeout (``[model].timeout_s``, 180 s).
        runner: Runs the child process.
        make_empty_dir: Creates a fresh empty directory from a data-root-relative
            path and returns its absolute path.
        clock: Supplies ``started_at_utc``.
        which: Executable lookup (``shutil.which``).
        base_env: Parent environment (defaults to ``os.environ`` at call time).
        remove_dir: Removes the per-call directory afterwards (``shutil.rmtree``).
        new_id: Supplies the unique part of each directory name.
        home: Home directory for stderr sanitising (defaults to the real one).
        events: Receives ``judge.workdir_cleanup_failed`` (the run's event log).
    """

    def __init__(
        self,
        *,
        executable: str,
        model_id: str,
        timeout_s: float,
        runner: CommandRunner,
        make_empty_dir: MakeEmptyDir,
        clock: Clock,
        which: Callable[[str], str | None] = shutil.which,
        base_env: Mapping[str, str] | None = None,
        remove_dir: RemoveDir = shutil.rmtree,
        new_id: Callable[[], str] = lambda: uuid.uuid4().hex,
        home: str | None = None,
        events: EventSink | None = None,
    ) -> None:
        self.executable = executable
        self.model_id = model_id
        self._timeout_s = timeout_s
        self._runner = runner
        self._make_empty_dir = make_empty_dir
        self._clock = clock
        self._which = which
        self._base_env = base_env
        self._remove_dir = remove_dir
        self._new_id = new_id
        self._home = home
        self._events = events
        self._availability: Availability | None = None

    @property
    def display_argv(self) -> tuple[str, ...]:
        """The argv as recorded in logs (configured program name, no prompt)."""
        return judge_argv(self.executable, self.model_id)

    def env(self) -> dict[str, str]:
        """Returns the child environment for the next call."""
        return child_env(os.environ if self._base_env is None else self._base_env)

    def _make_workdir(self) -> Path | None:
        """Makes the per-call empty directory; ``None`` if it cannot be made."""
        try:
            return self._make_empty_dir(f"{TMP_DIR_PREFIX}{self._new_id()}")
        except (OSError, PathRejected):
            return None

    def _cleanup(self, workdir: Path) -> None:
        """Removes the per-call directory; a failure is an event, never an error."""
        try:
            self._remove_dir(workdir)
        except OSError as exc:
            if self._events is not None:
                self._events.emit(
                    "judge.workdir_cleanup_failed", {"error": type(exc).__name__}
                )

    def _run_in(
        self, workdir: Path, argv: Sequence[str], stdin: str, timeout_s: float
    ) -> CompletedCommand:
        try:
            return self._runner.run(
                argv, cwd=workdir, env=self.env(), stdin=stdin, timeout_s=timeout_s
            )
        finally:
            self._cleanup(workdir)

    def availability(self) -> Availability:
        """Checks that the executable is on ``PATH``; makes no model call.

        When it is found, ``claude --version`` is run once (cached) so the version can
        be recorded; a failing version check leaves ``version`` as ``None``.

        Returns:
            ``available=False, reason="cli_not_found"`` when ``which`` finds nothing.
        """
        if self._availability is not None:
            return self._availability
        resolved = self._which(self.executable)
        if resolved is None:
            self._availability = Availability(available=False, reason="cli_not_found")
            return self._availability
        version: str | None = None
        completed: CompletedCommand | None = None
        workdir = self._make_workdir()
        if workdir is not None:
            try:
                completed = self._run_in(
                    workdir, (resolved, "--version"), "", VERSION_TIMEOUT_S
                )
            except OSError:
                completed = None
        if completed is not None and completed.returncode == 0:
            text = completed.stdout.strip()
            version = text.splitlines()[0] if text else None
        self._availability = Availability(available=True, version=version)
        return self._availability

    def complete(self, prompt: str) -> BackendReply:
        """Makes one fresh call with ``prompt`` on stdin.

        Args:
            prompt: The rendered prompt.

        Returns:
            The reply. ``CLI_NOT_FOUND`` and ``WORKDIR_FAILED`` (nothing started),
            spawn failure, timeout, non-zero exit, an unparseable envelope and
            ``is_error: true`` are all returned as ``error`` values.
        """
        started = self._clock.now_utc()
        resolved = self._which(self.executable)
        display = self.display_argv
        if resolved is None:
            return _failed(display, started, 0, BackendErrorKind.CLI_NOT_FOUND)
        workdir = self._make_workdir()
        if workdir is None:
            return _failed(display, started, 0, BackendErrorKind.WORKDIR_FAILED)
        argv = judge_argv(resolved, self.model_id)
        began = time.monotonic()
        try:
            completed = self._run_in(workdir, argv, prompt, self._timeout_s)
        except OSError:
            elapsed = int((time.monotonic() - began) * 1000)
            return _failed(display, started, elapsed, BackendErrorKind.SPAWN_FAILED)
        envelope = parse_envelope(completed)
        return BackendReply(
            argv=display,
            started_at_utc=started,
            duration_ms=completed.duration_ms,
            exit_code=None if completed.timed_out else completed.returncode,
            raw_stdout=completed.stdout,
            stderr=sanitize_stderr(completed.stderr, home=self._home),
            result_text=envelope.result_text,
            is_error=envelope.is_error,
            session_id=envelope.session_id,
            model_served=envelope.model_served,
            total_cost_usd=envelope.total_cost_usd,
            error=envelope.error,
        )


def _failed(
    argv: tuple[str, ...], started: datetime, duration_ms: int, kind: BackendErrorKind
) -> BackendReply:
    return BackendReply(
        argv=argv,
        started_at_utc=started,
        duration_ms=duration_ms,
        exit_code=None,
        raw_stdout="",
        stderr="",
        result_text=None,
        is_error=False,
        session_id=None,
        model_served=(),
        total_cost_usd=None,
        error=kind,
    )


class UnavailableBackend:
    """``ModelBackend`` that never calls anything (``--model-backend none``).

    Args:
        reason: Short code reported as the unavailable reason.
    """

    def __init__(self, reason: str = "backend_none") -> None:
        self.reason = reason
        self.model_id: str | None = None

    def availability(self) -> Availability:
        """Always unavailable."""
        return Availability(available=False, reason=self.reason)

    def complete(self, prompt: str) -> BackendReply:
        """Never valid to call.

        Args:
            prompt: Ignored.

        Raises:
            RuntimeError: Always; callers must check ``availability`` first.
        """
        raise RuntimeError("UnavailableBackend.complete must not be called")
