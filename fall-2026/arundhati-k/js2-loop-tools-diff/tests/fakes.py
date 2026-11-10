"""Constructed responses for offline tests. These are NOT real board responses."""

import json
import tempfile
from pathlib import Path

from jsagent2.transport import TransientError


def gh_body(n, start=1):
    return json.dumps({"jobs": [{"id": start + i, "title": f"Engineer {start + i}", "location": {"name": "Remote"},
                                 "absolute_url": f"https://example.invalid/{start + i}", "updated_at": "2026-11-01"}
                                for i in range(n)], "meta": {"total": n}}).encode()


def ashby_body(n):
    return json.dumps({"jobs": [{"id": f"a-{i}", "title": f"Engineer {i}", "location": "Remote",
                                 "jobUrl": f"https://example.invalid/a-{i}", "publishedAt": "2026-11-01"}
                                for i in range(n)]}).encode()


class ScriptedTransport:
    """Returns scripted outcomes per URL substring, in order. An outcome is (status, body) or an exception."""

    def __init__(self, script):
        self.script = {k: list(v) for k, v in script.items()}
        self.calls = []

    def __call__(self, url, timeout):
        self.calls.append(url)
        for key, outcomes in self.script.items():
            if key in url:
                outcome = outcomes.pop(0) if len(outcomes) > 1 else outcomes[0]
                if isinstance(outcome, Exception):
                    raise outcome
                return outcome
        raise AssertionError(f"unscripted url {url}")


class FakeClock:
    def __init__(self, step=0.0):
        self.t, self.step = 0.0, step
        self.slept = []

    def now(self):
        self.t += self.step
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


def timeout():
    return TransientError("timeout")


def tmp_root():
    root = Path(tempfile.mkdtemp()) / "proj"
    (root / "out").mkdir(parents=True)
    return root


BOARDS = [
    {"name": "Stripe", "ats": "greenhouse", "slug": "stripe"},
    {"name": "Figma", "ats": "greenhouse", "slug": "figma"},
    {"name": "Notion", "ats": "ashby", "slug": "notion"},
]
BUDGETS = {"max_boards": 5, "max_requests": 8, "max_seconds": 120, "request_timeout_seconds": 30, "retry_delay_seconds": 2}
