"""Shared test scaffolding: a throwaway assignment folder and a scripted fake transport."""
import json
import os
import shutil
import tempfile

from agent import transport

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIX = os.path.join(HERE, "fixtures")
PERSONA = os.path.join(ROOT, "persona", "aarav-patel.example.json")

BUDGETS = {"max_boards": 8, "max_requests": 12, "max_seconds": 90, "max_retries_per_board": 2,
           "request_timeout_seconds": 20, "max_response_bytes": 10_000_000}


def fixture_bytes(name):
    with open(os.path.join(FIX, name), "rb") as f:
        return f.read()


class TempBase:
    """A fresh folder shaped like the assignment folder: config/, runs/, persona/."""

    def __enter__(self):
        self.dir = os.path.realpath(tempfile.mkdtemp(prefix="js2-test-"))
        for sub in ("config", "runs", "persona"):
            os.makedirs(os.path.join(self.dir, sub))
        shutil.copy(PERSONA, os.path.join(self.dir, "persona"))
        with open(os.path.join(self.dir, "config", "watchlist.json"), "w") as f:
            json.dump({"boards": []}, f)
        return self

    def path(self, *p):
        return os.path.join(self.dir, *p)

    def __exit__(self, *a):
        shutil.rmtree(self.dir, ignore_errors=True)


def ok(body, status=200):
    return transport.Response(status=status, body=body, elapsed=0.01)


def err(kind):
    return transport.Response(status=None, body=b"", error_kind=kind, error=kind, elapsed=0.01)


class FakeNet:
    """url-substring -> list of Responses served in order (the last one repeats).
    Records every call so tests can count requests."""

    def __init__(self, script):
        self.script = {k: list(v) for k, v in script.items()}
        self.calls = []

    def __call__(self, url, timeout, max_bytes):
        from agent import policy
        d = policy.check_request("GET", url)
        if d["decision"] != policy.ALLOW:
            raise policy.PolicyDenied(d)
        self.calls.append(url)
        for k, seq in self.script.items():
            if k in url:
                return seq.pop(0) if len(seq) > 1 else seq[0]
        return ok(b'{"status":404}', 404)


class FakeClock:
    def __init__(self):
        self.t = 1000.0
        self.sleeps = []

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


def rd(path, mode="r"):
    with open(path, mode) as f:
        return f.read()


def wr(path, text):
    with open(path, "w") as f:
        f.write(text)
