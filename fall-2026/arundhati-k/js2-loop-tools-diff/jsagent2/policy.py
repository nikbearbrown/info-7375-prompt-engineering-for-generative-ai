"""Permission policy, enforced in code (GATE.md section 5).

Every network request, read, write and delete the agent makes goes through one of the check_* methods first.
"""

import os
from collections import namedtuple
from pathlib import Path
from urllib.parse import urlsplit

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com"})
OUT = "out"
STATE_FILE = "out/state/seen.json"

Decision = namedtuple("Decision", "verdict reason")  # verdict: allow | refuse | hold


class Policy:
    def __init__(self, root, approve_state_write=False, hosts=ALLOWED_HOSTS):
        self.root = Path(root)
        self.approve_state_write = approve_state_write
        self.hosts = frozenset(hosts)

    # --- network ---------------------------------------------------------------------------------
    def check_request(self, method, url):
        parts = urlsplit(url)
        if method != "GET":
            return Decision("refuse", f"method {method} not allowed: the agent only reads (GET)")
        if parts.scheme != "https":
            return Decision("refuse", f"scheme {parts.scheme!r} not allowed: https only")
        if parts.username or parts.password:
            return Decision("refuse", "credentials in URL not allowed")
        if parts.hostname not in self.hosts:
            return Decision("refuse", f"host {parts.hostname!r} is not on the allow-list {sorted(self.hosts)}")
        if parts.port not in (None, 443):
            return Decision("refuse", f"port {parts.port} not allowed")
        return Decision("allow", f"GET https://{parts.hostname} is on the allow-list")

    # --- files -----------------------------------------------------------------------------------
    def _full(self, path):
        p = Path(os.path.expanduser(str(path)))
        return p if p.is_absolute() else self.root / p

    def _inside(self, path, folder):
        """True if path, after resolving .. and every symlink, is folder itself or below it."""
        full = self._full(path).resolve()
        base = (self.root / folder).resolve()
        return full == base or base in full.parents

    def _has_symlink(self, path):
        """True if any existing component between the root and the target is a symlink."""
        full = Path(os.path.normpath(self._full(path)))
        root = Path(os.path.normpath(self.root))
        if root not in full.parents:
            return False  # outside the root: _inside already refuses it
        cur = root
        for part in full.relative_to(root).parts:
            cur = cur / part
            if cur.is_symlink():
                return True
        return False

    def check_read(self, path):
        if not self._inside(path, "."):
            return Decision("refuse", f"read outside the project folder: {path}")
        return Decision("allow", "read inside the project folder")

    def check_write(self, path):
        if not self._inside(path, OUT):
            return Decision("refuse", f"write outside {OUT}/: {path}")
        if self._has_symlink(path):
            return Decision("refuse", f"write through a symlink: {path}")
        if self._full(path).resolve() == (self.root / STATE_FILE).resolve():
            if self.approve_state_write:
                return Decision("allow", "state write approved with --approve-state-write")
            return Decision("hold", "writing the seen-jobs state needs --approve-state-write")
        return Decision("allow", f"write inside {OUT}/")

    def check_delete(self, path):
        if not self._inside(path, OUT) or self._has_symlink(path):
            return Decision("refuse", f"delete outside {OUT}/: {path}")
        return Decision("hold", "every delete needs my approval")

    # --- enforcement helpers used by the loop ----------------------------------------------------
    def write_bytes(self, path, data):
        d = self.check_write(path)
        if d.verdict != "allow":
            return d
        full = self._full(path)
        full.parent.mkdir(parents=True, exist_ok=True)
        # re-check after mkdir: a symlink could not have been created by us, but be strict
        d = self.check_write(path)
        if d.verdict != "allow":
            return d
        full.write_bytes(data)
        return d

    def read_bytes(self, path):
        d = self.check_read(path)
        if d.verdict != "allow":
            raise PermissionError(d.reason)
        return self._full(path).read_bytes()
