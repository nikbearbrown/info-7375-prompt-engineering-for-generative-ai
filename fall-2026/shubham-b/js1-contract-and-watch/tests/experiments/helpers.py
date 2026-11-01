"""Harness for experiment tests: a temporary repo, a fake git, synthetic strata."""

from __future__ import annotations

import json
import shutil
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from job_search_agent.experiments._calls import FirstReplyJudge
from job_search_agent.experiments._io import ExperimentContext
from job_search_agent.experiments.selection import HANDCHECK_IDS
from job_search_agent.judge.prompt import PromptContract, load_prompt
from job_search_agent.judge.rawlog import RawReplyLog
from job_search_agent.models import (
    Gate,
    LocationCheck,
    LocationLabel,
    Posting,
    RuleVerdict,
    SkillEvidence,
    VerdictLabel,
)
from tests.conftest import REPO_ROOT
from tests.fakes import FakeBackend, FakeGit, FixedClock
from tests.judge.doubles import MemoryWriter
from tests.tools.builders import fixture_resume, small_posting

_FALLBACK_PREFIXES = ("evidence/", "persona/")


class OverlayReader:
    """Reads from the temp repo, falling back to the real repo for evidence/persona."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def _path(self, rel: str) -> Path:
        local = self.root / rel
        if not local.exists() and rel.startswith(_FALLBACK_PREFIXES):
            return REPO_ROOT / rel
        return local

    def read_bytes(self, rel: str) -> bytes:
        return self._path(rel).read_bytes()

    def exists(self, rel: str) -> bool:
        return self._path(rel).is_file()


@dataclass
class Repo:
    """A temporary project tree wired into an ``ExperimentContext``."""

    root: Path
    git: FakeGit
    writer: MemoryWriter
    ctx: ExperimentContext
    backend_script: list[Any] = field(default_factory=list)

    def write(self, rel: str, content: str | bytes | Mapping[str, Any]) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        elif isinstance(content, str):
            path.write_text(content, encoding="utf-8")
        else:
            path.write_text(json.dumps(content, indent=2), encoding="utf-8")

    def commit(self, *rels: str) -> None:
        self.git.clean_tracked.update(rels)

    def data(self, rel: str) -> Any:
        return json.loads((self.root / "data" / rel).read_text(encoding="utf-8"))

    def load_prompt(self, version: str) -> PromptContract:
        return load_prompt(self.root, version)


def make_repo(tmp_path: Path) -> Repo:
    root = tmp_path / "repo"
    (root / "data").mkdir(parents=True)
    (root / "prompts").mkdir()
    shutil.copy(REPO_ROOT / "prompts/judge.v1.md", root / "prompts/judge.v1.md")
    procedure = REPO_ROOT / "experiments/prompt/PROCEDURE.md"
    (root / "experiments/prompt").mkdir(parents=True)
    shutil.copy(procedure, root / "experiments/prompt/PROCEDURE.md")
    (root / "experiments/sampling").mkdir(parents=True)
    # The fixture stays unconfirmed so the "not yet confirmed" path keeps its tests.
    labels = json.loads(
        (REPO_ROOT / "experiments/sampling/hand_labels.json").read_text("utf-8")
    )
    labels["confirmed_by_student"] = None
    (root / "experiments/sampling/hand_labels.json").write_text(
        json.dumps(labels, indent=2), "utf-8"
    )
    git = FakeGit(head_commit="a" * 40)
    writer = MemoryWriter(root / "data")
    clock = FixedClock(
        datetime(2026, 10, 30, 14, 0, tzinfo=UTC), step=timedelta(seconds=1)
    )
    ctx = ExperimentContext(
        writer=writer, reader=OverlayReader(root), git=git, clock=clock
    )
    return Repo(root=root, git=git, writer=writer, ctx=ctx)


# --- synthetic strata --------------------------------------------------------------

_SHAPES: Mapping[str, tuple[VerdictLabel, list[Gate], LocationLabel, int]] = {
    "M": (VerdictLabel.MATCH, [], LocationLabel.US_BASED, 3),
    "N1": (VerdictLabel.NO_MATCH, [Gate.LOCATION], LocationLabel.NON_US, 2),
    "N2": (VerdictLabel.NO_MATCH, [Gate.SKILLS], LocationLabel.US_BASED, 1),
    "N3": (VerdictLabel.NO_MATCH, [Gate.TITLE], LocationLabel.US_BASED, 2),
    "X": (
        VerdictLabel.NO_MATCH,
        [Gate.TITLE, Gate.SKILLS, Gate.LOCATION],
        LocationLabel.NOT_ESTABLISHED,
        0,
    ),
}


def make_verdict(stratum: str) -> RuleVerdict:
    label, gates, location, skills = _SHAPES[stratum]
    return RuleVerdict(
        label=label,
        location_check=LocationCheck(
            label=location, evidence=["$.location.name"], reason="synthetic"
        ),
        evidence=[
            SkillEvidence(
                term=f"T{i}",
                resume_path=f"$.skills.languages[{i}]",
                posting_path="$.content",
            )
            for i in range(skills)
        ],
        reason="synthetic",
        failed_gates=gates,
    )


@dataclass
class Board:
    postings: list[Posting]
    strata: dict[str, str]

    def evaluate(self, posting: Posting) -> RuleVerdict:
        return make_verdict(self.strata[posting.posting_id])

    def by_id(self) -> dict[str, Posting]:
        return {p.posting_id: p for p in self.postings}


def make_board(counts: Mapping[str, int], *, include_handcheck: bool = True) -> Board:
    postings: list[Posting] = []
    strata: dict[str, str] = {}
    next_id = 100001
    for stratum, count in counts.items():
        for _ in range(count):
            pid = str(next_id)
            next_id += 7
            postings.append(
                small_posting(
                    id=int(pid),
                    title=f"Role {pid}",
                    absolute_url=f"https://x.invalid/{pid}",
                )
            )
            strata[pid] = stratum
    if include_handcheck:
        for pid in HANDCHECK_IDS:
            postings.append(small_posting(id=int(pid), title=f"Handcheck {pid}"))
            strata[pid] = "M"
    return Board(postings, strata)


DEFAULT_COUNTS = {"M": 12, "N1": 6, "N2": 7, "N3": 9, "X": 5}


def hand_entry(pid: str, hand_label: str) -> dict[str, Any]:
    """A label entry whose recorded gates are consistent with ``hand_label``."""
    if hand_label == "MATCH":
        skills = [
            {
                "term": "Java",
                "resume_path": "$.skills.languages[2]",
                "posting_path": "$.content",
            },
            {
                "term": "AWS",
                "resume_path": "$.skills.cloud_devops[0]",
                "posting_path": "$.content",
            },
        ]
        return {
            "posting_id": pid,
            "hand_label": "MATCH",
            "title_pass": True,
            "skills": skills,
            "exclusion_phrase": None,
            "location_label": "US_BASED",
            "notes": "",
        }
    return {
        "posting_id": pid,
        "hand_label": "NO_MATCH",
        "title_pass": False,
        "skills": [],
        "exclusion_phrase": None,
        "location_label": "US_BASED",
        "notes": "",
    }


def write_labels(repo: Repo, hand: Mapping[str, str]) -> None:
    selection = repo.data("experiments/prompt/selection.json")
    for set_name in ("dev", "heldout"):
        repo.write(
            f"experiments/prompt/labels/{set_name}.labels.json",
            {
                "set": set_name,
                "labeled_by": "Test Student",
                "labels": [
                    hand_entry(pid, hand[pid]) for pid in selection["sets"][set_name]
                ],
            },
        )


def reply_text(label: str = "RELEVANT") -> str:
    return json.dumps(
        {
            "label": label,
            "summary": "s",
            "evidence": [
                {
                    "resume_path": "$.skills.languages[2]",
                    "posting_path": "$.content",
                    "reason": "r",
                }
            ],
            "uncertainties": [],
        }
    )


def first_reply_judge(
    repo: Repo, script: Iterable[Any]
) -> tuple[FirstReplyJudge, FakeBackend]:
    backend = FakeBackend(list(script))
    judge = FirstReplyJudge(
        backend=backend,
        resume=fixture_resume(),
        rawlog=RawReplyLog(repo.writer),
        model_requested="claude-sonnet-5-5",
    )
    return judge, backend
