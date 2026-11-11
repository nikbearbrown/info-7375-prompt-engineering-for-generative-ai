"""The only network access the agent has: one GET to an allow-listed host."""

import urllib.parse
import urllib.request

ALLOWED_HOSTS = {"boards-api.greenhouse.io"}


class HostNotAllowed(PermissionError):
    pass


def board_url(board):
    if not board.replace("-", "").isalnum():
        raise ValueError(f"bad board token: {board!r}")
    return (f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
            "?content=true")


def check_allowed(url):
    """Raise unless url is https on an allow-listed host. Runs before any
    network call."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS:
        raise HostNotAllowed(f"refusing to fetch {url!r}: host "
                             f"{parts.hostname!r} is not on the allow-list")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    # A redirect could leave the allow-list, so redirects are refused too.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_allowed(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get(url, timeout=60):
    """Return the raw response bytes."""
    check_allowed(url)
    opener = urllib.request.build_opener(_NoRedirect)
    req = urllib.request.Request(url, headers={
        "User-Agent": "INFO7375-js1-watch (student project; read-only)"})
    with opener.open(req, timeout=timeout) as resp:
        return resp.read()
