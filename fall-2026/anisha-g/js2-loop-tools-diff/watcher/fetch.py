"""The one tool that touches the network. Every request and every redirect is checked by the policy first."""
import socket, urllib.error, urllib.request
from dataclasses import dataclass

@dataclass
class Response:
    status: int
    body: bytes
    location: str = None          # set on a 3xx: the loop decides whether to follow (and counts it as a request)

class FetchTimeout(Exception): pass
class FetchError(Exception): pass

class PolicyRedirectHandler(urllib.request.HTTPRedirectHandler):
    """GATE 5a: a redirect to any host off the allow-list is blocked before it is followed. Allowed redirects are NOT
    followed here: they come back to the loop as a 3xx, so every hop is a separate, counted request (my 15-cap decision)."""
    def __init__(self, policy):
        super().__init__(); self.policy = policy
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.policy.check_request("GET", newurl)                        # raises Blocked naming the host
        return None                                                     # don't follow; urllib turns this into an HTTPError 3xx

def read_capped(fp, max_bytes):
    """Read at most max_bytes; a bigger body is an explicit failure, never silently cut."""
    data = fp.read(max_bytes + 1)
    if len(data) > max_bytes: raise FetchError(f"response larger than {max_bytes} bytes")
    return data

def make_fetch(policy, max_bytes=50_000_000):
    opener = urllib.request.build_opener(PolicyRedirectHandler(policy))
    def fetch(board, url, timeout):
        policy.check_request("GET", url)
        req = urllib.request.Request(url, headers={"User-Agent": "INFO7375-job-watch (student project, read-only)"})
        try:
            with opener.open(req, timeout=timeout) as r:
                return Response(r.status, read_capped(r, max_bytes))
        except urllib.error.HTTPError as e:
            return Response(e.code, read_capped(e, max_bytes), location=e.headers.get("Location") if e.headers else None)
        except (socket.timeout, TimeoutError) as e:
            raise FetchTimeout(f"timed out after {timeout:.0f}s") from e
        except urllib.error.URLError as e:
            if isinstance(e.reason, (socket.timeout, TimeoutError)):
                raise FetchTimeout(f"timed out after {timeout:.0f}s") from e
            raise FetchError(str(e.reason)) from e
    return fetch
