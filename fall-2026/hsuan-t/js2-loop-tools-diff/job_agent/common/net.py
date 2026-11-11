"""The only door to the network: every outgoing request, and every redirect it follows, is checked
by the run's permission policy (common/policy.py, GATE §5) first.

Kept apart from the watch so the policy check can't be skipped by a new board adapter: adapters
only build URLs, and only this function opens a connection.
"""

import urllib.error
import urllib.request

from .errors import FetchError
from .policy import Policy


class _CheckedRedirects(urllib.request.HTTPRedirectHandler):
    """urllib follows redirects by itself; without this an allowed host could send us anywhere
    (GATE §5: "Recheck every redirect destination before following it", boundary test 9)."""

    def __init__(self, policy: Policy):
        self.policy = policy

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.policy.check_url(newurl)   # PolicyError propagates: the redirect is never requested
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def http_get(url: str, policy: Policy, timeout: float = 60.0) -> tuple[bytes, str]:
    """Return the body bytes plus the status line and headers, so saved evidence shows what came back and when."""
    policy.check_url(url)
    opener = urllib.request.build_opener(_CheckedRedirects(policy))
    req = urllib.request.Request(url, headers={"User-Agent": "job-search-agent-js1"})
    try:
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read()
            headers = f"HTTP {resp.status}\n" + "".join(f"{k}: {v}\n" for k, v in resp.getheaders())
    # Order matters: HTTPError is a URLError, and a timeout can arrive bare (while reading) or
    # wrapped in URLError (while connecting); the loop retries timeouts but not a 404.
    except urllib.error.HTTPError as e:
        raise FetchError(f"fetch failed: HTTP {e.code} from {url}", "http", e.code, _body(e)) from e
    except TimeoutError as e:
        raise FetchError(f"fetch failed: timed out after {timeout:.1f}s ({url})", "timeout") from e
    except urllib.error.URLError as e:
        kind = "timeout" if isinstance(e.reason, TimeoutError) else "connection"
        raise FetchError(f"fetch failed: {e.reason} ({url})", kind) from e
    except OSError as e:              # connection reset while reading the body
        raise FetchError(f"fetch failed: {e} ({url})", "connection") from e
    return body, headers


def _body(e: urllib.error.HTTPError) -> bytes:
    """The error page, if it can be read; evidence only, so a failure here must not hide the HTTP error."""
    try:
        return e.read() or b""
    except OSError:
        return b""
