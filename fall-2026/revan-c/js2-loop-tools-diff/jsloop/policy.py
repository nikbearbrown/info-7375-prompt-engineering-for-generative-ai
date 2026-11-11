"""The permission policy from GATE.md, enforced before any network or filesystem call.

Network: only GET over HTTPS to the four exact board URLs; the fourth only in demonstration mode.
Files: read the fictional résumé, state/js2 and fixtures/js2; write only evidence/js2 and runs/js2,
and state/js2 only with --approve-state-write. Containment is checked on resolved real paths,
by path components, so `..`, sibling prefixes such as runs/js2-evil, and symlinks cannot escape.
"""
import os
import pathlib
import urllib.parse
from dataclasses import dataclass


class PolicyDenied(Exception):
    """An action the gate does not allow. `rule` names the part of the policy that refused it."""

    def __init__(self, rule, message):
        super().__init__(f"DENIED ({rule}): {message}")
        self.rule = rule


# ---- network ---------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Board:
    order: int
    name: str
    provider: str
    url: str
    demo_only: bool = False


BOARDS = (
    Board(1, "klaviyo", "greenhouse",
          "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true"),
    Board(2, "duolingo", "greenhouse",
          "https://boards-api.greenhouse.io/v1/boards/duolingo/jobs?content=true"),
    Board(3, "patchmypc", "lever",
          "https://api.lever.co/v0/postings/patchmypc?mode=json"),
    Board(4, "js2-deliberate-missing-board", "greenhouse",
          "https://boards-api.greenhouse.io/v1/boards/js2-deliberate-missing-board/jobs?content=true",
          demo_only=True),
)
BY_NAME = {b.name: b for b in BOARDS}
BY_URL = {b.url: b for b in BOARDS}
NORMAL_SELECTION = ("klaviyo", "duolingo", "patchmypc")
DEMO_SELECTION = NORMAL_SELECTION + ("js2-deliberate-missing-board",)
ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.lever.co"})
ALLOWED_METHODS = frozenset({"GET"})


def check_request(method, url, *, demo=False):
    """Return the allow-listed Board for this request, or raise PolicyDenied."""
    if method not in ALLOWED_METHODS:
        raise PolicyDenied("method", f"{method} refused; only GET is allowed")
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https":
        raise PolicyDenied("scheme", f"scheme {parts.scheme!r} refused; https only")
    if parts.username is not None or parts.password is not None:
        raise PolicyDenied("credentials", "credentials in the URL are refused; the agent never logs in")
    # Exact hostname membership: a look-alike such as boards-api.greenhouse.io.evil.com is not a member.
    if parts.hostname not in ALLOWED_HOSTS:
        raise PolicyDenied("host", f"host {parts.hostname!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")
    try:
        port = parts.port
    except ValueError:
        port = "invalid"
    if port is not None:
        raise PolicyDenied("port", f"explicit port {port!r} refused; only the default https port")
    board = BY_URL.get(url)
    if board is None:
        raise PolicyDenied("endpoint", f"{url} is not one of the {len(BOARDS)} exact URLs in GATE.md")
    if board.demo_only and not demo:
        raise PolicyDenied("demo-only", f"{board.name} is allowed only in the labeled demonstration run")
    return board


# ---- files -----------------------------------------------------------------------------------------

RESUME_PATH = "resumes/aarav-patel.json"
STATE_DIR = "state/js2"
READ_ONLY_DIRS = ("fixtures/js2",)
WRITE_DIRS = ("evidence/js2", "runs/js2")


def _inside(path, root):
    # Component containment, not string prefix: runs/js2-evil is not inside runs/js2.
    return path == root or path.is_relative_to(root)


class Workspace:
    """All agent file access goes through here. `base` is the repository root."""

    def __init__(self, base):
        self.base = pathlib.Path(os.path.realpath(base))
        self._write = {rel: self._real(rel) for rel in WRITE_DIRS}
        self._state = self._real(STATE_DIR)
        self._read_only = {rel: self._real(rel) for rel in READ_ONLY_DIRS}
        self._resume = self._real(RESUME_PATH)

    def _real(self, path):
        path = pathlib.Path(path)
        return pathlib.Path(os.path.realpath(path if path.is_absolute() else self.base / path))

    def rel(self, real_path):
        return pathlib.Path(real_path).relative_to(self.base).as_posix()

    def roots_problem(self):
        """A folder the policy names that itself resolves outside the repository makes every check unsound."""
        roots = {**self._write, STATE_DIR: self._state, **self._read_only, RESUME_PATH: self._resume}
        for rel, real in roots.items():
            if not _inside(real, self.base):
                return f"{rel} resolves to {real}, outside the repository {self.base}"
        return None

    def _require_sound_roots(self):
        problem = self.roots_problem()
        if problem:
            raise PolicyDenied("root-outside-repository", problem)

    # -- reads
    def check_read(self, path):
        self._require_sound_roots()
        real = self._real(path)
        if real == self._resume or _inside(real, self._state) or any(
                _inside(real, root) for root in self._read_only.values()):
            return real
        raise PolicyDenied("outside-read-roots",
                           f"{path} is not the fictional résumé, {STATE_DIR}/, or a fixtures/js2/ file")

    def read_bytes(self, path):
        return self.check_read(path).read_bytes()

    # -- writes
    def check_write(self, path, *, approve_state_write=False):
        self._require_sound_roots()
        real = self._real(path)
        if any(_inside(real, root) for root in self._write.values()):
            return real
        if _inside(real, self._state):
            if approve_state_write:
                return real
            raise PolicyDenied("needs-approval", f"writing {STATE_DIR}/ needs --approve-state-write")
        if real == self._resume or any(_inside(real, root) for root in self._read_only.values()):
            raise PolicyDenied("read-only", f"{path} may be read but never written")
        raise PolicyDenied("outside-write-roots",
                           f"{path} resolves to {real}, outside {', '.join(WRITE_DIRS)} and {STATE_DIR}")

    def write_new(self, path, data):
        """Create a new file; never overwrite. Returns the repository-relative path."""
        real = self.check_write(path)
        real.parent.mkdir(parents=True, exist_ok=True)
        # O_EXCL refuses an existing file; O_NOFOLLOW refuses a symlink planted at the final component.
        fd = os.open(real, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        return self.rel(real)

    def replace(self, path, data, *, approve_state_write=False):
        """Atomically replace a file the policy lets this run write."""
        real = self.check_write(path, approve_state_write=approve_state_write)
        tmp = self.check_write(real.with_name(real.name + ".tmp"), approve_state_write=approve_state_write)
        real.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o644)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp, real)
        return self.rel(real)

    def unique_path(self, directory, stem, suffix):
        """A not-yet-existing path in `directory`, as repository-relative text."""
        candidate = f"{directory}/{stem}{suffix}"
        n = 1
        while self._real(candidate).exists():
            candidate = f"{directory}/{stem}-{n}{suffix}"
            n += 1
        return candidate
