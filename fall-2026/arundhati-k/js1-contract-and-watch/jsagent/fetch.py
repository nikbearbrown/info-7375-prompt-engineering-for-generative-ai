"""Allow-listed, read-only fetch of one public Greenhouse board (CONTRACT §2, §4)."""

import re
import urllib.request
from urllib.parse import urlsplit

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})
BOARD_SLUG = re.compile(r"^[a-z0-9-]{1,64}$")
USER_AGENT = "js1-contract-and-watch/1.0 (INFO 7375 coursework; read-only)"


class HostNotAllowed(Exception):
    """Raised for any URL (including a redirect target) off the allow-list."""


def check_url(url):
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise HostNotAllowed(f"refused: scheme {parts.scheme!r} is not https ({url})")
    if parts.hostname not in ALLOWED_HOSTS:
        raise HostNotAllowed(f"refused: host {parts.hostname!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")
    if parts.username or parts.password:
        raise HostNotAllowed("refused: credentials in URL")
    return url


def board_url(board):
    if not BOARD_SLUG.match(board):
        raise ValueError(f"board name must match {BOARD_SLUG.pattern}: {board!r}")
    return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


class AllowListRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follows a redirect only if its target is itself on the allow-list."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def build_opener():
    return urllib.request.build_opener(AllowListRedirectHandler())


def fetch(url, opener=None, timeout=30):
    """GET only. Returns the raw response bytes exactly as received."""
    check_url(url)
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    opener = opener or build_opener()
    with opener.open(request, timeout=timeout) as response:
        check_url(response.geturl())
        return response.read()
