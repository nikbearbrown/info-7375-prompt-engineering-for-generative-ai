"""``jsa`` CLI: parser, exit codes, offline commands (PLAN §1.4, §1.5, §3.4).

Every command runs on the real modules in a temporary project copy; runs are built
by ``tests/pipeline_harness.py`` where a test needs a scripted model or board.
``tests/test_integration.py`` covers the full ``jsa run`` and ``jsa doctor`` paths.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from job_search_agent import cli
from job_search_agent.config import AgentConfig, ConfigOverrides, load_config
from job_search_agent.errors import ConfigError
from job_search_agent.fsio import OutputRoot
from job_search_agent.models import BackendErrorKind, CompletedCommand, ExitCode
from job_search_agent.pipeline import RunDeps, run_once
from job_search_agent.sources import ReplaySource
from job_search_agent.state import parse_state
from tests.conftest import HANDCHECK_RAW_REL, REPO_ROOT, RESUME_FIXTURE_REL
from tests.fakes import FakeBackend, FakeRunner, Reply
from tests.pipeline_harness import (
    CONSTRUCTED_ID,
    VALID_REPLY,
    Harness,
    constructed_with_added_posting,
    handcheck_body,
)

COMMANDS = ("run", "doctor", "pending", "rule", "verify-evidence", "audit-privacy")
ADDED = constructed_with_added_posting(handcheck_body(), title="Software Engineer, C")


@pytest.fixture
def h(tmp_path: Path) -> Harness:
    """A temporary project copy (config, prompt, evidence, fixture)."""
    return Harness.create(tmp_path)


@pytest.fixture
def no_claude(monkeypatch: pytest.MonkeyPatch) -> None:
    """``claude`` is not on PATH (doctor then makes no subprocess call)."""
    monkeypatch.setattr(shutil, "which", lambda name: None)


def config_path(h: Harness) -> Path:
    return h.root / "config" / "agent.toml"


def jsa(h: Harness, *argv: str) -> int:
    return cli.main(["--config", str(config_path(h)), *argv])


def edit_config(h: Harness, old: str, new: str) -> None:
    path = config_path(h)
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new), encoding="utf-8")


def baseline(h: Harness) -> None:
    run_once(h.deps(h.live_source(Reply(body=handcheck_body()))))


# --- parser ---------------------------------------------------------------------


def test_help(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--help"])
    assert exit_info.value.code == 0
    out = capsys.readouterr().out
    for command in COMMANDS:
        assert command in out
    assert "--data-dir" in out


def test_run_help_lists_replay_backend_and_data_dir(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        cli.main(["run", "--help"])
    out = capsys.readouterr().out
    assert "--replay" in out and "--model-backend" in out and "--data-dir" in out


# --- run and exit codes ---------------------------------------------------------

SCENARIOS: dict[str, tuple[Callable[[Harness], RunDeps], bool, ExitCode]] = {
    "baseline": (
        lambda h: h.deps(h.live_source(Reply(body=handcheck_body()))),
        False,
        ExitCode.OK,
    ),
    "no_new": (
        lambda h: h.deps(h.live_source(Reply(body=handcheck_body()))),
        True,
        ExitCode.OK,
    ),
    "with_new": (lambda h: h.deps(h.live_source(Reply(body=ADDED))), True, ExitCode.OK),
    "partial": (
        lambda h: h.deps(h.live_source(Reply(body=ADDED)), use_judge=False),
        True,
        ExitCode.PARTIAL_FAILURE,
    ),
    "fetch_failed": (
        lambda h: h.deps(h.failing_source()),
        True,
        ExitCode.FETCH_OR_RESPONSE,
    ),
    "empty": (
        lambda h: h.deps(
            h.live_source(Reply(body=b'{"jobs": [], "meta": {"total": 0}}'))
        ),
        True,
        ExitCode.FETCH_OR_RESPONSE,
    ),
    "invalid": (
        lambda h: h.deps(h.live_source(Reply(body=b"oops"))),
        True,
        ExitCode.FETCH_OR_RESPONSE,
    ),
}


def _built_by(
    h: Harness, make: Callable[[Harness], RunDeps]
) -> Callable[[AgentConfig, Path | None], RunDeps]:
    return lambda cfg, replay: make(h)


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_exit_codes_map_statuses(
    scenario: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    make, with_baseline, expected = SCENARIOS[scenario]
    h = Harness.create(tmp_path, backend=FakeBackend([VALID_REPLY]))
    if with_baseline:
        baseline(h)
    monkeypatch.setattr(cli, "build_run_deps", _built_by(h, make))
    assert jsa(h, "run") == int(expected)


def test_exit_code_for_refused_resume(h: Harness) -> None:
    edit_config(h, 'pinned_sha256 = "562a', 'pinned_sha256 = "000a')
    assert jsa(h, "run", "--model-backend", "none") == int(ExitCode.RESUME_REFUSED)
    assert not h.data("live").exists()


def test_exit_code_for_corrupt_state(
    h: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = h.data("live/state.json")
    state.parent.mkdir(parents=True)
    state.write_text("{}")
    monkeypatch.setattr(cli, "build_run_deps", _built_by(h, SCENARIOS["baseline"][0]))
    assert jsa(h, "run") == int(ExitCode.STATE_CORRUPT)


def test_exit_code_for_config_error(tmp_path: Path) -> None:
    assert cli.main(["--config", str(tmp_path / "missing.toml"), "run"]) == int(
        ExitCode.CONFIG_ERROR
    )


def test_model_backend_none_override_reaches_config(
    h: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: dict[str, Any] = {}

    def build(cfg: AgentConfig, replay: Path | None) -> RunDeps:
        seen["backend"] = cfg.model.backend
        seen["replay"] = replay
        raise ConfigError("stop here")

    monkeypatch.setattr(cli, "build_run_deps", build)
    assert jsa(h, "run", "--model-backend", "none") == int(ExitCode.CONFIG_ERROR)
    assert seen == {"backend": "none", "replay": None}


def test_build_run_deps_real_judge_has_no_unavailable_reason(h: Harness) -> None:
    cfg = load_config(
        config_path(h), overrides=ConfigOverrides(model_backend="claude-cli")
    )
    deps = cli.build_run_deps(cfg, h.root / HANDCHECK_RAW_REL, runner=FakeRunner())
    assert deps.judge is not None
    assert deps.unavailable_reason is None


def test_build_run_deps_replay_is_seeded_and_never_live(h: Harness) -> None:
    cfg = load_config(config_path(h), overrides=ConfigOverrides(model_backend="none"))
    deps = cli.build_run_deps(cfg, h.root / HANDCHECK_RAW_REL)
    assert deps.seeded is True
    assert isinstance(deps.source, ReplaySource)
    assert deps.judge is None and deps.unavailable_reason == "backend_none"
    result = deps.source.obtain()
    assert result.ok and result.replayed_from is not None
    assert result.replayed_from.path == HANDCHECK_RAW_REL


def test_replay_outside_project_refused(
    h: Harness, tmp_path_factory: pytest.TempPathFactory
) -> None:
    outside = tmp_path_factory.mktemp("outside") / "raw.json"
    outside.write_text("{}")
    with pytest.raises(ConfigError):
        cli.build_run_deps(load_config(config_path(h)), outside)


# --- doctor ---------------------------------------------------------------------


def test_doctor_offline_prints_no_resume_values(
    h: Harness, capsys: pytest.CaptureFixture[str], no_claude: None
) -> None:
    assert jsa(h, "doctor") == 0
    out = capsys.readouterr().out
    for value in h.resume().to_dict()["personal"].values():
        assert value not in out
    assert "Kiran" not in out
    assert str(h.root) not in out
    for name in ("python", "claude", "resume", "gitignore", "allow-list", "data dir"):
        assert f"] {name}:" in out
    assert "[WARN] claude: executable not on PATH" in out
    assert "boards-api.greenhouse.io" in out


def test_doctor_reports_claude_version_without_path(
    h: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: "/opt/secret/bin/claude")
    runner = FakeRunner(
        [CompletedCommand((), 0, "2.1.312 (Claude Code)\n", "", False, 3)]
    )
    checks = {c.name: c for c in cli.doctor_checks(load_config(config_path(h)), runner)}
    assert checks["claude"].level == "OK"
    assert "2.1.312" in checks["claude"].detail
    assert "/opt/secret" not in checks["claude"].detail
    assert runner.calls[0].argv[1:] == ("--version",)
    assert "ANTHROPIC_API_KEY" not in runner.calls[0].env


def test_doctor_resume_refusal_exit_3(
    h: Harness, capsys: pytest.CaptureFixture[str], no_claude: None
) -> None:
    edit_config(h, 'pinned_sha256 = "562a', 'pinned_sha256 = "000a')
    assert jsa(h, "doctor") == int(ExitCode.RESUME_REFUSED)
    assert "refused: DIGEST_MISMATCH" in capsys.readouterr().out


def test_doctor_resume_outside_read_roots_is_exit_5(
    h: Harness, capsys: pytest.CaptureFixture[str], no_claude: None
) -> None:
    under_src = "src/kiran.resume.example.json"
    (h.root / "src").mkdir()
    shutil.copyfile(REPO_ROOT / RESUME_FIXTURE_REL, h.root / under_src)
    edit_config(h, f'"{RESUME_FIXTURE_REL}"', f'"{under_src}"')
    assert jsa(h, "doctor") == int(ExitCode.CONFIG_ERROR)
    assert "[FAIL] resume: resume path is outside the readable roots" in (
        capsys.readouterr().out
    )


def test_doctor_gitignore_missing_rule_fails(h: Harness, no_claude: None) -> None:
    gitignore = h.root / ".gitignore"
    gitignore.write_text(gitignore.read_text().replace("data/tmp/", ""))
    assert jsa(h, "doctor") == int(ExitCode.CONFIG_ERROR)


# --- pending --------------------------------------------------------------------


def queue_pending(h: Harness) -> None:
    baseline(h)
    h.set_backend(FakeBackend([BackendErrorKind.TIMEOUT]))
    run_once(h.deps(h.live_source(Reply(body=ADDED))))


def test_pending_list_and_drop(h: Harness, capsys: pytest.CaptureFixture[str]) -> None:
    queue_pending(h)
    assert jsa(h, "pending", "list") == 0
    out = capsys.readouterr().out
    assert f"{CONSTRUCTED_ID} last_status=ERROR attempts=1" in out
    assert jsa(h, "pending", "drop", str(CONSTRUCTED_ID), "--reason", "  ") == 5
    assert jsa(h, "pending", "drop", "1", "--reason", "x") == 5
    assert jsa(h, "pending", "drop", str(CONSTRUCTED_ID), "--reason", "withdrawn") == 0
    state = parse_state(h.data("live/state.json").read_bytes())
    assert state.pending == []
    assert state.abandoned[0].reason == "withdrawn"
    capsys.readouterr()
    assert jsa(h, "pending", "list", "--data", "seeded") == 0
    assert "absent" in capsys.readouterr().out


def test_pending_drop_fails_fast_while_a_run_holds_the_lock(
    h: Harness, capsys: pytest.CaptureFixture[str]
) -> None:
    queue_pending(h)
    before = h.data("live/state.json").read_bytes()
    argv = ("pending", "drop", str(CONSTRUCTED_ID), "--reason", "withdrawn")
    with OutputRoot(h.config.data_dir).lock("live/.lock"):
        assert jsa(h, *argv) == int(ExitCode.LOCKED) == 7
    assert "lock" in capsys.readouterr().err
    assert h.data("live/state.json").read_bytes() == before
    assert jsa(h, *argv) == 0


def test_pending_drop_refuses_a_symlinked_state_file(h: Harness) -> None:
    queue_pending(h)
    state = h.data("live/state.json")
    target = h.data("other-state.json")  # inside data/: only the file policy refuses
    target.write_bytes(state.read_bytes())
    state.unlink()
    state.symlink_to(target)
    argv = ("pending", "drop", str(CONSTRUCTED_ID), "--reason", "withdrawn")
    assert jsa(h, *argv) == int(ExitCode.CONFIG_ERROR)
    assert parse_state(target.read_bytes()).pending  # nothing was dropped


def test_resume_gate_reads_through_the_read_policy(h: Harness) -> None:
    good = load_config(config_path(h))
    assert cli._load_resume(good).source_path == good.resume.path
    under_src = "src/job_search_agent/kiran.resume.example.json"
    (h.root / under_src).parent.mkdir(parents=True)
    shutil.copyfile(REPO_ROOT / RESUME_FIXTURE_REL, h.root / under_src)
    edit_config(h, f'"{RESUME_FIXTURE_REL}"', f'"{under_src}"')
    with pytest.raises(ConfigError):
        cli._load_resume(load_config(config_path(h)))


# --- rule -----------------------------------------------------------------------


def test_rule_prints_one_record_without_judgment(
    h: Harness, capsys: pytest.CaptureFixture[str]
) -> None:
    raw = str(h.root / HANDCHECK_RAW_REL)
    assert jsa(h, "rule", "--raw", raw, "--id", "8249901") == 0
    record = json.loads(capsys.readouterr().out)
    assert record["posting_id"] == "8249901"
    assert record["rule_evidence_errors"] == []
    assert "rule_verdict" in record and "model_judgment" not in record
    assert list(record)[:4] == ["posting_id", "title", "location", "updated_at"]
    assert jsa(h, "rule", "--raw", raw, "--id", "1") == int(ExitCode.CONFIG_ERROR)


# --- verify-evidence / docs / audit-privacy -------------------------------------


def test_verify_evidence_detects_tampering(
    h: Harness, capsys: pytest.CaptureFixture[str]
) -> None:
    baseline(h)
    run_once(h.deps(h.replay_source(), seeded=True))
    assert jsa(h, "verify-evidence") == 0
    out = capsys.readouterr().out
    assert out.count("[OK]") == 3  # hand-check meta, live meta, seeded pointer
    assert str(h.root) not in out
    raw = h.root / HANDCHECK_RAW_REL
    raw.write_bytes(raw.read_bytes() + b"\n")
    assert jsa(h, "verify-evidence") == int(ExitCode.PARTIAL_FAILURE)
    assert capsys.readouterr().out.count("[MISMATCH]") == 2


def test_docs_render_separates_live_and_seeded(
    h: Harness, capsys: pytest.CaptureFixture[str]
) -> None:
    live = run_once(h.deps(h.live_source(Reply(body=handcheck_body()))))
    seeded = run_once(h.deps(h.replay_source(), seeded=True))
    assert jsa(h, "docs", "render") == 0
    live_part, seeded_part = capsys.readouterr().out.split("## Seeded runs")
    assert live.run_id in live_part and seeded.run_id not in live_part
    assert seeded.run_id in seeded_part


def test_audit_privacy_finds_the_fixture_email(
    h: Harness, capsys: pytest.CaptureFixture[str]
) -> None:
    email = h.resume().to_dict()["personal"]["email"]
    leak = h.data("live/runs/r/report.md")
    leak.parent.mkdir(parents=True)
    leak.write_text(f"clean line\ncontact {email}\n", encoding="utf-8")
    h.data("live/clean.json").write_text("{}\n", encoding="utf-8")
    assert jsa(h, "audit-privacy", str(h.root / "data")) == 1
    out = capsys.readouterr().out
    assert "[FINDING] live/runs/r/report.md:2:9 RESUME_VALUE $.personal.email" in out
    assert "1 finding(s)" in out and "audit-privacy data:" in out
    assert email not in out
    leak.unlink()
    assert jsa(h, "audit-privacy", str(h.root / "data")) == 0


def test_main_reports_agent_error_without_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    secret_dir = tmp_path / "secret-dir"
    assert cli.main(["--config", str(secret_dir / "agent.toml"), "doctor"]) == 5
    assert str(secret_dir) not in capsys.readouterr().err
