"""The only code in the loop path that touches the network or disk: GATE.md sections 3 and 5.

Exactly three tools:
    fetch_json(url)
    read_file(path)
    write_file(path, data, approval=None, mode="replace")

Each calls Policy.check() first. A denial is recorded as an event and raised. fetch_json
returns the raw response (status, headers, bytes); providers check the content-type and parse.
The repeat rule (GATE.md section 3) is enforced here, so a wrong retry in the loop is refused.
"""
import hashlib
import json
import os
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from jobwatch import policy as policy_mod

USER_AGENT = "jobwatch/2 (INFO 7375 coursework; read-only)"
BOOKKEEPING = ("trace.jsonl", "manifest.json", "summary.json")
APPEND_ONLY = "trace.jsonl"


class PolicyDenied(Exception):
    def __init__(self, decision):
        super().__init__(f"{decision.kind} denied: {decision.target}: {decision.reason}")
        self.decision = decision


class ApprovalDenied(Exception):
    def __init__(self, decision):
        super().__init__(f"approval denied: {decision.kind} {decision.target}: {decision.reason}")
        self.decision = decision


class RepeatRefused(Exception):
    def __init__(self, action):
        super().__init__(f"repeat refused: {action}")
        self.action = action


@dataclass
class FetchResult:
    url: str
    status: int | None
    headers: dict = field(default_factory=dict)
    body: bytes = b""
    error: str | None = None

    @property
    def content_type(self):
        return self.headers.get("content-type")

    @property
    def sha256(self):
        return hashlib.sha256(self.body).hexdigest()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never follow a redirect; urllib then raises HTTPError for the 3xx (GATE.md section 5, W04)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


REDIRECT_HANDLER = NoRedirect


def build_transport(extra_handlers=()):
    """An opener with no proxy from the environment and redirects refused."""
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), REDIRECT_HANDLER(), *extra_handlers)


def canonical_url(url):
    """Lowercase scheme and host, no default port, sorted query, no fragment (GATE.md section 3)."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    try:
        port = p.port
    except ValueError:
        port = None
    netloc = host if port in (None, 443) else f"{host}:{port}"
    query = urlencode(sorted(parse_qsl(p.query, keep_blank_values=True)))
    return urlunsplit((p.scheme.lower(), netloc, p.path, query, ""))


def _media_type(content_type):
    return (content_type or "").split(";")[0].strip().lower()


def retry_is_sound(result):
    """Tools' own reading of GATE.md section 4: retry only a timeout, connection error, 5xx or non-JSON 200."""
    if result.error is not None:
        return True
    if result.status is not None and result.status >= 500:
        return True
    if result.status == 200:
        if _media_type(result.content_type) != "application/json":
            return True
        try:
            json.loads(result.body)
        except ValueError:
            return True
    return False


def _headers(msg):
    if msg is None:
        return {}
    return {k.lower(): v for k, v in msg.items()}


def _utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class Tools:
    def __init__(self, policy, *, transport=None, timeout=10, max_retries=1, approver=None,
                 on_event=None, wall_clock=_utc_now):
        self.policy = policy
        self.transport = transport if transport is not None else build_transport()
        self.timeout = timeout
        self.max_retries = max_retries
        self.approver = approver
        self.on_event = on_event
        self.wall_clock = wall_clock
        self.needs_deepak = False
        self.requests_sent = []
        self._fetches = {}
        self._writes = set()

    # --- events -----------------------------------------------------------------------------
    def _event(self, tool, args, decision, outcome, **extra):
        ev = {"ts": self.wall_clock(), "tool": tool, "args": args,
              "policy": decision.decision if decision else None,
              "policy_reason": decision.reason if decision else None,
              "http_status": None, "bytes": None, "sha256": None, "outcome": outcome}
        ev.update(extra)
        if self.on_event is not None:
            self.on_event(ev)
        return ev

    # --- tool 1 -----------------------------------------------------------------------------
    def fetch_json(self, url):
        args = {"url": url, "method": "GET"}
        decision = self.policy.check("fetch", url, method="GET")
        if not decision.allowed:
            self._event("fetch_json", args, decision, "denied")
            raise PolicyDenied(decision)
        action = ("fetch_json", "GET", canonical_url(url))
        previous = self._fetches.setdefault(action, [])
        if previous and (len(previous) > self.max_retries or not retry_is_sound(previous[-1])):
            self._event("fetch_json", args, decision, "REPEAT")
            raise RepeatRefused(action)
        result = self._send(url)
        previous.append(result)
        self._event("fetch_json", args, decision,
                    "error:" + result.error if result.error else "response",
                    http_status=result.status,
                    bytes=len(result.body) if result.error is None else None,
                    sha256=result.sha256 if result.error is None else None)
        return result

    def _send(self, url):
        request = urllib.request.Request(
            url, method="GET", headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        self.requests_sent.append(url)
        try:
            with self.transport.open(request, timeout=self.timeout) as resp:
                return FetchResult(url, resp.status, _headers(resp.headers), resp.read())
        except urllib.error.HTTPError as e:
            try:
                body = e.read() or b""
            except (OSError, AttributeError):
                body = b""
            return FetchResult(url, e.code, _headers(e.headers), body)
        except (TimeoutError, socket.timeout):
            return FetchResult(url, None, error="timeout")
        except urllib.error.URLError as e:
            kind = "timeout" if isinstance(e.reason, (TimeoutError, socket.timeout)) else "connection"
            return FetchResult(url, None, error=kind)
        except OSError:
            return FetchResult(url, None, error="connection")

    # --- tool 2 -----------------------------------------------------------------------------
    def read_file(self, path):
        args = {"path": str(path)}
        decision = self.policy.check("read", str(path))
        if not decision.allowed:
            self._event("read_file", args, decision, "denied")
            raise PolicyDenied(decision)
        real = policy_mod.resolve(str(path), self.policy.root)
        try:
            with open(real, "rb") as f:
                data = f.read()
        except FileNotFoundError:
            self._event("read_file", args, decision, "missing")
            raise
        except OSError as e:
            self._event("read_file", args, decision, f"error:{type(e).__name__}")
            raise
        self._event("read_file", args, decision, "read", bytes=len(data),
                    sha256=hashlib.sha256(data).hexdigest())
        return data

    # --- tool 3 -----------------------------------------------------------------------------
    def write_file(self, path, data, approval=None, mode="replace"):
        path = str(path)
        data = data.encode("utf-8") if isinstance(data, str) else data
        name = os.path.basename(path)
        bookkeeping = name in BOOKKEEPING or self._is_state_file(path)
        args = {"path": path, "mode": mode}
        decision = self.policy.check("write", path)

        if mode not in ("replace", "append") or (mode == "append" and name != APPEND_ONLY):
            self._event("write_file", args, decision, "denied: mode")
            raise PolicyDenied(policy_mod.Decision(policy_mod.DENY, "write", path,
                                                   'mode="append" is only for trace.jsonl'))
        if decision.decision == policy_mod.NEEDS_APPROVAL:
            approver = approval if approval is not None else self.approver
            approved = approver is not None and approver(f"write {path} ({decision.reason})") is True
            if not approved:
                self.needs_deepak = True
                if name != APPEND_ONLY:
                    self._event("write_file", args, decision, "approval denied")
                raise ApprovalDenied(decision)
        elif not decision.allowed:
            if name != APPEND_ONLY:
                self._event("write_file", args, decision, "denied")
            raise PolicyDenied(decision)

        real = policy_mod.resolve(path, self.policy.root)
        if not bookkeeping:
            if real in self._writes:
                self._event("write_file", args, decision, "REPEAT")
                raise RepeatRefused(("write_file", real))
            self._writes.add(real)

        os.makedirs(os.path.dirname(real), exist_ok=True)
        if mode == "append":
            with open(real, "ab") as f:
                f.write(data)
            return
        tmp = os.path.join(os.path.dirname(real), f".{name}.tmp")
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, real)
        if self._is_state_file(path):
            self.policy.consume_state_commit()
        self._event("write_file", args, decision, "written", bytes=len(data),
                    sha256=hashlib.sha256(data).hexdigest())

    def _is_state_file(self, path):
        return policy_mod.resolve(path, self.policy.root) == policy_mod.resolve(policy_mod.STATE_FILE, self.policy.root)
