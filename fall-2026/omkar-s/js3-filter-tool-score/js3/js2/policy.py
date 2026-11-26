"""Permission policy (GATE.md section 5), enforced in code.

Every network request and every file read/write is decided here: ALLOW, DENY or ASK.
ASK becomes ALLOW only if an approver callable is supplied and returns True; the normal
non-interactive run has no approver, so ASK means "not granted".
"""
import os
from urllib.parse import urlsplit

ALLOW, DENY, ASK = "ALLOW", "DENY", "ASK"

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.ashbyhq.com", "api.lever.co"})
ALLOWED_METHODS = frozenset({"GET"})
FORBIDDEN_HEADERS = frozenset({"authorization", "cookie", "proxy-authorization"})
# Named actions the agent must never take, whatever the input and whoever approves.
FORBIDDEN_ACTIONS = frozenset({"apply", "email", "message", "login"})


class PolicyDenied(Exception):
    def __init__(self, decision):
        super().__init__(f"{decision['decision']}: {decision['reason']}")
        self.decision = decision


def _d(kind, target, decision, reason, **extra):
    out = {"kind": kind, "target": target, "decision": decision, "reason": reason}
    out.update(extra)
    return out


def check_request(method, url, headers=None):
    """Decide one network request. Never does I/O."""
    method = (method or "").upper()
    parts = urlsplit(url)
    if method not in ALLOWED_METHODS:
        return _d("request", url, DENY, f"method {method} refused; GET only (applying is a POST)")
    if parts.scheme != "https":
        return _d("request", url, DENY, f"scheme {parts.scheme!r} refused; https only")
    if parts.username is not None or parts.password is not None or "@" in parts.netloc:
        return _d("request", url, DENY, "credentials in the URL are refused")
    try:
        port = parts.port
    except ValueError:
        return _d("request", url, DENY, "unparseable port")
    if port not in (None, 443):
        return _d("request", url, DENY, f"port {port} refused; 443 only")
    host = (parts.hostname or "").lower()
    if host not in ALLOWED_HOSTS:  # exact match: no substring, no endswith
        return _d("request", url, DENY, f"host {host!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")
    for h in (headers or {}):
        if h.lower() in FORBIDDEN_HEADERS:
            return _d("request", url, DENY, f"header {h!r} refused; the agent never sends credentials")
    return _d("request", url, ALLOW, f"GET to allow-listed host {host}")


def check_action(action, approver=None):
    """Named high-impact actions. Approval cannot unlock them."""
    a = (action or "").lower()
    if a in FORBIDDEN_ACTIONS:
        return _d("action", a, DENY, f"'{a}' is never allowed (GATE.md section 5); approval does not apply")
    return _d("action", a, DENY, f"unknown action '{a}'; only fetch/read/write exist")


def _inside(path, root):
    """True iff the REAL path of `path` is root or below it. Component-wise, not a string prefix."""
    real = os.path.realpath(path)
    root_real = os.path.realpath(root)
    try:
        return os.path.commonpath([real, root_real]) == root_real
    except ValueError:  # different drives on Windows
        return False


class Policy:
    """Bound to one assignment folder (`base`) and one output folder (`out`, inside base)."""

    def __init__(self, base, out, state_dir=None, config_dir=None, approver=None):
        self.base = os.path.realpath(base)
        self.out = os.path.realpath(out)
        self.state_dir = os.path.realpath(state_dir or os.path.join(out, "state"))
        self.config_dir = os.path.realpath(config_dir or os.path.join(base, "config"))
        self.approver = approver
        if not _inside(self.out, self.base):
            raise ValueError("output folder must be inside the assignment folder")

    def _resolve(self, path):
        return path if os.path.isabs(path) else os.path.join(self.base, path)

    def check_read(self, path):
        p = self._resolve(path)
        if _inside(p, self.base):
            return _d("read", path, ALLOW, "inside the assignment folder")
        return _d("read", path, DENY, "outside the assignment folder")

    def _ask(self, path, reason):
        if self.approver is None:
            return _d("write", path, ASK, reason + "; no approver in this run, so NOT granted", granted=False)
        granted = bool(self.approver(path, reason))
        return _d("write", path, ALLOW if granted else ASK,
                  reason + ("; approved" if granted else "; approver said no"), granted=granted)

    def check_write(self, path):
        p = self._resolve(path)
        if _inside(p, self.config_dir):
            return self._ask(path, "write to config/ changes a budget or the watch list")
        if not _inside(p, self.out):
            return _d("write", path, DENY, "outside the output folder runs/ (after resolving the real path)")
        if os.path.lexists(p):
            if _inside(p, self.state_dir) and p.endswith(".state.json"):
                return _d("write", path, ALLOW, "state file: the one file the loop updates each run")
            return self._ask(path, "overwriting existing evidence in runs/ (append-only)")
        return _d("write", path, ALLOW, "new file inside runs/")


def granted(decision):
    return decision["decision"] == ALLOW
