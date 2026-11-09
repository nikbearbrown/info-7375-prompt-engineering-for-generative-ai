"""CONSTRUCTED test doubles: fake boards, a fake network and a fake clock. Nothing here is a real response."""
import json
import shutil
import tempfile
from pathlib import Path

from agent import config, loop, resume, tools
from agent.policy import Policy

HOSTS = ["boards-api.greenhouse.io", "api.lever.co", "api.ashbyhq.com"]
BUDGETS = {"max_boards": 5, "max_requests": 10, "max_seconds": 60, "request_timeout_seconds": 10, "retry_wait_seconds": 2}
PERSONA = resume.load(config.RESUME)


def greenhouse(*ids, title="Software Engineer", content="&lt;p&gt;Python and AWS&lt;/p&gt;"):
    return json.dumps({"jobs": [{"id": i, "title": title, "location": {"name": "Remote, US"}, "content": content,
                                 "absolute_url": f"https://example.invalid/{i}"} for i in ids]}).encode()


def lever(*ids):
    return json.dumps([{"id": i, "text": "Backend Engineer", "categories": {"location": "New York"}, "country": "US",
                        "description": "<p>Python and Kafka</p>", "lists": [], "hostedUrl": f"https://example.invalid/{i}"}
                       for i in ids]).encode()


def ashby(*ids):
    return json.dumps({"jobs": [{"id": i, "title": "Software Engineer", "location": "Remote",
                                 "address": {"postalAddress": {"addressCountry": "United States"}},
                                 "descriptionHtml": "<p>TypeScript and AWS</p>", "jobUrl": f"https://example.invalid/{i}",
                                 "isListed": True} for i in ids]}).encode()


LEVER_404 = json.dumps({"ok": False, "error": "Document not found"}).encode()


class FakeNet:
    """Answers each URL from a queue of (status, body) pairs or exceptions, and records every call."""

    def __init__(self, answers):
        self.answers = {url: list(queue) for url, queue in answers.items()}
        self.calls = []

    def __call__(self, url, timeout):
        self.calls.append(url)
        answer = self.answers[url].pop(0) if len(self.answers[url]) > 1 else self.answers[url][0]
        if isinstance(answer, Exception):
            raise answer
        status, body = answer
        return tools.Response(status, body, url)


class FakeClock:
    def __init__(self, step=0.1):
        self.now, self.step, self.slept = 0.0, step, []

    def __call__(self):
        self.now += self.step
        return self.now

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.now += seconds


class Project:
    """A temporary folder that stands in for this project, with its own runs/ and evidence/."""

    def __init__(self, testcase):
        self.root = Path(tempfile.mkdtemp())
        testcase.addCleanup(shutil.rmtree, self.root)
        for d in ("runs", "evidence/raw", "config"):
            (self.root / d).mkdir(parents=True)
        self.policy = Policy(root=self.root, hosts=HOSTS)

    def run(self, boards, net, state=None, budgets=None, clock=None, hooks=None, now=None, tag=""):
        clock = clock or FakeClock()
        state = {} if state is None else state
        result = loop.run(boards, budgets or BUDGETS, self.policy, PERSONA, state, self.root / "evidence" / "raw",
                          now=now, get=net, clock=clock, sleep=clock.sleep, hooks=hooks, tag=tag)
        run_dir = self.root / "runs" / f"{result.started_at.replace('-', '').replace(':', '')}{tag}"
        self.policy.write_text(run_dir / "report.json", json.dumps(loop.summary(result)))
        return result, state, run_dir


def url(system, name):
    from agent import ats
    return ats.board_url(system, name)
