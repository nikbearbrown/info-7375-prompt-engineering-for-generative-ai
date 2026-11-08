"""Permission policy, enforced in code. See GATE.md "Permission policy" and POLICY.md.

Every network call, file read, and file write the agent makes goes through one of the
check_* functions here. They return a Decision; the guarded helpers (guarded_write,
guarded_read) raise PolicyDenied instead of touching the disk when the answer is not ALLOW.
"""

import os
from dataclasses import dataclass
from urllib.parse import urlsplit

ALLOW = "allow"
DENY = "deny"
NEEDS_APPROVAL = "needs_approval"

ALLOWED_HOSTS = frozenset({
    "boards-api.greenhouse.io",
    "api.lever.co",
    "api.ashbyhq.com",
})
ALLOWED_METHODS = frozenset({"GET"})
FORBIDDEN_ACTIONS = frozenset({"apply", "email", "message", "login"})
CREDENTIAL_HEADERS = frozenset({"authorization", "cookie", "proxy-authorization"})

# Folder names relative to the assignment folder.
READ_ROOTS = ("config", "fixtures", "jobs")
WRITE_ROOTS = ("jobs",)
APPROVAL_WRITE_ROOTS = ("config",)
APPROVAL_DELETE_ROOTS = (os.path.join("jobs", "state"),)


@dataclass(frozen=True)
class Decision:
    result: str
    reason: str

    @property
    def allowed(self):
        return self.result == ALLOW


class PolicyDenied(Exception):
    def __init__(self, decision, what):
        super().__init__(f"{decision.result}: {decision.reason} ({what})")
        self.decision = decision


def normalize_url(url):
    """Lowercase scheme and host and drop a default port; used for the repeat rule."""
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    port = parts.port
    netloc = host if port in (None, 443) else f"{host}:{port}"
    query = f"?{parts.query}" if parts.query else ""
    return f"{parts.scheme.lower()}://{netloc}{parts.path}{query}"


def check_request(method, url, headers=None):
    if method.upper() not in ALLOWED_METHODS:
        return Decision(DENY, f"method {method} not allowed")
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        return Decision(DENY, "malformed URL")
    if parts.scheme.lower() != "https":
        return Decision(DENY, f"scheme {parts.scheme!r} not allowed")
    if parts.username is not None or parts.password is not None:
        return Decision(DENY, "credentials in URL")
    for name in (headers or {}):
        if name.lower() in CREDENTIAL_HEADERS:
            return Decision(DENY, f"credential header {name}")
    host = (parts.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        return Decision(DENY, f"host {host!r} not allowed")
    if port not in (None, 443):
        return Decision(DENY, f"port {port} not allowed")
    if "apply" in [seg.lower() for seg in parts.path.split("/")]:
        return Decision(DENY, "apply path")
    return Decision(ALLOW, "allowed host, https, GET")


def check_action(name):
    if name.lower() in FORBIDDEN_ACTIONS:
        return Decision(DENY, f"forbidden action {name}")
    return Decision(ALLOW, f"action {name}")


def _resolve(base, path):
    """Absolute, symlink-resolved path, or None if the path is unusable."""
    if "\0" in str(path):
        return None
    joined = os.path.join(base, path)  # an absolute `path` replaces base, as intended
    return os.path.realpath(joined)


def _inside(base, target, roots):
    for root in roots:
        root_real = os.path.realpath(os.path.join(base, root))
        if os.path.commonpath([root_real, target]) == root_real:
            return True
    return False


def check_read(base, path):
    target = _resolve(base, path)
    if target is None:
        return Decision(DENY, "invalid path")
    if _inside(base, target, READ_ROOTS):
        return Decision(ALLOW, "inside read roots")
    return Decision(DENY, "outside read roots")


def check_write(base, path, approved=False):
    target = _resolve(base, path)
    if target is None:
        return Decision(DENY, "invalid path")
    if _inside(base, target, WRITE_ROOTS):
        return Decision(ALLOW, "inside write root")
    if _inside(base, target, APPROVAL_WRITE_ROOTS):
        if approved:
            return Decision(ALLOW, "approved config write")
        return Decision(NEEDS_APPROVAL, "config write needs approval")
    return Decision(DENY, "outside write root")


def check_delete(base, path, approved=False):
    target = _resolve(base, path)
    if target is None:
        return Decision(DENY, "invalid path")
    if _inside(base, target, APPROVAL_DELETE_ROOTS):
        if approved:
            return Decision(ALLOW, "approved baseline reset")
        return Decision(NEEDS_APPROVAL, "baseline reset needs approval")
    if _inside(base, target, WRITE_ROOTS):
        return Decision(ALLOW, "inside write root")
    return Decision(DENY, "outside write root")


def guarded_write(base, path, data, approved=False):
    decision = check_write(base, path, approved=approved)
    if not decision.allowed:
        raise PolicyDenied(decision, f"write {path}")
    target = _resolve(base, path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    mode = "wb" if isinstance(data, bytes) else "w"
    with open(target, mode) as f:
        f.write(data)
    return target


def guarded_read(base, path, binary=False):
    decision = check_read(base, path)
    if not decision.allowed:
        raise PolicyDenied(decision, f"read {path}")
    with open(_resolve(base, path), "rb" if binary else "r") as f:
        return f.read()
