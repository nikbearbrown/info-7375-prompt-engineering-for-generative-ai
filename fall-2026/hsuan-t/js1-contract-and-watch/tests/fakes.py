"""Fake board data, a fake network and a fake Claude for the tests, so no test ever touches the real
Stripe board, the Claude API, the repo's state/ runs/ evidence/ folders, or the internet.

Shared here (not copied into each test file) so every Wrong-version test builds postings the same
way the real Greenhouse API sends them: HTML escaped once inside "content", location under "name".
"""

import html
import json
from datetime import datetime, timedelta, timezone

from job_agent.common.paths import Paths
from job_agent.judges.claude import Reply
from job_agent.pipeline import run

# A posting the demo profile accepts at every check: target role, US location, a résumé skill
# (Java), 2 years (≤ 2 + 2), no "no sponsorship" phrase, no salary. Tests change one field at a
# time from here, so the check that cuts it is the one the test is about.
GOOD = {
    "title": "Backend Engineer, Payments",
    "location": "US-Remote",
    "content": "<p>You will build APIs in Java.</p><p>2+ years of experience.</p>",
}

# Cut at check 1a ("senior" is an exclude word) — the opposite verdict of GOOD.
SENIOR = {**GOOD, "title": "Senior Backend Engineer, Payments"}

START = datetime(2026, 10, 31, 12, 0, 0, tzinfo=timezone.utc)


def job(posting_id: int, title: str = GOOD["title"], location: str = GOOD["location"],
        content: str = GOOD["content"]) -> dict:
    """One job as Greenhouse sends it: the JD's HTML arrives escaped (&lt;p&gt;), which strip_html must undo."""
    return {"id": posting_id, "title": title, "location": {"name": location}, "content": html.escape(content)}


def board(*jobs: dict) -> bytes:
    return json.dumps({"jobs": list(jobs), "meta": {"total": len(jobs)}}).encode()


class FakeFetcher:
    """Stands in for net.http_get: returns a given body and remembers every URL it was asked for,
    so a test can prove a run stopped *before* fetching."""

    def __init__(self, body: bytes = b'{"jobs": []}'):
        self.body = body
        self.urls: list[str] = []

    def __call__(self, url: str) -> tuple[bytes, str]:
        self.urls.append(url)
        return self.body, "HTTP 200\nContent-Type: application/json\n"


def good_answer(posting: dict) -> dict:
    """A reply that passes every validator row: it quotes the title Claude was shown."""
    return {"posting_id": posting["posting_id"], "verdict": "relevant", "justification": [
        {"posting_field": "title", "compared_to": "profile.target_roles[]",
         "result": "a backend role", "quote": posting["title"]}]}


class FakeClaude:
    """Stands in for claude_api.make_ask(): answer(posting) builds the reply, so each test decides
    what "Claude" says; it also remembers which postings were sent (to check the test cap)."""

    def __init__(self, answer=good_answer, stop_reason: str = "end_turn"):
        self.answer = answer
        self.stop_reason = stop_reason
        self.sent: list[int] = []

    def __call__(self, system: str, user: str) -> Reply:
        posting = json.loads(user)["posting"]
        self.sent.append(posting["posting_id"])
        reply = self.answer(posting)
        text = reply if isinstance(reply, str) else json.dumps(reply)
        return Reply(text, self.stop_reason, {"model": "fake"})


def run_once(paths: Paths, body: bytes, n: int = 0, resume=None, profile=None, ask=None) -> dict:
    """One full pipeline run on a fake board; returns the verdicts.json it wrote.

    n shifts the clock by n seconds because run folders are named by the second and the pipeline
    refuses two runs in the same second.
    """
    outcome = run("stripe", resume or paths.default_resume, profile or paths.default_profile, paths,
                  now=START + timedelta(seconds=n), fetcher=FakeFetcher(body), ask=ask or FakeClaude())
    return json.loads((outcome.folder / "verdicts.json").read_text())


def by_id(doc: dict, judge: str = "rule") -> dict[int, dict]:
    """One judge's verdicts by posting id; verdicts.json holds both judges' verdicts for each posting."""
    return {v["posting_id"]: v for v in doc["verdicts"] if v["judge"] == judge}
