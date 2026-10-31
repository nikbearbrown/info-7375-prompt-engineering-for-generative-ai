"""The only module that opens network connections. Every request is checked against the
allow-list first; redirects are refused (CONTRACT.md 'Refuses')."""

import datetime as dt
import urllib.error
import urllib.request
from dataclasses import dataclass

from jobwatch.errors import FetchError, RefusedError

BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"
MODEL_URL = "https://api.anthropic.com/v1/messages"
ALLOWED = {("GET", BOARD_URL), ("POST", MODEL_URL)}
USER_AGENT = "jobwatch/0.1 (INFO 7375 course project; read-only public job board client)"


@dataclass(frozen=True)
class FetchResult:
    body: bytes
    url: str
    status: int
    content_type: str
    retrieved_at: str


def check_allowed(method, url):
    if (method, url) not in ALLOWED:
        raise RefusedError(f"refused: {method} {url} is not on the allow-list")


class RefuseRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RefusedError(f"refused: the server redirected ({code}) to {newurl}")


def _open(req, timeout):
    return urllib.request.build_opener(RefuseRedirects()).open(req, timeout=timeout)


def request(method, url, *, data=None, headers=None, opener=None, timeout=60):
    check_allowed(method, url)
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"User-Agent": USER_AGENT, **(headers or {})})
    return (opener or _open)(req, timeout=timeout)


def utc_now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_board(opener=None):
    """One GET of the allow-listed board endpoint. The body is returned unchanged."""
    try:
        with request("GET", BOARD_URL, headers={"Accept": "application/json"}, opener=opener) as response:
            body = response.read()
            status = response.status
            content_type = response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as error:
        raise FetchError(f"board returned HTTP {error.code}") from None
    except (urllib.error.URLError, OSError) as error:
        raise FetchError(f"board fetch failed: {error}") from None
    return FetchResult(body, BOARD_URL, status, content_type, utc_now())
