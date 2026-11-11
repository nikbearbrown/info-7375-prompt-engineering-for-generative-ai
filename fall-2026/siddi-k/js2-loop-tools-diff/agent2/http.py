"""The agent's only network tool: an allow-listed GET that never follows a redirect (pattern carried over from JS1)."""
from __future__ import annotations

import socket
import urllib.error
import urllib.request

from . import policy


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise policy.Refused(f"redirect {code} to {newurl!r} refused: redirects are never followed")


def fetch(url: str, timeout: float) -> tuple[int, bytes]:
    """Returns (HTTP status, body). Raises TimeoutError on a timeout and policy.Refused on anything off-policy."""
    policy.check_url(url)
    opener = urllib.request.build_opener(_NoRedirect())
    req = urllib.request.Request(url, headers={"User-Agent": "js2-job-search-agent (INFO 7375 course project)"})
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except urllib.error.URLError as e:
        if isinstance(e.reason, (socket.timeout, TimeoutError)):
            raise TimeoutError(str(e.reason)) from None
        raise
    except socket.timeout as e:
        raise TimeoutError(str(e)) from None
