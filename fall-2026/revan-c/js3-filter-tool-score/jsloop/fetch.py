"""The one network tool: a single GET to an allow-listed board URL. It never follows redirects."""
import http.client
import socket
import urllib.parse
from dataclasses import dataclass

from .policy import check_request

USER_AGENT = "js2-loop-tools-diff/1.0 (INFO7375 course project; read-only)"


@dataclass(frozen=True)
class FetchResult:
    status: int | None     # HTTP status, or None when no response arrived
    body: bytes | None     # exact bytes received, or None when there were none
    error: str | None      # what went wrong, in words; None for a plain 200


def http_get(url, timeout):
    # Checked again here, at the tool, so no caller can reach the network around the loop's check.
    # Demonstration gating (the fourth board) is the loop's preflight decision; host and URL are checked here.
    check_request("GET", url, demo=True)
    parts = urllib.parse.urlsplit(url)
    # http.client sends exactly one request and does not follow redirects, so none is ever followed.
    conn = http.client.HTTPSConnection(parts.hostname, timeout=timeout)
    try:
        conn.request("GET", f"{parts.path}?{parts.query}",
                     headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        response = conn.getresponse()
        body = response.read()
        status = response.status
        if 300 <= status < 400:
            location = response.getheader("Location")
            return FetchResult(status, body, f"HTTP {status} redirect to {location!r} refused, not followed")
        if status != 200:
            return FetchResult(status, body, f"HTTP {status}")
        return FetchResult(200, body, None)
    except (socket.timeout, TimeoutError):
        return FetchResult(None, None, f"timed out after {timeout:.1f} s")
    except (OSError, http.client.HTTPException) as exc:
        return FetchResult(None, None, f"network error: {exc.__class__.__name__}: {exc}")
    finally:
        conn.close()
