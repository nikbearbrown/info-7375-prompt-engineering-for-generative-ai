"""The permission policy (GATE.md, Permission policy), enforced in the program and not in a prompt.

Every request the loop sends passes check_request, and every file it reads or writes passes
Files.check_read, Files.check_write, Files.check_state_write or Files.check_state_delete. A
refusal raises Refused (NeedsApproval for a write that needs --approve) before anything happens.

How a path is checked: it is made absolute against the repo (not resolved), then refused if it has a
".." part, refused unless it sits lexically inside one of the allowed folders, and refused if the
folder or any existing part below it is a symlink. With ".." and symlinks refused, where a path
points on disk is where it reads, so the lexical check is sound. Folders above the allowed ones
are not inspected: on a Mac, /tmp and /var are themselves symlinks.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePath
from urllib.parse import urlsplit, urlunsplit

from .errors import NeedsApproval, Refused

# The only hosts, and on each the only path and query the agent may GET.
HOSTS = {
    "api.ashbyhq.com": (re.compile(r"/posting-api/job-board/[a-z0-9][a-z0-9-]{0,63}"), ""),
    "boards-api.greenhouse.io": (re.compile(r"/v1/boards/[a-z0-9][a-z0-9-]{0,63}/jobs"), "content=true"),
    "api.lever.co": (re.compile(r"/v0/postings/[a-z0-9][a-z0-9-]{0,63}"), "mode=json"),
}
METHODS = ("GET",)
# Characters that let two URL parsers disagree about where the host ends.
_SUSPICIOUS = set("\\ \t\r\n") | {chr(c) for c in range(32)} | {chr(127)}


def check_request(method: str, url: str) -> str:
    """Return the URL rebuilt from its checked parts, or raise Refused naming the problem."""
    if method not in METHODS:
        raise Refused(f"refused: {method} {url!r}: the agent sends GET requests only")
    if not isinstance(url, str) or any(ch in _SUSPICIOUS for ch in url):
        raise Refused(f"refused: {url!r} contains characters a URL should not have")
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise Refused(f"refused: {url!r} is not https")
    if parts.username is not None or parts.password is not None:
        raise Refused(f"refused: {url!r} names a user or password")
    host = parts.hostname  # lowercased by urlsplit
    if not host:
        raise Refused(f"refused: {url!r} has no host")
    if host not in HOSTS:
        raise Refused(f"refused: host {host!r} is not on the allow-list ({', '.join(sorted(HOSTS))})")
    try:
        port = parts.port
    except ValueError:
        raise Refused(f"refused: {url!r} has an unreadable port") from None
    if port not in (None, 443):
        raise Refused(f"refused: {url!r} uses port {port}, not 443")
    path, query = HOSTS[host]
    if not path.fullmatch(parts.path) or parts.query != query or parts.fragment:
        raise Refused(f"refused: {url!r} is not a board path the agent may read on {host}")
    return urlunsplit(("https", host, parts.path, parts.query, ""))


class Files:
    """Where the loop may read and write. Paths in messages are shown relative to the repo."""

    def __init__(self, repo: Path, write_roots, read_roots):
        self.repo = Path(repo).absolute()
        self.write_roots = [self._absolute(r) for r in write_roots]
        self.read_roots = [self._absolute(r) for r in read_roots]

    def check_write(self, path) -> Path:
        return self._check(path, self.write_roots, "write")

    def check_read(self, path) -> Path:
        return self._check(path, self.read_roots, "read")

    def check_state_write(self, path, old, new, approval=None) -> str:
        """"first", "append" or "approved"; NeedsApproval when the write would replace a board's state."""
        target = self.check_write(path)
        if old is None:
            if target.exists():
                raise NeedsApproval(f"refused: write {self.shown(target)}: a state file is already there; "
                                    "replacing it needs --approve")
            return "first"
        problem = replaces(old, new)
        if not problem:
            return "append"
        if approval:
            return "approved"
        raise NeedsApproval(f"refused: write {self.shown(target)} would replace a board's state ({problem}); "
                            "this needs --approve")

    def check_state_delete(self, path, approval=None) -> str:
        target = self.check_write(path)
        if not approval:
            raise NeedsApproval(f"refused: deleting {self.shown(target)} would remove a board's state; "
                                "this needs --approve")
        return "approved"

    def shown(self, path) -> str:
        target = self._absolute(path)
        try:
            return str(PurePath(target).relative_to(self.repo))
        except ValueError:
            return str(path)

    def _absolute(self, path) -> Path:
        path = Path(path)
        return path if path.is_absolute() else self.repo / path

    def _check(self, path, roots, kind) -> Path:
        target = self._absolute(path)
        if ".." in target.parts:
            raise Refused(f"refused: {kind} {path}: a path with '..' is never followed")
        for root in roots:
            if _inside(target, root):
                _refuse_symlinks(target, root, kind, path)
                return target
        allowed = ", ".join(self.shown(r) for r in roots)
        raise Refused(f"refused: {kind} {path}: outside the folders the agent may {kind} ({allowed})")


def _inside(target, root) -> bool:
    try:
        PurePath(target).relative_to(root)
        return True
    except ValueError:
        return False


def _refuse_symlinks(target, root, kind, shown) -> None:
    current = Path(root)
    if current.is_symlink():
        raise Refused(f"refused: {kind} {shown}: {current.name} is a symlink, and symlinks are never followed")
    for part in PurePath(target).parts[len(PurePath(root).parts):]:
        current = current / part
        if current.is_symlink():
            raise Refused(f"refused: {kind} {shown}: {current.name} is a symlink, and symlinks are never followed")


def replaces(old: dict, new: dict) -> str:
    """Why writing `new` over `old` would replace a board's state, or "" when it only adds to it."""
    for key in ("schema", "system", "name"):
        if old.get(key) != new.get(key):
            return f"its {key} would change"
    dropped = set(old.get("seen_ids") or []) - set(new.get("seen_ids") or [])
    if dropped:
        return f"{len(dropped)} seen id{'s' if len(dropped) != 1 else ''} would be dropped"
    old_runs = old.get("runs") or []
    if (new.get("runs") or [])[: len(old_runs)] != old_runs:
        return "its earlier runs would change"
    return ""
