"""Boundary cases B21-B27 (GATE A3): plan ceilings, the résumé read, reset tokens.

Each expected result is the prediction in GATE A3, written before these tests ran.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from job_search_agent.config import load_config
from job_search_agent.errors import ConfigError
from job_search_agent.watch import LoopExit, load_checked_plan, reset_board
from tests.conftest import REPO_ROOT
from tests.watch.harness import Project

GOOD_PLAN = """
[budget]
max_boards = 6
max_requests = 10
max_seconds = 180

[retry]
max_retries = 1
pause_s = 2.0
min_seconds_left = 5.0

[policy]
allowed_hosts = {hosts}
write_root = "{write_root}"

[[boards]]
provider = "greenhouse"
token = "stripe"
"""


def _plan(
    root: Path,
    rel: str,
    *,
    hosts: str = '["boards-api.greenhouse.io", "api.ashbyhq.com"]',
    write_root: str = "data/watch",
) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(GOOD_PLAN.format(hosts=hosts, write_root=write_root))
    return path


def test_b21_plan_cannot_add_a_host(tmp_path: Path) -> None:
    path = _plan(
        tmp_path, "config/w.toml", hosts='["boards-api.greenhouse.io", "jobs.lever.co"]'
    )
    with pytest.raises(ConfigError, match="hosts outside GATE"):
        load_checked_plan(path, tmp_path)


def test_b22_plan_cannot_widen_the_write_root(tmp_path: Path) -> None:
    path = _plan(tmp_path, "config/w.toml", write_root="data")
    with pytest.raises(ConfigError, match="inside data/watch"):
        load_checked_plan(path, tmp_path)


def test_b23_plan_inside_the_write_folder_is_refused(tmp_path: Path) -> None:
    path = _plan(tmp_path, "data/watch/plan.toml")
    with pytest.raises(ConfigError, match="where the agent can write"):
        load_checked_plan(path, tmp_path)


def test_b24_private_plan_is_refused_before_parsing(tmp_path: Path) -> None:
    path = tmp_path / "private" / "plan.toml"
    path.parent.mkdir()
    path.write_text("not toml at all [[[")
    with pytest.raises(ConfigError, match="private"):
        load_checked_plan(path, tmp_path)


def test_b25_narrowing_is_allowed(tmp_path: Path) -> None:
    path = _plan(
        tmp_path,
        "config/w.toml",
        hosts='["boards-api.greenhouse.io"]',
        write_root="data/watch/sub",
    )
    _plan_obj, policy = load_checked_plan(path, tmp_path)
    assert policy.allowed_hosts == frozenset({"boards-api.greenhouse.io"})
    assert policy.write_root == (tmp_path / "data/watch/sub").resolve()


def test_the_committed_plans_load(tmp_path: Path) -> None:
    for name in ("watch.toml", "watch-wrong-board.toml"):
        load_checked_plan(REPO_ROOT / "config" / name, REPO_ROOT)


def test_b26_resume_in_private_stops_the_loop(p: Project) -> None:
    private = p.root / "private" / "kiran.resume.example.json"
    private.parent.mkdir()
    shutil.copyfile(p.config.resume_path, private)
    agent = p.root / "config" / "agent.toml"
    text = agent.read_text().replace(
        'path = "persona/kiran-joshi.resume.example.json"',
        'path = "private/kiran.resume.example.json"',
    )
    agent.write_text(text)
    p.config = load_config(agent)
    report = p.run(p.plan([("greenhouse", "stripe")]), {})
    assert report.exit is LoopExit.ERROR
    assert report.reason == "resume_read_refused:private"
    assert report.requests_used == 0


def test_b27_reset_refuses_an_unsafe_token(p: Project) -> None:
    state = p.state("ashby-ramp")
    state.parent.mkdir(parents=True)
    state.write_text("{}")
    asked: list[str] = []
    policy = p.policy()
    with pytest.raises(ConfigError):
        reset_board(policy, "greenhouse", "x/../ashby-ramp", approver=asked.append)
    assert asked == []
    assert state.exists()
