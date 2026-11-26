"""Shared harness for the watch-loop tests: a temporary project, CONSTRUCTED boards."""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path
from typing import Any

import httpx

from job_search_agent.config import AgentConfig, load_config
from job_search_agent.events import EventLog
from job_search_agent.evidence_validator import validate_rule_evidence
from job_search_agent.fsio import ReadPolicy, create_output_root
from job_search_agent.pipeline import RunDeps
from job_search_agent.policy import PermissionPolicy
from job_search_agent.providers import get_provider
from job_search_agent.resume import load_verified_resume
from job_search_agent.rule.verdict import evaluate
from job_search_agent.watch import (
    LoopDeps,
    LoopReport,
    WatchPlan,
    build_policy,
    run_loop,
)
from tests.conftest import FIXED_START, REPO_ROOT, RESUME_FIXTURE_REL
from tests.fakes import FakeGit, FixedClock, RecordingTransport, mock_transport
from tests.tools.builders import job

GH = "https://boards-api.greenhouse.io/v1/boards/{}/jobs?content=true"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/{}"
UUID = "34413f8d-26bf-4bbc-8ade-eb309a0e2245"
UUID_NEW = "8fb1615c-34bf-47c4-a1d1-b7b2f836bbd3"

Handler = Callable[[httpx.Request], httpx.Response]


def gh_body(*ids: int) -> bytes:
    jobs = [job(id=i, content="&lt;p&gt;Java and Python on AWS&lt;/p&gt;") for i in ids]
    return json.dumps({"jobs": jobs, "meta": {"total": len(jobs)}}).encode()


def ashby_body(*ids: str) -> bytes:
    jobs = [
        {
            "id": i,
            "title": "Software Engineer",
            "location": "New York, NY",
            "department": "Engineering",
            "descriptionHtml": "<p>TypeScript, PostgreSQL and Docker</p>",
        }
        for i in ids
    ]
    return json.dumps({"jobs": jobs, "apiVersion": "1"}).encode()


def ok(body: bytes) -> Handler:
    return lambda _request: httpx.Response(200, content=body)


def status(code: int) -> Handler:
    return lambda _request: httpx.Response(code, content=b'{"error":"x"}')


def sequence(*handlers: Handler) -> Handler:
    """Serves the handlers in order, one per request; extra requests fail the test."""
    queue = list(handlers)

    def serve(request: httpx.Request) -> httpx.Response:
        assert queue, "more requests than the test expected"
        return queue.pop(0)(request)

    return serve


def timeout(request: httpx.Request) -> httpx.Response:
    raise httpx.ReadTimeout("constructed timeout", request=request)


class FakeTimer:
    """Seconds clock; tests advance it."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


class Project:
    """A temporary project: the fixture, agent config and a constructed plan."""

    def __init__(self, root: Path) -> None:
        self.root = root
        for rel in ("config/agent.toml", RESUME_FIXTURE_REL, "prompts/judge.v1.md"):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / rel, root / rel)
        self.config: AgentConfig = load_config(root / "config" / "agent.toml")
        self.clock = FixedClock(FIXED_START, step=timedelta(seconds=1))
        self.timer = FakeTimer()
        self.sleeps: list[float] = []
        self.transport: RecordingTransport | None = None

    def plan(
        self,
        boards: list[tuple[str, str]],
        *,
        max_boards: int = 6,
        max_requests: int = 10,
        max_seconds: float = 180,
        hosts: tuple[str, ...] = ("boards-api.greenhouse.io", "api.ashbyhq.com"),
    ) -> WatchPlan:
        return WatchPlan.model_validate(
            {
                "budget": {
                    "max_boards": max_boards,
                    "max_requests": max_requests,
                    "max_seconds": max_seconds,
                },
                "retry": {"max_retries": 1, "pause_s": 2.0, "min_seconds_left": 5.0},
                "policy": {"allowed_hosts": list(hosts), "write_root": "data/watch"},
                "boards": [{"provider": p, "token": t} for p, t in boards],
            }
        )

    def policy(self) -> PermissionPolicy:
        """The policy of a default plan for this project."""
        return build_policy(self.plan([("greenhouse", "stripe")]), self.root)

    def board_deps(self, cfg: AgentConfig) -> RunDeps:
        read = ReadPolicy(cfg.project_root).read_bytes

        def resume() -> Any:  # noqa: ANN401 - VerifiedResume
            return load_verified_resume(
                cfg.resume_path,
                cfg.resume.pinned_sha256,
                read_bytes=read,
                project_root=cfg.project_root,
            )

        return RunDeps(
            config=cfg,
            clock=self.clock,
            source=_NoSource(),
            provider=get_provider(cfg.board.provider),
            load_resume=resume,
            evaluate=evaluate,
            validate_evidence=validate_rule_evidence,
            judge=None,
            out=create_output_root(cfg.data_dir),
            git=FakeGit(),
            events=EventLog(),
            seeded=False,
            read_repo_file=lambda rel: read(cfg.project_root / rel),
        )

    def run(self, plan: WatchPlan, routes: dict[str, Handler]) -> LoopReport:
        self.transport = mock_transport(routes)
        deps = LoopDeps(
            plan=plan,
            base_config=self.config,
            policy=build_policy(plan, self.root),
            clock=self.clock,
            monotonic=self.timer,
            board_deps=self.board_deps,
            transport=self.transport,
            sleep=self.sleeps.append,
        )
        return run_loop(deps)

    def loop_dir(self, report: LoopReport) -> Path:
        return self.root / "data" / "watch" / "loops" / report.loop_id

    def trace(self, report: LoopReport) -> list[dict[str, Any]]:
        lines = (self.loop_dir(report) / "trace.jsonl").read_text().splitlines()
        return [json.loads(line) for line in lines]

    def state(self, board: str) -> Path:
        return self.root / "data/watch/boards" / board / "live/state.json"


class _NoSource:
    def obtain(self) -> Any:  # noqa: ANN401
        raise AssertionError("the loop must replace the board's source")
