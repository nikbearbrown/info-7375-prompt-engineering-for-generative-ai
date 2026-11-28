"""HTTPS GET with a deadline for the whole response (GATE.md 'Budgets').

http.client never follows redirects, so a 3xx comes back to the caller unchanged (GATE.md
refuses redirects; the student decided a redirect leaves the board unverified). The
permission policy is checked by the caller, jobwatch/loop.py, before this is reached."""

import http.client
import time
from dataclasses import dataclass
from urllib.parse import urlsplit

USER_AGENT = "jobwatch/0.2 (INFO 7375 course project; read-only public job board client)"
CHUNK_BYTES = 64 * 1024


@dataclass(frozen=True)
class Response:
    status: int
    body: bytes
    content_type: str
    location: str | None


class Timeout(Exception):
    """The full response had not arrived by the deadline."""


class ConnectionFailed(Exception):
    """No HTTP response: the connection or the protocol failed."""


def _time_left(deadline, clock, sock):
    """Seconds left before the deadline; the socket is told to wait no longer than that."""
    remaining = deadline - clock()
    if remaining <= 0:
        raise Timeout("the full response had not arrived by the deadline")
    if sock is not None:
        try:
            sock.settimeout(remaining)
        except OSError:
            pass
    return remaining


def https_get(url, deadline, *, clock=time.monotonic, connection_factory=None):
    """One GET. `deadline` is a clock() value. Every receive is bounded by the time left
    and the body is read one receive at a time (read1), so a body that trickles in or
    stalls is abandoned with Timeout at the deadline, not after it."""
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname:
        raise ValueError(f"not an https URL: {url}")
    factory = connection_factory or http.client.HTTPSConnection
    remaining = deadline - clock()
    if remaining <= 0:
        raise Timeout("the deadline had passed before the request started")
    target = parts.path + (f"?{parts.query}" if parts.query else "")
    try:
        connection = factory(parts.hostname, timeout=remaining)
    except OSError as error:
        raise ConnectionFailed(f"connection failed: {error}") from None
    response = None
    try:
        connection.request("GET", target, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
        # Keep our own reference: with "Connection: close", http.client drops connection.sock.
        sock = getattr(connection, "sock", None)
        _time_left(deadline, clock, sock)
        response = connection.getresponse()
        chunks = []
        while True:
            _time_left(deadline, clock, sock)
            chunk = response.read1(CHUNK_BYTES)
            if not chunk:
                break
            chunks.append(chunk)
    except TimeoutError:
        raise Timeout("the full response had not arrived by the deadline") from None
    except (OSError, http.client.HTTPException) as error:
        raise ConnectionFailed(f"connection failed: {error}") from None
    finally:
        if response is not None:
            response.close()
        connection.close()
    return Response(response.status, b"".join(chunks), response.getheader("Content-Type", "") or "",
                    response.getheader("Location"))
