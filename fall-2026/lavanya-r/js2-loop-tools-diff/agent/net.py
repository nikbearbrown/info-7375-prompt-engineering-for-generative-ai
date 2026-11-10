"""The only network code in JS2: one GET, after the policy says yes.

Returns a Response for any HTTP answer (200, 404, 503 ...). Raises Timeout
for a timeout or connection failure. Redirects are re-checked by the policy.
"""

import socket
import urllib.error
import urllib.request
from dataclasses import dataclass

USER_AGENT = "INFO7375-js2-loop (student project; read-only; GET only)"


@dataclass
class Response:
    status: int
    body: bytes


class Timeout(Exception):
    """No answer in time, or the connection failed."""


def make_get(policy):
    class _CheckedRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            policy.check_url(newurl)          # raises Refused
            return super().redirect_request(req, fp, code, msg, headers,
                                            newurl)

    opener = urllib.request.build_opener(_CheckedRedirect)

    def get(url, timeout):
        policy.check_action("fetch_board")
        policy.check_url(url, "GET")
        req = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": USER_AGENT,
                                              "Accept": "application/json"})
        try:
            with opener.open(req, timeout=timeout) as resp:
                return Response(resp.status, resp.read())
        except urllib.error.HTTPError as e:
            return Response(e.code, e.read() or b"")
        except (socket.timeout, TimeoutError) as e:
            raise Timeout(f"timeout after {timeout}s: {e}") from None
        except urllib.error.URLError as e:
            if isinstance(e.reason, (socket.timeout, TimeoutError)):
                raise Timeout(f"timeout after {timeout}s") from None
            raise Timeout(f"connection failed: {e.reason}") from None

    return get
