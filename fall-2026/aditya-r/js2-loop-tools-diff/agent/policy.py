"""JS2 runtime permission policy, enforced in code (GATE.md §5; GATE_ADDENDUM_1.md §1–2).

Network: unauthenticated HTTPS GET to the selected public board endpoints on two exact hosts.
Filesystem: reads only from named project folders; writes only inside out/, create-only except the
working-state file; out/approved-shortlists/ needs a verified approval; approvals/ is never written.

These are application-level controls, not an operating-system sandbox (GATE.md §5).
"""
import os
import re
from pathlib import Path
from urllib.parse import urlsplit


class PolicyError(Exception):
    """A prohibited action. The loop treats it as a run-level error (exit 2)."""


# exact hostname -> (path pattern, permitted query strings)
ENDPOINTS = {
    "boards-api.greenhouse.io": (re.compile(r"/v1/boards/[a-z0-9][a-z0-9-]{0,63}/jobs"), {"content=true"}),
    "api.ashbyhq.com": (re.compile(r"/posting-api/job-board/[A-Za-z0-9][A-Za-z0-9._-]{0,63}"), {""}),
}


def check_request(method, url):
    """Raise PolicyError unless this is a permitted board GET. Returns the parsed URL."""
    if method != "GET":
        raise PolicyError(f"refused: method {method!r} (only GET is permitted)")
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise PolicyError(f"refused: scheme {parts.scheme!r} (HTTPS only)")
    host = (parts.hostname or "").lower()
    if host not in ENDPOINTS:
        raise PolicyError(f"refused: host {host!r} is not on the allow-list {sorted(ENDPOINTS)}")
    if parts.username is not None or parts.password is not None:
        raise PolicyError("refused: credentials in URL")
    try:
        port = parts.port
    except ValueError:
        raise PolicyError("refused: malformed port") from None
    if port not in (None, 443):
        raise PolicyError(f"refused: port {port} (only the default HTTPS port)")
    path_re, queries = ENDPOINTS[host]
    if not path_re.fullmatch(parts.path) or parts.query not in queries or parts.fragment:
        raise PolicyError(f"refused: {parts.path!r}?{parts.query!r} is not a selected public board endpoint")
    return parts


def _inside(path, base):
    """Component-wise containment of two resolved paths (never a string-prefix test)."""
    return path == base or base in path.parents


class PathPolicy:
    READ_DIRS = ("config", "resume", "prompts", "state", "evidence", "out", "approvals")

    def __init__(self, root, out="out"):
        self.root = Path(root).resolve(strict=True)
        out_path = self.root / out
        if out_path.is_symlink():
            raise PolicyError(f"refused: output folder {out_path} is a symlink")
        self.out = out_path.resolve()
        if not _inside(self.out, self.root):
            raise PolicyError("refused: output folder is outside the project root")
        self.protected = self.out / "approved-shortlists"
        self.working_state = self.out / "state"
        self.approvals = (self.root / "approvals").resolve()
        self.read_bases = [(self.root / d).resolve() for d in self.READ_DIRS]

    def _resolve(self, path):
        p = Path(path)
        return (p if p.is_absolute() else self.root / p).resolve()  # follows symlinks and '..'

    def check_read(self, path):
        r = self._resolve(path)
        if not any(_inside(r, b) for b in self.read_bases):
            raise PolicyError(f"refused: read of {path} (outside the permitted read folders)")
        return r

    def check_write(self, path, *, approved_export=False):
        r = self._resolve(path)
        if _inside(r, self.approvals):
            raise PolicyError(f"refused: write to {path} (the runtime never creates or edits approval records)")
        if not _inside(r, self.out) or r == self.out:
            raise PolicyError(f"refused: write to {path} (outside {self.out.name}/)")
        if _inside(r, self.protected) and not approved_export:
            raise PolicyError(f"refused: write to {path} (protected export; needs a verified approval)")
        return r

    def _prepare(self, path, approved_export):
        r = self.check_write(path, approved_export=approved_export)
        r.parent.mkdir(parents=True, exist_ok=True)
        r2 = r.parent.resolve() / r.name  # re-check after creating parents (narrows, does not close, races)
        if r2 != r or r.is_symlink():
            raise PolicyError(f"refused: write to {path} (path changed or is a symlink)")
        return r

    def write_new(self, path, data, *, approved_export=False):
        """Create-only write. An existing target (or a symlink at the target) is refused."""
        r = self._prepare(path, approved_export)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(r, flags, 0o644)
        except FileExistsError:
            raise PolicyError(f"refused: {path} already exists (create-only)") from None
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        return r

    def open_new_stream(self, path):
        """Create-only append stream (used for the run trace)."""
        r = self._prepare(path, False)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(r, flags, 0o644)
        except FileExistsError:
            raise PolicyError(f"refused: {path} already exists (create-only)") from None
        return os.fdopen(fd, "a", encoding="utf-8")

    def replace_state(self, path, data):
        """Atomic replacement, permitted only for the working-state folder out/state/."""
        r = self.check_write(path)
        if not _inside(r, self.working_state):
            raise PolicyError(f"refused: replacement of {path} (only working state may be replaced)")
        tmp = r.with_name(f".{r.name}.tmp-{os.getpid()}")
        self.write_new(tmp, data)
        os.replace(tmp, r)
        return r

    def mkdir_new(self, path):
        r = self.check_write(path)
        r.parent.mkdir(parents=True, exist_ok=True)
        try:
            r.mkdir()
        except FileExistsError:
            raise PolicyError(f"refused: {path} already exists (run directories are unique)") from None
        return r
