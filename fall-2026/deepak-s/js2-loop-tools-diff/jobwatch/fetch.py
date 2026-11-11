"""The board fetch: CONTRACT.md In (Network), Refuses 1, Order steps 4 and 6."""
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlsplit

from jobwatch.errors import REFUSED, Stop

BOARD_HOST = "boards-api.greenhouse.io"
TIMEOUT_S = 20
USER_AGENT = "jobwatch/1 (INFO 7375 coursework; read-only)"


def board_url(token):
    return f"https://{BOARD_HOST}/v1/boards/{token}/jobs?content=true"


def check_url(url, host=BOARD_HOST):
    """https only, exact host (case-insensitive), no userinfo, no explicit port, no trailing dot."""
    parts = urlsplit(url)
    netloc = parts.netloc
    if (
        parts.scheme != "https"
        or "@" in netloc
        or ":" in netloc
        or netloc.endswith(".")
        or netloc.lower() != host
    ):
        raise Stop(REFUSED, f"URL refused: only https://{host}/ is allowed")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never follow a redirect; urllib then raises HTTPError for the 3xx."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def default_opener():
    return urllib.request.build_opener(_NoRedirect())


@dataclass
class Response:
    status: int
    headers: object
    body: bytes


class FetchFailed(Exception):
    """No HTTP response at all; `kind` names what went wrong."""

    def __init__(self, kind):
        super().__init__(kind)
        self.kind = kind


def fetch(url, opener):
    check_url(url)
    request = urllib.request.Request(
        url, method="GET", headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with opener.open(request, timeout=TIMEOUT_S) as resp:
            return Response(resp.status, resp.headers, resp.read())
    except urllib.error.HTTPError as e:
        try:
            body = e.read() or b""
        except (OSError, AttributeError):
            body = b""
        return Response(e.code, e.headers, body)
    except (TimeoutError, socket.timeout):
        raise FetchFailed("timeout") from None
    except urllib.error.URLError as e:
        raise FetchFailed(f"url_error:{type(e.reason).__name__}") from None
    except OSError as e:
        raise FetchFailed(f"os_error:{type(e).__name__}") from None
