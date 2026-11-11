"""Offline fakes for the loop tests. No network, no real clock."""
import json
import os
import tempfile

from jsagent.fetch import FetchResult
from jsagent.loop import empty_state
from jsagent.policy import Policy

BUDGETS = {"max_boards": 5, "max_requests": 10, "max_seconds": 60, "request_timeout_seconds": 10}
HOSTS = ["boards-api.greenhouse.io", "api.ashbyhq.com"]
GH = "https://boards-api.greenhouse.io/v1/boards/{}/jobs"
AS = "https://api.ashbyhq.com/posting-api/job-board/{}"


def jobs(*pairs):
    return json.dumps({"jobs": [{"id": i, "title": t} for i, t in pairs]}).encode()


def ok(*pairs):
    return FetchResult(200, jobs(*pairs), None)


TIMEOUT = FetchResult(None, b"", "timeout")
NOT_FOUND = FetchResult(404, b'{"status":404,"error":"Job not found"}', None)
SERVER = FetchResult(503, b"unavailable", None)
EMPTY = FetchResult(200, b'{"jobs": []}', None)
GARBAGE = FetchResult(200, b"<html>not json</html>", None)


class FakeFetch:
    """url -> list of results, served in order (the last one repeats)."""

    def __init__(self, table):
        self.table = {u: list(v) if isinstance(v, list) else [v] for u, v in table.items()}
        self.calls = []

    def __call__(self, url, timeout):
        self.calls.append(url)
        seq = self.table[url]
        return seq.pop(0) if len(seq) > 1 else seq[0]


class FakeClock:
    def __init__(self, step=0.0):
        self.now, self.step = 0.0, step

    def __call__(self):
        self.now += self.step
        return self.now


def workspace():
    root = tempfile.mkdtemp(prefix="js2test-")
    out = os.path.join(root, "out")
    os.makedirs(out)
    pol = Policy(root, out, HOSTS, approval_files=[os.path.join(out, "state", "seen_ids.json")])
    return root, out, pol


def make(loop_cls, boards, table, budgets=None, clock=None, run_id="r1"):
    root, out, pol = workspace()
    cfg = {"budgets": dict(BUDGETS, **(budgets or {})), "allowed_hosts": HOSTS,
           "boards": [{"system": s, "board": b} for s, b in boards]}
    fetch = FakeFetch(table)
    loop = loop_cls(cfg, pol, fetch, out, run_id, label="test", clock=clock or FakeClock())
    return loop, fetch


def run(loop_cls, boards, table, state=None, **kw):
    loop, fetch = make(loop_cls, boards, table, **kw)
    report, new_state = loop.run(state or empty_state())
    return report, new_state, fetch, loop


def by_board(report):
    return {f"{b['system']}:{b['board']}": b for b in report["boards"]}
