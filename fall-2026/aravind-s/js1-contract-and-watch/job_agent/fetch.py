"""The only door to the network (CONTRACT.md, In; Refuses 1 and 4).

One GET of the board URL. The allow-list is checked before any connection opens. Redirects are
refused, not followed, and proxy settings from the environment are ignored, so the program never
talks to a host that was not checked. tests/test_network_door.py fails if any other module of
job_agent imports a networking library.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

from . import allowlist
from .errors import Refused

USER_AGENT = "job-search-agent/0.1 (student course project; reads one public job board, never applies)"
TIMEOUT_SECONDS = 60
KEPT_HEADERS = ("Content-Type", "Content-Length", "Date", "Last-Modified", "ETag")


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    headers: dict
    body: bytes
    received_at: str  # UTC, ISO 8601


class NoRedirects(urllib.request.HTTPRedirectHandler):
    """A redirect could lead off the allow-list, so it ends the request."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Refused(f"refused: the server answered {code} with a redirect to {newurl!r}; redirects are not followed")


def build_opener() -> urllib.request.OpenerDirector:
    # ProxyHandler({}) replaces the default one, which would read HTTPS_PROXY from the environment.
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirects())


def get(url: str, opener=None) -> Response:
    """GET one allow-listed URL and return the response as received, whatever its status."""
    checked = allowlist.check(url)  # raises Refused before anything else happens
    request = urllib.request.Request(
        checked, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}, method="GET"
    )
    if request.host not in allowlist.ALLOWED_HOSTS:  # urllib's own reading of the host must agree
        raise Refused(f"refused: urllib reads the host of {checked!r} as {request.host!r}")
    opener = opener if opener is not None else build_opener()
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as reply:
            return _response(checked, reply.status, reply.headers, reply.read())
    except urllib.error.HTTPError as reply:  # 4xx or 5xx: a response arrived, so it is kept
        with reply:
            return _response(checked, reply.code, reply.headers, reply.read())


def _response(url: str, status: int, headers, body: bytes) -> Response:
    kept = {name: headers.get(name) for name in KEPT_HEADERS if headers.get(name) is not None}
    received = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return Response(url=url, status=int(status), headers=kept, body=bytes(body), received_at=received)
