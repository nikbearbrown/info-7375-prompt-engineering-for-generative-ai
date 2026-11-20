"""Permission policy, enforced in code (GATE.md > Permission Policy).

Every network request and every file read or write the agent makes goes
through a Policy check first. A failed check raises PolicyViolation; the loop
catches it and ends the run with exit status `error`.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.lever.co"})
ALLOWED_METHODS = frozenset({"GET"})
ALLOWED_SCHEMES = frozenset({"https"})

# Files outside out/ that may be written only with --approve.
PROTECTED_FILES = ("boards.json", "budget.json", "GATE.md")


class PolicyViolation(Exception):
    """Raised when an action breaks the permission policy."""

    def __init__(self, kind: str, target: str, reason: str):
        self.kind = kind          # "request", "read" or "write"
        self.target = target
        self.reason = reason
        super().__init__(f"{kind} blocked: {target} ({reason})")


class Policy:
    """Checks requests and file access against GATE.md.

    root:    the js2-loop-tools-diff/ folder (reads allowed anywhere inside it)
    approve: True only when the run was started with --approve
    """

    def __init__(self, root: Path, approve: bool = False):
        self.root = Path(root).resolve()
        self.out_dir = self.root / "out"
        self.approve = approve
        self.protected = {self.root / name for name in PROTECTED_FILES}

    # ---- network -------------------------------------------------------

    def check_request(self, method: str, url: str) -> None:
        if method.upper() not in ALLOWED_METHODS:
            raise PolicyViolation("request", url, f"method {method} not allowed")
        parts = urlsplit(url)
        if parts.scheme not in ALLOWED_SCHEMES:
            raise PolicyViolation("request", url, f"scheme {parts.scheme!r} not allowed")
        # Exact match on the parsed hostname: no substring or suffix matching
        # (WRONG_VERSIONS #6), and user:pass@ or :port tricks are rejected.
        host = (parts.hostname or "").lower()
        if host not in ALLOWED_HOSTS:
            raise PolicyViolation("request", url, f"host {host!r} not allowed")
        if parts.username or parts.password or parts.port is not None:
            raise PolicyViolation("request", url, "credentials or port in URL not allowed")

    # ---- filesystem ----------------------------------------------------

    def _resolve(self, path: Path | str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.root / p
        # resolve() follows symlinks and collapses "..", so the check below
        # sees where a write would really land (WRONG_VERSIONS #7, #8).
        return p.resolve()

    def check_read(self, path: Path | str) -> Path:
        real = self._resolve(path)
        if not real.is_relative_to(self.root):
            raise PolicyViolation("read", str(path), "outside the project folder")
        return real

    def check_write(self, path: Path | str) -> Path:
        real = self._resolve(path)
        out_real = self.out_dir.resolve()
        # is_relative_to compares whole path components, so out-evil/ is not
        # inside out/ (a string startswith check would let it through).
        if real == out_real or real.is_relative_to(out_real):
            return real
        if real in self.protected:
            if self.approve:
                return real
            raise PolicyViolation("write", str(path), "protected file; needs --approve")
        raise PolicyViolation("write", str(path), "outside out/")


def guarded_write(policy: Policy, path: Path | str, text: str) -> Path:
    """The only way agent code writes a file: check first, then write."""
    real = policy.check_write(path)
    real.parent.mkdir(parents=True, exist_ok=True)
    real.write_text(text, encoding="utf-8")
    return real
