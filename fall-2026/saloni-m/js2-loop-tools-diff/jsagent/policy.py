"""The permission policy from GATE.md section 5, enforced in code (not in a prompt).

Three kinds of request are checked here, and nothing in the agent bypasses them:

- check_request(method, url): network. https + GET only, host exactly on the allow-list,
  no credentials in the URL (the agent never logs in), default port only.
- check_read(path): reads must resolve (symlinks followed) inside the project folder.
- check_write(path, approved): writes must resolve inside out/. Overwriting a file listed as
  approval-required (the saved job history) returns NEEDS_APPROVAL unless approved=True.

Paths are compared after os.path.realpath, with os.path.commonpath, so "..", a sibling folder
whose name starts with "out" (out-evil), and a symlink that points out of out/ are all refused.
"""
import os
import urllib.parse
from collections import namedtuple

ALLOW = "allow"
DENY = "deny"
NEEDS_APPROVAL = "needs_approval"

Decision = namedtuple("Decision", "outcome reason")


class PolicyError(PermissionError):
    def __init__(self, decision):
        super().__init__(f"{decision.outcome}: {decision.reason}")
        self.decision = decision


def _inside(real, root):
    return real == root or os.path.commonpath([real, root]) == root


class Policy:
    def __init__(self, project_root, out_dir, allowed_hosts, approval_files=()):
        self.project_root = os.path.realpath(project_root)
        self.out_dir = os.path.realpath(out_dir)
        if not _inside(self.out_dir, self.project_root):
            raise ValueError(f"out_dir {self.out_dir} is not inside the project {self.project_root}")
        self.allowed_hosts = frozenset(h.lower() for h in allowed_hosts)
        self.approval_files = frozenset(os.path.realpath(p) for p in approval_files)

    # -- network -------------------------------------------------------------------------
    def check_request(self, method, url):
        if method != "GET":
            return Decision(DENY, f"method {method} is not allowed; GET only (the agent never applies or posts)")
        try:
            parts = urllib.parse.urlsplit(url)
            port = parts.port
        except ValueError as e:
            return Decision(DENY, f"unparseable URL: {e}")
        if parts.scheme != "https":
            return Decision(DENY, f"scheme {parts.scheme!r} is not https")
        if parts.username is not None or parts.password is not None:
            return Decision(DENY, "credentials in URL; the agent never logs in")
        if port not in (None, 443):
            return Decision(DENY, f"port {port} is not the default https port")
        host = (parts.hostname or "").lower()
        if host not in self.allowed_hosts:
            return Decision(DENY, f"host {host!r} is not on the allow-list {sorted(self.allowed_hosts)}")
        return Decision(ALLOW, f"GET {host} is on the allow-list")

    # -- files ---------------------------------------------------------------------------
    def check_read(self, path):
        real = os.path.realpath(path)
        if not _inside(real, self.project_root):
            return Decision(DENY, f"read of {real} is outside the project folder")
        return Decision(ALLOW, "read inside the project folder")

    def check_write(self, path, approved=False):
        real = os.path.realpath(path)
        if not _inside(real, self.out_dir):
            why = " (through a symlink)" if real != os.path.abspath(path) else ""
            return Decision(DENY, f"write to {real} is outside {self.out_dir}{why}")
        if real in self.approval_files and os.path.exists(real) and not approved:
            return Decision(NEEDS_APPROVAL, f"overwriting {real} needs Saloni's approval (--approve-state)")
        return Decision(ALLOW, "write inside out/")

    def write_bytes(self, path, data, approved=False):
        d = self.check_write(path, approved)
        if d.outcome != ALLOW:
            raise PolicyError(d)
        os.makedirs(os.path.dirname(os.path.realpath(path)), exist_ok=True)
        with open(os.path.realpath(path), "wb") as f:
            f.write(data)
        return os.path.realpath(path)

    def read_bytes(self, path):
        d = self.check_read(path)
        if d.outcome != ALLOW:
            raise PolicyError(d)
        with open(os.path.realpath(path), "rb") as f:
            return f.read()
