"""The only code that touches the network (pattern from my JS2 watcher/fetch.py). Every request and redirect is checked first."""
import socket, urllib.error, urllib.request
from dataclasses import dataclass
from js3.policy import Policy

@dataclass
class Response:
    status: int
    body: bytes

class _NoOffListRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, policy): super().__init__(); self.policy = policy
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.policy.check_request("GET", newurl); return super().redirect_request(req, fp, code, msg, headers, newurl)

def make_fetch(policy=None, max_bytes=60_000_000):
    policy = policy or Policy()
    opener = urllib.request.build_opener(_NoOffListRedirect(policy))
    def fetch(url, timeout):
        policy.check_request("GET", url)
        req = urllib.request.Request(url, headers={"User-Agent": "INFO7375-job-filter (student project, read-only)"})
        try:
            with opener.open(req, timeout=timeout) as r:
                body = r.read(max_bytes + 1)
                if len(body) > max_bytes: raise IOError(f"response larger than {max_bytes} bytes")
                return Response(r.status, body)
        except urllib.error.HTTPError as e:
            return Response(e.code, e.read(10_000))
        except (socket.timeout, TimeoutError, urllib.error.URLError) as e:
            raise IOError(f"network error: {e}") from e
    return fetch
