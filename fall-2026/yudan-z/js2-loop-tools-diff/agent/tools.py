"""The agent's only tools: fetch, read, write. Each call passes the policy (GATE §6), the budget (§3)
and the repeat rule (§4), and leaves one observation in the trace."""
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from agent.policy import Refused


class FetchFailed(Exception):
    def __init__(self, url, kind, status=None, detail=""):
        super().__init__(f"{kind} {status or ''} {url} {detail}".strip())
        self.url, self.kind, self.status, self.detail = url, kind, status, detail

    @property
    def transient(self):
        """GATE §5: timeouts, connection errors, 5xx and 429 may pass; 404 and other 4xx will not."""
        return self.kind in ("timeout", "connection") or (self.status is not None and
                                                         (self.status >= 500 or self.status == 429))


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """GATE revision 2026-11-09: a redirect could lead to a host the policy never checked, so a 3xx
    comes back as an error status instead of being followed."""
    def redirect_request(self, *a, **k):
        return None


def http_get(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": "js2-loop-tools-diff (course assignment)"})
    try:
        with urllib.request.build_opener(_NoRedirect).open(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def normalise(url):
    u = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((u.scheme, (u.hostname or "").lower(), u.path.rstrip("/"), u.query, ""))


class Tools:
    def __init__(self, policy, budget, trace, fetcher=http_get, timeout=20):
        self.policy, self.budget, self.trace = policy, budget, trace
        self.fetcher, self.timeout = fetcher, timeout
        self.fetched, self.written = set(), set()

    def _log(self, tool, target, outcome, **detail):
        self.trace.append({"t": round(self.budget.elapsed(), 3), "tool": tool, "target": target,
                           "outcome": outcome, **detail})

    def fetch(self, url, retry=False):
        self.policy.check_tool("fetch")
        try:
            self.policy.check_fetch(url)
        except Refused as e:
            self._log("fetch", url, "refused", reason=str(e))
            raise
        key = normalise(url)
        if key in self.fetched and not retry:
            self._log("fetch", url, "repeat-refused")
            raise Refused(f"refused: {url} was already fetched in this run (GATE §4)")
        self.budget.take_request()                 # raises BudgetExhausted before the request is made
        self.fetched.add(key)
        try:
            status, body = self.fetcher(url, self.timeout)
        except (TimeoutError, OSError) as e:
            kind = "timeout" if isinstance(e, TimeoutError) or "timed out" in str(e) else "connection"
            self._log("fetch", url, kind, retry=retry, detail=str(e)[:200])
            raise FetchFailed(url, kind, detail=str(e)[:200])
        self._log("fetch", url, f"http-{status}", retry=retry, bytes=len(body))
        if status != 200:
            raise FetchFailed(url, "http", status)
        return body

    def read_bytes(self, path):
        self.policy.check_tool("read")
        real = self.policy.check_read(path)
        with open(real, "rb") as f:
            data = f.read()
        self._log("read", path, "ok", bytes=len(data))
        return data

    def write_new(self, path, data):
        """Create a file that must not exist yet (evidence, traces, reports)."""
        self.policy.check_tool("write")
        try:
            real = self.policy.check_write(path)
            if os.path.exists(real) or real in self.written:
                raise Refused(f"refused: {path} exists; replacing it needs --approve replace-evidence:... (GATE §4, §6)")
        except Refused as e:
            self._log("write", path, "refused", reason=str(e))
            raise
        os.makedirs(os.path.dirname(real), exist_ok=True)
        with open(real, "xb") as f:
            f.write(data)
        self.written.add(real)
        self._log("write", path, "ok", bytes=len(data))
        return real

    def write_state(self, path, data):
        """Update a board's own seen-id list (an ordinary write inside runs/)."""
        self.policy.check_tool("write")
        try:
            real = self.policy.check_write(path)
        except Refused as e:
            self._log("write", path, "refused", reason=str(e))
            raise
        os.makedirs(os.path.dirname(real), exist_ok=True)
        tmp = real + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, real)
        self._log("write", path, "ok", bytes=len(data))
        return real

    def reset_state(self, path, key):
        self.policy.check_tool("write")
        try:
            real = self.policy.check_write(path, action="reset-state", approval_key=key)
        except Refused as e:
            self._log("write", path, "needs-approval", reason=str(e))
            raise
        if os.path.exists(real):
            os.remove(real)
        self._log("write", path, "reset", approval=key)


def now():
    return time.monotonic()
