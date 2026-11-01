"""HTTP GET under the policy, with failures classified for the error policy in GATE.md."""
from __future__ import annotations

import socket
import urllib.error
import urllib.request

from .policy import Policy, Refused

USER_AGENT = "info7375-js2-student-agent (read-only)"


class Permanent(Exception):
    """Retrying will not help (e.g. HTTP 404 / 410, other 4xx)."""


class Transient(Exception):
    """May clear on a retry (timeout, connection error, HTTP 429 / 5xx)."""


def fetch(policy: Policy, url: str, timeout: float) -> bytes:
    policy.check_request("GET", url)

    class _CheckedRedirects(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            policy.check_request("GET", newurl)   # refused before the redirect is followed
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    opener = urllib.request.build_opener(_CheckedRedirects)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
    try:
        with opener.open(req, timeout=timeout) as resp:
            policy.check_request("GET", resp.geturl())
            return resp.read()
    except Refused:
        raise
    except urllib.error.HTTPError as e:
        if e.code == 429 or e.code >= 500:
            raise Transient(f"HTTP {e.code}") from e
        raise Permanent(f"HTTP {e.code}") from e
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as e:
        reason = getattr(e, "reason", e)
        raise Transient(f"{type(reason).__name__}: {reason}") from e
