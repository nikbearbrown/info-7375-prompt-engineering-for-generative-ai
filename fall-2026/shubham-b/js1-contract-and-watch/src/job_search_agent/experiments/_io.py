"""Shared I/O seams for the experiment harnesses.

Every runtime output goes through ``fsio.OutputRoot``, whose paths are relative to
the data directory (``"experiments/prompt/SEAL.json"``).
Inputs and earlier outputs are read through ``RepoReader`` with repo-relative paths
(``"experiments/prompt/labels/dev.labels.json"``,
``"data/experiments/prompt/SEAL.json"``). Ordering gates ask git through the
``GitInspector`` port.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, ClassVar, Protocol

from job_search_agent.errors import AgentError
from job_search_agent.fsio import OutputRoot, ReadPolicy
from job_search_agent.models import ExitCode
from job_search_agent.ports import Clock, GitInspector
from job_search_agent.sources import sha256_hex


class ExperimentError(AgentError):
    """An experiment command refused to run (a gate or an input check failed).

    The message says which gate and what to do; it never contains résumé values.
    """

    exit_code: ClassVar[ExitCode] = ExitCode.EXPERIMENT_REFUSED


class RepoReader(Protocol):
    """Reads files by repo-relative path (through ``fsio.ReadPolicy`` in production)."""

    def read_bytes(self, rel: str) -> bytes:
        """Returns the file's bytes; raises ``FileNotFoundError`` if absent."""
        ...

    def exists(self, rel: str) -> bool:
        """Returns True if the file exists."""
        ...


class LocalRepoReader:
    """``RepoReader`` limited to the read roots of ``fsio.ReadPolicy``.

    Args:
        policy: The project's read policy.
    """

    def __init__(self, policy: ReadPolicy) -> None:
        self._policy = policy

    def _path(self, rel: str) -> Path:
        pure = PurePosixPath(rel)
        if pure.is_absolute() or ".." in pure.parts:
            raise ExperimentError(f"refusing to read outside the project: {rel}")
        return self._policy.check(rel)

    def read_bytes(self, rel: str) -> bytes:
        """Returns the file's bytes."""
        return self._path(rel).read_bytes()

    def exists(self, rel: str) -> bool:
        """Returns True if the file exists."""
        return self._path(rel).is_file()


@dataclass(frozen=True)
class ExperimentContext:
    """Injected dependencies shared by every harness.

    Attributes:
        writer: Output root (data-dir-relative writes).
        reader: Repo-relative reads.
        git: Repository questions for the ordering gates.
        clock: Timestamps.
        data_dir: Repo-relative data directory (``"data"``).
    """

    writer: OutputRoot
    reader: RepoReader
    git: GitInspector
    clock: Clock
    data_dir: str = "data"

    def repo_rel(self, data_rel: str) -> str:
        """Maps a data-dir-relative path to a repo-relative one."""
        return f"{self.data_dir}/{data_rel}"

    def data_exists(self, data_rel: str) -> bool:
        """Returns True if an output already exists."""
        return self.reader.exists(self.repo_rel(data_rel))

    def read_data_json(self, data_rel: str) -> Any:  # noqa: ANN401 - parsed JSON
        """Reads an earlier output as JSON."""
        return read_json(self.reader, self.repo_rel(data_rel))

    def committed(self, data_rel: str) -> bool:
        """Returns True if an output is tracked by git and unchanged since commit."""
        return self.git.is_tracked_and_clean(Path(self.repo_rel(data_rel)))


def read_json(reader: RepoReader, rel: str) -> Any:  # noqa: ANN401 - parsed JSON
    """Reads and parses a JSON file.

    Args:
        reader: The repo reader.
        rel: Repo-relative path.

    Returns:
        The parsed value.

    Raises:
        ExperimentError: If the file is missing or not JSON.
    """
    try:
        raw = reader.read_bytes(rel)
    except FileNotFoundError as exc:
        raise ExperimentError(f"missing file: {rel}") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ExperimentError(f"not valid JSON: {rel}") from exc


def file_sha256(reader: RepoReader, rel: str) -> str:
    """Returns the SHA-256 of a repo file.

    Raises:
        ExperimentError: If the file is missing.
    """
    try:
        return sha256_hex(reader.read_bytes(rel))
    except FileNotFoundError as exc:
        raise ExperimentError(f"missing file: {rel}") from exc


def record_calls(
    ctx: ExperimentContext,
    rel: str,
    header: Mapping[str, Any],
    calls: Iterable[Callable[[], Mapping[str, Any]]],
) -> dict[str, Any]:
    """Makes the calls in order, rewriting ``rel`` atomically after each one.

    The file exists with ``"complete": false`` before the first call, so a started
    study is never re-run, and a crash keeps every call made so far. Only after the
    last call are ``"complete": true`` and ``finished_at_utc`` written.

    Args:
        ctx: Shared dependencies.
        rel: Data-relative output file (a manifest or a results file).
        header: Study facts copied to the top of the file.
        calls: Each makes one call and returns its JSON record.

    Returns:
        The final document.
    """
    done: list[Mapping[str, Any]] = []
    doc: dict[str, Any] = {
        **header,
        "retry": "none (first reply only)",
        "complete": False,
        "calls": done,
    }
    ctx.writer.write_json_atomic(rel, doc)
    for call in calls:
        done.append(call())
        ctx.writer.write_json_atomic(rel, doc)
    doc["finished_at_utc"] = ctx.clock.now_utc().isoformat()
    doc["complete"] = True
    ctx.writer.write_json_atomic(rel, doc)
    return doc


def is_complete(doc: Mapping[str, Any]) -> bool:
    """Returns True only for a study file that says ``"complete": true``."""
    return doc.get("complete") is True


STUDENT_MARKER = "<!-- STUDENT WRITES THIS -->"
"""Placeholder for every human-judgment section in generated documents."""
