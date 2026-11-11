"""The permission check every fetch, read and write passes first (GATE.md v0.3 §5).

Also CONTRACT.md v0.5 items 1, 2 and 5. One function, Policy.check, decides;
agent/tool_layer.py calls it before it touches the network or a file. A
refusal names the rule it broke, and nothing is sent or written.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .errors import Refusal

# §5 / v0.5 item 2: the whole host, lowercased, exactly one of these.
ALLOWED_HOSTS = ("boards-api.greenhouse.io", "api.ashbyhq.com")
# v0.5 item 1: the two fetch URL forms, as (path pattern, exact query) per host.
# Decision 2026-11-06: a board name is letters, digits, "_" and "-" only, so
# no "..", "/" or encoded character can reach the server's path.
_BOARD = r"(?P<board>[A-Za-z0-9][A-Za-z0-9_-]*)"
URL_FORMS = {
    "boards-api.greenhouse.io": (re.compile(rf"/v1/boards/{_BOARD}/jobs"), "content=true"),
    "api.ashbyhq.com": (re.compile(rf"/posting-api/job-board/{_BOARD}"), "includeCompensation=true"),
}

# §5: the working subfolders, judged by whole folder name after resolution.
WRITABLE_DIRS = ("state", "evidence", "output")
# §5 and v0.5 item 5: never written. Decision 2026-11-06 (Prasad): not even with --approve.
READ_ONLY_DIRS = (("evidence", "gate_probes"), ("evidence", "snapshots"))
# §5 Never: "no approval overrides this one".
NEVER_WRITE = "GATE.md"
# §5: "any change to CONTRACT.md or the config" needs approval.
APPROVAL_FILES = ("config.json", "CONTRACT.md")

R_FETCH_SCHEME = "§5 fetch: https only"
R_FETCH_USERINFO = "§5 fetch: no userinfo"
R_FETCH_PORT = "§5 fetch: no non-default port"
R_FETCH_HOST = "§5 fetch: host exactly boards-api.greenhouse.io or api.ashbyhq.com"
R_FETCH_FORM = "CONTRACT v0.5 item 1: one of the two fetch URL forms"
R_FETCH_BOARD = "CONTRACT v0.5 item 1: a board listed in the config for that host"
R_READ_INSIDE = "§5 read: inside the project folder only"
R_WRITE_INSIDE = "§5 write: inside the project folder only, approval or not"
R_WRITE_FILE = "§5 write: one named file"
R_WRITE_GATE = "§5 never: GATE.md is never written, approval or not"
R_WRITE_READ_ONLY = "§5 write: evidence/gate_probes/ and evidence/snapshots/ are read-only, approval or not"
R_WRITE_APPROVAL = "§5 approval: needs --approve <exact path> on this run"
R_WRITE_APPROVAL_USED = "§5 approval: one write per approval"


class PolicyRefusal(Refusal):
    """A request §5 forbids. reasons is a list of (rule, detail) pairs."""

    def __init__(self, action, target, reasons):
        self.action = action
        self.target = target
        self.reasons = list(reasons)
        details = "; ".join(f"[{rule}] {detail}" for rule, detail in self.reasons)
        super().__init__(f"refused {action} {str(target)!r}: {details}")

    @property
    def rules(self):
        return [rule for rule, _ in self.reasons]


@dataclass(frozen=True)
class Permit:
    """What the check allowed. path is the resolved real path the tool must use."""

    action: str
    target: str
    url: str = None
    path: Path = None
    overwrite: bool = False
    approval: str = None


def _folded(parts):
    return tuple(part.casefold() for part in parts)


class Policy:
    """One run's permission state: the project folder, the configured boards as
    (host, name) pairs, and that run's --approve flags."""

    def __init__(self, project_root, boards, approvals=()):
        self.root = Path(project_root).resolve()
        # Decision 2026-11-06: the host is compared lowercased, as in §5; the
        # board name exactly, as the config writes it.
        self.boards = frozenset((host.lower(), name) for host, name in boards)
        # Decision 2026-11-06: an approval names a path the way a write does,
        # relative to the project folder; both sides are compared resolved.
        self._approvals = []
        for flag in approvals:
            self._approvals.append({"flag": str(flag), "path": self.resolve(flag), "used": False})

    def resolve(self, target):
        """The resolved real path a target names, relative to the project folder."""
        path = Path(target)
        if not path.is_absolute():
            path = self.root / path
        return path.resolve()


    def approval_record(self):
        """Every --approve flag of this run, for the run report (§5)."""
        return [{"flag": a["flag"], "path": str(a["path"]), "used": a["used"]} for a in self._approvals]

    def check(self, action, target):
        """Return a Permit, or raise PolicyRefusal before anything is sent or written."""
        if action == "fetch":
            return self._check_fetch(target)
        if action == "read":
            return self._check_read(target)
        if action == "write":
            return self._check_write(target)
        raise PolicyRefusal(action, target, [("§5 tools", f"{action!r} is not fetch, read or write")])

    def _check_fetch(self, url):
        reasons = []
        if not isinstance(url, str) or not url.isascii() or any(ch <= " " or ch == "\x7f" for ch in url):
            raise PolicyRefusal("fetch", url, [(R_FETCH_FORM, "URL is not printable ASCII without spaces")])
        parts = urlsplit(url)
        if parts.scheme != "https":
            reasons.append((R_FETCH_SCHEME, f"scheme is {parts.scheme!r}"))
        if "@" in parts.netloc:
            reasons.append((R_FETCH_USERINFO, f"{parts.netloc.rpartition('@')[0]!r} stands before '@'"))
        try:
            port = parts.port
        except ValueError:
            reasons.append((R_FETCH_PORT, f"port in {parts.netloc!r} is not a number"))
        else:
            # Decision 2026-11-06: an explicit :443 is the default port, so the host rule allows it.
            if port not in (None, 443):
                reasons.append((R_FETCH_PORT, f"port {port}"))
        host = parts.hostname  # urlsplit lowercases it
        if host not in ALLOWED_HOSTS:
            reasons.append((R_FETCH_HOST, f"host {host!r} is not exactly one of {', '.join(ALLOWED_HOSTS)}"))
        else:
            path_form, query = URL_FORMS[host]
            match = path_form.fullmatch(parts.path)
            if not match or parts.query != query or parts.fragment:
                reasons.append((R_FETCH_FORM, f"{parts.path!r}?{parts.query!r} is not the {host} form"))
            elif (host, match["board"]) not in self.boards:
                reasons.append((R_FETCH_BOARD, f"board {match['board']!r} is not configured for {host}"))
        if reasons:
            raise PolicyRefusal("fetch", url, reasons)
        return Permit("fetch", url, url=url)

    def _inside(self, real):
        return real == self.root or real.is_relative_to(self.root)

    def _check_read(self, target):
        real = self.resolve(target)
        if not self._inside(real):
            raise PolicyRefusal("read", target, [(R_READ_INSIDE, f"resolves to {real}")])
        return Permit("read", str(target), path=real)

    def _check_write(self, target):
        real = self.resolve(target)
        if not self._inside(real):
            raise PolicyRefusal("write", target, [(R_WRITE_INSIDE, f"resolves to {real}")])
        rel = real.relative_to(self.root).parts
        folded = _folded(rel)
        # Protected names compare case-insensitively, so a case-insensitive
        # disk (macOS) cannot reach GATE.md as gate.md.
        gate = self.root / NEVER_WRITE
        if folded == (NEVER_WRITE.casefold(),) or (real.exists() and gate.exists() and os.path.samefile(real, gate)):
            raise PolicyRefusal("write", target, [(R_WRITE_GATE, f"resolves to {real}")])
        if any(folded[: len(ro)] == _folded(ro) for ro in READ_ONLY_DIRS):
            raise PolicyRefusal("write", target, [(R_WRITE_READ_ONLY, f"resolves to {real}")])
        if not rel or real.is_dir():
            raise PolicyRefusal("write", target, [(R_WRITE_FILE, f"{real} is a folder")])

        needs = []
        if len(rel) < 2 or rel[0] not in WRITABLE_DIRS:
            needs.append(f"{'/'.join(rel)} is outside {', '.join(d + '/' for d in WRITABLE_DIRS)}")
        if folded in [(name.casefold(),) for name in APPROVAL_FILES]:
            needs.append(f"{rel[0]} is a change to the config or the contract")
        overwrite = real.exists()
        if overwrite:
            needs.append(f"{'/'.join(rel)} already exists")
        if not needs:
            return Permit("write", str(target), path=real)

        approval = next((a for a in self._approvals if a["path"] == real), None)
        if approval is None:
            raise PolicyRefusal("write", target, [(R_WRITE_APPROVAL, need) for need in needs])
        if approval["used"]:
            raise PolicyRefusal("write", target, [(R_WRITE_APPROVAL_USED, f"--approve {approval['flag']} was already used this run")])
        approval["used"] = True
        return Permit("write", str(target), path=real, overwrite=overwrite, approval=approval["flag"])
