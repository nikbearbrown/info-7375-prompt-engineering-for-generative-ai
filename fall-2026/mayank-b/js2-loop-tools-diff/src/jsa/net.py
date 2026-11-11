"""The only module that touches the network. GET only, allow-listed host, redirects refused."""
from __future__ import annotations

import socket
import urllib.error
import urllib.request

from .policy import PolicyError, check_url

USER_AGENT = "info7375-js2-student-agent/0.1 (read-only public job boards)"


class Timeout(Exception):
    pass


class NetError(Exception):
    pass


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        raise PolicyError("redirect-refused", f"{code} -> {newurl}")


_OPENER = urllib.request.build_opener(_NoRedirect())


def fetch(url: str, timeout: float) -> tuple[int, bytes]:
    """Return (http_status, body_bytes). 4xx/5xx come back as a status, not an exception.

    Raises Timeout, NetError, or PolicyError (off-list host, non-https, redirect).
    """
    check_url(url, "GET")
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        if 300 <= e.code < 400:
            raise PolicyError("redirect-refused", str(e.code)) from e
        return e.code, e.read() or b""
    except PolicyError:
        raise
    except (socket.timeout, TimeoutError) as e:
        raise Timeout(str(e)) from e
    except urllib.error.URLError as e:
        if isinstance(e.reason, (socket.timeout, TimeoutError)):
            raise Timeout(str(e.reason)) from e
        raise NetError(str(e.reason)) from e
