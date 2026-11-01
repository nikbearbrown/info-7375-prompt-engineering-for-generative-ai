"""The only door to the network: every outgoing request passes the allow-list here.

Kept apart from the watch so the Claude judge (Step 5) uses the same allow-list without depending
on board code (CONTRACT Refuses: never contact a host outside the list).
"""

import urllib.error
import urllib.request
from urllib.parse import urlparse

from .errors import WatchError

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.anthropic.com"})


def check_host(url: str) -> None:
    """Refuse before a request is made, not after: a refused host must never see a byte from us."""
    host = urlparse(url).hostname
    if host not in ALLOWED_HOSTS:
        raise WatchError(f"host not on allow-list: {host}")


def http_get(url: str, timeout: float = 60.0) -> tuple[bytes, str]:
    """Return the body bytes plus the status line and headers, so saved evidence shows what came back and when."""
    check_host(url)
    req = urllib.request.Request(url, headers={"User-Agent": "job-search-agent-js1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            headers = f"HTTP {resp.status}\n" + "".join(f"{k}: {v}\n" for k, v in resp.getheaders())
    except urllib.error.HTTPError as e:
        raise WatchError(f"fetch failed: HTTP {e.code} from {url}") from e
    except urllib.error.URLError as e:
        raise WatchError(f"fetch failed: {e.reason} ({url})") from e
    return body, headers
