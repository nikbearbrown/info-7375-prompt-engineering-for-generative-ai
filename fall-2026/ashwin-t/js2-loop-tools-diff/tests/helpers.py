"""Offline test helpers: a fake clock, a scripted transport, and a throwaway project root.

Every test project lives beneath tests/tmp/ (the only place GATE.md lets tests write) and is
removed afterwards. Nothing here touches the network or the real state/ and runs/ folders.
"""
from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jobloop import fetch, providers

PROJECT = Path(__file__).resolve().parent.parent
TMP = PROJECT / "tests" / "tmp"
RESUME = PROJECT / "data" / "supriya-sharma.resume.json"


class FakeClock:
    def __init__(self, start: float = 1000.0):
        self.t = start
        self.sleeps = []

    def __call__(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.t += seconds

    def wall(self):
        return datetime(2026, 11, 9, 12, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=self.t - 1000.0)


def gh_body(ids, title="Software Engineer", location="Boston, MA") -> bytes:
    return json.dumps({"jobs": [{"id": i, "title": title, "content": "&lt;p&gt;Python and SQL&lt;/p&gt;",
                                 "location": {"name": location}, "offices": [],
                                 "absolute_url": f"https://example.invalid/{i}"} for i in ids],
                       "meta": {"total": len(ids)}}).encode()


def ashby_body(ids, title="Backend Engineer") -> bytes:
    return json.dumps({"apiVersion": "1", "jobs": [{"id": str(i), "title": title, "location": "Remote, US",
                                                    "secondaryLocations": [], "descriptionPlain": "Python, SQL",
                                                    "jobUrl": f"https://example.invalid/{i}"} for i in ids]}).encode()


def lever_body(ids, title="Software Engineer") -> bytes:
    return json.dumps([{"id": str(i), "text": title, "categories": {"location": "Boston"},
                        "descriptionPlain": "Python SQL", "lists": [], "additionalPlain": "",
                        "hostedUrl": f"https://example.invalid/{i}"} for i in ids]).encode()


def ok(body: bytes, elapsed: float = 0.2) -> fetch.Response:
    return fetch.Response(200, {"content-type": "application/json"}, body, elapsed)


def status(code: int, body: bytes = b'{"error": "x"}', headers=None, elapsed: float = 0.1) -> fetch.Response:
    return fetch.Response(code, {"content-type": "application/json", **(headers or {})}, body, elapsed)


def timeout(elapsed: float = 10.0) -> fetch.TransportFailure:
    return fetch.TransportFailure("timeout", "timed out", elapsed)


class FakeTransport:
    """script: {url: [Response | TransportFailure, ...]} consumed in order. Records every call."""

    def __init__(self, clock: FakeClock, script: dict):
        self.clock, self.script, self.calls = clock, {u: list(v) for u, v in script.items()}, []

    def __call__(self, url: str, timeout_s: float):
        self.calls.append((url, timeout_s))
        queue = self.script.get(url)
        if not queue:
            raise AssertionError(f"unexpected request to {url}")
        item = queue.pop(0)
        self.clock.t += min(item.elapsed, timeout_s)
        if isinstance(item, fetch.TransportFailure):
            raise item
        return item


def url(provider: str, board: str) -> str:
    return providers.endpoint(provider, board)


class Project:
    """A throwaway project root: config/, data/, optional state/, runs/."""

    def __init__(self, boards, state=None):
        self.root = TMP / f"proj-{uuid.uuid4().hex[:10]}"
        (self.root / "config").mkdir(parents=True)
        (self.root / "data").mkdir()
        shutil.copy(RESUME, self.root / "data" / RESUME.name)
        self.write_config(boards)
        if state is not None:
            (self.root / "state").mkdir()
            (self.root / "state" / "seen.json").write_text(json.dumps(state))

    def write_config(self, boards):
        cfg = {"schema_version": 1,
               "boards": [{"provider": p, "board": b, "purpose": purpose} for p, b, purpose in boards]}
        (self.root / "config" / "boards.json").write_text(json.dumps(cfg))

    def state_bytes(self):
        p = self.root / "state" / "seen.json"
        return p.read_bytes() if p.exists() else None

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


def state_for(entries: dict) -> dict:
    return {"schema_version": 1, "last_finished_run": "2026-11-08T12:00:00Z",
            "boards": {k: {"seen_ids": sorted(str(i) for i in ids), "last_observed": "2026-11-08T12:00:00Z"}
                       for k, ids in entries.items()}}
