"""Permission policy, enforced in code (GATE.md §6).

Two questions, answered without side effects:
  check_url(url, method)            -> may the agent send this request?
  authorize(root, target, mode, ...) -> may the agent read/write this path? returns the path to use.

Every refusal raises PolicyError with a short machine-readable reason (the BOUNDARY-TESTS.md codes).
"""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlsplit

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com"})
ALLOWED_METHODS = frozenset({"GET"})
READ_ROOTS = ("config", "persona", "state", "runs")
APPROVAL_PATHS = ("state/seen-ids.json",)


class PolicyError(Exception):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason
        self.detail = detail


def check_url(url: str, method: str = "GET") -> str:
    """Allow only GET over https to an exact allow-listed host (no userinfo, no port tricks)."""
    if method.upper() not in ALLOWED_METHODS:
        raise PolicyError("method-not-allowed", method)
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise PolicyError("scheme-not-https", url)
    if parts.username or parts.password or parts.port not in (None, 443):
        raise PolicyError("host-not-allowed", url)
    if not _host_ok(parts.hostname or ""):
        raise PolicyError("host-not-allowed", parts.hostname or url)
    return url


def _host_ok(host: str) -> bool:
    return host in ALLOWED_HOSTS  # exact match, never substring/suffix (W8)


def _approval_ok(approval: object, run_id: str | None) -> bool:
    return isinstance(approval, str) and run_id is not None and approval == run_id  # never merely truthy (W3)


def _resolve(root: Path, target: str | os.PathLike) -> Path:
    # Ported from JS1's safeWrite: path.resolve(root, target). Cleans "." and ".." textually.
    return Path(os.path.abspath(os.path.join(root, target)))


def _inside(path: Path, base: Path) -> bool:
    # Component-wise containment (not a string prefix), so "runs-evil" is not inside "runs".
    return path == base or path.is_relative_to(base)


def authorize(root: str | os.PathLike, target: str | os.PathLike, mode: str, *,
              run_id: str | None = None, approval: object = None) -> Path:
    """Return the path the caller may use, or raise PolicyError.

    mode "read":  inside one of READ_ROOTS.
    mode "write": inside runs/<run_id>/ freely; state/seen-ids.json only with approval == run_id
                  (an exact string, never a merely truthy value); anything else refused.
    """
    root = Path(os.path.abspath(root))
    path = _resolve(root, target)
    if mode == "read":
        if any(_inside(path, _resolve(root, r)) for r in READ_ROOTS):
            return path
        raise PolicyError("outside-read-roots", str(target))
    if mode != "write":
        raise PolicyError("mode-not-allowed", mode)
    for rel in APPROVAL_PATHS:
        if path == _resolve(root, rel):
            if approval is None:
                raise PolicyError("approval-required", rel)
            if not _approval_ok(approval, run_id):
                raise PolicyError("approval-invalid", repr(approval))
            return path
    if run_id is None:
        raise PolicyError("outside-write-root", str(target))
    if _inside(path, _resolve(root, Path("runs") / run_id)):
        return path
    raise PolicyError("outside-write-root", str(target))


def write_text(root, target, text: str, mode: str = "write", **kw) -> Path:
    """Authorize, then write atomically (tmp + rename), as JS1 did."""
    path = authorize(root, target, mode, **kw)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
    return path


def write_bytes(root, target, data: bytes, **kw) -> Path:
    path = authorize(root, target, "write", **kw)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)
    return path


def read_text(root, target) -> str:
    return authorize(root, target, "read").read_text(encoding="utf-8")
