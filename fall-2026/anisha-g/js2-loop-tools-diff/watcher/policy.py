"""Permission policy, enforced in code (GATE.md section 5). Nothing here is a prompt: every network call and every file
write in this program goes through these checks first."""
import os, re
from pathlib import Path
from urllib.parse import urlsplit

class Blocked(Exception): """The policy refuses this action."""
class NeedsApproval(Exception): """Allowed only after the person running the agent approves this specific action."""

ALLOWED_HOSTS = {"boards-api.greenhouse.io", "api.lever.co"}          # GATE 5a: exact match only
ALLOWED_PATHS = [re.compile(r"^/v1/boards/[a-z0-9-]+/jobs$"),          # Greenhouse public job list
                 re.compile(r"^/v0/postings/[a-z0-9-]+$")]             # Lever public postings
REPORT_DIR = "reports/job-watch"                                       # GATE 5c

class Policy:
    def __init__(self, base_dir="."):
        self.base = Path(base_dir).resolve()
        self.root = (self.base / REPORT_DIR).resolve()

    # ---- network (GATE 5a, 5b) ----
    def check_request(self, method, url):
        if method != "GET":
            raise Blocked(f"method {method} refused: only GET (read-only) is allowed")
        u = urlsplit(url)
        if u.scheme != "https":
            raise Blocked(f"scheme {u.scheme!r} refused: HTTPS only")
        if u.username is not None or u.password is not None or "@" in u.netloc:
            raise Blocked(f"credentials in URL refused; real host is {u.hostname}")
        if u.hostname not in ALLOWED_HOSTS:
            raise Blocked(f"host {u.hostname} is not on the allow-list")
        if u.port not in (None, 443):
            raise Blocked(f"port {u.port} refused")
        if not any(p.match(u.path) for p in ALLOWED_PATHS):
            raise Blocked(f"path {u.path} refused: only public job-list endpoints (never apply, message or log in)")

    # ---- files (GATE 5, 5c) ----
    def _inside(self, path):
        real = Path(os.path.realpath(path))                            # resolves .. and symlinks
        return real, os.path.commonpath([str(real), str(self.root)]) == str(self.root)

    def check_write(self, path, approved=False):
        real, inside = self._inside(path)
        if not inside:
            raise Blocked(f"write to {path} refused: resolves to {real}, outside {REPORT_DIR}/")
        if real.exists() and not approved:
            raise NeedsApproval(f"{real} already exists: overwriting needs your approval")
        return real

    def check_read(self, path):
        real, inside = self._inside(path)
        if not inside:
            raise Blocked(f"read of {path} refused: outside {REPORT_DIR}/")
        return real

    def check_delete(self, path):
        raise Blocked(f"delete of {path} refused: the agent never deletes files")
