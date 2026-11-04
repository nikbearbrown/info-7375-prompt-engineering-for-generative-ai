"""The only network access in this codebase. Allow-listed, HTTPS only, and
redirects off the allow-list are refused (urllib would otherwise follow them)."""
import re
import urllib.request
from urllib.parse import urlparse

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})
TIMEOUT_S = 30


class HostNotAllowed(PermissionError):
    pass


def check_url(url):
    u = urlparse(url)
    if u.scheme != "https" or u.hostname not in ALLOWED_HOSTS:
        raise HostNotAllowed(f"refusing to fetch {url!r}: host not on allow-list {sorted(ALLOWED_HOSTS)}")
    return url


class _AllowListRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_opener = urllib.request.build_opener(_AllowListRedirects)


def board_jobs_url(board):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", board):
        raise ValueError(f"invalid board token {board!r}")
    # content=true: without it the list endpoint returns titles only, and the
    # rule (CONTRACT.md) checks title OR content.
    return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


def fetch(url):
    """Return the raw response bytes."""
    check_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": "js1-contract-and-watch (INFO7375 coursework)"})
    with _opener.open(req, timeout=TIMEOUT_S) as resp:
        check_url(resp.geturl())
        return resp.read()
