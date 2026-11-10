"""The permission policy (GATE.md section 5). It only decides; agent/tools.py acts on "allow".

The policy never reads or writes a file. It looks at paths with os.path, and it parses
URLs with the same function the fetcher uses, so the two cannot disagree about a host.
"""

import os
import re

from agent.tools import split_url

# host -> (allowed path, allowed query parameters)
ALLOWED_PATHS = {
    "boards-api.greenhouse.io": (re.compile(r"/v1/boards/[A-Za-z0-9-]+/jobs"), {"content"}),
    "api.lever.co": (re.compile(r"/v0/postings/[A-Za-z0-9-]+"), {"mode"}),
    "api.ashbyhq.com": (re.compile(r"/posting-api/job-board/[A-Za-z0-9-]+"), set()),
}
READ_FOLDERS = ("config", "persona", "jobs", "fixtures")


class Decision:
    def __init__(self, outcome, reason, target=None):
        self.outcome, self.reason, self.target = outcome, reason, target

    @property
    def allowed(self):
        return self.outcome == "allow"

    def as_dict(self):
        return {"outcome": self.outcome, "reason": self.reason, "target": self.target}

    def __repr__(self):
        return "Decision(%r, %r)" % (self.outcome, self.reason)


def allow(reason, target=None):
    return Decision("allow", reason, target)


def refuse(reason, target=None):
    return Decision("refuse", reason, target)


def host_allowed(host):
    """The allow-listed host this is, or None. Exact match only (GATE.md W4)."""
    return host if host in ALLOWED_PATHS else None


def is_inside(root, path):
    """True if path, after resolving `..` and symbolic links, is root or inside it (GATE.md W1-W3).

    Containment is decided by path components (commonpath), not by comparing strings,
    so `jobs-evil` is not inside `jobs`.
    """
    real = os.path.realpath(path)
    return os.path.commonpath([root, real]) == root


class Policy:
    def __init__(self, root, approvals=()):
        self.root = os.path.realpath(root)
        self.jobs = os.path.join(self.root, "jobs")
        self.state = os.path.join(self.jobs, "state")
        self.approvals = frozenset(a.lower() for a in approvals)
        self.created = set()

    def check_fetch(self, method, url):
        if method != "GET":
            return refuse("method %s: GET only" % method, url)
        try:
            parts = split_url(url)
        except ValueError as error:
            return refuse("URL cannot be parsed (%s)" % error, url)
        if parts.scheme != "https":
            return refuse("scheme %r: HTTPS only" % parts.scheme, url)
        if parts.username is not None or parts.password is not None:
            return refuse("credentials in the URL", url)
        if parts.port not in (None, 443):
            return refuse("port %s: 443 only" % parts.port, url)
        host = host_allowed(parts.hostname)
        if host is None:
            return refuse("host %r is not on the allow-list" % parts.hostname, url)
        path_pattern, params = ALLOWED_PATHS[host]
        if not path_pattern.fullmatch(parts.path):
            return refuse("path %r is not a board listing on %s" % (parts.path, host), url)
        if parts.fragment:
            return refuse("fragment in the URL", url)
        if not set(parts.query_keys) <= params or len(parts.query_keys) != len(set(parts.query_keys)):
            return refuse("query parameters %s not allowed on %s" % (parts.query_keys, host), url)
        return allow("allow-listed board on %s" % host, url)

    def check_read(self, path):
        for folder in READ_FOLDERS:
            if is_inside(os.path.join(self.root, folder), path):
                return allow("read inside %s/" % folder, self.show(path))
        return refuse("read outside config/, persona/, jobs/ and fixtures/ of this folder", self.show(path))

    def check_write(self, path, kind="new", board=None, drops_ids=False):
        if kind == "state":
            if not is_inside(self.state, path):
                return refuse("state files are written in jobs/state/ only", self.show(path))
            if drops_ids:
                if (board or "").lower() in self.approvals:
                    return allow("state reset approved for %s by --approve-state-reset" % board, self.show(path))
                return Decision("needs_approval", "this write drops seen ids for %s: a reset needs "
                                "--approve-state-reset %s" % (board, board), self.show(path))
            return allow("state update that keeps every seen id", self.show(path))
        if not is_inside(self.jobs, path):
            return refuse("writes go inside jobs/ only", self.show(path))
        if kind == "append":
            if os.path.realpath(path) in self.created:
                return allow("append to a file this run created", self.show(path))
            return refuse("append only to a file this run created", self.show(path))
        if kind == "new":
            if os.path.lexists(path):
                return refuse("file exists: evidence is written once", self.show(path))
            return allow("new file inside jobs/", self.show(path))
        return refuse("unknown write kind %r" % kind, self.show(path))

    def show(self, path):
        """How a decision names a file: relative to this folder, so no absolute path (with my username) is written."""
        absolute = os.path.abspath(path)
        if os.path.commonpath([self.root, absolute]) == self.root:
            return os.path.relpath(absolute, self.root).replace(os.sep, "/")
        return "(outside this folder)/" + os.path.basename(absolute)

    def note_created(self, path):
        self.created.add(os.path.realpath(path))
