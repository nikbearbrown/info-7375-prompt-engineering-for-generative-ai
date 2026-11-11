"""Permission policy, enforced in code (GATE.md section 5). Nothing here is a prompt: every network call and every file
write the agent makes goes through these checks first. (watch.py reads its own boards.json config directly; that read is
the operator's input, not an agent action.)"""
import os, re
from pathlib import Path
from urllib.parse import urlsplit

class Blocked(Exception): """The policy refuses this action."""
class NeedsApproval(Exception): """Allowed only after the person running the agent approves this specific action."""

ALLOWED_HOSTS = {"boards-api.greenhouse.io", "api.lever.co"}          # GATE 5a: exact match only
ALLOWED_PATHS = [re.compile(r"^/v1/boards/[A-Za-z0-9_-]+/jobs$"),     # Greenhouse public job list
                 re.compile(r"^/v0/postings/[A-Za-z0-9_-]+$")]        # Lever public postings
REPORT_DIR = "reports/job-watch"                                       # GATE 5c

class Policy:
    def __init__(self, base_dir="."):
        self.base = Path(base_dir).resolve()
        self.root = self.base / REPORT_DIR                                 # lexical: NOT resolved, so a symlinked folder can't move it

    # ---- network (GATE 5a, 5b) ----
    def check_request(self, method, url):
        if method != "GET":
            raise Blocked(f"method {method} refused: only GET (read-only) is allowed")
        try:
            u = urlsplit(url); port = u.port
        except ValueError as e:
            raise Blocked(f"malformed URL refused: {e}")
        if u.scheme != "https":
            raise Blocked(f"scheme {u.scheme!r} refused: HTTPS only")
        if u.username is not None or u.password is not None or "@" in u.netloc:
            raise Blocked(f"credentials in URL refused; real host is {u.hostname}")
        if u.hostname not in ALLOWED_HOSTS:
            raise Blocked(f"host {u.hostname} is not on the allow-list")
        if port not in (None, 443):
            raise Blocked(f"port {port} refused")
        if not any(p.match(u.path) for p in ALLOWED_PATHS):
            if re.search(r"/(applications?|apply|login|signin|messages?|email)\b", u.path):
                raise Blocked(f"path {u.path} refused: the agent never applies, messages, emails or logs in")
            raise Blocked(f"path {u.path} refused: not a public job-list endpoint")

    # ---- files (GATE 5, 5c) ----
    def _root_ok(self):
        # the report folder itself (and reports/) must be real folders inside the project, not symlinks pointing elsewhere
        for d in (self.base / "reports", self.root):
            if d.is_symlink(): return False
        return Path(os.path.realpath(self.root)) == self.root

    def _inside(self, path):
        real = Path(os.path.realpath(path))                            # resolves .. and symlinks
        inside = self._root_ok() and os.path.commonpath([str(real), str(self.root)]) == str(self.root)
        return real, inside

    def check_write(self, path, approved=False):
        """approved: True (this call's file only) or the path of the one file you approved."""
        real, inside = self._inside(path)
        if not inside:
            raise Blocked(f"write to {path} refused: resolves to {real}, outside {REPORT_DIR}/ (or {REPORT_DIR}/ is a symlink)")
        if real == self.root or real.is_dir():
            raise Blocked(f"write to {path} refused: it is a folder, not a report file")
        if real.exists():
            ok = approved is True or (approved not in (None, False) and Path(os.path.realpath(approved)) == real)
            if not ok: raise NeedsApproval(f"{real} already exists: overwriting needs your approval for this file")
        return real

    def check_read(self, path):
        real, inside = self._inside(path)
        if not inside:
            raise Blocked(f"read of {path} refused: outside {REPORT_DIR}/")
        return real

    def check_delete(self, path):
        raise Blocked(f"delete of {path} refused: the agent never deletes files")
