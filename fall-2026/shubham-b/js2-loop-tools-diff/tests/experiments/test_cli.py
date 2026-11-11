"""``jsa exp`` registration and handler behaviour (no real wiring)."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pytest

from job_search_agent.cli import build_parser
from job_search_agent.errors import PathRejected
from job_search_agent.experiments._io import ExperimentError, LocalRepoReader
from job_search_agent.experiments.cli import register
from job_search_agent.fsio import ReadPolicy
from job_search_agent.models import ExitCode
from tests.experiments.helpers import make_repo


class _FakeWiring:
    def __init__(self, context: Any) -> None:
        self.context = context


def _parser(wiring: Any) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jsa")
    sub = parser.add_subparsers(dest="command", required=True)
    register(sub, wiring=lambda _args: wiring)
    return parser


def test_bad_prompt_choice_rejected() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(
            ["exp", "prompt", "run", "--prompt", "v3", "--set", "dev"]
        )


def test_refused_gate_returns_distinct_exit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = make_repo(tmp_path)
    parser = _parser(_FakeWiring(repo.ctx))
    args = parser.parse_args(["exp", "prompt", "seal"])
    assert args.handler(args) == int(ExitCode.EXPERIMENT_REFUSED)
    assert "refused: no selection yet" in capsys.readouterr().err


def test_sampling_table_success_prints_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = make_repo(tmp_path)
    parser = _parser(_FakeWiring(repo.ctx))
    args = parser.parse_args(["exp", "sampling", "table"])
    assert args.handler(args) == int(ExitCode.EXPERIMENT_REFUSED)  # no manifest yet
    assert "no sampling manifest" in capsys.readouterr().err


def test_local_repo_reader_keeps_to_the_read_roots(tmp_path: Path) -> None:
    (tmp_path / "evidence").mkdir()
    (tmp_path / "evidence" / "ok.json").write_text("{}")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "secret.py").write_text("x")
    reader = LocalRepoReader(ReadPolicy(tmp_path))
    assert reader.read_bytes("evidence/ok.json") == b"{}"
    assert reader.exists("evidence/ok.json")
    with pytest.raises(PathRejected):
        reader.read_bytes("src/secret.py")
    with pytest.raises(ExperimentError):
        reader.read_bytes("../outside.json")
