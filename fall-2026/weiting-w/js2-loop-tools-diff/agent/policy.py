"""GATE.md §5 — the permission policy, in code.

Not in a prompt, not in a docstring the model is asked to respect: a `Policy`
object with three gatekeeping methods, and every network call and file write in
this package goes through it. It holds whether or not a model is involved at
all.

The three methods are deliberately separate — `check_request`, `check_read`,
`check_write` — because a surface that may read a folder is not thereby allowed
to write it (GATE.md §5.2).
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from .errors import (
    DisallowedHost,
    DisallowedPort,
    DisallowedScheme,
    MethodNotAllowed,
    NeedsApproval,
    PathEscapes,
    RefusedRealResume,
)

POLICY_VERSION = "P-v1"

#: GATE.md §5.1 — three hosts, three applicant-tracking systems.
ALLOWED_HOSTS = frozenset(
    {
        "boards-api.greenhouse.io",
        "api.lever.co",
        "api.ashbyhq.com",
    }
)

ALLOWED_METHODS = frozenset({"GET"})
ALLOWED_SCHEMES = frozenset({"https"})

#: Paths the agent may read, relative to the project root.
READABLE_SUBTREES = ("config", "data", "evidence")

#: Never readable, whatever else allows it. Carried over from JS1 R2.
NEVER_READ = ("*.real.json",)

#: A write under here needs --approve-overwrite if the file already exists.
APPROVAL_SUBTREE = "raw"


def _inside(root: Path, candidate: Path) -> bool:
    """True when `candidate` resolves to something strictly inside `root`.

    Both are fully resolved first, so `..` segments and symlinks are followed
    before the comparison. This is a parent-chain check and **not** a string
    prefix test: `evidence-evil` is not inside `evidence`, even though its name
    starts with it. That string test is wrong version W2 in GATE.md §7.
    """
    root = root.resolve()
    candidate = candidate.resolve()
    if candidate == root:
        return False
    return root in candidate.parents


@dataclass
class Policy:
    """The whole permission surface of the agent.

    `project_root` anchors the readable subtrees; `output_root` is the only
    writable tree. `approve_overwrite` is the one thing a caller may set, and
    it only ever *adds* the overwrite permission — it cannot widen a host, a
    method, or a path.
    """

    project_root: Path
    output_root: Path
    approve_overwrite: bool = False
    allowed_hosts: frozenset[str] = ALLOWED_HOSTS
    _issued: set[tuple[str, str]] = field(default_factory=set, repr=False)

    # --- 5.1 network -------------------------------------------------------

    def check_request(self, method: str, url: str) -> str:
        """Return `url` if this exact request is permitted; else refuse.

        Refusals happen on the string, before any socket is opened, so the
        boundary tests need no network at all.
        """
        if method not in ALLOWED_METHODS:
            raise MethodNotAllowed(
                f"method {method!r} is not allowed; this package sends only "
                f"{sorted(ALLOWED_METHODS)} and has no request-body code path"
            )
        parts = urlsplit(url)
        if parts.scheme not in ALLOWED_SCHEMES:
            raise DisallowedScheme(
                f"scheme {parts.scheme!r} is not allowed; allowed: {sorted(ALLOWED_SCHEMES)}"
            )
        host = (parts.hostname or "").casefold()
        # Exact equality on the parsed hostname. Not endswith, not substring:
        # `boards-api.greenhouse.io.evil.example` must not match, and an
        # allowed host appearing in a query string must not match either.
        if host not in self.allowed_hosts:
            raise DisallowedHost(
                f"host {host!r} is not on the allow-list; allowed: "
                f"{sorted(self.allowed_hosts)}"
            )
        if parts.port is not None and parts.port != 443:
            raise DisallowedPort(f"port {parts.port} is not allowed")
        return url

    # --- 5.2 filesystem ----------------------------------------------------

    def check_read(self, path: str | Path) -> Path:
        path = Path(path)
        name = path.name
        for pattern in NEVER_READ:
            if fnmatch.fnmatch(name, pattern):
                raise RefusedRealResume(
                    f"refusing to read {name!r}: the agent loads only a "
                    "validated persona resume (GATE.md §5.2)"
                )
        for subtree in READABLE_SUBTREES:
            if _inside(self.project_root / subtree, path):
                return path
        raise PathEscapes(
            f"{path} is not inside any readable subtree "
            f"{READABLE_SUBTREES} of {self.project_root}"
        )

    def check_write(self, path: str | Path) -> Path:
        path = Path(path)
        if not _inside(self.output_root, path):
            raise PathEscapes(
                f"{path} does not resolve to a location inside {self.output_root}"
            )
        # 5.3 approval: overwriting saved raw evidence is the one filesystem
        # action I most want to be unable to do by accident.
        if (
            self.output_root / APPROVAL_SUBTREE
        ).resolve() in path.resolve().parents and path.exists():
            if not self.approve_overwrite:
                raise NeedsApproval(
                    f"{path} already exists under {APPROVAL_SUBTREE}/; pass "
                    "--approve-overwrite to replace saved raw evidence"
                )
        return path

    # --- GATE.md §3 the repeat rule ---------------------------------------

    def note_action(self, method: str, url: str) -> None:
        """Record a (method, url) as issued; refuse a second one in this run."""
        from .errors import RepeatedAction

        key = (method, url)
        if key in self._issued:
            raise RepeatedAction(
                f"{method} {url} was already issued in this run (GATE.md §3)"
            )
        self._issued.add(key)

    def forget_actions(self) -> None:
        """Clear the per-run action log. Used only when starting a new run."""
        self._issued.clear()

    def describe(self) -> dict:
        """What the run report prints about the policy that was in force."""
        return {
            "policy_version": POLICY_VERSION,
            "allowed_hosts": sorted(self.allowed_hosts),
            "allowed_methods": sorted(ALLOWED_METHODS),
            "output_root": str(self.output_root),
            "readable_subtrees": list(READABLE_SUBTREES),
            "approve_overwrite": self.approve_overwrite,
        }
