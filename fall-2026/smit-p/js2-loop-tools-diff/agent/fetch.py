"""The only way the agent reaches the network.

LiveTransport does real HTTPS GETs; ReplayTransport serves saved files and marks every
response as SEEDED so a replayed run can never be mistaken for a live one. Both are wrapped
by GuardedFetcher, which asks the permission policy before every request.
"""

import json
import os
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from agent import policy

USER_AGENT = "js2-job-watch/0.1 (INFO 7375 course project; read-only; no apply)"
TIMEOUT_S = 15


@dataclass
class Response:
    http_status: object  # int, or None when no HTTP response arrived
    body: bytes
    error: object  # None, "timeout", or "connection: ..."
    elapsed_ms: int
    seeded: bool = False


class LiveTransport:
    seeded = False

    def get(self, url, headers):
        start = time.monotonic()
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
                body = r.read()
                return Response(r.status, body, None, _ms(start))
        except urllib.error.HTTPError as e:
            return Response(e.code, e.read(), None, _ms(start))
        except (socket.timeout, TimeoutError):
            return Response(None, b"", "timeout", _ms(start))
        except urllib.error.URLError as e:
            if isinstance(e.reason, (socket.timeout, TimeoutError)):
                return Response(None, b"", "timeout", _ms(start))
            return Response(None, b"", f"connection: {e.reason}", _ms(start))


class ReplayTransport:
    """Serves responses from a scenario file: {url: [response, response, ...]}.

    Each response is {"status": 200, "body_file": "..."} or {"status": 200, "body": ...}
    or {"error": "timeout"}. Successive requests to the same URL take successive entries.
    """

    seeded = True

    def __init__(self, base, scenario_path):
        self.base = base
        self.dir = os.path.dirname(scenario_path)
        self.scenario = json.loads(policy.guarded_read(base, scenario_path))
        self.calls = {}

    def get(self, url, headers):
        key = policy.normalize_url(url)
        script = {policy.normalize_url(k): v for k, v in self.scenario["responses"].items()}
        if key not in script:
            return Response(None, b"", "connection: no seeded response for this URL", 0, True)
        n = self.calls.get(key, 0)
        self.calls[key] = n + 1
        entry = script[key][min(n, len(script[key]) - 1)]
        if "error" in entry:
            return Response(None, b"", entry["error"], 0, True)
        if "body_file" in entry:
            body = policy.guarded_read(self.base, os.path.join(self.dir, entry["body_file"]),
                                       binary=True)
        else:
            body = json.dumps(entry["body"]).encode()
        return Response(entry["status"], body, None, 0, True)


class GuardedFetcher:
    def __init__(self, transport, min_gap_s=1.0, clock=time.monotonic, sleep=time.sleep):
        self.transport = transport
        self.min_gap_s = min_gap_s
        self.clock = clock
        self.sleep = sleep
        self.last_call = {}
        self.last_wait_s = 0.0

    def get(self, url):
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        decision = policy.check_request("GET", url, headers)
        if not decision.allowed:
            raise policy.PolicyDenied(decision, f"GET {url}")
        host = url.split("/")[2].lower()
        self.last_wait_s = 0.0
        if not self.transport.seeded and host in self.last_call:
            wait = self.min_gap_s - (self.clock() - self.last_call[host])
            if wait > 0:
                self.sleep(wait)
                self.last_wait_s = round(wait, 3)
        resp = self.transport.get(url, headers)
        self.last_call[host] = self.clock()
        return resp


def _ms(start):
    return int((time.monotonic() - start) * 1000)
