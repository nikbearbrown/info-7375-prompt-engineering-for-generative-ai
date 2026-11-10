"""The permission policy in code: GATE.md section 5.

Every tool in jobwatch/tools.py calls Policy.check() before it touches the network or disk.
check() returns a Decision of ALLOW, DENY or NEEDS_APPROVAL. It never performs the action.

URLs are parsed with urllib.parse and hosts matched exactly. Paths are resolved with
os.path.realpath and contained with os.path.commonpath; no prefix comparison on strings.
"""
import ipaddress
import os
from dataclasses import dataclass
from urllib.parse import urlsplit

ALLOW = "ALLOW"
DENY = "DENY"
NEEDS_APPROVAL = "NEEDS_APPROVAL"

# GATE.md section 5, host table; section 0, host-to-system mapping.
HOST_SYSTEM = {
    "boards-api.greenhouse.io": "greenhouse",
    "api.lever.co": "lever",
    "api.eu.lever.co": "lever",
    "api.ashbyhq.com": "ashby",
}
ALLOWED_METHODS = ("GET",)
READ_DIRS = ("config", "examples", "schema", "fixtures", "state", "runs")
STATE_FILE = os.path.join("state", "seen.json")
END_OF_RUN_EXITS = ("FINISHED", "INCOMPLETE")


@dataclass(frozen=True)
class Decision:
    decision: str
    kind: str
    target: str
    reason: str

    @property
    def allowed(self):
        return self.decision == ALLOW


@dataclass(frozen=True)
class UrlTarget:
    scheme: str
    has_userinfo: bool
    host: str
    port: int | None


def parse_url(url):
    """The parts of a URL the policy judges, from urllib.parse (GATE.md section 5, W03)."""
    parts = urlsplit(url)
    try:
        port = parts.port
    except ValueError:
        port = -1
    return UrlTarget(
        scheme=parts.scheme.lower(),
        has_userinfo=parts.username is not None or parts.password is not None or "@" in parts.netloc,
        host=(parts.hostname or "").lower(),
        port=port,
    )


def host_allowed(host):
    """Exact match against the allow-list (W02)."""
    return host in HOST_SYSTEM


def is_ip_literal(host):
    try:
        ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return False
    return True


def resolve(path, root):
    """Absolute, symlink-free path (W05)."""
    return os.path.realpath(os.path.join(root, path))


def is_within(path, base):
    """True when the resolved `path` is `base` or inside it (W01). Both already resolved."""
    try:
        return os.path.commonpath([path, base]) == base
    except ValueError:
        return False


class Policy:
    """GATE.md section 5. `root` is the assignment folder; `run_id` names the one writable run dir."""

    def __init__(self, root, run_id=None):
        self.root = os.path.realpath(root)
        self.run_id = run_id
        self._state_commit_armed = None

    # --- the end-of-run state replace (GATE.md sections 1 and 5) ---------------------------
    def arm_state_commit(self, exit_status):
        """Allow exactly one write to state/seen.json, only for FINISHED or INCOMPLETE."""
        self._state_commit_armed = exit_status if exit_status in END_OF_RUN_EXITS else None

    def consume_state_commit(self):
        self._state_commit_armed = None

    # --- the check ----------------------------------------------------------------------------
    def check(self, kind, target, *, method="GET"):
        if kind == "fetch":
            return self._check_fetch(target, method)
        if kind == "read":
            return self._check_read(target)
        if kind == "write":
            return self._check_write(target)
        return Decision(DENY, kind, str(target), f"unknown action kind {kind!r}")

    def _check_fetch(self, url, method):
        def deny(why):
            return Decision(DENY, "fetch", url, why)

        if method.upper() not in ALLOWED_METHODS:
            return deny(f"method {method} is not allowed; GET only")
        t = parse_url(url)
        if t.scheme != "https":
            return deny(f"scheme {t.scheme or '(none)'} is not allowed; https only")
        if t.has_userinfo:
            return deny("userinfo in the URL is not allowed")
        if t.port not in (None, 443):
            return deny(f"port {t.port} is not allowed; 443 only")
        if not t.host:
            return deny("no host")
        if is_ip_literal(t.host):
            return deny("IP-literal hosts are not allowed")
        if not host_allowed(t.host):
            return deny(f"host {t.host} is not on the allow-list")
        return Decision(ALLOW, "fetch", url, f"GET to allow-listed host {t.host}")

    def _dir(self, *parts):
        return os.path.realpath(os.path.join(self.root, *parts))

    def _check_read(self, path):
        real = resolve(path, self.root)
        for d in READ_DIRS:
            if is_within(real, self._dir(d)):
                return Decision(ALLOW, "read", path, f"read inside {d}/")
        return Decision(DENY, "read", path, "read outside config/, examples/, schema/, fixtures/, state/, runs/")

    def _check_write(self, path):
        real = resolve(path, self.root)
        if self.run_id and is_within(real, self._dir("runs", self.run_id)):
            return Decision(ALLOW, "write", path, f"write inside runs/{self.run_id}/")
        if real == self._dir(STATE_FILE) and self._state_commit_armed:
            return Decision(ALLOW, "write", path, f"end-of-run state replace ({self._state_commit_armed})")
        if is_within(real, self._dir("state")):
            return Decision(NEEDS_APPROVAL, "write", path, "state change outside the end-of-run replace")
        if is_within(real, self._dir("config")):
            return Decision(NEEDS_APPROVAL, "write", path, "write to config/")
        return Decision(DENY, "write", path, "write outside the current run directory")
