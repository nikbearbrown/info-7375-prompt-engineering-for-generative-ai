"""Test fixtures: a throwaway project root for the policy, and a scripted fetch so no test touches the network."""
from __future__ import annotations

import contextlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent2 import loop, policy  # noqa: E402

BUDGETS = {"boards": 4, "requests": 12, "seconds": 120}
EMPTY_SR = json.dumps({"offset": 0, "limit": 100, "totalFound": 0, "content": []}).encode()


def gh_body(n: int) -> bytes:
    return json.dumps({"jobs": [{"id": i, "title": f"Job {i}", "location": {"name": "SF"}} for i in range(n)],
                       "meta": {"total": n}}).encode()


def sr_body(ids, total=None) -> bytes:
    ids = list(ids)
    return json.dumps({"offset": 0, "limit": 100, "totalFound": len(ids) if total is None else total,
                       "content": [{"id": str(i), "name": f"Job {i}", "location": {"fullLocation": "Sydney"}} for i in ids]}).encode()


@contextlib.contextmanager
def temp_root():
    """Point the policy at a fresh folder laid out like the real one (config/, evidence/runs/, GATE.md)."""
    tmp = Path(tempfile.mkdtemp(prefix="js2t")).resolve()
    (tmp / "config").mkdir()
    (tmp / "config" / "boards.json").write_text("{}", encoding="utf-8")
    (tmp / "evidence" / "runs").mkdir(parents=True)
    (tmp / "GATE.md").write_text("gate", encoding="utf-8")
    saved = policy.ROOT, policy.WRITE_ROOT
    policy.ROOT, policy.WRITE_ROOT = tmp, tmp / "evidence" / "runs"
    try:
        yield tmp
    finally:
        policy.ROOT, policy.WRITE_ROOT = saved
        shutil.rmtree(tmp, ignore_errors=True)


class FakeFetch:
    """url -> list of scripted results, consumed in order (the last repeats). A result is (status, body),
    the string 'timeout', or an exception instance to raise."""

    def __init__(self, script: dict):
        self.script, self.calls = script, []

    def __call__(self, url, timeout):
        policy.check_url(url)                       # the real tool checks policy first; so does the fake
        self.calls.append(url)
        seq = self.script[url]
        res = seq[min(sum(1 for c in self.calls if c == url) - 1, len(seq) - 1)]
        if res == "timeout":
            raise TimeoutError("scripted timeout")
        if isinstance(res, Exception):
            raise res
        return res


class FakeClock:
    def __init__(self, step=0.0):
        self.t, self.step = 0.0, step

    def __call__(self):
        self.t += self.step
        return self.t

    def sleep(self, s):
        self.t += s


def board(provider, slug, company=None):
    return {"company": company or slug, "provider": provider, "slug": slug}


_ids = iter(range(1, 10_000))


def run(boards, script, budgets=BUDGETS, clock=None, run_id=None):
    """Each run gets its own run id: reusing one would overwrite evidence, which the policy refuses."""
    run_id = run_id or f"2026-11-11T00-00-{next(_ids):04d}Z"
    fetch, clock = FakeFetch(script), clock or FakeClock()
    s = loop.run({"budgets": budgets, "boards": boards}, fetch=fetch, clock=clock, sleep=clock.sleep,
                 run_id=run_id, log=lambda *a: None)
    return s, fetch


GH = "https://boards-api.greenhouse.io/v1/boards/{}/jobs"
SR = "https://api.smartrecruiters.com/v1/companies/{}/postings?limit=100&offset={}"
