import datetime as dt
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from policy import Policy  # noqa: E402
from tools import Response, Tools, TransientError  # noqa: E402

GH = "https://boards-api.greenhouse.io/v1/boards/{}/jobs?content=true"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/{}"
LEVER = "https://api.lever.co/v0/postings/{}?mode=json"


def gh_body(*ids):
    return json.dumps({"jobs": [{"id": i, "title": f"Job {i}", "location": {"name": "United States"},
                                 "absolute_url": f"https://example.invalid/{i}"} for i in ids], "meta": {"total": len(ids)}}).encode()


def ashby_body(*ids):
    return json.dumps({"jobs": [{"id": str(i), "title": f"Job {i}", "location": "Remote",
                                 "jobUrl": f"https://example.invalid/{i}"} for i in ids], "apiVersion": "1"}).encode()


def lever_body(*ids):
    return json.dumps([{"id": str(i), "text": f"Job {i}", "categories": {"location": "Baku"},
                        "hostedUrl": f"https://example.invalid/{i}"} for i in ids]).encode()


class ScriptedTools(Tools):
    """Real Tools and a real Policy; only _send (the wire) is scripted. Every request still
    passes policy.check_request first. Each URL maps to a list of outcomes, used in order."""

    def __init__(self, policy, script):
        super().__init__(policy)
        self.script = {url: list(outcomes) for url, outcomes in script.items()}
        self.sent = []

    def _send(self, request, timeout):
        url = request.full_url
        self.sent.append((request.get_method(), url, dict(request.header_items())))
        outcome = self.script[url].pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        status, body = outcome
        return Response(url, status, body, 0.01)


class Clock:
    def __init__(self, step=0.0):
        self.now, self.step = 0.0, step

    def __call__(self):
        self.now += self.step
        return self.now


def workspace(boards):
    """A temporary agent folder holding config/boards.json, used as the policy root."""
    root = tempfile.mkdtemp(prefix="js2-test-")
    os.makedirs(os.path.join(root, "config"))
    with open(os.path.join(root, "config", "boards.json"), "w") as f:
        json.dump({"boards": boards}, f)
    return root


def board(system, token, employer="X"):
    return {"system": system, "token": token, "employer": employer}


_tick = [0]


def stamp():
    """A distinct run time per call, so two runs in one test never share a folder."""
    _tick[0] += 1
    return dt.datetime(2026, 11, 9, 12, 0, 0, tzinfo=dt.timezone.utc) + dt.timedelta(seconds=_tick[0])


def make(boards, script, approve=lambda action: False):
    root = workspace(boards)
    return root, ScriptedTools(Policy(root, approve=approve), script)


def read_state(root, name="state/seen.json"):
    with open(os.path.join(root, name)) as f:
        return json.load(f)


__all__ = ["ROOT", "GH", "ASHBY", "LEVER", "gh_body", "ashby_body", "lever_body", "ScriptedTools", "Clock",
           "workspace", "board", "stamp", "make", "read_state", "TransientError"]
