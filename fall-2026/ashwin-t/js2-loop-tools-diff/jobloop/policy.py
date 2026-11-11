"""The permission policy (GATE.md section 5), enforced in code before every operation.

Nothing here reads a prompt, a posting, or a model reply. Approval for the one state
write comes only from the `approve_state_write` argument, which only the command-line
flag `--approve-state-write` sets (see loop.main).

Decisions are one of ALLOW, DENY, APPROVAL_REQUIRED, always with a reason.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Union
from urllib.parse import urlsplit

ALLOW, DENY, APPROVAL_REQUIRED = "allow", "deny", "approval-required"

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com", "api.lever.co"})
ALLOWED_METHODS = frozenset({"GET"})

# Folders the runtime may create files beneath (never the folder itself).
WRITE_ROOTS = (("runs",), ("tests", "tmp"))
# The one approval-gated write, and the temp files used to replace it atomically.
STATE_DIR = ("state",)
STATE_FILE = ("state", "seen.json")
STATE_TEMP_PREFIX = ".seen.json."
STATE_TEMP_SUFFIX = ".tmp"
# Folders the runtime may read beneath.
READ_ROOTS = (("config",), ("data",), ("state",), ("runs",), ("seeded",),
              ("tests", "fixtures"), ("tests", "tmp"))

# The project root is this package's parent, independent of the launch directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

PathLike = Union[str, os.PathLike]


@dataclass(frozen=True)
class Decision:
    outcome: str
    reason: str

    @property
    def allowed(self) -> bool:
        return self.outcome == ALLOW


class PolicyViolation(RuntimeError):
    """An operation the policy does not allow was attempted. The run stops with `error`."""

    def __init__(self, decision: Decision, what: str):
        super().__init__(f"{decision.outcome}: {what}: {decision.reason}")
        self.decision = decision


# ---------------------------------------------------------------- network


def check_request(method: str, url: str, allowed_endpoints: Iterable[str]) -> Decision:
    """May the loop send this request? Only GET, only https:443, only exact hosts,
    and only the canonical endpoints built for the configured boards."""
    if method not in ALLOWED_METHODS:
        return Decision(DENY, f"method {method!r} is not allowed; the agent only reads (GET)")
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as exc:
        return Decision(DENY, f"URL cannot be parsed: {exc}")
    if parts.scheme != "https":
        return Decision(DENY, f"scheme {parts.scheme!r} is not https")
    if parts.username is not None or parts.password is not None:
        return Decision(DENY, "user information in URLs is not allowed")
    if port not in (None, 443):
        return Decision(DENY, f"port {port} is not allowed; only 443")
    if parts.hostname not in ALLOWED_HOSTS:
        return Decision(DENY, f"host {parts.hostname!r} is not on the allow-list")
    if parts.fragment:
        return Decision(DENY, "URL fragments are not allowed")
    if url not in set(allowed_endpoints):
        return Decision(DENY, "not one of the configured board-listing endpoints")
    return Decision(ALLOW, "GET to a configured board endpoint on an allow-listed host")


# ---------------------------------------------------------------- paths


def _relative_parts(root: Path, path: PathLike) -> tuple:
    """Split `path` into components relative to `root`, lexically, without touching the disk.
    Raises ValueError for traversal, empty or '.' components, or an absolute path outside root."""
    raw = os.fspath(path)
    if "\x00" in raw:
        raise ValueError("NUL byte in path")
    if ".." in raw.split("/"):
        raise ValueError(f"path {raw!r} contains '..'")
    p = PurePosixPath(raw)
    if p.is_absolute():
        try:
            p = p.relative_to(PurePosixPath(os.fspath(root)))
        except ValueError:
            raise ValueError(f"absolute path {raw!r} is outside the project root") from None
    if not p.parts:
        raise ValueError("empty path")
    return p.parts


def _under(parts: tuple, root: tuple) -> bool:
    """Component-wise containment: strictly beneath `root`. 'runs-evil' is not under 'runs'."""
    return len(parts) > len(root) and parts[:len(root)] == root


def _symlink_component(root: Path, parts: tuple) -> str:
    """Return the first existing component (from the root down) that is a symlink, or ''."""
    current = root
    for part in parts:
        current = current / part
        try:
            if current.is_symlink():
                return "/".join(current.relative_to(root).parts)
        except OSError:
            return ""
        if not current.exists():
            return ""
    return ""


def _is_state_temp(parts: tuple) -> bool:
    return (len(parts) == 2 and parts[0] == STATE_DIR[0]
            and parts[1].startswith(STATE_TEMP_PREFIX) and parts[1].endswith(STATE_TEMP_SUFFIX)
            and "/" not in parts[1])


def check_write(path: PathLike, *, root: Path = PROJECT_ROOT, approve_state_write: bool = False,
                run_status: str = "") -> Decision:
    """May the runtime create or replace this file?"""
    root = Path(root)
    try:
        parts = _relative_parts(root, path)
    except ValueError as exc:
        return Decision(DENY, str(exc))
    link = _symlink_component(root, parts)
    if link:
        return Decision(DENY, f"path component {link!r} is a symlink; writes never follow symlinks")
    if parts == STATE_FILE or _is_state_temp(parts):
        if not approve_state_write:
            return Decision(APPROVAL_REQUIRED, "writing state/seen.json needs --approve-state-write")
        if run_status != "finished":
            return Decision(DENY, f"state may be written only after a finished run, not {run_status or 'no run'!r}")
        return Decision(ALLOW, "approved state write after a finished run")
    for write_root in WRITE_ROOTS:
        if _under(parts, write_root):
            return Decision(ALLOW, f"beneath writable folder {'/'.join(write_root)}/")
    return Decision(DENY, f"{'/'.join(parts)!r} is not beneath runs/ or tests/tmp/")


def check_read(path: PathLike, *, root: Path = PROJECT_ROOT) -> Decision:
    """May the runtime read this file?"""
    root = Path(root)
    try:
        parts = _relative_parts(root, path)
    except ValueError as exc:
        return Decision(DENY, str(exc))
    link = _symlink_component(root, parts)
    if link:
        return Decision(DENY, f"path component {link!r} is a symlink; reads never follow symlinks")
    for read_root in READ_ROOTS:
        if _under(parts, read_root):
            return Decision(ALLOW, f"beneath readable folder {'/'.join(read_root)}/")
    return Decision(DENY, f"{'/'.join(parts)!r} is not beneath a readable folder")


# ------------------------------------------------- opening files without following links
#
# The checks above say yes or no. The functions below do the actual I/O by walking one
# directory at a time with O_NOFOLLOW, so a symlink swapped in after the check is still
# refused by the operating system (no check-then-follow).

_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def _open_dir(root: Path, parts: tuple, create: bool) -> int:
    fd = os.open(os.fspath(root), os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in parts:
            try:
                nfd = os.open(part, _DIR_FLAGS, dir_fd=fd)
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(part, 0o755, dir_fd=fd)
                nfd = os.open(part, _DIR_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = nfd
        return fd
    except BaseException:
        os.close(fd)
        raise


def _require(decision: Decision, what: str) -> None:
    if not decision.allowed:
        raise PolicyViolation(decision, what)


def read_bytes(path: PathLike, *, root: Path = PROJECT_ROOT) -> bytes:
    root = Path(root)
    _require(check_read(path, root=root), f"read {os.fspath(path)}")
    parts = _relative_parts(root, path)
    dfd = _open_dir(root, parts[:-1], create=False)
    try:
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dfd)
    finally:
        os.close(dfd)
    with os.fdopen(fd, "rb") as f:
        return f.read()


def exists(path: PathLike, *, root: Path = PROJECT_ROOT) -> bool:
    """Existence check for a readable path (used for the optional state file)."""
    _require(check_read(path, root=root), f"stat {os.fspath(path)}")
    return (Path(root) / os.fspath(path)).exists()


def make_new_dir(path: PathLike, *, root: Path = PROJECT_ROOT) -> None:
    """Create a new directory beneath a writable root. Fails if it already exists."""
    root = Path(root)
    probe = os.path.join(os.fspath(path), "probe")
    _require(check_write(probe, root=root), f"mkdir {os.fspath(path)}")
    parts = _relative_parts(root, path)
    dfd = _open_dir(root, parts[:-1], create=True)
    try:
        os.mkdir(parts[-1], 0o755, dir_fd=dfd)          # FileExistsError if it exists
    finally:
        os.close(dfd)


def open_new_file(path: PathLike, *, root: Path = PROJECT_ROOT):
    """Open a NEW file for binary writing. Existing evidence is never overwritten (O_EXCL)."""
    root = Path(root)
    _require(check_write(path, root=root), f"write {os.fspath(path)}")
    parts = _relative_parts(root, path)
    dfd = _open_dir(root, parts[:-1], create=True)
    try:
        fd = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=dfd)
    finally:
        os.close(dfd)
    return os.fdopen(fd, "wb")


def write_new_file(path: PathLike, data: bytes, *, root: Path = PROJECT_ROOT) -> None:
    with open_new_file(path, root=root) as f:
        f.write(data)


def replace_state(data: bytes, *, approve_state_write: bool, run_status: str,
                  root: Path = PROJECT_ROOT) -> None:
    """Atomically create or replace state/seen.json: temp file in state/, fsync, rename."""
    root = Path(root)
    target = "/".join(STATE_FILE)
    _require(check_write(target, root=root, approve_state_write=approve_state_write,
                         run_status=run_status), f"write {target}")
    temp = f"{STATE_TEMP_PREFIX}{os.getpid()}.{os.urandom(4).hex()}{STATE_TEMP_SUFFIX}"
    _require(check_write(f"{STATE_DIR[0]}/{temp}", root=root, approve_state_write=approve_state_write,
                         run_status=run_status), f"write state/{temp}")
    dfd = _open_dir(root, STATE_DIR, create=True)
    try:
        fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=dfd)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            os.rename(temp, STATE_FILE[1], src_dir_fd=dfd, dst_dir_fd=dfd)
        except BaseException:
            try:
                os.unlink(temp, dir_fd=dfd)
            except FileNotFoundError:
                pass
            raise
    finally:
        os.close(dfd)
