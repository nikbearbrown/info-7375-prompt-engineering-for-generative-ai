"""Permission policy (GATE.md section 6), enforced in code.

Network: only GET, only to three exact hostnames, checked on every request including each
redirect hop, before the request is sent. Files: writes only inside <root>/out, reads only
inside <root>/{config,data,out,evidence}; both compare resolved path ancestry, never strings.
"""

import json
import os
import re
import tempfile
from pathlib import Path

import httpx


class PolicyError(Exception):
    """An action the permission policy refuses. Raised before the action happens."""


ALLOWED_HOSTS = frozenset({
    "boards-api.greenhouse.io",
    "api.lever.co",
    "api.ashbyhq.com",
})
ALLOWED_METHODS = frozenset({"GET"})
REQUEST_TIMEOUT_SECONDS = 10
MAX_REDIRECTS = 3

WRITE_DIR = "out"
READ_DIRS = ("config", "data", "out", "evidence")

_BOARD_KEY = re.compile(r"^[a-z]+:[A-Za-z0-9._-]+$")


# ---------- Network ----------

def _check_request(request: httpx.Request) -> None:
    # httpx calls request hooks for every request it sends, so each redirect hop is checked too.
    if request.method not in ALLOWED_METHODS:
        raise PolicyError(f"method not allowed: {request.method}")
    if request.url.scheme != "https":
        raise PolicyError(f"scheme not allowed: {request.url.scheme!r}")
    host = request.url.host
    if host not in ALLOWED_HOSTS:
        raise PolicyError(f"host not allowed: {host!r}")


def check_url(url: str) -> None:
    """Static check of a configured URL, using the same rule as the client hook."""
    _check_request(httpx.Request("GET", url))


def make_client(transport=None) -> httpx.Client:
    return httpx.Client(
        transport=transport,
        timeout=REQUEST_TIMEOUT_SECONDS,
        max_redirects=MAX_REDIRECTS,
        event_hooks={"request": [_check_request]},
    )


# ---------- Paths ----------

def _absolute(path, root) -> Path:
    p = Path(path)
    return p if p.is_absolute() else Path(root) / p


def _approved_dir(name: str, root) -> Path:
    """Resolved <root>/<name>; refused if that folder itself resolves somewhere else (a symlink)."""
    root_r = Path(root).resolve()
    d = (Path(root) / name).resolve()
    if d != root_r / name:
        raise PolicyError(f"{name}/ resolves outside the project: {d}")
    return d


def check_write(path, root) -> Path:
    """Return the resolved path if a write there is allowed (inside <root>/out), else raise."""
    p = _absolute(path, root)
    if ".." in p.parts:
        raise PolicyError(f"parent-directory traversal refused: {path}")
    out = _approved_dir(WRITE_DIR, root)
    resolved = p.resolve()
    if not resolved.is_relative_to(out):
        raise PolicyError(f"write outside out/ refused: {path} -> {resolved}")
    return resolved


def check_read(path, root) -> Path:
    """Return the resolved path if a read there is allowed, else raise."""
    resolved = _absolute(path, root).resolve()
    for name in READ_DIRS:
        if resolved.is_relative_to(_approved_dir(name, root)):
            return resolved
    raise PolicyError(f"read outside {', '.join(d + '/' for d in READ_DIRS)} refused: {path}")


# ---------- Writes (every write goes through check_write) ----------

def make_dir(path, root) -> Path:
    resolved = check_write(path, root)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def write_new(path, data, root) -> Path:
    """Create a file that must not already exist."""
    resolved = check_write(path, root)
    mode = "xb" if isinstance(data, bytes) else "x"
    kwargs = {} if isinstance(data, bytes) else {"encoding": "utf-8", "newline": ""}
    with open(resolved, mode, **kwargs) as f:
        f.write(data)
    return resolved


def append_line(path, line: str, root) -> Path:
    resolved = check_write(path, root)
    with open(resolved, "a", encoding="utf-8", newline="") as f:
        f.write(line + "\n")
    return resolved


def write_atomic(path, text: str, root) -> Path:
    """Write via a temp file in the same folder, then os.replace, so readers never see half a file."""
    resolved = check_write(path, root)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=resolved.parent, prefix=resolved.name + ".", suffix=".tmp")
    try:
        check_write(tmp, root)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, resolved)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return resolved


# ---------- State ----------

def safe_key(board_key: str) -> str:
    """File-name form of a board key: '<system>:<board>' -> '<system>_<board>'."""
    if not isinstance(board_key, str) or not _BOARD_KEY.match(board_key):
        raise PolicyError(f"board key not allowed: {board_key!r}")
    return board_key.replace(":", "_")


def state_path(board_key: str, root) -> Path:
    return Path(root) / WRITE_DIR / "state" / f"{safe_key(board_key)}.json"


def reset_state(board_key: str, root, approvals) -> Path:
    """Replace a board's state with an empty seen list, only with --approve reset:<board_key>."""
    needed = f"reset:{board_key}"
    if needed not in set(approvals or ()):
        raise PolicyError(f"state reset needs explicit approval: --approve {needed}")
    return write_atomic(state_path(board_key, root), json.dumps({"seen_ids": []}), root)
