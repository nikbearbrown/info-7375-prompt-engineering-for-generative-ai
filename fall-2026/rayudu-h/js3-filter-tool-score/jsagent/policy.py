"""The permission policy from GATE.md, enforced in code (not in a prompt).

Every network request and every file read/write goes through a Policy check first.
A refused action raises Refused before any byte is sent or written; the loop logs it.
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com"})
ALLOWED_METHODS = frozenset({"GET"})
WRITE_DIRS = ("runs", "state")
APPROVAL_RESET_STATE = "reset-state"


class Refused(Exception):
    """An action the permission policy does not allow."""


class Policy:
    def __init__(self, root: Path = ROOT, approvals=()):
        self.root = Path(root).resolve()
        self.approvals = frozenset(approvals)
        self.write_roots = tuple((self.root / d).resolve() for d in WRITE_DIRS)

    # ---- network --------------------------------------------------------------------------
    def check_request(self, method: str, url: str) -> None:
        if method.upper() not in ALLOWED_METHODS:
            raise Refused(f"method {method} is not allowed (GET only)")
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise Refused(f"scheme {parsed.scheme!r} is not allowed (HTTPS only): {url}")
        if parsed.hostname not in ALLOWED_HOSTS:
            raise Refused(f"host {parsed.hostname!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")

    # ---- files ----------------------------------------------------------------------------
    def _resolve(self, path) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.root / p
        # resolve() follows symlinks in every existing component, so a symlink pointing
        # outside lands outside; '..' is collapsed; prefix tricks are compared as paths.
        return p.resolve()

    def check_read(self, path) -> Path:
        real = self._resolve(path)
        if not real.is_relative_to(self.root):
            raise Refused(f"read outside this folder: {path}")
        return real

    def check_write(self, path) -> Path:
        real = self._resolve(path)
        if not any(real == w or real.is_relative_to(w) for w in self.write_roots):
            raise Refused(f"write outside {', '.join(WRITE_DIRS)}/: {path}")
        return real

    def check_reset_state(self, path) -> Path:
        real = self.check_write(path)
        if APPROVAL_RESET_STATE not in self.approvals:
            raise Refused(f"resetting state needs Hemanth's approval (--approve {APPROVAL_RESET_STATE}): {path}")
        return real
