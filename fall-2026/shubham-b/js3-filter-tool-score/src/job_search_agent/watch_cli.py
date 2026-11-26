"""``jsa watch run`` and ``jsa watch reset`` (GATE.md).

Exit codes of ``jsa watch run``: 0 ``FINISHED``, 8 ``INCOMPLETE``, 9
``BUDGET_EXHAUSTED``, 10 ``ERROR`` (GATE §2); 7 if another loop holds the lock; 5 for a
bad plan or config. ``jsa watch reset`` exits 0 only if the state was deleted.
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, Final

from job_search_agent.clock import SystemClock
from job_search_agent.config import AgentConfig, ConfigOverrides, load_config
from job_search_agent.errors import ConfigError
from job_search_agent.models import ExitCode
from job_search_agent.pipeline import RunDeps
from job_search_agent.policy import PermissionPolicy
from job_search_agent.sysio import SubprocessGit, SubprocessRunner
from job_search_agent.watch import (
    DEFAULT_PLAN_PATH,
    LoopDeps,
    LoopExit,
    WatchPlan,
    board_key,
    key_text,
    load_checked_plan,
    render_report,
    reset_board,
    run_loop,
)

RunDepsBuilder = Callable[..., RunDeps]
"""``cli.build_run_deps``, passed in to avoid an import cycle."""

EXIT_CODES: Final = {
    LoopExit.FINISHED: ExitCode.OK,
    LoopExit.INCOMPLETE: ExitCode.WATCH_INCOMPLETE,
    LoopExit.BUDGET_EXHAUSTED: ExitCode.WATCH_BUDGET_EXHAUSTED,
    LoopExit.ERROR: ExitCode.WATCH_ERROR,
}


def _plan_and_policy(
    args: argparse.Namespace,
) -> tuple[AgentConfig, WatchPlan, PermissionPolicy]:
    cfg = load_config(args.config, overrides=ConfigOverrides())
    plan, policy = load_checked_plan(args.plan, cfg.project_root)
    return cfg, plan, policy


def cmd_watch_run(args: argparse.Namespace, build_run_deps: RunDepsBuilder) -> int:
    """``jsa watch run [--plan config/watch.toml]``."""
    cfg, plan, policy = _plan_and_policy(args)
    runner = SubprocessRunner()
    git = SubprocessGit(cfg.project_root, runner=runner)
    try:
        commit: str | None = git.head()
    except (OSError, RuntimeError):
        commit = None
    deps = LoopDeps(
        plan=plan,
        base_config=cfg,
        policy=policy,
        clock=SystemClock(),
        monotonic=time.monotonic,
        board_deps=lambda board_cfg: dataclasses.replace(
            build_run_deps(board_cfg, None, runner=runner), terminal=None
        ),
        code_commit=commit,
    )
    report = run_loop(deps)
    print(render_report(report), end="")
    print(f"\nTrace and report: {plan.policy.write_root}/loops/{report.loop_id}/")
    return int(EXIT_CODES[report.exit])


def cmd_watch_reset(args: argparse.Namespace) -> int:
    """``jsa watch reset PROVIDER/TOKEN``: asks first; refused without a terminal."""
    _cfg, _plan, policy = _plan_and_policy(args)
    provider, _, token = args.board.partition("/")
    if not provider or not token:
        raise ConfigError("board must be PROVIDER/TOKEN, e.g. greenhouse/ramp")
    expected = key_text(board_key(provider, token))

    def ask(question: str) -> bool:
        try:
            return input(question).strip() == expected
        except EOFError:  # Ctrl-D at the prompt is a no
            return False

    approver = ask if sys.stdin.isatty() else None
    verdict, deleted = reset_board(policy, provider, token, approver=approver)
    print(f"{expected}: {verdict.decision.value} ({verdict.reason}); deleted={deleted}")
    return int(ExitCode.OK if deleted else ExitCode.CONFIG_ERROR)


def register(sub: Any, build_run_deps: RunDepsBuilder) -> None:  # noqa: ANN401
    """Adds the ``watch`` command group to the ``jsa`` parser.

    Args:
        sub: The ``jsa`` subparsers object.
        build_run_deps: ``cli.build_run_deps``.
    """
    parser = sub.add_parser("watch", help="the JS2 loop over several boards (GATE.md)")
    actions = parser.add_subparsers(dest="watch_action", required=True)
    for name, help_text in (
        ("run", "check every planned board once, within the budget"),
        ("reset", "delete one board's saved state (asks for approval)"),
    ):
        child = actions.add_parser(name, help=help_text)
        child.add_argument(
            "--plan", type=Path, default=DEFAULT_PLAN_PATH, help="watch plan TOML"
        )
        if name == "run":
            child.set_defaults(handler=lambda a: cmd_watch_run(a, build_run_deps))
        else:
            child.add_argument("board", metavar="PROVIDER/TOKEN")
            child.set_defaults(handler=cmd_watch_reset)
