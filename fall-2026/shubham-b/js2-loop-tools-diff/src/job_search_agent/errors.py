"""Exception hierarchy (changes are additive only).

Every exception the agent raises on purpose derives from ``AgentError`` and carries
the process exit code the CLI uses when it reaches the top level uncaught. Messages
never contain résumé values, credentials, full URLs or absolute paths: they carry
short codes, and any extra context is kept on attributes for tests to inspect.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import ClassVar

from job_search_agent.models import ExitCode, RefusalCode


class AgentError(Exception):
    """Base class for every deliberate agent failure."""

    exit_code: ClassVar[ExitCode] = ExitCode.CONFIG_ERROR


class ConfigError(AgentError):
    """The configuration file or a CLI override is missing, malformed or unsafe.

    Raised, for example, when the state path resolves outside the data directory
    (CONTRACT §3).
    """

    exit_code: ClassVar[ExitCode] = ExitCode.CONFIG_ERROR


class ResumeRefused(AgentError):  # noqa: N818 - name fixed by PLAN §1.1
    """The résumé gate refused the fixture (CONTRACT §12); nothing is sent anywhere.

    All failing checks are collected, so ``codes`` lists every reason at once.

    Args:
        codes: Every failing check. Must not be empty.

    Attributes:
        codes: The failing checks.

    Raises:
        ValueError: If ``codes`` is empty.
    """

    exit_code: ClassVar[ExitCode] = ExitCode.RESUME_REFUSED

    def __init__(self, codes: Iterable[RefusalCode]) -> None:
        self.codes: frozenset[RefusalCode] = frozenset(codes)
        if not self.codes:
            raise ValueError("ResumeRefused needs at least one refusal code")
        super().__init__("resume refused: " + ", ".join(sorted(self.codes)))


class StateCorrupt(AgentError):  # noqa: N818 - name fixed by PLAN §1.1
    """The state file exists but cannot be trusted; the run stops before fetching.

    The file is left untouched (PLAN §1.3 step 2).

    Args:
        reason: Short code, e.g. ``"not_json"``, ``"schema_version"``,
            ``"integrity"``.

    Attributes:
        reason: The short code.
    """

    exit_code: ClassVar[ExitCode] = ExitCode.STATE_CORRUPT

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"state file corrupt: {reason}")


class HostNotAllowed(AgentError):  # noqa: N818 - name fixed by PLAN §1.1
    """The allow-list transport refused a request before it was sent (CONTRACT §11).

    The message names the host and reason only; the full URL is never included,
    because it could carry userinfo credentials.

    Args:
        host: The refused host (lowercased), or ``""`` if none could be parsed.
        reason: Short code: ``"scheme"``, ``"host"``, ``"port"`` or ``"userinfo"``.

    Attributes:
        host: The refused host.
        reason: The short code.
    """

    exit_code: ClassVar[ExitCode] = ExitCode.FETCH_OR_RESPONSE

    def __init__(self, host: str, reason: str) -> None:
        self.host = host
        self.reason = reason
        super().__init__(f"request refused ({reason}): host {host or '<none>'!r}")


class PathRejected(AgentError):  # noqa: N818 - name fixed by PLAN §1.1
    """A read or write path violates the file policy (``fsio``).

    The message holds the reason only, because the rejected path may be absolute and
    outputs must not leak absolute paths.

    Args:
        reason: Short code, e.g. ``"absolute"``, ``"dotdot"``, ``"symlink"``,
            ``"nul"``, ``"outside_root"``.
        path: The rejected path as given.

    Attributes:
        reason: The short code.
        path: The rejected path (for tests; do not print it).
    """

    exit_code: ClassVar[ExitCode] = ExitCode.CONFIG_ERROR

    def __init__(self, reason: str, path: str) -> None:
        self.reason = reason
        self.path = path
        super().__init__(f"path rejected: {reason}")


class InvalidResponse(AgentError):  # noqa: N818 - name fixed by PLAN §1.1
    """The board response cannot be parsed or has the wrong shape (CONTRACT §9).

    Args:
        code: Short code, e.g. ``"not_json"``, ``"not_object"``, ``"jobs_not_list"``,
            ``"meta_total"``, ``"no_valid_ids"``.
        detail: Optional short factual detail (no posting content).

    Attributes:
        code: The short code.
        detail: The detail string.
    """

    exit_code: ClassVar[ExitCode] = ExitCode.FETCH_OR_RESPONSE

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        suffix = f" ({detail})" if detail else ""
        super().__init__(f"invalid response: {code}{suffix}")


class RunLocked(AgentError):  # noqa: N818 - parallel to the other policy errors
    """Another ``jsa`` process holds the data lock for this mode (live or seeded).

    ``jsa run`` and ``jsa pending drop`` take an exclusive, non-blocking ``flock`` on
    ``data/<live|seeded>/.lock`` for their whole duration, so two of them can never
    read and rewrite the same state file at once. Nothing has been fetched or
    written when this is raised.

    Args:
        rel: The lock's data-root-relative path, e.g. ``"live/.lock"``.

    Attributes:
        rel: The lock path.
    """

    exit_code: ClassVar[ExitCode] = ExitCode.LOCKED

    def __init__(self, rel: str) -> None:
        self.rel = rel
        super().__init__(f"another jsa process holds the lock {rel}; retry later")


class RunIdTaken(AgentError):  # noqa: N818 - parallel to the other policy errors
    """A run folder with this run ID already exists (two runs in the same second).

    Run IDs have one-second resolution (``RUN_ID_PATTERN``) and are stored in the
    state file, so they are never suffixed; the second run stops before fetching.

    Args:
        run_id: The run ID that is already taken.

    Attributes:
        run_id: The run ID.
    """

    exit_code: ClassVar[ExitCode] = ExitCode.LOCKED

    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        super().__init__(
            f"run id {run_id} is already used (a run started in the same second); "
            "retry in a second"
        )
