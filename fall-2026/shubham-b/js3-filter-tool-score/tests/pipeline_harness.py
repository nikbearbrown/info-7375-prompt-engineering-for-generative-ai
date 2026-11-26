"""A temporary project wired to the real pipeline collaborators.

Real: ``GreenhouseProvider``, ``rule.verdict.evaluate``, ``validate_rule_evidence``,
the résumé gate, ``fsio.OutputRoot`` on the temporary ``data/``, the allow-listed
fetcher (over an ``httpx`` mock transport), and the judge (``CliJudge`` with prompt
v1) over a scripted ``FakeBackend``. Only git is a fake (``FakeGit``).

Response variants are built in memory from the committed hand-check bytes; every such
variant is CONSTRUCTED (so named here) and is never written to ``evidence/``.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Any

import httpx

from job_search_agent.config import AgentConfig, load_config
from job_search_agent.events import EventLog
from job_search_agent.evidence_validator import validate_rule_evidence
from job_search_agent.fsio import OutputRoot, ReadPolicy, create_output_root
from job_search_agent.http import build_fetcher_from_settings
from job_search_agent.judge.judge import CliJudge
from job_search_agent.judge.prompt import load_prompt
from job_search_agent.judge.rawlog import RawReplyLog
from job_search_agent.models import RuleVerdict, VerifiedResume
from job_search_agent.pipeline import RunDeps
from job_search_agent.ports import RawSource
from job_search_agent.privacy import scan_text, scan_tree, sensitive_values
from job_search_agent.providers.greenhouse import GreenhouseProvider
from job_search_agent.resume import load_verified_resume
from job_search_agent.rule.verdict import evaluate
from job_search_agent.sources import LiveSource, ReplaySource
from tests.conftest import (
    FIXED_START,
    HANDCHECK_META_REL,
    HANDCHECK_RAW_REL,
    REPO_ROOT,
    RESUME_FIXTURE_REL,
)
from tests.fakes import (
    FakeBackend,
    FakeGit,
    FixedClock,
    RecordingTransport,
    Reply,
    mock_transport,
)

JOBS_URL = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"
CONSTRUCTED_ID = 999000001
"""ID of the posting added to constructed variants of the hand-check response."""
COMMIT = "a" * 40

PROJECT_FILES = (
    "config/agent.toml",
    ".gitignore",
    "prompts/judge.v1.md",
    HANDCHECK_RAW_REL,
    HANDCHECK_META_REL,
    RESUME_FIXTURE_REL,
)

VALID_REPLY = json.dumps(
    {
        "label": "RELEVANT",
        "summary": "Constructed fake reply for tests.",
        "evidence": [
            {
                "resume_path": "$.skills.languages[0]",
                "posting_path": "$.content",
                "reason": "constructed",
            }
        ],
        "uncertainties": [],
    }
)

Validate = Callable[[RuleVerdict, Mapping[str, Any], Mapping[str, Any]], list[str]]


# --- constructed responses --------------------------------------------------------


def handcheck_body() -> bytes:
    """The committed §13 raw response bytes."""
    return (REPO_ROOT / HANDCHECK_RAW_REL).read_bytes()


def constructed_with_added_posting(body: bytes, *, title: str) -> bytes:
    """CONSTRUCTED variant: the hand-check response plus one new posting."""
    obj = json.loads(body)
    extra = dict(obj["jobs"][0])
    extra["id"] = CONSTRUCTED_ID
    extra["title"] = title
    extra["location"] = {"name": "New York, NY, US"}
    extra["content"] = "&lt;p&gt;We use TypeScript and React and Python.&lt;/p&gt;"
    obj["jobs"].append(extra)
    obj["meta"]["total"] = len(obj["jobs"])
    return json.dumps(obj).encode("utf-8")


def constructed_without(body: bytes, posting_id: int) -> bytes:
    """CONSTRUCTED variant: the response with one posting removed."""
    obj = json.loads(body)
    obj["jobs"] = [j for j in obj["jobs"] if j.get("id") != posting_id]
    obj["meta"]["total"] = len(obj["jobs"])
    return json.dumps(obj).encode("utf-8")


# --- failure injection ------------------------------------------------------------


class InjectingRoot(OutputRoot):
    """The real ``OutputRoot`` with write-failure injection and an access log.

    Args:
        root: The data directory.
        fail_writes: Data-root rels (or a trailing file name such as
            ``"records.json"``) whose writes raise ``OSError``.

    Attributes:
        writes: Every atomic write's rel, in order.
        reads: Every read's rel, in order.
    """

    def __init__(self, root: Path, *, fail_writes: set[str] | None = None) -> None:
        super().__init__(root)
        self.fail_writes = fail_writes or set()
        self.writes: list[str] = []
        self.reads: list[str] = []

    def write_bytes_atomic(self, rel: str, data: bytes) -> Path:
        if any(rel == f or rel.endswith("/" + f) for f in self.fail_writes):
            raise OSError(f"injected write failure: {rel}")
        self.writes.append(rel)
        return super().write_bytes_atomic(rel, data)

    def read_bytes(self, rel: str) -> bytes:
        self.reads.append(rel)
        return super().read_bytes(rel)


# --- harness ----------------------------------------------------------------------


@dataclass
class Harness:
    """A temporary project copy; ``deps`` wires one run of the real pipeline."""

    root: Path
    config: AgentConfig
    out: OutputRoot
    clock: FixedClock
    git: FakeGit
    backend: FakeBackend
    terminal_lines: list[str] = field(default_factory=list)
    transports: list[RecordingTransport] = field(default_factory=list)
    events: list[EventLog] = field(default_factory=list)

    @classmethod
    def create(cls, root: Path, *, backend: FakeBackend | None = None) -> Harness:
        """Copies the config, prompt, evidence and fixture into ``root``."""
        for rel in PROJECT_FILES:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / rel, root / rel)
        config = load_config(root / "config" / "agent.toml")
        return cls(
            root=root,
            config=config,
            out=create_output_root(config.data_dir),
            clock=FixedClock(FIXED_START, step=timedelta(seconds=1)),
            git=FakeGit(head_commit=COMMIT),
            backend=backend if backend is not None else FakeBackend(),
        )

    def set_backend(self, backend: FakeBackend) -> None:
        """Scripts the model replies of the next judged postings."""
        self.backend = backend

    def judge(self) -> CliJudge:
        """The real judge (prompt v1, raw-reply logs) over the scripted backend."""
        return CliJudge(
            self.backend,
            load_prompt(self.root, self.config.model.prompt_version),
            RawReplyLog(self.out, repo_rel=self.config.repo_rel),
            model_requested=self.config.model.model_id,
        )

    def resume(self) -> VerifiedResume:
        """The project's fixture, through the real résumé gate."""
        return load_verified_resume(
            self.config.resume_path,
            self.config.resume.pinned_sha256,
            read_bytes=ReadPolicy(self.root).read_bytes,
            project_root=self.root,
        )

    def live_source(self, reply: Reply) -> LiveSource:
        """The allow-listed fetcher, serving ``reply`` for the board URL."""
        return self._live({JOBS_URL: reply})

    def failing_source(self) -> LiveSource:
        """A board whose every request fails at the transport (no body)."""

        def refuse(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("constructed transport failure", request=request)

        return self._live(refuse)

    def _live(self, routes: Any) -> LiveSource:  # noqa: ANN401 - mock_transport routes
        transport = mock_transport(routes)
        self.transports.append(transport)
        fetcher = build_fetcher_from_settings(self.config.http, inner=transport)
        return LiveSource(fetcher, JOBS_URL)

    def replay_source(self, repo_rel: str = HANDCHECK_RAW_REL) -> ReplaySource:
        """Replays a saved raw file through the read policy."""
        return ReplaySource(
            self.root / repo_rel, repo_rel, read_bytes=ReadPolicy(self.root).read_bytes
        )

    def deps(
        self,
        source: RawSource,
        *,
        seeded: bool = False,
        use_judge: bool = True,
        load_resume: Callable[[], VerifiedResume] | None = None,
        validate: Validate = validate_rule_evidence,
        out: OutputRoot | None = None,
    ) -> RunDeps:
        """The run's dependencies; keyword arguments inject one failure each."""
        log = EventLog()
        self.events.append(log)
        read = ReadPolicy(self.root).read_bytes
        return RunDeps(
            config=self.config,
            clock=self.clock,
            source=source,
            provider=GreenhouseProvider(),
            load_resume=load_resume or self.resume,
            evaluate=evaluate,
            validate_evidence=validate,
            judge=self.judge() if use_judge else None,
            out=out if out is not None else self.out,
            git=self.git,
            events=log,
            seeded=seeded,
            read_repo_file=lambda rel: read(self.root / rel),
            terminal=self.terminal_lines.append,
        )

    def data(self, rel: str) -> Path:
        """Absolute path of a data-relative file."""
        return self.config.data_dir / rel

    def run_dir(self, run_id: str, *, seeded: bool = False) -> Path:
        """The run folder of ``run_id``."""
        return self.data(f"{'seeded' if seeded else 'live'}/runs/{run_id}")

    def all_output_text(self) -> str:
        """Every output file except the saved raw board, plus the terminal text."""
        parts = [
            p.read_text(encoding="utf-8", errors="replace")
            for p in sorted(self.config.data_dir.rglob("*"))
            if p.is_file() and p.name != "greenhouse-stripe.json"
        ]
        return "\n".join(parts + self.terminal_lines)

    def privacy_findings(self) -> list[str]:
        """The privacy scanner's findings over ``data/`` and the terminal text."""
        values = sensitive_values(self.resume())
        findings = scan_tree(self.config.data_dir, values)
        findings += scan_text("\n".join(self.terminal_lines), values)
        return [f.describe() for f in findings]
