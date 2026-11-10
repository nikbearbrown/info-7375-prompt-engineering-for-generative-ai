"""SYNTHETIC helpers for JS2 loop and boundary tests: a temp project root, a scripted transport, a fake clock.
Nothing here touches the network, the real out/ folder, or a model."""
import json
from pathlib import Path

from agent.net import TransportError
from tests.fixtures import NOT_RELEVANT, PERSONA, RELEVANT, posting, valid_response

GH = "https://boards-api.greenhouse.io/v1/boards/{}/jobs?content=true"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/{}"


def gh_body(*postings, total=None):
    return json.dumps({"jobs": list(postings), "meta": {"total": len(postings) if total is None else total}}).encode()


def ashby_body(*ids):
    return json.dumps({"apiVersion": "1", "jobs": [
        {"id": i, "title": "Data Engineer", "descriptionHtml": "<p>Python and SQL</p>", "jobUrl": f"https://jobs.ashbyhq.com/x/{i}",
         "location": "Synthetic City"} for i in ids]}).encode()


def make_root(tmp_path, boards, js1_state=None):
    root = tmp_path / "proj"
    for d in ("config", "resume", "state", "out", "approvals"):
        (root / d).mkdir(parents=True, exist_ok=True)
    (root / "config" / "boards.json").write_text(json.dumps({"boards": boards}))
    (root / "resume" / "persona.json").write_text(json.dumps(PERSONA))
    if js1_state is not None:
        (root / "state" / "seen.json").write_text(json.dumps(js1_state))
    return root


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s


class Transport:
    """Scripted responses per URL: each item is (status, body[, headers]) or a TransportError.
    Records every call; advances the fake clock by `cost` seconds per call."""

    def __init__(self, script, clock=None, cost=0.1):
        self.script = {u: list(v) for u, v in script.items()}
        self.calls, self.clock, self.cost = [], clock, cost

    def __call__(self, url, timeout, deadline):
        self.calls.append(url)
        if self.clock:
            self.clock.t += self.cost
        item = self.script[url].pop(0)
        if isinstance(item, Exception):
            raise item
        status, body, *h = item
        return status, (h[0] if h else {"content-type": "application/json"}), body


def judge_valid(posting_, resume, timeout):
    return {"response_text": valid_response(posting_), "models_used": ["SYNTHETIC"], "wall_seconds": 0.0}


def judge_invalid(posting_, resume, timeout):
    return {"response_text": "not json", "models_used": ["SYNTHETIC"], "wall_seconds": 0.0}


def board(provider, name, **extra):
    return {"provider": provider, "board": name, **extra}


def run(root, transport, clock=None, judge=judge_valid, **kw):
    from agent.loop import run_loop
    clock = clock or Clock()
    code, run_dir = run_loop(root, resume="resume/persona.json", transport=transport, judge_fn=judge,
                             clock=clock, sleep=clock.sleep, **kw)
    rep = json.loads((run_dir / "report.json").read_text()) if run_dir else None
    return code, rep, run_dir


def trace(run_dir):
    return [json.loads(line) for line in (Path(run_dir) / "trace.jsonl").read_text().splitlines()]


__all__ = ["GH", "ASHBY", "gh_body", "ashby_body", "make_root", "Clock", "Transport", "TransportError",
           "judge_valid", "judge_invalid", "board", "run", "trace", "RELEVANT", "NOT_RELEVANT", "posting"]
