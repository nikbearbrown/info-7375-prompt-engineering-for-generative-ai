"""The only door to the network (CONTRACT.md, In; Refuses 1 and 4; GATE.md, Permission policy).

get() is layer 1's single GET of the OpenAI board, checked by the allow-list. get_board() is the
loop's GET of one board, checked by the permission policy (host, path, query and method). Both
check before any connection opens, refuse redirects instead of following them, and ignore proxy
settings from the environment, so the program never talks to a host that was not checked.
tests/test_network_door.py fails if any other module of job_agent imports a networking library.
"""

from __future__ import annotations

import http.client
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

from . import allowlist, gate, policy
from .errors import BoardNoAnswer, Redirected, Refused

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


# Layer 2 (GATE.md): one board's GET for the loop.

BOARD_USER_AGENT = ("job-search-agent/0.2 (student course project; reads public job boards, never applies)")


class RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """A board that answers with a redirect is unverified (GATE.md, Error policy): the redirect is not followed."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Redirected(f"the board answered {code} with a redirect to {newurl!r}; redirects are not followed")


def board_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), RefuseRedirects())


def get_board(url: str, timeout: float = gate.REQUEST_TIMEOUT, opener=None, monotonic=time.monotonic) -> Response:
    """GET one board URL that the policy allows, and return the answer as received, whatever its status.

    Raises Refused (checked before any connection), Redirected, or BoardNoAnswer with `transient` set
    for a timeout, a dropped or refused connection and a DNS failure (GATE.md, Error policy).
    """
    checked = policy.check_request("GET", url)  # raises Refused before anything else happens
    request = urllib.request.Request(
        checked, headers={"User-Agent": BOARD_USER_AGENT, "Accept": "application/json"}, method="GET")
    if request.host not in policy.HOSTS:  # urllib's own reading of the host must agree
        raise Refused(f"refused: urllib reads the host of {checked!r} as {request.host!r}")
    opener = opener if opener is not None else board_opener()
    deadline = monotonic() + timeout
    try:
        reply = opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as error_reply:  # 4xx or 5xx: an answer arrived, so it is kept
        reply = error_reply
    except (OSError, http.client.HTTPException) as exc:
        raise BoardNoAnswer(f"no answer from the board ({_why(exc)})", transient=_transient(exc)) from None
    status = reply.code if isinstance(reply, urllib.error.HTTPError) else reply.status
    try:
        with reply:
            body = _read_by(reply, deadline, timeout, monotonic)
    except BoardNoAnswer:
        raise
    except (OSError, http.client.HTTPException) as exc:  # the answer broke off partway
        raise BoardNoAnswer(f"no answer from the board ({_why(exc)})", transient=_transient(exc)) from None
    return _response(checked, status, reply.headers, body)


def _read_by(reply, deadline: float, timeout: float, monotonic) -> bytes:
    """The whole body, unless it takes longer than one request may take (GATE.md, Budgets)."""
    chunks = []
    while True:
        if monotonic() > deadline:
            raise BoardNoAnswer(f"no answer from the board (the answer took longer than {timeout:g} s)",
                                transient=True)
        chunk = reply.read(1 << 16)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


def _why(exc) -> str:
    reason = getattr(exc, "reason", None)
    shown = reason if reason is not None else exc
    return f"{type(shown).__name__}: {shown}"


def _transient(exc) -> bool:
    """A timeout, a dropped or refused connection, or a DNS failure. Anything else (a TLS failure) is not."""
    reason = exc.reason if isinstance(exc, urllib.error.URLError) else exc
    if isinstance(reason, (TimeoutError, ConnectionError, http.client.IncompleteRead)):
        return True
    return type(reason).__name__ in ("timeout", "gaierror")  # socket.timeout (Python 3.9) and DNS failures
