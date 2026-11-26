"""End-to-end seams with every real module wired.

Hermetic: the board is an ``httpx.MockTransport`` serving the committed hand-check
raw bytes (or a CONSTRUCTED variant built in memory), ``git`` and ``claude`` are
``FakeRunner`` scripts behind a router, and the project is a temporary copy. The
autouse guards in ``conftest`` block real sockets and subprocesses throughout.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from job_search_agent import cli
from job_search_agent.config import AgentConfig, ConfigOverrides, load_config
from job_search_agent.evidence_validator import validate_rule_evidence
from job_search_agent.experiments._wiring import Wiring
from job_search_agent.experiments.cli import register
from job_search_agent.experiments.prompt_experiment import (
    HANDCHECK_RAW_REL,
    PROCEDURE_REL,
    SELECTION,
)
from job_search_agent.http import AllowListFetcher
from job_search_agent.models import (
    CompletedCommand,
    ExitCode,
    JudgmentStatus,
    RunReport,
    RunStatus,
    VerdictLabel,
    exit_code_for_status,
)
from job_search_agent.pipeline import run_once
from job_search_agent.privacy import scan_tree, sensitive_values
from job_search_agent.resume import load_verified_resume
from tests.conftest import HANDCHECK_META_REL, REPO_ROOT, RESUME_FIXTURE_REL
from tests.fakes import (
    FakeRunner,
    FixedClock,
    RecordingTransport,
    Reply,
    mock_transport,
)
from tests.pipeline_harness import (
    CONSTRUCTED_ID,
    VALID_REPLY,
    constructed_with_added_posting,
)

JOBS_URL = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"
R1_ARGV_TAIL = (
    "-p",
    "--no-session-persistence",
    "--tools",
    "",
    "--disallowedTools",
    "mcp__*",
    "--strict-mcp-config",
    "--setting-sources",
    "project",
    "--safe-mode",
    "--output-format",
    "json",
    "--model",
    "claude-sonnet-5-5",
)
"""PLAN amendment R1, written out literally so drift in ``judge_argv`` is caught."""

PROJECT_FILES = (
    "config/agent.toml",
    ".gitignore",
    HANDCHECK_RAW_REL,
    HANDCHECK_META_REL,
    RESUME_FIXTURE_REL,
    "prompts/judge.v1.md",
    PROCEDURE_REL,
    "experiments/sampling/hand_labels.json",
)
BASELINE_AT = datetime(2026, 10, 30, 1, 0, tzinfo=UTC)
SECOND_AT = datetime(2026, 10, 31, 1, 0, tzinfo=UTC)
COMMIT = "a" * 40


# --- doubles ----------------------------------------------------------------------


def _done(stdout: str = "", code: int = 0) -> CompletedCommand:
    return CompletedCommand((), code, stdout, "", False, 3)


def _envelope(result: str) -> str:
    return json.dumps(
        {
            "type": "result",
            "subtype": "success",
            "is_error": False,
            "result": result,
            "session_id": "integration-session",
            "total_cost_usd": 0.0,
            "modelUsage": {"claude-sonnet-5-5": {}},
        }
    )


CLAUDE_VERSION = _done("2.1.312 (Claude Code)\n")


@dataclass
class Router:
    """``CommandRunner`` that sends ``git`` to one script and everything else to
    another (``claude``), so each can be asserted on separately."""

    git: FakeRunner = field(default_factory=FakeRunner)
    claude: FakeRunner = field(default_factory=FakeRunner)

    def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str],
        stdin: str,
        timeout_s: float,
    ) -> CompletedCommand:
        target = self.git if Path(argv[0]).name == "git" else self.claude
        return target.run(argv, cwd=cwd, env=env, stdin=stdin, timeout_s=timeout_s)


def _run_git() -> FakeRunner:
    """What one run asks git: ``rev-parse HEAD``, then ``status --porcelain``."""
    return FakeRunner([_done(COMMIT + "\n"), _done("")])


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A temporary project with the real config, fixture, evidence and prompt.

    A fake ``claude`` executable is first on ``PATH`` (it is never started: every
    child process goes through a ``FakeRunner``), and the parent environment holds
    an API key that the R1 child environment must strip.
    """
    for rel in PROJECT_FILES:
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / rel, tmp_path / rel)
    bin_dir = tmp_path / "fake-bin"
    bin_dir.mkdir()
    fake_claude = bin_dir / "claude"
    fake_claude.write_text("#!/bin/sh\nexit 99\n")
    fake_claude.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-integration-0000000000000000")
    return tmp_path


def _config(project: Path, *, backend_none: bool = False) -> AgentConfig:
    overrides = ConfigOverrides(model_backend="none") if backend_none else None
    return load_config(project / "config/agent.toml", overrides=overrides)


def _handcheck() -> bytes:
    return (REPO_ROOT / HANDCHECK_RAW_REL).read_bytes()


def _constructed() -> bytes:
    """CONSTRUCTED: the hand-check response plus one posting (in memory only)."""
    return constructed_with_added_posting(
        _handcheck(), title="Software Engineer, Constructed Integration"
    )


def _board(body: bytes) -> RecordingTransport:
    return mock_transport({JOBS_URL: Reply(body=body)})


def _run(
    cfg: AgentConfig, router: Router, body: bytes, at: datetime
) -> tuple[RunReport, RecordingTransport]:
    router.git = _run_git()
    transport = _board(body)
    deps = cli.build_run_deps(
        cfg,
        None,
        clock=FixedClock(at, step=timedelta(seconds=1)),
        runner=router,
        transport=transport,
    )
    return run_once(deps), transport


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_dir(cfg: AgentConfig, report: RunReport) -> Path:
    return (
        cfg.data_dir
        / ("seeded" if report.seeded else "live")
        / "runs"
        / (report.run_id)
    )


def _assert_privacy_clean(cfg: AgentConfig) -> None:
    resume = load_verified_resume(
        cfg.resume_path, cfg.resume.pinned_sha256, project_root=cfg.project_root
    )
    findings = scan_tree(cfg.data_dir, sensitive_values(resume))
    assert [f.describe() for f in findings] == []


# --- (a) live baseline, then a CONSTRUCTED new posting judged by claude ---------


def test_live_baseline_then_new_posting_with_real_modules(project: Path) -> None:
    cfg = _config(project)
    router = Router()

    baseline, first = _run(cfg, router, _handcheck(), BASELINE_AT)
    assert baseline.status is RunStatus.BASELINE
    assert baseline.fetched_count == len(json.loads(_handcheck())["jobs"])
    assert router.claude.calls == []  # a baseline judges nothing

    constructed = _constructed()
    router.claude = FakeRunner([CLAUDE_VERSION, _done(_envelope(VALID_REPLY))])
    second, again = _run(cfg, router, constructed, SECOND_AT)
    assert second.status is RunStatus.SUCCESS_WITH_NEW
    assert second.new_ids == [str(CONSTRUCTED_ID)]
    assert second.code_commit == COMMIT
    assert [str(r.url) for r in first.requests + again.requests] == [JOBS_URL] * 2

    run_dir = _run_dir(cfg, second)
    (record,) = _read_json(run_dir / "records.json")
    raw_posting = json.loads(constructed)["jobs"][-1]
    resume_data = _read_json(project / RESUME_FIXTURE_REL)
    assert record["posting_id"] == str(CONSTRUCTED_ID)
    assert record["rule_evidence_errors"] == []
    assert (
        validate_rule_evidence(record["rule_verdict"], raw_posting, resume_data) == []
    )
    assert record["model_judgment"]["status"] == JudgmentStatus.VALID.value

    judge_calls = [c for c in router.claude.calls if c.argv[1:] != ("--version",)]
    assert len(judge_calls) == 1
    (call,) = judge_calls
    assert call.argv == (str(project / "fake-bin" / "claude"), *R1_ARGV_TAIL)
    assert "ANTHROPIC_API_KEY" not in call.env
    assert call.env["CLAUDE_CODE_DISABLE_CLAUDE_MDS"] == "1"
    assert "Software Engineer, Constructed Integration" in call.stdin
    assert call.cwd.parent == cfg.data_dir / "tmp"
    assert call.cwd.name.startswith("claude-") and not call.cwd.exists()

    log_ref = record["model_judgment"]["diagnostic"]["attempts"][0]["raw_log_ref"]
    log = _read_json(project / log_ref)
    assert log["argv"] == ["claude", *R1_ARGV_TAIL]
    assert log["seeded"] is False
    assert log["claude_version"] == "2.1.312 (Claude Code)"

    _assert_privacy_clean(cfg)


# --- (b) backend none: honest UNAVAILABLE, PARTIAL_FAILURE, pending --------------


def test_backend_none_marks_unavailable_partial_failure_and_pending(
    project: Path,
) -> None:
    cfg = _config(project, backend_none=True)
    router = Router()
    _run(cfg, router, _handcheck(), BASELINE_AT)
    report, _ = _run(cfg, router, _constructed(), SECOND_AT)

    assert report.status is RunStatus.PARTIAL_FAILURE
    assert exit_code_for_status(report.status) is ExitCode.PARTIAL_FAILURE
    (record,) = _read_json(_run_dir(cfg, report) / "records.json")
    judgment = record["model_judgment"]
    assert judgment["status"] == JudgmentStatus.UNAVAILABLE.value
    assert judgment["diagnostic"]["unavailable_reason"] == "backend_none"
    assert record["rule_verdict"]["label"] in {v.value for v in VerdictLabel}
    state = _read_json(cfg.state_path)
    assert [p["posting_id"] for p in state["pending"]] == [str(CONSTRUCTED_ID)]
    assert router.claude.calls == []
    _assert_privacy_clean(cfg)


# --- (c) --replay: a seeded run, labeled in all six places, no network ----------


def test_replay_is_seeded_in_six_places_without_network(
    project: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    router = Router(git=_run_git())
    monkeypatch.setattr(cli, "SubprocessRunner", lambda: router)
    config = project / "config/agent.toml"
    raw = project / HANDCHECK_RAW_REL
    assert cli.main(["--config", str(config), "run", "--replay", str(raw)]) == 0
    terminal = capsys.readouterr().out
    cfg = _config(project)

    runs = sorted((cfg.data_dir / "seeded" / "runs").iterdir())
    assert len(runs) == 1 and not (cfg.data_dir / "live").exists()  # 1. folder
    run_dir = runs[0]
    assert run_dir.name.endswith("-SEEDED")  # 2. run ID
    report = _read_json(run_dir / "report.json")  # 3. report.json and meta
    pointer = _read_json(run_dir / "raw" / "REPLAYED_FROM.json")
    assert (report["seeded"], report["mode"]) == (True, "replay")
    assert (pointer["seeded"], pointer["source"]) == (True, "replay")
    assert pointer["path"] == HANDCHECK_RAW_REL
    assert report["status"] == RunStatus.BASELINE.value
    banner = f"> SEEDED RUN — replayed from saved file {HANDCHECK_RAW_REL} "
    first_line = (run_dir / "report.md").read_text(encoding="utf-8").splitlines()[0]
    assert first_line.startswith(banner)  # 4. report.md
    assert first_line.endswith("No network request was made.")
    assert terminal.startswith(banner)  # 5. terminal summary
    assert cli.main(["--config", str(config), "docs", "render"]) == 0
    live_part, seeded_part = capsys.readouterr().out.split("## Seeded runs")
    assert run_dir.name in seeded_part and run_dir.name not in live_part  # 6.

    events = (run_dir / "events.jsonl").read_text(encoding="utf-8")
    assert '"http.' not in events
    assert report["code_commit"] == COMMIT and router.claude.calls == []
    _assert_privacy_clean(cfg)


# --- (d) jsa doctor and doctor --probe-model ------------------------------------


def test_doctor_passes_with_real_modules(
    project: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    router = Router(claude=FakeRunner([CLAUDE_VERSION]))
    monkeypatch.setattr(cli, "SubprocessRunner", lambda: router)
    assert cli.main(["--config", str(project / "config/agent.toml"), "doctor"]) == 0
    out = capsys.readouterr().out
    assert "[OK] resume:" in out and "[OK] claude: found on PATH" in out
    assert "[FAIL]" not in out and str(project) not in out


def test_doctor_probe_model_records_one_r1_call(
    project: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    router = Router(
        claude=FakeRunner([CLAUDE_VERSION, CLAUDE_VERSION, _done(_envelope("OK"))])
    )
    monkeypatch.setattr(cli, "SubprocessRunner", lambda: router)
    config = str(project / "config/agent.toml")
    assert cli.main(["--config", config, "doctor", "--probe-model"]) == 0
    out = capsys.readouterr().out
    assert "[OK] probe-model: facts recorded in data/doctor/" in out
    (path,) = (project / "data" / "doctor").iterdir()
    facts = _read_json(path)
    assert facts["argv"] == ["claude", *R1_ARGV_TAIL]
    assert (facts["reply_is_ok"], facts["session_id"]) == (True, "integration-session")
    assert router.claude.calls[-1].argv[1:] == R1_ARGV_TAIL


# --- (e) experiments wiring with the real modules --------------------------------


def test_experiment_wiring_builds_from_real_modules(project: Path) -> None:
    wiring = Wiring(project / "config/agent.toml", runner=Router())
    postings = wiring.handcheck_postings
    assert len(postings) == len(json.loads(_handcheck())["jobs"])
    verdict = wiring.evaluate()(wiring.postings_by_id()["8249901"])
    assert verdict.label in set(VerdictLabel)
    assert wiring.load_prompt("v1").prompt_id
    assert wiring.judge_call().model_requested == "claude-sonnet-5-5"
    assert isinstance(wiring.fetcher(), AllowListFetcher)
    assert wiring.context.data_dir == "data"


def test_exp_prompt_select_runs_against_committed_raw(
    project: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    router = Router(
        git=FakeRunner([_done(), _done(), _done(COMMIT + "\n"), _done("")])
    )  # PROCEDURE.md tracked and clean; HEAD; not dirty
    wiring = Wiring(project / "config/agent.toml", runner=router)
    parser = argparse.ArgumentParser(prog="jsa")
    register(parser.add_subparsers(dest="command"), wiring=lambda _args: wiring)
    args = parser.parse_args(["exp", "prompt", "select"])
    assert args.handler(args) == 0
    selection = _read_json(project / "data" / SELECTION)
    meta = _read_json(project / HANDCHECK_META_REL)
    assert selection["raw_sha256"] == meta["sha256"]
    assert selection["code_commit"] == COMMIT
    assert set(selection["sets"]) == {"dev", "heldout"}
    assert router.git.calls[0].argv[1:] == (
        "ls-files",
        "--error-unmatch",
        "--",
        PROCEDURE_REL,
    )
    assert '"raw_sha256"' in capsys.readouterr().out


# --- (f) --data-dir keeps trial runs away from the graded data/ evidence ---------


def test_replay_with_data_dir_writes_nothing_under_live_or_seeded(
    project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    router = Router(git=_run_git())
    monkeypatch.setattr(cli, "SubprocessRunner", lambda: router)
    argv = [
        "--config",
        str(project / "config/agent.toml"),
        "run",
        "--replay",
        str(project / HANDCHECK_RAW_REL),
        "--model-backend",
        "none",
        "--data-dir",
        "data/scratch",
    ]
    assert cli.main(argv) == 0
    data = project / "data"
    assert not (data / "live").exists() and not (data / "seeded").exists()
    assert (data / "scratch" / "seeded" / "state.json").is_file()
    (run_dir,) = (data / "scratch" / "seeded" / "runs").iterdir()
    report = _read_json(run_dir / "report.json")
    assert report["raw_evidence"]["path"] == HANDCHECK_RAW_REL


def test_data_dir_outside_the_project_is_a_config_error(
    project: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    outside = tmp_path_factory.mktemp("elsewhere")
    config = str(project / "config/agent.toml")
    for argv in (
        ["--config", config, "--data-dir", str(outside), "doctor"],
        ["--config", config, "pending", "list", "--data-dir", "../escape"],
    ):
        assert cli.main(argv) == int(ExitCode.CONFIG_ERROR)
    assert list(outside.iterdir()) == []


def test_exp_wiring_honours_data_dir(project: Path) -> None:
    config = str(project / "config/agent.toml")
    for argv in (
        ["--config", config, "--data-dir", "data/scratch", "exp", "sampling", "table"],
        ["--config", config, "exp", "sampling", "table", "--data-dir", "data/scratch"],
    ):
        args = cli.build_parser().parse_args(argv)
        assert args.data_dir == "data/scratch"
    wiring = Wiring(
        project / "config/agent.toml",
        overrides=ConfigOverrides(data_dir="data/scratch"),
    )
    assert wiring.context.data_dir == "data/scratch"


# --- (g) every state reader refuses a symlinked state file ----------------------


def test_symlinked_state_is_refused_by_doctor_and_pending_list(
    project: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    router = Router(git=_run_git(), claude=FakeRunner([CLAUDE_VERSION]))
    monkeypatch.setattr(cli, "SubprocessRunner", lambda: router)
    config = str(project / "config/agent.toml")
    raw = str(project / HANDCHECK_RAW_REL)
    assert cli.main(["--config", config, "run", "--replay", raw]) == 0
    state = project / "data" / "seeded" / "state.json"
    # The target stays inside data/, so only the file policy (not the config's
    # resolve-inside-data.dir check) can refuse it.
    target = project / "data" / "other-state.json"
    target.write_bytes(state.read_bytes())  # a valid state, if it were followed
    state.unlink()
    state.symlink_to(target)
    capsys.readouterr()

    code = cli.main(["--config", config, "doctor"])
    out, err = capsys.readouterr()
    assert code == int(ExitCode.CONFIG_ERROR), err
    assert "[FAIL] seeded state: seeded/state.json: refused (symlink)" in out
    argv = ["--config", config, "pending", "list", "--data", "seeded"]
    assert cli.main(argv) == int(ExitCode.CONFIG_ERROR)
    assert "pending" not in capsys.readouterr().out
