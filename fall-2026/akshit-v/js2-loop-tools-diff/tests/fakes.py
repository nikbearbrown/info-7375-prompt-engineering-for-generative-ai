"""Test doubles. Every response here is CONSTRUCTED, not a real board response."""
import json

from agent2.fetch import Response
from agent2.loop import Board

FIGMA = Board("greenhouse", "figma")
SPOTIFY = Board("lever", "spotify")
SNOW = Board("ashby", "snowflake")
BAD = Board("greenhouse", "no-such-board-js2")


def gh(n):
    return Response("ok", 200, json.dumps({"jobs": [{"id": i, "title": f"Job {i}", "content": ""} for i in range(n)]}).encode())


def lever(n):
    return Response("ok", 200, json.dumps([{"id": f"u{i}", "text": f"Job {i}"} for i in range(n)]).encode())


def ashby(n):
    return Response("ok", 200, json.dumps({"jobs": [{"id": f"a{i}", "title": f"Job {i}", "isListed": True} for i in range(n)]}).encode())


NOT_FOUND = Response("http_error", 404, b'{"status":404,"error":"Job not found"}', "HTTP 404")
TIMEOUT = Response("transient", None, None, "TimeoutError: timed out")


class FakeTransport:
    """Answers per URL from a script: a list of responses consumed in order."""
    label = "CONSTRUCTED"

    def __init__(self, script):
        self.script = {k: list(v) for k, v in script.items()}
        self.calls = []

    def get(self, url, timeout):
        self.calls.append(url)
        return self.script[url].pop(0)


class FakeClock:
    def __init__(self, step=0.0):
        self.now, self.step = 0.0, step

    def __call__(self):
        self.now += self.step
        return self.now

    def sleep(self, s):
        self.now += s


def no_save(key, attempt, body):
    return None
