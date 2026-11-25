"""Permission policy, enforced in code. INHERITED from my JS2 watcher/policy.py (GATE section 5), adapted for JS3:
the same exact-host allow-list, GET only, HTTPS only, no apply/login/message paths; Greenhouse now asks for
?content=true (full posting text, FILTER.md section 3). Writes are allowed only in data/, out/ and transcripts/."""
import os, re
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

class Blocked(Exception): """The policy refuses this action."""

ALLOWED_HOSTS = {"boards-api.greenhouse.io", "api.lever.co"}
ALLOWED_PATHS = [re.compile(r"^/v1/boards/[A-Za-z0-9_-]+/jobs$"), re.compile(r"^/v0/postings/[A-Za-z0-9_-]+$")]
ALLOWED_QUERY = {"content": {"true"}, "mode": {"json"}}
WRITE_DIRS = ("data", "out", "transcripts")

class Policy:
    def __init__(self, base_dir="."):
        self.base = Path(base_dir).resolve()

    def check_request(self, method, url):
        if method != "GET": raise Blocked(f"method {method} refused: only GET (read-only) is allowed")
        try: u = urlsplit(url); port = u.port
        except ValueError as e: raise Blocked(f"malformed URL refused: {e}")
        if u.scheme != "https": raise Blocked(f"scheme {u.scheme!r} refused: HTTPS only")
        if u.username is not None or u.password is not None or "@" in u.netloc:
            raise Blocked(f"credentials in URL refused; real host is {u.hostname}")
        if u.hostname not in ALLOWED_HOSTS: raise Blocked(f"host {u.hostname} is not on the allow-list")
        if port not in (None, 443): raise Blocked(f"port {port} refused")
        if not any(p.match(u.path) for p in ALLOWED_PATHS):
            if re.search(r"/(applications?|apply|login|signin|messages?|email)\b", u.path):
                raise Blocked(f"path {u.path} refused: the agent never applies, messages, emails or logs in")
            raise Blocked(f"path {u.path} refused: not a public job-list endpoint")
        for k, vs in parse_qs(u.query).items():
            if k not in ALLOWED_QUERY or not set(vs) <= ALLOWED_QUERY[k]: raise Blocked(f"query {k}={vs} refused")

    def check_write(self, path):
        real = Path(os.path.realpath(path))
        for d in WRITE_DIRS:
            root = self.base / d
            if not root.is_symlink() and os.path.commonpath([str(real), str(root)]) == str(root) and real != root:
                return real
        raise Blocked(f"write to {path} refused: resolves to {real}, outside {', '.join(WRITE_DIRS)}/")
