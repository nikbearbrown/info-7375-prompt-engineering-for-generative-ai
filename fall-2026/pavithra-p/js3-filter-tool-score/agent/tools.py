"""The agent's one network tool: a GET that the permission policy checks before it connects, and again on a redirect."""
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass


class Timeout(Exception):
    """The request took longer than the per-request timeout in config/budgets.json."""


class NetworkError(Exception):
    """No HTTP answer at all (for example DNS or a refused connection). Not retried: it is not on GATE.md's list."""


@dataclass
class Response:
    status: int
    body: bytes
    url: str


def _redirect_handler(policy):
    class CheckedRedirects(urllib.request.HTTPRedirectHandler):
        """A redirect is a new request, so it must pass the same policy."""

        def redirect_request(self, req, fp, code, msg, headers, newurl):
            policy.check_request("GET", newurl)
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    return CheckedRedirects


def http_get(url, policy, timeout, opener=None):
    """GET one URL and return its status and body unchanged. Never sends a body; 4xx and 5xx are returned, not raised."""
    policy.check_request("GET", url)
    opener = opener or urllib.request.build_opener(_redirect_handler(policy))
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "js2-loop-tools-diff (INFO 7375 coursework)"})
    try:
        with opener.open(request, timeout=timeout) as response:
            return Response(response.status, response.read(), url)
    except urllib.error.HTTPError as e:
        return Response(e.code, e.read(), url)
    except (socket.timeout, TimeoutError) as e:
        raise Timeout(f"no answer within {timeout} s") from e
    except urllib.error.URLError as e:
        if isinstance(e.reason, (socket.timeout, TimeoutError)):
            raise Timeout(f"no answer within {timeout} s") from e
        raise NetworkError(str(e.reason)) from e
