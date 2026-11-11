"""Test helpers: a fake clock, a scripted transport spy, response builders, a fake HTTPS
handler, an open() spy, and an "out" root. Everything here is synthetic."""

import builtins
import email.message
import io
import json
import os
import urllib.request
import urllib.response
from dataclasses import dataclass
from pathlib import Path

from agent.errors import TransportError, TransportTimeout
from agent.providers import Board, listing_url
from agent.transport import Response

TESTS_DIR = Path(__file__).resolve().parent
FIXTURES = TESTS_DIR / "fixtures"
GREENHOUSE_SMALL = FIXTURES / "greenhouse_small.json"
ASHBY_SMALL = FIXTURES / "ashby_small.json"

STRIPE = Board("greenhouse", "stripe")
NOTION = Board("ashby", "notion")
LINEAR = Board("ashby", "linear")
INVALID = Board("greenhouse", "info7375-tushar-js2-deliberately-invalid-20261109")
DEMO_BOARDS = (STRIPE, NOTION, LINEAR, INVALID)


class FakeClock:
    """Monotonic clock driven by the test. sleep() advances it by the requested seconds
    plus `oversleep` (real sleeps can overshoot), and records each request."""

    def __init__(self, start: float = 1000.0, oversleep: float = 0.0):
        self.now = start
        self.oversleep = oversleep
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds + self.oversleep


@dataclass
class Slow:
    """A scripted step that takes `seconds` on the fake clock before giving `result`."""
    seconds: float
    result: object


class TransportSpy:
    """Records every transport call.

    Modes: `routes` maps a URL to a list of scripted steps (a Response, an exception
    instance, or Slow(seconds, step)); `inner` delegates; otherwise `response` or a default
    empty 200 is returned. An unscripted call fails the test.
    """

    def __init__(self, response: Response | None = None, inner=None, routes: dict | None = None,
                 clock: FakeClock | None = None):
        self.response = response
        self.inner = inner
        self.routes = {url: list(steps) for url, steps in (routes or {}).items()}
        self.clock = clock
        self.calls: list[tuple[str, str, float]] = []

    def __call__(self, method, url, timeout):
        self.calls.append((method, url, timeout))
        if self.inner is not None:
            return self.inner(method, url, timeout)
        if self.routes:
            steps = self.routes.get(url)
            if not steps:
                raise AssertionError(f"unscripted transport call: {method} {url}")
            step = steps.pop(0)
            if isinstance(step, Slow):
                self.clock.advance(step.seconds)
                step = step.result
            if callable(step) and not isinstance(step, BaseException):
                step = step()  # a side effect at call time, returning the real step
            if isinstance(step, BaseException):
                raise step
            return step
        if self.response is not None:
            return self.response
        return Response(url, 200, (("Content-Type", "application/json"),), b'{"jobs": []}')

    def urls(self) -> list[str]:
        return [url for _, url, _ in self.calls]


# ---------- synthetic responses ----------

def jobs_body(ids, **extra) -> bytes:
    return json.dumps({"_synthetic": True, **extra, "jobs": [{"id": i} for i in ids]}).encode()


def ok(board: Board, ids) -> Response:
    return Response(listing_url(board), 200, (("Content-Type", "application/json"),), jobs_body(ids))


def status(board: Board, code: int, body: bytes = b"synthetic error body", headers=()) -> Response:
    return Response(listing_url(board), code, tuple(headers), body)


def timeout() -> TransportTimeout:
    return TransportTimeout("synthetic timeout")


def dns_failure() -> TransportError:
    return TransportError("synthetic DNS failure")


def write_config(path: Path, boards, **extra) -> Path:
    entries = [{"provider": b.provider, "token": b.token} if isinstance(b, Board) else b for b in boards]
    path.write_text(json.dumps({"boards": entries, **extra}))
    return path


class FakeHTTPSHandler(urllib.request.BaseHandler):
    """Stands in for urllib's HTTPSHandler: answers every request with one canned response
    and records each request it receives, so a followed redirect would show up here."""

    def __init__(self, status: int, reason: str, headers: dict, body: bytes = b""):
        self.status, self.reason, self.headers, self.body = status, reason, headers, body
        self.requests: list[tuple[str, str]] = []

    def https_open(self, req):
        self.requests.append((req.get_method(), req.full_url))
        message = email.message.Message()
        for key, value in self.headers.items():
            message[key] = value
        stream = self.body if hasattr(self.body, "read") else io.BytesIO(self.body)
        response = urllib.response.addinfourl(stream, message, req.full_url, code=self.status)
        response.msg = self.reason
        return response


class OpenSpy:
    """Records os.open, builtins.open and io.open calls, passing them through."""

    def __init__(self, monkeypatch):
        self.calls: list[tuple[str, str]] = []
        real_os_open, real_open = os.open, builtins.open

        def os_open(path, flags, *args, **kwargs):
            self.calls.append(("os.open", os.fspath(path)))
            return real_os_open(path, flags, *args, **kwargs)

        def py_open(file, *args, **kwargs):
            self.calls.append(("open", os.fspath(file) if not isinstance(file, int) else str(file)))
            return real_open(file, *args, **kwargs)

        monkeypatch.setattr(os, "open", os_open)
        monkeypatch.setattr(builtins, "open", py_open)
        monkeypatch.setattr(io, "open", py_open)


def make_out_root(tmp_path: Path) -> Path:
    """A temporary output root named "out"."""
    root = tmp_path / "out"
    root.mkdir()
    return root


class SlowBody:
    """A response body that takes `per_read` fake seconds per chunk."""

    def __init__(self, clock: FakeClock, chunks: int, per_read: float, chunk: bytes = b"x" * 16):
        self.clock, self.remaining, self.per_read, self.chunk = clock, chunks, per_read, chunk
        self.reads = 0
        self.closed = False

    def read(self, size=-1):
        self.reads += 1
        self.clock.advance(self.per_read)
        if self.remaining <= 0:
            return b""
        self.remaining -= 1
        return self.chunk

    def close(self):
        self.closed = True


# ---------- running the agent with fakes ----------

RUN_ID = "run-test"


def run_agent(tmp_path: Path, boards, routes: dict, *, clock: FakeClock | None = None,
              state=None, run_id: str = RUN_ID, config_path: Path | None = None):
    """Run the loop with a scripted TransportSpy. `routes` maps Board -> scripted steps.
    `state` (a dict, or raw bytes) is written to out/state.json before the run."""
    from agent import loop

    clock = clock or FakeClock()
    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    if state is not None:
        data = state if isinstance(state, bytes) else json.dumps(state).encode()
        (out / "state.json").write_bytes(data)
    if config_path is None:
        config_path = write_config(tmp_path / "boards.json", boards)
    spy = TransportSpy(routes={listing_url(b): steps for b, steps in routes.items()}, clock=clock)
    result = loop.run(config_path, out, transport=spy, clock=clock, sleep=clock.sleep, run_id=run_id)
    return result, spy, out


def read_summary(out: Path, run_id: str = RUN_ID) -> dict:
    return json.loads((out / "runs" / run_id / "summary.json").read_text())


def read_trace(out: Path, run_id: str = RUN_ID) -> list[dict]:
    lines = (out / "runs" / run_id / "trace.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines]


def board_entry(summary: dict, board: Board) -> dict:
    return next(b for b in summary["boards"] if b["board"] == board.key)
