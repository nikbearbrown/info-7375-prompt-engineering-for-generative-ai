"""Boundary cases for the JS2 permission policy (BOUNDARY_TESTS.md). Predictions were written before the policy code existed.

File cases run in a throwaway project folder, never in the real repository.
"""
import os
import tempfile
import urllib.request
from pathlib import Path

GATE_HOSTS = {"boards-api.greenhouse.io", "api.lever.co"}
SAMSARA = "https://boards-api.greenhouse.io/v1/boards/samsara/jobs"


def _net(url, method="GET"):
    from jsagent import policy
    try:
        policy.check_url(url, GATE_HOSTS, method=method)
        return "allow"
    except policy.PolicyViolation:
        return "deny"


def _redirect(newurl):
    from jsagent import net, policy
    handler = net.PolicyRedirectHandler(GATE_HOSTS, 3, lambda url: None)
    try:
        handler.redirect_request(urllib.request.Request(SAMSARA), None, 302, "Found", {}, newurl)
        return "allow"
    except policy.PolicyViolation:
        return "deny"


class Sandbox:
    """proj/ with config/ and out/, plus outside/ next to it (the symlink target)."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name).resolve()
        self.proj = base / "proj"
        self.outside = base / "outside"
        for d in [self.proj / "config", self.proj / "out", self.outside]:
            d.mkdir(parents=True)
        (self.proj / "config" / "allowlist.json").write_text('{"hosts": []}')
        os.symlink(self.outside, self.proj / "out" / "link")

    def policy(self, approvals=()):
        from jsagent import policy
        return policy.FilePolicy(self.proj / "out", root=self.proj, approvals=approvals)

    def close(self):
        self._tmp.cleanup()


def _write(sb, rel, approvals=(), existing=False):
    from jsagent import policy
    path = sb.proj / rel
    if existing:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"first")
    try:
        sb.policy(approvals=[sb.proj / a for a in approvals]).check_write(path)
        return "allow"
    except policy.NeedsApproval:
        return "needs approval"
    except policy.PolicyViolation:
        return "deny"


def _read(sb, path):
    from jsagent import policy
    try:
        sb.policy().check_read(path)
        return "allow"
    except policy.PolicyViolation:
        return "deny"


def _out_root(sb, rel):
    from jsagent import policy
    try:
        policy.FilePolicy(sb.proj / rel, root=sb.proj)
        return "allow"
    except policy.PolicyViolation:
        return "deny"


RAW = "out/runs/r1/raw/x.json"

CASES = [
    ("B01", "GET host off the list (Ashby)", "deny", lambda sb: _net("https://api.ashbyhq.com/posting-api/job-board/kraken.com")),
    ("B02", "GET lookalike host", "deny", lambda sb: _net("https://boards-api.greenhouse.io.evil.com/v1/boards/samsara/jobs")),
    ("B03", "GET nonstandard port 8443", "deny", lambda sb: _net("https://boards-api.greenhouse.io:8443/v1/boards/samsara/jobs")),
    ("B04", "GET with user:pw@", "deny", lambda sb: _net("https://user:pw@boards-api.greenhouse.io/v1/boards/samsara/jobs")),
    ("B05", "GET plain http", "deny", lambda sb: _net("http://boards-api.greenhouse.io/v1/boards/samsara/jobs")),
    ("B06", "POST to an allowed host", "deny", lambda sb: _net(SAMSARA, method="POST")),
    ("B07", "redirect to a host off the list", "deny", lambda sb: _redirect("https://evil.example.com/")),
    ("B08", "write out/../config/allowlist.json", "deny", lambda sb: _write(sb, "out/../config/allowlist.json")),
    ("B09", "write out-evil/x.json", "deny", lambda sb: _write(sb, "out-evil/x.json")),
    ("B10", "write through a symlink out of out/", "deny", lambda sb: _write(sb, "out/link/x.json")),
    ("B11", "read config/allowlist.json", "allow", lambda sb: _read(sb, sb.proj / "config" / "allowlist.json")),
    ("B12", "write config/allowlist.json", "deny", lambda sb: _write(sb, "config/allowlist.json")),
    ("B13", "create a new raw file in out/", "allow", lambda sb: _write(sb, RAW)),
    ("B14", "overwrite an existing raw file, no approval", "needs approval", lambda sb: _write(sb, RAW, existing=True)),
    ("B15", "overwrite with --approve for that path", "allow", lambda sb: _write(sb, RAW, approvals=[RAW], existing=True)),
    ("B16", "--out config/", "deny", lambda sb: _out_root(sb, "config")),
    ("B17", "read ~/.ssh/id_rsa", "deny", lambda sb: _read(sb, Path.home() / ".ssh" / "id_rsa")),
    ("B18", "GET uppercase allowed host", "allow", lambda sb: _net("https://BOARDS-API.greenhouse.io/v1/boards/samsara/jobs")),
]


def run_case(fn):
    sb = Sandbox()
    try:
        return fn(sb)
    except Exception as e:  # an import error or crash is an outcome too, never a silent pass
        return f"error: {type(e).__name__}: {e}"[:120]
    finally:
        sb.close()
