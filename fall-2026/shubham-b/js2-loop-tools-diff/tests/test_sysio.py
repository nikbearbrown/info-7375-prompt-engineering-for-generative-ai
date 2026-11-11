"""Subprocess runner, git inspector, event log and sources."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from job_search_agent.events import ABS_PATH_PLACEHOLDER, EventLog
from job_search_agent.fsio import create_output_root
from job_search_agent.models import CompletedCommand, FetchErrorKind
from job_search_agent.sources import (
    EvidenceStatus,
    ReplaySource,
    parse_fetched_at,
    verify_saved_evidence,
)
from job_search_agent.sysio import (
    GitUnavailableError,
    SubprocessGit,
    SubprocessRunner,
    minimal_env,
)
from tests.conftest import HANDCHECK_META_REL, HANDCHECK_RAW_REL, REPO_ROOT
from tests.fakes import FakeRunner


def done(
    stdout: str = "", code: int | None = 0, timed_out: bool = False
) -> CompletedCommand:
    return CompletedCommand((), code, stdout, "", timed_out, 1)


# --- sysio ----------------------------------------------------------------------


def test_git_head_dirty_and_tracked(tmp_path: Path) -> None:
    runner = FakeRunner(
        [
            done("a" * 40 + "\n"),
            done(" M src/x.py\n"),
            done("x"),
            done("", 0),
            done("", 1),
        ]
    )
    git = SubprocessGit(tmp_path, runner=runner)
    assert git.head() == "a" * 40
    assert git.is_dirty() is True
    assert git.is_tracked_and_clean(Path("experiments/SEAL.json")) is True
    assert git.is_tracked_and_clean(Path("x")) is False
    argvs = [c.argv for c in runner.calls]
    assert argvs[0] == ("git", "rev-parse", "HEAD")
    assert argvs[1] == ("git", "status", "--porcelain", "--untracked-files=no")
    assert argvs[2] == (
        "git",
        "ls-files",
        "--error-unmatch",
        "--",
        "experiments/SEAL.json",
    )
    assert argvs[3] == ("git", "diff", "--quiet", "HEAD", "--", "experiments/SEAL.json")
    assert all(c.cwd == tmp_path for c in runner.calls)


def test_git_failures_raise(tmp_path: Path) -> None:
    git = SubprocessGit(tmp_path, runner=FakeRunner([done("fatal", 128)]))
    with pytest.raises(GitUnavailableError):
        git.head()
    git = SubprocessGit(tmp_path, runner=FakeRunner([OSError("no git")]))
    with pytest.raises(GitUnavailableError):
        git.is_dirty()
    git = SubprocessGit(tmp_path, runner=FakeRunner([done(timed_out=True, code=None)]))
    with pytest.raises(GitUnavailableError):
        git.head()


def test_minimal_env_drops_credentials() -> None:
    env = minimal_env({"PATH": "/bin", "ANTHROPIC_API_KEY": "sk-ant-x", "HOME": "/h"})
    assert env == {"PATH": "/bin", "HOME": "/h", "LC_ALL": "C"}


@pytest.mark.subprocess
def test_subprocess_runner_runs_and_times_out(tmp_path: Path) -> None:
    runner = SubprocessRunner()
    result = runner.run(
        [sys.executable, "-c", "import sys; print(sys.stdin.read().upper())"],
        cwd=tmp_path,
        env=minimal_env(),
        stdin="hi",
        timeout_s=30,
    )
    assert result.returncode == 0 and result.stdout.strip() == "HI"
    slow = runner.run(
        [sys.executable, "-c", "import time; time.sleep(5)"],
        cwd=tmp_path,
        env=minimal_env(),
        stdin="",
        timeout_s=0.2,
    )
    assert slow.timed_out and slow.returncode is None


def test_subprocess_runner_uses_argv_list_without_shell(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    seen: dict[str, Any] = {}

    def fake_run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        seen["args"] = args
        seen.update(kwargs)
        return subprocess.CompletedProcess(args, 0, b"out", b"err")

    monkeypatch.setattr(subprocess, "run", fake_run)
    done = SubprocessRunner().run(
        ["claude", "-p"], cwd=tmp_path, env={"A": "1"}, stdin="hi", timeout_s=5
    )
    assert seen["args"] == ["claude", "-p"]
    assert "shell" not in seen and seen["input"] == b"hi" and seen["env"] == {"A": "1"}
    assert (done.returncode, done.stdout, done.stderr, done.timed_out) == (
        0,
        "out",
        "err",
        False,
    )


def test_subprocess_runner_timeout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        raise subprocess.TimeoutExpired(args, 5, output=b"partial")

    monkeypatch.setattr(subprocess, "run", fake_run)
    done = SubprocessRunner().run(["x"], cwd=tmp_path, env={}, stdin="", timeout_s=5)
    assert done.timed_out and done.returncode is None and done.stdout == "partial"


# --- events ---------------------------------------------------------------------


def test_event_log_buffers_until_attached_and_scrubs_paths(tmp_path: Path) -> None:
    out = create_output_root(tmp_path / "data")
    log = EventLog()
    log.emit("http.request", {"host": "boards-api.greenhouse.io"})
    log.emit("x", {"where": "/Users/someone/file", "nested": ["~/x", "ok"]})
    log.attach(out, "live/runs/r/events.jsonl")
    log.emit("y", {})
    lines = [
        json.loads(line)
        for line in (tmp_path / "data/live/runs/r/events.jsonl")
        .read_text()
        .splitlines()
    ]
    assert [e["seq"] for e in lines] == [1, 2, 3]
    assert lines[1]["where"] == ABS_PATH_PLACEHOLDER
    assert lines[1]["nested"] == [ABS_PATH_PLACEHOLDER, "ok"]
    with pytest.raises(ValueError):
        log.emit("z", {"seq": 1})
    with pytest.raises(RuntimeError):
        log.attach(out, "other.jsonl")


# --- sources --------------------------------------------------------------------


def test_parse_fetched_at_formats() -> None:
    assert parse_fetched_at("2026-10-29T22-41-31Z") is not None
    assert parse_fetched_at("2026-10-30T02:11:07+00:00") is not None
    assert parse_fetched_at("2026-10-30T02:11:07") is None  # naive
    assert parse_fetched_at(None) is None and parse_fetched_at("nope") is None


def test_replay_missing_meta_is_unreadable(tmp_path: Path) -> None:
    raw = tmp_path / "raw.json"
    raw.write_text("{}")
    result = ReplaySource(raw, "raw.json").obtain()
    assert result.error is FetchErrorKind.REPLAY_UNREADABLE and result.body is None


def test_verify_saved_evidence_ok_and_missing(tmp_path: Path) -> None:
    for rel in (HANDCHECK_RAW_REL, HANDCHECK_META_REL):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_bytes((REPO_ROOT / rel).read_bytes())
    pointer = tmp_path / "data/seeded/runs/r-SEEDED/raw/REPLAYED_FROM.json"
    pointer.parent.mkdir(parents=True)
    pointer.write_text(json.dumps({"path": "evidence/gone.json", "sha256": "0" * 64}))
    checks = verify_saved_evidence(tmp_path)
    assert [c.status for c in checks] == [EvidenceStatus.MISSING, EvidenceStatus.OK]
    assert all(not c.descriptor.startswith("/") for c in checks)
