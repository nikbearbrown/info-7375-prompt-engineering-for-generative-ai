"""Standard-library HTTP transport that never follows redirects (P10).

A transport is any callable (method, url, timeout) -> Response. send() is the only entry
point the agent uses: it runs policy.check_request() first, so a denied request never
reaches the transport and costs zero attempts.

The opener is assembled by hand rather than with urllib.request.build_opener(), so it has
no redirect follower, no proxy handler (environment proxies are ignored), and no handlers
for http, ftp, file, or data URLs. A 3xx comes back as a Response with is_redirect set;
no second request is made.

Not in build step 1: the F12 monotonic attempt deadline and chunked body read.
"""

import http.client
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass

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


def build_opener(https_handler=None) -> urllib.request.OpenerDirector:
    """An opener for HTTPS only, with certificate checks and no redirect following."""
    director = urllib.request.OpenerDirector()
    handlers = (
        urllib.request.UnknownHandler(),  # any scheme other than https fails here
        https_handler or urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        NoRedirectHandler(),
        urllib.request.HTTPDefaultErrorHandler(),
        urllib.request.HTTPErrorProcessor(),
    )
    for handler in handlers:
        director.add_handler(handler)
    return director


def _headers(message) -> tuple[tuple[str, str], ...]:
    return tuple(message.items()) if message is not None else ()


class UrllibTransport:
    def __init__(self, opener: urllib.request.OpenerDirector | None = None):
        self.opener = opener or build_opener()

    def __call__(self, method: str, url: str, timeout: float) -> Response:
        request = urllib.request.Request(url, method=method)
        try:
            with self.opener.open(request, timeout=timeout) as response:
                return Response(url, response.status, _headers(response.headers), response.read())
        except urllib.error.HTTPError as err:  # 3xx, 4xx and 5xx all come back as a Response
            try:
                body = err.read() if err.fp is not None else b""
            finally:
                err.close()
            return Response(url, err.code, _headers(err.headers), body)
        except urllib.error.URLError as err:
            if isinstance(err.reason, TimeoutError):
                raise TransportTimeout(f"timed out: {url}") from None
            raise TransportError(f"could not reach {url}: {err.reason}") from None
        except TimeoutError:
            raise TransportTimeout(f"timed out reading {url}") from None
        except (http.client.HTTPException, OSError) as err:
            raise TransportError(f"transport failure for {url}: {type(err).__name__}: {err}") from None


def send(board, method: str, url: str, *, transport, timeout: float) -> Response:
    """Check the request against policy, then make exactly one transport call."""
    check_request(method, url, board)
    return transport(method, url, timeout)
