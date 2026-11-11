"""The only network tool the agent has: a policy-gated, unauthenticated GET.

Every URL, including every redirect target, goes through Policy.check_request first.
Returns a FetchResult; it never raises for HTTP errors or timeouts (the loop decides what they
mean), but it does raise PolicyError if the policy refuses a URL or a redirect.
"""
import socket
import urllib.error
import urllib.request
from collections import namedtuple

from jsagent.policy import ALLOW, PolicyError

USER_AGENT = "INFO7375-JS2-student-watcher/1.0 (public job-board GETs only; no login)"

FetchResult = namedtuple("FetchResult", "status body error")  # error: None | "timeout" | "network: ..."


class _PolicyRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, policy):
        super().__init__()
        self.policy = policy

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        d = self.policy.check_request("GET", newurl)
        if d.outcome != ALLOW:
            raise PolicyError(d)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def make_fetcher(policy):
    opener = urllib.request.build_opener(_PolicyRedirect(policy))

    def fetch(url, timeout):
        d = policy.check_request("GET", url)
        if d.outcome != ALLOW:
            raise PolicyError(d)
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
        try:
            with opener.open(req, timeout=timeout) as resp:
                return FetchResult(resp.status, resp.read(), None)
        except urllib.error.HTTPError as e:
            return FetchResult(e.code, e.read() or b"", None)
        except (socket.timeout, TimeoutError):
            return FetchResult(None, b"", "timeout")
        except urllib.error.URLError as e:
            if isinstance(e.reason, (socket.timeout, TimeoutError)):
                return FetchResult(None, b"", "timeout")
            return FetchResult(None, b"", f"network: {e.reason}")

    return fetch
