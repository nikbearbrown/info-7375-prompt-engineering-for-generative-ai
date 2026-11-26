"""HTTP for the JS2 loop (GATE.md sections 2 and 5): GET only, at least 1 s apart per host, every redirect hop checked and counted.

LiveFetcher talks to the network. ReplayFetcher serves saved files for SEEDED runs. Both return a Response and never raise for
an HTTP or network failure: the loop's error policy decides what a failure means. Policy violations do raise.
"""
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlsplit

from . import policy

USER_AGENT = "INFO7375-job-search-agent-2 (student coursework; read-only)"


@dataclass
class Response:
    status: Optional[int]
    body: Optional[bytes]
    error: Optional[str] = None
    final_url: Optional[str] = None
    hops: int = 0
    kind: Optional[str] = None  # for failures with no status: timeout | connection | tls | redirect_limit
    retry_after: Optional[float] = None


class RedirectLimit(Exception):
    pass


class PolicyRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Checks every hop against the policy before following it, and charges it to the request budget."""

    def __init__(self, allow, max_hops, on_hop):
        super().__init__()
        self.allow, self.max_hops, self.on_hop, self.hops = allow, max_hops, on_hop, 0

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        policy.check_url(newurl, self.allow)
        self.hops += 1
        if self.hops > self.max_hops:
            raise RedirectLimit(f"more than {self.max_hops} redirect hops")
        self.on_hop(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _retry_after(headers):
    try:
        return float(headers.get("Retry-After"))
    except (TypeError, ValueError, AttributeError):
        return None


class LiveFetcher:
    def __init__(self, allow, max_hops, on_hop, before_wait, min_gap_s=1.0, clock=time.monotonic, sleep=time.sleep):
        self.allow, self.max_hops, self.on_hop, self.before_wait = allow, max_hops, on_hop, before_wait
        self.min_gap_s, self.clock, self.sleep = min_gap_s, clock, sleep
        self.last = {}

    def get(self, url, timeout):
        policy.check_url(url, self.allow)
        host = urlsplit(url).hostname
        if host in self.last:
            gap = self.min_gap_s - (self.clock() - self.last[host])
            if gap > 0:
                self.before_wait(gap)  # the pacing wait counts against the time budget
                self.sleep(gap)
        handler = PolicyRedirectHandler(self.allow, self.max_hops, self.on_hop)
        opener = urllib.request.build_opener(handler)  # urllib verifies TLS certificates by default
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with opener.open(req, timeout=timeout) as resp:
                body = resp.read()
                policy.check_url(resp.geturl(), self.allow)
                return Response(resp.status, body, final_url=resp.geturl(), hops=handler.hops)
        except urllib.error.HTTPError as e:
            try:
                body = e.read()
            except OSError:
                body = None
            return Response(e.code, body, error=f"HTTP {e.code}", final_url=url, hops=handler.hops,
                            retry_after=_retry_after(e.headers))
        except RedirectLimit as e:
            return Response(None, None, error=str(e), final_url=url, hops=handler.hops, kind="redirect_limit")
        except urllib.error.URLError as e:
            reason = e.reason
            kind = "tls" if isinstance(reason, ssl.SSLCertVerificationError) else (
                "timeout" if isinstance(reason, TimeoutError) else "connection")
            return Response(None, None, error=f"{type(reason).__name__}: {reason}"[:200], final_url=url, hops=handler.hops, kind=kind)
        except TimeoutError as e:
            return Response(None, None, error=f"TimeoutError: {e}"[:200], final_url=url, hops=handler.hops, kind="timeout")
        except OSError as e:  # connection reset and similar
            return Response(None, None, error=f"{type(e).__name__}: {e}"[:200], final_url=url, hops=handler.hops, kind="connection")
        finally:
            self.last[host] = self.clock()


class ReplayFetcher:
    """SEEDED runs: answer constructed URLs from saved files. URLs still pass the network policy; files pass the read policy."""

    def __init__(self, files_by_url, files, allow):
        self.files_by_url = {policy.normalize_url(u): p for u, p in files_by_url.items()}
        self.files, self.allow = files, allow

    def get(self, url, timeout):
        policy.check_url(url, self.allow)
        path = self.files_by_url.get(policy.normalize_url(url))
        if path is None:
            return Response(None, None, error="replay: no saved file for this URL", final_url=url, kind="connection")
        return Response(200, self.files.check_read(path).read_bytes(), final_url=url)
