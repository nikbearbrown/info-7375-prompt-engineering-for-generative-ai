"""Real ``CommandRunner`` and ``GitInspector`` implementations (subprocess-based).

Children are never started through a shell, always get an explicit, complete
environment and a timeout. ``SubprocessGit`` runs read-only git commands through any
``CommandRunner``, so it is testable with ``tests.fakes.FakeRunner``.
"""

from __future__ import annotations

import os
import subprocess
import time
from collections.abc import Mapping, Sequence
from pathlib import Path

from job_search_agent.models import CompletedCommand
from job_search_agent.ports import CommandRunner

GIT_TIMEOUT_S = 15.0

_GIT_ENV_KEYS = ("PATH", "HOME", "TMPDIR", "SYSTEMROOT")


class GitUnavailableError(RuntimeError):
    """A git command failed (not a repository, git missing, timeout)."""


class SubprocessRunner:
    """Runs a child process with ``subprocess.run`` (no shell)."""

    def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str],
        stdin: str,
        timeout_s: float,
    ) -> CompletedCommand:
        """Runs ``argv`` to completion or timeout (``ports.CommandRunner``).

        Args:
            argv: Program and arguments.
            cwd: Working directory.
            env: The complete child environment.
            stdin: Text for the child's stdin.
            timeout_s: Seconds before the child is killed.

        Returns:
            The captured result; ``timed_out`` is set when the timeout expired.

        Raises:
            OSError: If the program cannot be started.
        """
        start = time.monotonic()
        try:
            done = subprocess.run(  # noqa: S603 - fixed argv, no shell
                list(argv),
                cwd=cwd,
                env=dict(env),
                input=stdin.encode("utf-8"),
                capture_output=True,
                timeout=timeout_s,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return CompletedCommand(
                argv=tuple(argv),
                returncode=None,
                stdout=_decode(exc.stdout),
                stderr=_decode(exc.stderr),
                timed_out=True,
                duration_ms=int((time.monotonic() - start) * 1000),
            )
        return CompletedCommand(
            argv=tuple(argv),
            returncode=done.returncode,
            stdout=_decode(done.stdout),
            stderr=_decode(done.stderr),
            timed_out=False,
            duration_ms=int((time.monotonic() - start) * 1000),
        )


def _decode(data: bytes | str | None) -> str:
    if data is None:
        return ""
    if isinstance(data, str):
        return data
    return data.decode("utf-8", errors="replace")


def minimal_env(source: Mapping[str, str] | None = None) -> dict[str, str]:
    """Returns a minimal child environment (PATH, HOME, ...), ``LC_ALL=C``.

    Args:
        source: Environment to copy from; defaults to ``os.environ``.

    Returns:
        A new mapping without credentials or unrelated variables.
    """
    base = os.environ if source is None else source
    env = {k: base[k] for k in _GIT_ENV_KEYS if k in base}
    env["LC_ALL"] = "C"
    return env


class SubprocessGit:
    """Read-only repository facts via ``git`` (``ports.GitInspector``).

    Args:
        repo_root: The repository root (the child's cwd).
        runner: Process runner; defaults to ``SubprocessRunner``.
        executable: The git executable.
    """

    def __init__(
        self,
        repo_root: Path,
        *,
        runner: CommandRunner | None = None,
        executable: str = "git",
    ) -> None:
        self._root = repo_root
        self._runner: CommandRunner = runner or SubprocessRunner()
        self._git = executable

    def _run(self, *args: str) -> CompletedCommand:
        try:
            done = self._runner.run(
                [self._git, *args],
                cwd=self._root,
                env=minimal_env(),
                stdin="",
                timeout_s=GIT_TIMEOUT_S,
            )
        except OSError as exc:
            raise GitUnavailableError("git could not be started") from exc
        if done.timed_out:
            raise GitUnavailableError("git timed out")
        return done

    def head(self) -> str:
        """Returns the full commit hash of ``HEAD``.

        Raises:
            GitUnavailableError: If git fails.
        """
        done = self._run("rev-parse", "HEAD")
        commit = done.stdout.strip()
        if done.returncode != 0 or len(commit) not in (40, 64):
            raise GitUnavailableError("git rev-parse HEAD failed")
        return commit

    def is_dirty(self) -> bool:
        """Returns True if tracked files differ from ``HEAD``.

        Raises:
            GitUnavailableError: If git fails.
        """
        done = self._run("status", "--porcelain", "--untracked-files=no")
        if done.returncode != 0:
            raise GitUnavailableError("git status failed")
        return bool(done.stdout.strip())

    def is_tracked_and_clean(self, path: Path) -> bool:
        """Returns True if ``path`` is tracked and identical to ``HEAD``.

        Args:
            path: Repo-relative path.

        Raises:
            GitUnavailableError: If git cannot be run.
        """
        rel = path.as_posix()
        tracked = self._run("ls-files", "--error-unmatch", "--", rel)
        if tracked.returncode != 0:
            return False
        diff = self._run("diff", "--quiet", "HEAD", "--", rel)
        return diff.returncode == 0
