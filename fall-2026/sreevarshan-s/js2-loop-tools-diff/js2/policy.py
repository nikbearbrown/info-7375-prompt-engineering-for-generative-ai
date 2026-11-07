"""Permission policy (GATE.md section 6), enforced in code.

Every decision is appended to DECISIONS and sent to the "js2.policy" logger.
allow_write returns True, False, or NEEDS_APPROVAL.
"""

import logging
import os
import time
from urllib.parse import urlsplit

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

ALLOWED_HOSTS = {"boards-api.greenhouse.io", "api.lever.co"}
ALLOWED_OUTPUT = os.path.join(PROJECT_ROOT, "output")
EVIDENCE_EXTENSIONS = {".json"}

NEEDS_APPROVAL = "needs_approval"

log = logging.getLogger("js2.policy")

DECISIONS = []


def _record(kind, target, decision, reason):
    entry = {
        "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "kind": kind,
        "target": target,
        "decision": decision,
        "reason": reason,
    }
    DECISIONS.append(entry)
    log.info("%s %s: %s (%s)", kind, decision, target, reason)
    return entry


def allow_request(url):
    """True only for https URLs whose host is on the allow-list."""
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if parts.scheme != "https":
        _record("request", url, "blocked", "scheme %r is not https" % parts.scheme)
        return False
    if host not in ALLOWED_HOSTS:
        _record("request", url, "blocked", "host %r is not on the allow-list" % host)
        return False
    _record("request", url, "allowed", "https and host %r is on the allow-list" % host)
    return True


def allow_write(path):
    """True, False, or NEEDS_APPROVAL for writing to path.

    The real path (symlinks and .. resolved) must sit strictly inside
    ALLOWED_OUTPUT. Overwriting an existing evidence file needs approval.
    """
    real = os.path.realpath(path)
    root = os.path.realpath(ALLOWED_OUTPUT)
    if not real.startswith(root + os.sep):
        _record("write", path, "blocked", "real path %s is outside %s" % (real, root))
        return False
    if os.path.lexists(real) and os.path.splitext(real)[1].lower() in EVIDENCE_EXTENSIONS:
        _record("write", path, NEEDS_APPROVAL, "would overwrite existing evidence file %s" % real)
        return NEEDS_APPROVAL
    _record("write", path, "allowed", "real path %s is inside %s" % (real, root))
    return True


def write_bytes(path, data):
    """Write data to path only if allow_write returns True.

    Returns the decision. Writes to the resolved path and refuses to follow
    a symlink created after the check.
    """
    decision = allow_write(path)
    if decision is not True:
        return decision
    real = os.path.realpath(path)
    os.makedirs(os.path.dirname(real), exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(real, flags, 0o644)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    return decision
