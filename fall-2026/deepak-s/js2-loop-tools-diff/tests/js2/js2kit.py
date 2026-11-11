"""SEEDED test kit for JS2 (written by Claude Code, Claude Opus 5.5, 2026-11-10). No test touches the network.

SeededTransport stands in for urllib's opener: it serves a queue of SEEDED responses per URL and
records every request. FakeClock replaces time.monotonic and time.sleep so retries, spacing and
timeouts cost no real time.
"""
import io
import json
import shutil
import socket
import urllib.error
from datetime import datetime, timezone
from email.message import Message
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEEDED = ROOT / "fixtures" / "seeded"
CAPTURE = ROOT / "evidence" / "manual-capture" / "20261110T184001Z"
NOW = datetime(2026, 11, 10, 20, 0, 0, tzinfo=timezone.utc)
JSON = {"Content-Type": "application/json; charset=utf-8"}

GH = "https://boards-api.greenhouse.io/v1/boards/{}/jobs"
LEVER_EU = "https://api.eu.lever.co/v0/postings/{}?mode=json"
LEVER_US = "https://api.lever.co/v0/postings/{}?mode=json"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/{}"


def seeded(name):
    return (SEEDED / name).read_bytes()


class FakeClock:
    def __init__(self):
        self.t = 0.0
        self.sleeps = []

    def now(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


class _Resp:
    def __init__(self, status, body, headers):
        self.status = status
        self._body = body
        msg = Message()
        for k, v in headers.items():
            msg[k] = v
        self.headers = msg

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class SeededTransport:
    """routes: url -> list of responses, served in order; the last one repeats.
    A response is (status, body, headers) or "timeout" or "connection"."""

    def __init__(self, routes, clock=None, timeout_cost=10):
        self.routes = {u: (r if isinstance(r, list) else [r]) for u, r in routes.items()}
        self.requests = []
        self.clock = clock
        self.timeout_cost = timeout_cost

    def open(self, request, timeout=None):
        url = request.full_url
        self.requests.append({"url": url, "method": request.get_method(), "timeout": timeout})
        if url not in self.routes:
            raise AssertionError(f"unexpected request to {url}")
        queue = self.routes[url]
        resp = queue.pop(0) if len(queue) > 1 else queue[0]
        if resp == "timeout":
            if self.clock:
                self.clock.t += self.timeout_cost
            raise socket.timeout("timed out")
        if resp == "connection":
            raise urllib.error.URLError(ConnectionRefusedError("refused"))
        status, body, headers = resp
        if 200 <= status < 300:
            return _Resp(status, body, headers)
        msg = Message()
        for k, v in headers.items():
            msg[k] = v
        raise urllib.error.HTTPError(url, status, "seeded", msg, io.BytesIO(body))


def ok(body):
    return (200, body, JSON)


def setup_workdir(path, boards, budgets=None):
    """A clean JS2 folder copy: config, persona, schema. `boards` is the list for config/boards.json."""
    (path / "config").mkdir()
    real = json.loads((ROOT / "config" / "budgets.json").read_text(encoding="utf-8"))
    real.update(budgets or {})
    (path / "config" / "budgets.json").write_text(json.dumps(real), encoding="utf-8")
    (path / "config" / "boards.json").write_text(json.dumps({"boards": boards}), encoding="utf-8")
    (path / "examples").mkdir()
    shutil.copy(ROOT / "examples" / "persona_resume.json", path / "examples" / "persona_resume.json")
    (path / "schema").mkdir()
    shutil.copy(ROOT / "schema" / "resume.schema.json", path / "schema" / "resume.schema.json")
    return path


def board(system, slug, host, **extra):
    return {"system": system, "slug": slug, "host": host, **extra}


THREE = [board("greenhouse", "seeded-gh", "boards-api.greenhouse.io"),
         board("lever", "seeded-lv", "api.eu.lever.co"),
         board("ashby", "seeded-ab", "api.ashbyhq.com")]


def three_ok_routes():
    return {GH.format("seeded-gh"): ok(seeded("SEEDED_greenhouse_two_jobs.json")),
            LEVER_EU.format("seeded-lv"): ok(seeded("SEEDED_lever_six.json")),
            ASHBY.format("seeded-ab"): ok(seeded("SEEDED_ashby_two_jobs.json"))}


def run_loop(transport, clock=None, now=NOW, config="config/boards.json", approver=None):
    from jobwatch import cli

    clock = clock or FakeClock()
    return cli.main(["loop", "--config", config], opener=transport, now=now, clock=clock.now,
                    sleep=clock.sleep, approver=approver)


def run_dir(workdir, now=NOW):
    return workdir / "runs" / now.strftime("%Y%m%dT%H%M%SZ")


def summary(workdir, now=NOW):
    return json.loads((run_dir(workdir, now) / "summary.json").read_text(encoding="utf-8"))


def trace(workdir, now=NOW):
    return [json.loads(line) for line in (run_dir(workdir, now) / "trace.jsonl").read_text(encoding="utf-8").splitlines()]


def board_result(s, key):
    (b,) = [b for b in s["boards"] if b["key"] == key]
    return b


import pytest  # noqa: E402


@pytest.fixture
def wd(tmp_path, monkeypatch):
    """A clean working copy of the JS2 folder with the three-board SEEDED config. Tests import this fixture."""
    work = tmp_path / "js2"
    work.mkdir()
    setup_workdir(work, THREE)
    monkeypatch.chdir(work)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    return work
