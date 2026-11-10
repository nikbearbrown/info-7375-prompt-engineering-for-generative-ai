"""GATE.md permission policy, enforced in code.

- check_url: the only hosts this agent may call (HTTPS only, default port,
  no userinfo). Extends JS1's agent/fetch.py check_url with api.lever.co.
- WritePolicy: every file this agent writes goes through it. A target is
  resolved to its real absolute path (symlinks followed, `..` collapsed) and
  must be strictly inside one of evidence/, state/, logs/ - themselves
  resolved and required to sit inside the project root. Containment is a
  path-component check (Path.is_relative_to), so `state_evil/` is not
  "inside" `state/`.
- New-board state: creating a state file that does not exist yet requires
  the board to have been approved with --approve-new-board <name>. This is
  enforced at the write itself, not only by the caller's pre-check.

There is deliberately no code anywhere in this project to apply to a job,
send email or any message, or log in - those capabilities are absent, not
refused.
"""
import os
import re
from pathlib import Path
from urllib.parse import urlparse

# api.anthropic.com is deliberately absent: JS2 has no judgment code yet. It is
# added back (here and in GATE.md) in the same change that adds judgment code.
ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.lever.co"})
WRITE_DIRS = ("evidence", "state", "logs")
STATE_FILE_RE = re.compile(r"(?P<board>[A-Za-z0-9_-]+)_seen\.json")


class PermissionDenied(PermissionError):
    pass


class HostNotAllowed(PermissionDenied):
    pass


class WriteOutsideAllowedDirs(PermissionDenied):
    pass


class NewBoardNotApproved(PermissionDenied):
    pass


def check_url(url):
    u = urlparse(url)
    try:
        port = u.port
    except ValueError:
        port = "invalid"
    if (u.scheme != "https" or u.hostname not in ALLOWED_HOSTS
            or u.username is not None or u.password is not None or port not in (None, 443)):
        raise HostNotAllowed(f"refusing to call {url!r}: not https on an allow-listed host {sorted(ALLOWED_HOSTS)}")
    return url


def _real(p):
    return Path(os.path.realpath(p))


class WritePolicy:
    def __init__(self, root, approved_new_boards=()):
        self.root = _real(root)
        self.approved_new_boards = frozenset(approved_new_boards)

    def allowed_dirs(self):
        """Resolved fresh on every call, so a directory swapped for a symlink
        after construction is still caught."""
        dirs = {}
        for name in WRITE_DIRS:
            d = _real(self.root / name)
            if not d.is_relative_to(self.root):
                raise WriteOutsideAllowedDirs(f"{name}/ resolves to {d}, outside project root {self.root}")
            dirs[name] = d
        return dirs

    def state_path(self, board):
        return self.root / "state" / f"{board}_seen.json"

    def check_write(self, target):
        """Return (allowed dir name, real path) or raise."""
        real = _real(target)
        for name, d in self.allowed_dirs().items():
            if real != d and real.is_relative_to(d):
                if name == "state":
                    self._check_state_write(real)
                return name, real
        raise WriteOutsideAllowedDirs(
            f"refusing to write {str(target)!r} (resolves to {real}): not inside {', '.join(d + '/' for d in WRITE_DIRS)}")

    def _check_state_write(self, real):
        m = STATE_FILE_RE.fullmatch(real.name)
        if not m or real.parent != self.allowed_dirs()["state"]:
            raise WriteOutsideAllowedDirs(f"refusing to write {real}: state/ holds only <board>_seen.json files")
        board = m["board"]
        if not real.exists() and board not in self.approved_new_boards:
            raise NewBoardNotApproved(
                f"refusing to create state for new board {board!r}: re-run with --approve-new-board {board}")

    def write_bytes(self, target, data):
        _, real = self.check_write(target)
        real.parent.mkdir(parents=True, exist_ok=True)
        _, real2 = self.check_write(target)  # re-check: mkdir must not have changed where it resolves
        if real2 != real:
            raise WriteOutsideAllowedDirs(f"{target} changed resolution during write ({real} -> {real2})")
        tmp = real.with_name(f".{real.name}.{os.getpid()}.tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            os.replace(tmp, real)  # rename replaces a symlink itself, never its target
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
        return real
