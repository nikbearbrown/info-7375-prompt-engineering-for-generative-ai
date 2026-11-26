"""``jsa watch reset`` at a terminal: Ctrl-D at the question is a no, not a crash."""

from __future__ import annotations

import argparse
import builtins

import pytest

from job_search_agent import watch_cli
from job_search_agent.models import ExitCode
from tests.watch.harness import Project


def test_ctrl_d_at_the_question_deletes_nothing(
    p: Project, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = p.state("greenhouse-ramp")
    state.parent.mkdir(parents=True)
    state.write_text("{}")

    def eof(_question: str) -> str:
        raise EOFError

    monkeypatch.setattr(
        watch_cli, "_plan_and_policy", lambda _a: (None, None, p.policy())
    )
    monkeypatch.setattr(watch_cli.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(builtins, "input", eof)
    code = watch_cli.cmd_watch_reset(argparse.Namespace(board="greenhouse/ramp"))
    assert code == ExitCode.CONFIG_ERROR
    assert state.read_text() == "{}"
