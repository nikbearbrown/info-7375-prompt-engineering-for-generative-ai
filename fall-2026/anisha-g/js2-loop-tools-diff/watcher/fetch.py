"""The one tool that touches the network. Every request and every redirect is checked by the policy first."""
import socket, urllib.error, urllib.request
from dataclasses import dataclass

@dataclass
class Response:
    status: int
    body: bytes

class FetchTimeout(Exception): pass
class FetchError(Exception): pass

class PolicyRedirectHandler(urllib.request.HTTPRedirectHandler):
    """GATE 5a: a redirect to any host off the allow-list is blocked before it is followed."""
    def __init__(self, policy):
        super().__init__(); self.policy = policy
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.policy.check_request("GET", newurl)                        # raises Blocked naming the host
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def make_fetch(policy, max_bytes=8_000_000):
    opener = urllib.request.build_opener(PolicyRedirectHandler(policy))
    def fetch(board, url, timeout):
        policy.check_request("GET", url)
        req = urllib.request.Request(url, headers={"User-Agent": "INFO7375-job-watch (student project, read-only)"})
        try:
            with opener.open(req, timeout=timeout) as r:
                return Response(r.status, r.read(max_bytes))
        except urllib.error.HTTPError as e:
            return Response(e.code, e.read(max_bytes))
        except (socket.timeout, TimeoutError) as e:
            raise FetchTimeout(f"timed out after {timeout:.0f}s") from e
        except urllib.error.URLError as e:
            if isinstance(e.reason, (socket.timeout, TimeoutError)):
                raise FetchTimeout(f"timed out after {timeout:.0f}s") from e
            raise FetchError(str(e.reason)) from e
    return fetch
