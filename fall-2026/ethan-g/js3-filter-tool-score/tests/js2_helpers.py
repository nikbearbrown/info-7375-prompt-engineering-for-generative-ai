"""Shared helpers for the JS2 tests: constructed board responses and a scripted fetcher (no network)."""
import importlib.util
import io
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PERSONA = ROOT / "persona" / "evan-gordon.resume.json"
HOSTS = {"boards-api.greenhouse.io", "api.lever.co"}
BIG = {"max_boards": 12, "max_requests": 100, "max_seconds": 60, "request_timeout_s": 5, "max_redirect_hops": 3,
       "max_loop_steps": 200}


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_run", ROOT / "scripts" / "verify_run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gh_url(board):
    return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"


def gh_detail_url(board, job_id):
    return f"{gh_url(board)}/{job_id}"


def lever_url(board):
    return f"https://api.lever.co/v0/postings/{board}?mode=json"


def gh_job(i, title="Account Executive", loc="Boston, MA", content=None):
    j = {"id": i, "title": title, "location": {"name": loc}, "absolute_url": f"https://example.com/{i}",
         "updated_at": "2026-11-10T12:00:00-05:00"}
    if content is not None:
        j["content"] = content
    return j


def gh_body(jobs):
    return json.dumps({"jobs": jobs, "meta": {"total": len(jobs)}}).encode()


def lever_body(postings):
    return json.dumps(postings).encode()


def lever_posting(pid, text="Account Executive", loc="Boston, MA", desc=""):
    return {"id": pid, "text": text, "categories": {"location": loc, "team": "Sales"}, "descriptionPlain": desc,
            "lists": [], "additionalPlain": "", "hostedUrl": f"https://jobs.lever.co/x/{pid}", "createdAt": 1762790400000}


def ok(body):
    from jsagent import net
    return net.Response(200, body)


def http(code, body=b'{"error": "constructed"}', retry_after=None):
    from jsagent import net
    return net.Response(code, body, error=f"HTTP {code}", retry_after=retry_after)


def timeout():
    from jsagent import net
    return net.Response(None, None, error="TimeoutError: timed out", kind="timeout")


class FakeFetcher:
    """Serves scripted responses per URL, in order (the last one repeats). Records every call."""

    def __init__(self, script):
        self.script = {k: list(v) for k, v in script.items()}
        self.calls = []

    def get(self, url, timeout):
        from jsagent import net
        self.calls.append(url)
        queue = self.script.get(url)
        if not queue:
            return net.Response(None, None, error="no scripted response", kind="connection")
        return queue.pop(0) if len(queue) > 1 else queue[0]


class LoopSandbox:
    """A temporary output root. Board files are written inside it (the policy lets the loop read its own output root)."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name).resolve()
        self.out = self.base / "out"
        self.out.mkdir()
        self.n = 0

    def boards_file(self, entries):
        self.n += 1
        path = self.out / f"boards_test_{self.n}.json"
        path.write_text(json.dumps({"boards": [{"provider": p, "board": b} for p, b in entries]}))
        return path

    def run(self, entries, script, budgets=BIG, **kw):
        from jsagent import loop
        fetcher = kw.pop("fetcher", None) or FakeFetcher(script)
        stream = io.StringIO()
        kw.setdefault("baselines", {})
        res = loop.run(boards_path=self.boards_file(entries), out_root=self.out, fetcher=fetcher, budgets=budgets,
                       sleep=lambda s: None, no_claude=True, resume_path=PERSONA, stream=stream, **kw)
        res["console"] = stream.getvalue()
        return res, fetcher

    def state(self):
        return json.loads((self.out / "state" / "state.json").read_text())

    def close(self):
        self._tmp.cleanup()
