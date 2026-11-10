"""Test doubles for the loop (GATE.md). Every board answer built here is a CONSTRUCTED fixture.

A temporary repo holds runs/, state/, persona/, prompts/ and the board list; FakeNet stands in for
fetch.get_board and records every URL asked for; StubJudges uses the real rule and a stand-in for
Claude; the clocks are under the test's control. Nothing here touches the network or Claude.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from job_agent import policy, rule
from job_agent.errors import BoardNoAnswer
from job_agent.fetch import Response

REPO = Path(__file__).resolve().parent.parent
URLS = {
    ("ashby", "openai"): "https://api.ashbyhq.com/posting-api/job-board/openai",
    ("greenhouse", "verkada"): "https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true",
    ("lever", "palantir"): "https://api.lever.co/v0/postings/palantir?mode=json",
    ("greenhouse", "no-such-board-js2-test"):
        "https://boards-api.greenhouse.io/v1/boards/no-such-board-js2-test/jobs?content=true",
}


def url(system, name):
    return URLS.get((system, name)) or {
        "ashby": f"https://api.ashbyhq.com/posting-api/job-board/{name}",
        "greenhouse": f"https://boards-api.greenhouse.io/v1/boards/{name}/jobs?content=true",
        "lever": f"https://api.lever.co/v0/postings/{name}?mode=json"}[system]


def ashby_job(i, title="Software Engineer, Example Team", **extra):
    data = {"id": i, "title": title, "employmentType": "FullTime", "location": "San Francisco",
            "secondaryLocations": [], "workplaceType": "Hybrid", "jobUrl": f"https://jobs.ashbyhq.com/openai/{i}",
            "address": {"postalAddress": {"addressCountry": "United States", "addressRegion": "California",
                                          "addressLocality": "San Francisco"}},
            "descriptionPlain": "A constructed test posting."}
    data.update(extra)
    return data


def greenhouse_job(i, title="Backend Software Engineer", place="San Mateo, CA United States"):
    return {"id": i, "title": title, "location": {"name": place}, "absolute_url": f"https://example.com/gh/{i}",
            "metadata": [{"name": "Employment Type", "value": "Full-Time"}],
            "content": "&lt;p&gt;A constructed test posting.&lt;/p&gt;"}


def lever_job(i, title="Software Engineer - Example", place="New York, NY"):
    return {"id": i, "text": title, "hostedUrl": f"https://jobs.lever.co/palantir/{i}", "country": "US",
            "workplaceType": "hybrid", "categories": {"commitment": "Full-time", "location": place,
                                                      "allLocations": [place]},
            "descriptionPlain": "A constructed test posting.", "lists": [], "additionalPlain": ""}


def body(system, jobs) -> bytes:
    if system == "lever":
        return json.dumps(jobs).encode("utf-8")
    return json.dumps({"_fixture": "CONSTRUCTED TEST FIXTURE", "jobs": jobs}).encode("utf-8")


def answer(system, name, jobs=None, status=200, raw=None) -> Response:
    data = raw if raw is not None else body(system, jobs or [])
    return Response(url=url(system, name), status=status, headers={"Content-Type": "application/json"},
                    body=data, received_at="2026-11-07T12:00:00Z")


class FakeNet:
    """Stands in for fetch.get_board: per URL, a list of answers (or exceptions) handed out in order."""

    def __init__(self, plan=None):
        self.plan = {k: list(v) for k, v in (plan or {}).items()}
        self.calls = []

    def __call__(self, target, timeout=None):
        self.calls.append(target)
        queue = self.plan.get(target) or []
        if not queue:
            raise AssertionError(f"FakeNet: nothing planned for {target}")
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    def count(self, target):
        return self.calls.count(target)


def timeout():
    return BoardNoAnswer("no answer from the board (timeout: timed out)", transient=True)


class StubJudges:
    """The real rule; a stand-in for Claude that records each call and answers not_relevant."""

    model = "stub-model"

    def __init__(self, prompt: Path):
        self.prompt = prompt
        self.claude_calls = []

    def rule_verdict(self, job, resume):
        return rule.judge(job, resume)

    def claude_verdict(self, job, resume, record_dir):
        self.claude_calls.append(job["id"])
        return {"judge": "claude", "label": "judgment", "verdict": "not_relevant", "valid": True,
                "record": f"claude/stub-{job['id']}.json", "lines": ["stand-in Claude verdict (test)"]}

    def describe(self):
        return {"file": self.prompt.name, "sha256": "0" * 64, "model": self.model}


class Clock:
    """monotonic(): moves `step` seconds per call, or jumps when the test says so."""

    def __init__(self, step=0.0):
        self.t, self.step = 1000.0, step

    def __call__(self):
        self.t += self.step
        return self.t


class Workspace:
    """A temporary repo with the folders the loop reads and writes, and the policy over it."""

    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="job-agent-loop-"))
        for folder in ("runs", "state", "persona", "prompts"):
            (self.root / folder).mkdir()
        shutil.copy(REPO / "persona" / "jane-doe.json", self.root / "persona" / "jane-doe.json")
        (self.root / "prompts" / "baseline.txt").write_text("stand-in prompt\n", encoding="utf-8")
        self.files = policy.Files(self.root, write_roots=["runs", "state"],
                                  read_roots=["persona", "prompts", "boards.json", "boards", "state", "runs"])
        self.judges = StubJudges(self.root / "prompts" / "baseline.txt")
        self.screen = []
        self.sleeps = []
        self.hour = 0

    def boards(self, *entries):
        items = []
        for entry in entries:
            item = {"system": entry[0], "name": entry[1]}
            if len(entry) > 2:
                item.update(entry[2])
            items.append(item)
        (self.root / "boards.json").write_text(json.dumps({"boards": items}), encoding="utf-8")

    def now(self):
        return datetime(2026, 11, 7, 12 + self.hour, 0, 0, tzinfo=timezone.utc)

    def run(self, net, budgets=None, approve=None, monotonic=None, replay=None, state="state", runs="runs"):
        from job_agent import loop
        self.hour += 1
        return loop.run(boards_path=self.root / "boards.json", resume_path=self.root / "persona" / "jane-doe.json",
                        state_root=self.root / state, runs_root=self.root / runs, files=self.files,
                        judges=self.judges, budgets=budgets, approve=approve, replay=replay, get=net,
                        now=self.now, monotonic=monotonic or Clock(), sleep=self.sleeps.append,
                        say=self.screen.append)

    def state(self, system, name):
        path = self.root / "state" / f"{system}-{name}.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def run_dirs(self):
        return sorted(p for p in (self.root / "runs").iterdir() if p.is_dir())

    def trace(self, run_dir):
        return [json.loads(line) for line in (run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()]

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)
