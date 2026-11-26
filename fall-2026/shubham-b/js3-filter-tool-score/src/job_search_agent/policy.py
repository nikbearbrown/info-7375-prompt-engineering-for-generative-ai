"""The JS2 permission policy, in code (GATE §6).

Every tool the watch loop uses asks this policy first: the fetcher before each request,
the loop before it opens a write folder, the plan loader before it reads, and
``jsa watch reset`` before it deletes. A check returns a ``Verdict`` value; callers
turn a refusal into a failed board or a refused command, never into a guess.

Containment and host checks reuse the project's single implementations
(``fsio.relative_within``, ``http.check_url``) through ``inside`` and ``host_refusal``,
so "inside" and "allowed" mean the same thing here as everywhere else.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final

import httpx

from job_search_agent.errors import HostNotAllowed, PathRejected
from job_search_agent.fsio import relative_within
from job_search_agent.http import check_url

NEVER_ACTIONS: Final = frozenset({"apply", "email", "message", "login"})
"""Refused with or without approval (GATE §6). The agent has no tool for any of them."""

TOOLS: Final = frozenset({"fetch", "read", "write", "delete"})
"""The only actions the agent has; each one still passes its own check."""

HOST_CEILING: Final = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com"})
"""GATE §6: the only hosts a plan may allow; widening it is a reviewed code change."""

WRITE_CEILING: Final = "data/watch"
"""GATE §6: every plan's write root must be this folder or inside it."""

PRIVATE_DIRS: Final = ("private",)
"""Top-level folders that hold the real résumé and other personal files."""

Approver = Callable[[str], bool]
"""Shows a question to Shubham and returns True only on an explicit yes."""


class Decision(StrEnum):
    """What the policy says about one request."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    NEEDS_APPROVAL = "NEEDS_APPROVAL"


@dataclass(frozen=True, slots=True)
class Verdict:
    """One policy answer.

    Attributes:
        decision: Allow, deny, or ask Shubham first.
        reason: Short code (``"host"``, ``"outside_write_root"``, ...); ``""`` when
            allowed without conditions.
    """

    decision: Decision
    reason: str = ""

    @property
    def allowed(self) -> bool:
        """True only for ``ALLOW``."""
        return self.decision is Decision.ALLOW


_ALLOW: Final = Verdict(Decision.ALLOW)


def _deny(reason: str) -> Verdict:
    return Verdict(Decision.DENY, reason)


def inside(path: Path, root: Path) -> bool:
    """Returns True if ``path``, resolved through symlinks, is ``root`` or below it.

    Compared by path components, so ``data/watch-evil`` is not inside ``data/watch``.

    Args:
        path: Absolute candidate path.
        root: Absolute containing directory.
    """
    try:
        relative_within(path, root, allow_root=True)
    except PathRejected:
        return False
    return True


def host_refusal(url: httpx.URL, allowed_hosts: frozenset[str]) -> str | None:
    """Returns why ``url`` may not be requested, or ``None`` if it may.

    Args:
        url: The candidate URL.
        allowed_hosts: Exact, lowercase host names.

    Returns:
        ``"scheme"``, ``"userinfo"``, ``"host"`` or ``"port"``; ``None`` if allowed.
    """
    try:
        check_url(url, allowed_hosts)
    except HostNotAllowed as exc:
        return exc.reason
    return None


class PermissionPolicy:
    """Hosts, read and write folders, approvals and never-actions (GATE §6).

    Args:
        project_root: The repository root; reads must stay inside it.
        write_root: The only folder the agent may write (``data/watch``).
        allowed_hosts: Exact host names the agent may request.

    Raises:
        ValueError: If ``write_root`` is not inside ``project_root``.
    """

    def __init__(
        self, *, project_root: Path, write_root: Path, allowed_hosts: Iterable[str]
    ) -> None:
        self._project = project_root.resolve()
        self._write_root = write_root.resolve()
        self._hosts = frozenset(h.lower() for h in allowed_hosts)
        if self._write_root == self._project or not inside(
            self._write_root, self._project
        ):
            raise ValueError("write_root must be a folder inside the project")

    @property
    def write_root(self) -> Path:
        """The resolved write folder."""
        return self._write_root

    @property
    def allowed_hosts(self) -> frozenset[str]:
        """The exact host names that may be requested."""
        return self._hosts

    def _absolute(self, path: Path | str) -> Path | None:
        text = os.fspath(path)
        if "\x00" in text:
            return None
        candidate = Path(text)
        return candidate if candidate.is_absolute() else self._project / candidate

    def check_action(self, action: str) -> Verdict:
        """Refuses the never-actions and anything that is not one of the agent's tools.

        Args:
            action: An action name, e.g. ``"fetch"`` or ``"apply"``.
        """
        if action in NEVER_ACTIONS:
            return _deny("never")
        if action not in TOOLS:
            return _deny("unknown_action")
        return _ALLOW

    def check_request(self, method: str, url: str) -> Verdict:
        """Checks one HTTP request: GET only, HTTPS, port 443, an allowed host.

        Args:
            method: The HTTP method.
            url: The absolute URL.
        """
        if method.upper() != "GET":
            return _deny("method")
        try:
            parsed = httpx.URL(url)
        except (httpx.InvalidURL, TypeError):
            return _deny("invalid_url")
        reason = host_refusal(parsed, self._hosts)
        return _ALLOW if reason is None else _deny(reason)

    def check_read(self, path: Path | str) -> Verdict:
        """Allows reads inside the project, except the private folders and ``.env``.

        Args:
            path: Absolute, or relative to the project root.
        """
        target = self._absolute(path)
        if target is None:
            return _deny("nul")
        if not inside(target, self._project):
            return _deny("outside_project")
        resolved = target.resolve()
        if any(inside(resolved, self._project / name) for name in PRIVATE_DIRS):
            return _deny("private")
        if resolved.name == ".env" or resolved.name.startswith(".env."):
            return _deny("private")
        return _ALLOW

    def check_write(self, path: Path | str) -> Verdict:
        """Allows a write only inside the write folder (resolved through symlinks).

        Args:
            path: Absolute, or relative to the project root.
        """
        target = self._absolute(path)
        if target is None:
            return _deny("nul")
        if not inside(target, self._write_root):
            return _deny("outside_write_root")
        return _ALLOW

    def check_delete(self, path: Path | str) -> Verdict:
        """A delete inside the write folder needs Shubham's approval; others are denied.

        Args:
            path: Absolute, or relative to the project root.
        """
        verdict = self.check_write(path)
        if not verdict.allowed:
            return verdict
        return Verdict(Decision.NEEDS_APPROVAL, "delete")


def settle(verdict: Verdict, *, approver: Approver | None, question: str) -> Verdict:
    """Turns ``NEEDS_APPROVAL`` into ``ALLOW`` or ``DENY`` by asking Shubham.

    With no approver (no terminal), the answer is no.

    Args:
        verdict: A policy verdict.
        approver: Asks the question, or ``None`` when nobody can be asked.
        question: What Shubham is asked to approve.

    Returns:
        ``verdict`` unchanged unless it needed approval; then ``ALLOW`` with reason
        ``"approved"`` or ``DENY`` with reason ``"not_approved"``.
    """
    if verdict.decision is not Decision.NEEDS_APPROVAL:
        return verdict
    if approver is not None and approver(question):
        return Verdict(Decision.ALLOW, "approved")
    return _deny("not_approved")
