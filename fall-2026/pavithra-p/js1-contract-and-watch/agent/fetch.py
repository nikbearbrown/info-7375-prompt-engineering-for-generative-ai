"""The only network code: one GET to an allow-listed host (CONTRACT.md, Refuses 1 and 3)."""
import urllib.parse
import urllib.request

from .config import ALLOWED_HOSTS


class RefusedHost(Exception):
    """Raised before any connection is made to a host that is not on the allow-list."""


def check_url(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS:
        raise RefusedHost(f"refused: {parts.hostname or url!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}")
    return url


class _AllowListRedirects(urllib.request.HTTPRedirectHandler):
    """A redirect is a new request, so it must pass the same allow-list."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, opener=None, timeout=30):
    """GET one allow-listed URL and return the response body unchanged. Never sends a body."""
    check_url(url)
    opener = opener or urllib.request.build_opener(_AllowListRedirects)
    request = urllib.request.Request(
        url, method="GET", headers={"User-Agent": "js1-contract-and-watch (INFO 7375 coursework)"}
    )
    with opener.open(request, timeout=timeout) as response:
        return response.read()
