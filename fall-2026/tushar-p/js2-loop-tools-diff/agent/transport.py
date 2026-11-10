"""Standard-library HTTP transport that never follows redirects (P10).

A transport is any callable (method, url, timeout) -> Response. send() is the only entry
point the agent uses: it runs policy.check_request() first, so a denied request never
reaches the transport and costs zero attempts.

The opener is assembled by hand rather than with urllib.request.build_opener(), so it has
no redirect follower, no proxy handler (environment proxies are ignored), and no handlers
for http, ftp, file, or data URLs. A 3xx comes back as a Response with is_redirect set;
no second request is made.

F12: each attempt has one monotonic deadline (start + the timeout the budget gives it).
The remaining time bounds the TCP connect, the TLS handshake and header read (as the socket
timeout), and every chunk of the body read. The system DNS lookup is the exception; see
DeadlineHTTPSConnection.
"""

import functools
import http.client
import socket
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

BODY_CHUNK_BYTES = 64 * 1024

# GATE v0.4: every request identifies the watch honestly; it never impersonates a browser.
AGENT_USER_AGENT = "info7375-js2-watch/0.1 (student project; tushar-js2@example.com)"

from .errors import TransportError, TransportTimeout
from .policy import check_request


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    headers: tuple[tuple[str, str], ...]
    body: bytes

    @property
    def is_redirect(self) -> bool:
        return 300 <= self.status < 400

    def header(self, name: str) -> str | None:
        wanted = name.lower()
        return next((value for key, value in self.headers if key.lower() == wanted), None)

    @property
    def location(self) -> str | None:
        return self.header("Location") if self.is_redirect else None


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Declines every redirect, so urllib raises HTTPError for the 3xx instead of following."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

    def http_error_302(self, req, fp, code, msg, headers):
        return None

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302


class DeadlineHTTPSConnection(http.client.HTTPSConnection):
    """HTTPSConnection whose TCP connect respects the handler's attempt deadline (F12).

    TLS wrapping (with hostname verification), the request, and the header read stay in
    http.client; only the address lookup and TCP connect are replaced.
    """

    def __init__(self, host, *, handler, **kwargs):
        super().__init__(host, **kwargs)
        self._handler = handler
        self._create_connection = self._connect_within_deadline

    def _remaining(self) -> float:
        if self._handler.deadline is None:
            return self.timeout
        return self._handler.deadline - self._handler.clock()

    def _connect_within_deadline(self, address, timeout=None, source_address=None):
        host, port = address
        # DNS: socket.getaddrinfo blocks in the system resolver and is NOT bounded by any
        # timeout the standard library offers. Its elapsed time still counts against the
        # attempt, so recheck the deadline when it returns and never continue an expired
        # attempt. (GATE F12; listed under "Not checked" at sign-off.)
        infos = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
        if self._remaining() <= 0:
            raise TimeoutError("attempt deadline passed during the DNS lookup")
        last_error = None
        for family, sock_type, proto, _, sockaddr in infos:
            remaining = self._remaining()
            if remaining <= 0:
                raise TimeoutError("attempt deadline passed while connecting")
            sock = socket.socket(family, sock_type, proto)
            try:
                sock.settimeout(remaining)
                if source_address:
                    sock.bind(source_address)
                sock.connect(sockaddr)
                return sock
            except OSError as err:
                sock.close()
                last_error = err
        raise last_error or OSError(f"getaddrinfo returned no addresses for {host}")

    def connect(self):
        super().connect()  # TCP via _connect_within_deadline, then TLS with the same timeout
        remaining = self._remaining()
        if remaining <= 0:
            raise TimeoutError("attempt deadline passed during the TLS handshake")
        self.sock.settimeout(remaining)  # request send and header read get the time left
        self._handler.socket = self.sock


class DeadlineHTTPSHandler(urllib.request.HTTPSHandler):
    """HTTPS handler that carries the current attempt's deadline into each connection."""

    def __init__(self, context=None, clock=time.monotonic):
        super().__init__(context=context or ssl.create_default_context())
        self.clock = clock
        self.deadline = None
        self.socket = None

    def begin_attempt(self, deadline: float) -> None:
        self.deadline = deadline
        self.socket = None

    def set_socket_timeout(self, seconds: float) -> None:
        """Best effort: bound the next body read to the time left in the attempt."""
        if self.socket is not None:
            try:
                self.socket.settimeout(max(seconds, 0.001))
            except OSError:
                pass

    def https_open(self, req):
        connection = functools.partial(DeadlineHTTPSConnection, handler=self)
        return self.do_open(connection, req, context=self._context)


def build_opener(https_handler=None) -> urllib.request.OpenerDirector:
    """An opener for HTTPS only, with certificate checks and no redirect following."""
    director = urllib.request.OpenerDirector()
    handlers = (
        urllib.request.UnknownHandler(),  # any scheme other than https fails here
        https_handler or DeadlineHTTPSHandler(),
        NoRedirectHandler(),
        urllib.request.HTTPDefaultErrorHandler(),
        urllib.request.HTTPErrorProcessor(),
    )
    for handler in handlers:
        director.add_handler(handler)
    return director


def _headers(message) -> tuple[tuple[str, str], ...]:
    return tuple(message.items()) if message is not None else ()


def read_body(stream, deadline: float, clock, set_timeout=None, chunk_bytes: int = BODY_CHUNK_BYTES) -> bytes:
    """Read a response body in chunks, never starting a chunk after the deadline (F12)."""
    chunks = []
    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            raise TransportTimeout("attempt deadline passed during the body read")
        if set_timeout is not None:
            set_timeout(remaining)
        chunk = stream.read(chunk_bytes)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


class UrllibTransport:
    def __init__(self, opener: urllib.request.OpenerDirector | None = None, clock=time.monotonic):
        self.clock = clock
        self._https = None
        if opener is None:
            self._https = DeadlineHTTPSHandler(clock=clock)
            opener = build_opener(https_handler=self._https)
        self.opener = opener

    def _read(self, stream, deadline: float) -> bytes:
        set_timeout = self._https.set_socket_timeout if self._https is not None else None
        try:
            return read_body(stream, deadline, self.clock, set_timeout)
        except TimeoutError:
            raise TransportTimeout("timed out during the body read") from None
        except (http.client.HTTPException, OSError) as err:
            raise TransportError(f"body read failed: {type(err).__name__}: {err}") from None

    def __call__(self, method: str, url: str, timeout: float) -> Response:
        deadline = self.clock() + timeout
        if self._https is not None:
            self._https.begin_attempt(deadline)
        # Set on the Request itself so urllib's default "Python-urllib/x.y" is never added.
        request = urllib.request.Request(url, method=method, headers={"User-Agent": AGENT_USER_AGENT})
        try:
            with self.opener.open(request, timeout=timeout) as response:
                if self.clock() >= deadline:
                    raise TransportTimeout(f"attempt deadline passed before the body: {url}")
                return Response(url, response.status, _headers(response.headers),
                                self._read(response, deadline))
        except urllib.error.HTTPError as err:  # 3xx, 4xx and 5xx all come back as a Response
            try:
                body = self._read(err, deadline) if err.fp is not None else b""
            finally:
                err.close()
            return Response(url, err.code, _headers(err.headers), body)
        except TransportError:
            raise
        except urllib.error.URLError as err:
            if isinstance(err.reason, TimeoutError):
                raise TransportTimeout(f"timed out: {url}: {err.reason}") from None
            raise TransportError(f"could not reach {url}: {err.reason}") from None
        except TimeoutError:
            raise TransportTimeout(f"timed out reading {url}") from None
        except (http.client.HTTPException, OSError) as err:
            raise TransportError(f"transport failure for {url}: {type(err).__name__}: {err}") from None


def send(board, method: str, url: str, *, transport, timeout: float) -> Response:
    """Check the request against policy, then make exactly one transport call."""
    check_request(method, url, board)
    return transport(method, url, timeout)
