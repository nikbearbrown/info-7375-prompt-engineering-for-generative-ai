"""Test doubles: a scripted fetcher and a fake clock (no network, no waiting)."""
import json
from watcher.fetch import Response, FetchTimeout

def gh(*ids):  return Response(200, json.dumps({"jobs": [{"id": i, "title": f"Job {i}"} for i in ids]}).encode())
def lever(*ids): return Response(200, json.dumps([{"id": str(i), "text": f"Job {i}"} for i in ids]).encode())
NOT_FOUND = Response(404, b'{"status":404,"error":"Job board not found"}')
BLANK = Response(200, b"")
TIMEOUT = FetchTimeout("timed out")

class Clock:
    def __init__(self): self.t = 0.0
    def __call__(self): return self.t

class ScriptedFetch:
    """script: {board_key: [result for attempt 1, result for attempt 2, ...]}; each call can also advance the clock."""
    def __init__(self, script, clock=None, cost=1.0):
        self.script = {k: list(v) for k, v in script.items()}; self.calls = []; self.clock = clock; self.cost = cost
    def __call__(self, board, url, timeout):
        self.calls.append(board)
        if self.clock: self.clock.t += self.cost
        r = self.script[board].pop(0)
        if isinstance(r, Exception): raise r
        return r
