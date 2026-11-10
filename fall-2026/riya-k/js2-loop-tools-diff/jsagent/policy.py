"""The permission policy from GATE.md, enforced in code. Every check runs BEFORE a connection or a write.

Nothing here is a prompt. A refusal raises PolicyError with a reason; every decision is recorded in `self.log`.
"""

import json
import os
import urllib.parse
from pathlib import Path

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com", "api.smartrecruiters.com"})
ALLOWED_METHODS = frozenset({"GET"})
# GATE.md "Never": these are not flags that can be turned on; there is no code path that performs them.
NEVER = ("apply", "email", "message", "log in", "POST/PUT/DELETE", "show a real résumé")


class PolicyError(PermissionError):
    pass


def inside(path, root):
    """True only if the REAL path (symlinks and '..' resolved) is root itself or below it.

    Uses path components, not string prefixes, so 'runs-evil' is not inside 'runs' (GATE.md wrong version 6).
    """
    real, base = Path(os.path.realpath(path)), Path(os.path.realpath(root))
    return real == base or base in real.parents


class Policy:
    def __init__(self, out_dir, read_roots, approve=False):
        self.out_dir = Path(out_dir)
        self.read_roots = [Path(r) for r in read_roots]
        self.approve = approve
        self.log = []
        self.clock = None  # set by the loop's Session so policy decisions carry the same run time as other events
        self.display_root = None  # paths under this root are logged relative to it (no home-folder paths in traces)

    def _show(self, target):
        if self.display_root is not None and isinstance(target, Path):
            try:
                return str(Path(os.path.abspath(target)).relative_to(os.path.abspath(self.display_root)))
            except ValueError:
                pass
        return str(target)

    def _decide(self, kind, target, allowed, reason):
        entry = {"kind": kind, "target": self._show(target), "decision": "allow" if allowed else "refuse",
                 "reason": reason}
        if self.clock:
            entry = {"t": self.clock(), **entry}
        self.log.append(entry)
        if not allowed:
            raise PolicyError(f"refused {kind} {target}: {reason}")

    def check_request(self, method, url):
        u = urllib.parse.urlsplit(url)
        if method.upper() not in ALLOWED_METHODS:
            return self._decide("request", f"{method} {url}", False, f"method {method} not allowed (GET only)")
        if u.scheme != "https":
            return self._decide("request", url, False, f"scheme {u.scheme!r} not allowed (https only)")
        if u.username or u.password:
            return self._decide("request", url, False, "credentials in URL (the agent never logs in)")
        # Exact match on the parsed hostname: 'boards-api.greenhouse.io.evil.com' is a different host (wrong version 7).
        if u.hostname not in ALLOWED_HOSTS:
            return self._decide("request", url, False, f"host {u.hostname!r} not on allow-list {sorted(ALLOWED_HOSTS)}")
        if u.port not in (None, 443):
            return self._decide("request", url, False, f"port {u.port} not allowed")
        return self._decide("request", url, True, "allow-listed host, https, GET")

    def check_read(self, path):
        ok = any(inside(path, r) for r in self.read_roots) or inside(path, self.out_dir)
        return self._decide("read", path, ok, "inside a read root" if ok else "outside every read root")

    def check_write(self, path):
        ok = inside(path, self.out_dir)
        return self._decide("write", path, ok,
                            "inside output folder" if ok else f"resolves outside output folder {self.out_dir}")

    def check_state_write(self, path, old_ids, new_ids):
        """A state write that REMOVES ids needs --approve (GATE.md). Adding ids never does."""
        self.check_write(path)
        removed = set(old_ids) - set(new_ids)
        if removed and not self.approve:
            return self._decide("state-write", path, False,
                                f"would remove {len(removed)} seen id(s); needs --approve")
        reason = (f"removes {len(removed)} id(s), APPROVED by --approve" if removed else "adds ids only")
        return self._decide("state-write", path, True, reason)

    # Guarded file operations: the only way the agent writes or reads files.
    def read_bytes(self, path):
        self.check_read(path)
        return Path(path).read_bytes()

    def write_bytes(self, path, data):
        self.check_write(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.check_write(path)  # re-check after mkdir: a parent could have been a planted symlink
        Path(path).write_bytes(data)

    def write_text(self, path, text):
        self.write_bytes(path, text.encode("utf-8"))

    def write_state(self, path, old_ids, state):
        self.check_state_write(path, old_ids, state["seen_ids"])
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.check_write(path)
        Path(path).write_text(json.dumps(state, indent=1) + "\n")
