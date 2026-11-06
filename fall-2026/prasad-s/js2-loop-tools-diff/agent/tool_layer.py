"""The three tools: fetch, read, write (GATE.md v0.2 §4, §5).

Each one calls Policy.check first and acts only on what the Permit names.
This module is the only JS2 code meant to open the network or write a file;
the loop is wired to it in CP5b. There is no delete tool (§5 Never).
"""

import socket
import urllib.error
import urllib.request
from dataclasses import dataclass

TIMEOUT_SECONDS = 10  # GATE.md §4, CONTRACT v0.5 item 6


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """§4: a redirect is never followed; its status and Location are returned instead."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _send(request, timeout):
    """The one place a request leaves the process. Tests replace this function."""
    return urllib.request.build_opener(_RefuseRedirects).open(request, timeout=timeout)


@dataclass(frozen=True)
class FetchResult:
    """A response with a status, whatever the status. The caller decides what it means (§4)."""

    url: str
    status: int
    content_type: str
    location: str
    body: bytes


class FetchError(Exception):
    """No status came back. kind is "timeout" or "connection" (§4's two retryable rows)."""

    def __init__(self, kind, url, detail):
        self.kind = kind
        self.url = url
        super().__init__(f"{kind} fetching {url}: {detail}")


class ToolLayer:
    def __init__(self, policy, timeout=TIMEOUT_SECONDS):
        self.policy = policy
        self.timeout = timeout

    def fetch(self, url):
        """One GET attempt. Retries belong to the loop, which counts each attempt (§2)."""
        permit = self.policy.check("fetch", url)
        request = urllib.request.Request(permit.url, headers={"Accept": "application/json"}, method="GET")
        try:
            with _send(request, self.timeout) as response:
                status, headers, body = response.status, response.headers, response.read()
        except urllib.error.HTTPError as exc:  # 3xx (not followed), 4xx, 5xx all have a status
            status, headers, body = exc.code, exc.headers, exc.read()
        except (TimeoutError, socket.timeout) as exc:
            raise FetchError("timeout", permit.url, exc) from exc
        except urllib.error.URLError as exc:
            kind = "timeout" if isinstance(exc.reason, (TimeoutError, socket.timeout)) else "connection"
            raise FetchError(kind, permit.url, exc.reason) from exc
        except OSError as exc:
            raise FetchError("connection", permit.url, exc) from exc
        return FetchResult(
            url=permit.url,
            status=status,
            content_type=headers.get("Content-Type", "") if headers else "",
            location=headers.get("Location", "") if headers else "",
            body=body,
        )

    def read(self, path):
        permit = self.policy.check("read", path)
        return permit.path.read_bytes()

    def write(self, path, data):
        """Write bytes to the resolved path. A new file is created exclusively, so a
        file that appears after the check is never overwritten without approval."""
        permit = self.policy.check("write", path)
        if isinstance(data, str):
            data = data.encode("utf-8")
        permit.path.parent.mkdir(parents=True, exist_ok=True)
        with open(permit.path, "wb" if permit.overwrite else "xb") as fh:
            fh.write(data)
        return permit
