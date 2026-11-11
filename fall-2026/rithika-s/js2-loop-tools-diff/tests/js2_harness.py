"""Offline harness for JS2 loop tests. Nothing here opens a network connection.

Every response body built here is CONSTRUCTED: hand-written to exercise one
case, not copied from any real board.
"""

import json
import shutil
from pathlib import Path

from agent import loop, transport

ROOT = Path(__file__).resolve().parent.parent

SCALE = "https://boards-api.greenhouse.io/v1/boards/scaleai/jobs?content=true"
DATABRICKS = ("https://boards-api.greenhouse.io/v1/boards/databricks/jobs"
              "?content=true")
OPENAI = "https://api.ashbyhq.com/posting-api/job-board/openai"
NO_SUCH = ("https://boards-api.greenhouse.io/v1/boards/"
           "rithika-js2-no-such-board/jobs")

BOARDS = [
    {"name": "scaleai", "ats": "greenhouse", "url": SCALE},
    {"name": "databricks", "ats": "greenhouse", "url": DATABRICKS},
    {"name": "openai", "ats": "ashby", "url": OPENAI},
    {"name": "rithika-js2-no-such-board", "ats": "greenhouse",
     "url": NO_SUCH},
]
BUDGETS = {"max_boards": 4, "max_requests": 8, "max_run_seconds": 90,
           "max_request_seconds": 20, "max_claude_calls": 0}


def gh_body(ids, total=None):
    """CONSTRUCTED Greenhouse-shaped body."""
    jobs = [{"id": i, "title": f"Constructed role {i}",
             "location": {"name": "Remote"}, "content": "&lt;p&gt;x&lt;/p&gt;",
             "absolute_url": f"https://example.invalid/{i}"} for i in ids]
    return json.dumps({"_comment": "CONSTRUCTED", "jobs": jobs,
                       "meta": {"total": len(ids) if total is None
                                else total}}).encode()


def ashby_body(ids):
    """CONSTRUCTED Ashby-shaped body."""
    jobs = [{"id": i, "title": f"Constructed role {i}", "location": "SF",
             "descriptionHtml": "<p>x</p>",
             "jobUrl": f"https://example.invalid/{i}"} for i in ids]
    return json.dumps({"_comment": "CONSTRUCTED", "apiVersion": "1",
                       "jobs": jobs}).encode()


NOT_FOUND = b'{"status":404,"error":"Job not found"}'


def ok(body):
    return transport.Response(200, body)


def status(code, body=b"", headers=None):
    return transport.Response(code, body, headers or {})


def default_script():
    return {SCALE: [ok(gh_body([1, 2, 3]))],
            DATABRICKS: [ok(gh_body([10, 11]))],
            OPENAI: [ok(ashby_body(["a-1", "a-2"]))],
            NO_SUCH: [status(404, NOT_FOUND)]}


class FakeClock:
    def __init__(self):
        self.now = 1000.0
        self.sleeps = []

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


class FakeTransport:
    """Serves scripted responses per URL; the last one repeats.

    An entry may be a Response or an exception instance to raise.
    `seconds_per_call` advances the fake clock to simulate slow requests.
    """

    def __init__(self, script, clock=None, seconds_per_call=0.0):
        self.script = {url: list(items) for url, items in script.items()}
        self.calls = []
        self.clock = clock
        self.seconds_per_call = seconds_per_call

    def __call__(self, method, url, headers, timeout):
        self.calls.append({"method": method, "url": url,
                           "headers": dict(headers), "timeout": timeout})
        if self.clock is not None:
            self.clock.now += self.seconds_per_call
        items = self.script.get(url)
        if not items:
            raise AssertionError(f"unscripted request to {url}")
        index = sum(1 for c in self.calls if c["url"] == url) - 1
        item = items[min(index, len(items) - 1)]
        if isinstance(item, Exception):
            raise item
        return transport.Response(item.status, item.body, item.headers, url)

    def count(self, url):
        return sum(1 for c in self.calls if c["url"] == url)


def make_root(tmp, boards=None, budgets=None, resume_text=None):
    root = Path(tmp)
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "data").mkdir(exist_ok=True)
    (root / "out").mkdir(exist_ok=True)
    (root / "config" / "boards.json").write_text(
        json.dumps({"boards": BOARDS if boards is None else boards}))
    (root / "config" / "budgets.json").write_text(
        json.dumps(BUDGETS if budgets is None else budgets))
    if resume_text is None:
        shutil.copy(ROOT / "data" / "resume.example.json",
                    root / "data" / "resume.example.json")
    else:
        (root / "data" / "resume.example.json").write_text(resume_text)
    return root


def run(root, fake=None, run_id="RUN1", clock=None, replay_dir=None,
        mode=None):
    clock = clock or FakeClock()
    runner = loop.Runner(root=root, transport=fake, replay_dir=replay_dir,
                         clock=clock, sleep=clock.sleep, run_id=run_id,
                         mode=mode)
    return runner.run(), runner


def summary(root, run_id="RUN1"):
    return json.loads((Path(root) / "out" / "runs" / run_id /
                       "summary.json").read_text())


def report(root, run_id="RUN1"):
    return (Path(root) / "out" / "runs" / run_id / "report.md").read_text()


def trace(root, run_id="RUN1"):
    path = Path(root) / "out" / "runs" / run_id / "trace.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()]


def board(summary_data, name):
    return next(b for b in summary_data["boards"] if b["name"] == name)


def state_path(root, name, seeded=False):
    base = Path(root) / "out" / "state"
    return (base / "seeded" if seeded else base) / f"{name}.json"


def write_state(root, name, ids, seeded=False):
    path = state_path(root, name, seeded)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"board": name, "updated": "EARLIER",
                                "mode": "LIVE",
                                "seen_ids": [str(i) for i in ids]}))
    return path
