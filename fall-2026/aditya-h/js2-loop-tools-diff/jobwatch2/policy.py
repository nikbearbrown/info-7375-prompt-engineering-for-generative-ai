"""The permission policy from GATE.md, enforced in code. Every request, read, write and state reset is
asked here first; nothing in a prompt can widen it."""
import os
import pathlib
import re
import urllib.parse
from typing import NamedTuple

SLUG = r"[a-z0-9-]+"
ROUTES = {
    "boards-api.greenhouse.io": (re.compile(rf"^/v1/boards/{SLUG}/jobs$"), {"", "content=true"}),
    "api.ashbyhq.com": (re.compile(rf"^/posting-api/job-board/{SLUG}$"), {""}),
    "api.lever.co": (re.compile(rf"^/v0/postings/{SLUG}$"), {"mode=json"}),
}
CREDENTIAL_HEADERS = {"authorization", "cookie", "proxy-authorization"}


class Decision(NamedTuple):
    allowed: bool
    reason: str


ALLOW = Decision(True, "allowed")


def deny(reason):
    return Decision(False, reason)


class Policy:
    def __init__(self, root, approvals=()):
        self.root = pathlib.Path(os.path.realpath(root))
        self.runs = self.root / "runs"
        self.approvals = frozenset(approvals)
        self.sent = {}  # action key -> number of times sent this run

    # --- network -------------------------------------------------------------------------------
    @staticmethod
    def action_key(method, url):
        p = urllib.parse.urlsplit(url)
        return (method.upper(), p.hostname, p.path, p.query)

    def request(self, method, url, headers=None, retry=False):
        if method.upper() != "GET":
            return deny(f"method {method} not allowed: GET only (never apply, post or send)")
        p = urllib.parse.urlsplit(url)
        if p.scheme != "https":
            return deny(f"scheme {p.scheme!r} not allowed: https only")
        if p.hostname not in ROUTES or p.port is not None or p.username or p.password:
            return deny(f"host {p.netloc!r} not allowed: allow-list is {sorted(ROUTES)}")
        path_re, queries = ROUTES[p.hostname]
        if not path_re.match(p.path):
            return deny(f"path {p.path!r} is not a board listing on {p.hostname}")
        if p.query not in queries:
            return deny(f"query {p.query!r} not allowed on {p.hostname}")
        for h in headers or {}:
            if h.lower() in CREDENTIAL_HEADERS:
                return deny(f"credential header {h!r} not allowed (never log in)")
        n = self.sent.get(self.action_key(method, url), 0)
        if n == 1 and retry:
            return ALLOW  # the one sanctioned retry after a transient error
        if n >= 1:
            return deny("repeat-blocked: same action already taken this run")
        return ALLOW

    def record_request(self, method, url):
        k = self.action_key(method, url)
        self.sent[k] = self.sent.get(k, 0) + 1

    # --- files ---------------------------------------------------------------------------------
    def _resolve(self, path):
        p = pathlib.Path(path).expanduser()
        if not p.is_absolute():
            p = self.root / p
        return pathlib.Path(os.path.realpath(p))

    @staticmethod
    def _inside(child, parent):
        return os.path.commonpath([child, parent]) == str(parent)

    def read(self, path):
        if self._inside(self._resolve(path), self.root):
            return ALLOW
        return deny(f"read {path!r} is outside the assignment folder")

    def write(self, path):
        if self._inside(self._resolve(path), pathlib.Path(os.path.realpath(self.runs))):
            return ALLOW
        return deny(f"write {path!r} is outside runs/ (resolved {self._resolve(path)})")

    def reset(self, board_key):
        if board_key in self.approvals:
            return ALLOW
        return deny(f"needs-approval: resetting {board_key!r} requires --approve-reset {board_key}")
