"""``jsa exp ...``: the experiment command group (PLAN §1.5).

``register(subparsers)`` is called by ``job_search_agent.cli.build_parser``::

    jsa exp sampling run --n 4
    jsa exp sampling table
    jsa exp prompt select | seal | run --prompt v1 --set dev | freeze | score
    jsa exp surfaces prepare [--posting-id ID] | run a|b|c [--dry-run] | capture

A refused gate prints its reason and exits with ``ExitCode.EXPERIMENT_REFUSED`` (6).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from job_search_agent.config import ConfigOverrides
from job_search_agent.experiments import prompt_experiment, sampling, surfaces
from job_search_agent.experiments._io import ExperimentError
from job_search_agent.experiments._wiring import Wiring
from job_search_agent.experiments.selection import HANDCHECK_IDS
from job_search_agent.judge.payload import build_posting_payload, build_resume_payload

WiringFactory = Callable[[argparse.Namespace], Wiring]

type Subparsers = argparse._SubParsersAction[argparse.ArgumentParser]


def _default_wiring(args: argparse.Namespace) -> Wiring:
    return Wiring(Path(args.config), overrides=ConfigOverrides(data_dir=args.data_dir))


def _handler(
    action: Callable[[Wiring, argparse.Namespace], Any],
    factory: WiringFactory,
) -> Callable[[argparse.Namespace], int]:
    def run(args: argparse.Namespace) -> int:
        try:
            result = action(factory(args), args)
        except ExperimentError as exc:
            print(f"jsa exp: refused: {exc}", file=sys.stderr)
            return int(exc.exit_code)
        if result is not None:
            print(json.dumps(_summary(result), indent=2, sort_keys=True, default=str))
        return 0

    return run


def _summary(result: Any) -> Any:  # noqa: ANN401 - JSON-like
    """Keeps terminal output short: counts and paths, never call contents."""
    if isinstance(result, dict):
        return {
            k: (f"<{len(v)} items>" if isinstance(v, list) and len(v) > 8 else v)
            for k, v in result.items()
            if k not in ("calls", "rows", "cells", "surfaces", "repo_before")
        }
    return result


# --- actions ---------------------------------------------------------------------


def _sampling_run(w: Wiring, args: argparse.Namespace) -> Any:  # noqa: ANN401
    return sampling.cmd_sampling_run(
        w.context,
        n=args.n,
        postings=w.postings_by_id(),
        prompt=w.load_prompt("v1"),
        judge_call=w.judge_call(),
        model_requested=w.config.model.model_id,
    )


def _sampling_table(w: Wiring, _args: argparse.Namespace) -> Any:  # noqa: ANN401
    return sampling.cmd_sampling_table(w.context)


def _prompt_select(w: Wiring, _args: argparse.Namespace) -> Any:  # noqa: ANN401
    return prompt_experiment.cmd_select(
        w.context,
        postings=w.handcheck_postings,
        evaluate=w.evaluate(),
    )


def _prompt_seal(w: Wiring, _args: argparse.Namespace) -> Any:  # noqa: ANN401
    return prompt_experiment.cmd_seal(w.context)


def _prompt_run(w: Wiring, args: argparse.Namespace) -> Any:  # noqa: ANN401
    return prompt_experiment.cmd_run(
        w.context,
        prompt_version=args.prompt,
        set_name=args.set,
        postings=w.postings_by_id(),
        load_prompt=w.load_prompt,
        judge_call=w.judge_call(),
    )


def _prompt_freeze(w: Wiring, _args: argparse.Namespace) -> Any:  # noqa: ANN401
    return prompt_experiment.cmd_freeze(w.context, load_prompt=w.load_prompt)


def _prompt_score(w: Wiring, _args: argparse.Namespace) -> Any:  # noqa: ANN401
    return prompt_experiment.cmd_score(w.context)


def _repo_snapshot(w: Wiring) -> Callable[[], dict[str, Any]]:
    root = w.config.project_root
    env = w.child_env()
    exclude = f"{w.context.data_dir}/{surfaces.OUT}"
    return lambda: surfaces.git_repo_snapshot(w.runner, root, env, exclude=exclude)


def _surfaces_prepare(w: Wiring, args: argparse.Namespace) -> Any:  # noqa: ANN401
    postings = w.postings_by_id()
    if args.posting_id not in postings:
        raise ExperimentError(f"posting {args.posting_id} not in the hand-check file")
    return surfaces.cmd_prepare(
        w.context,
        prompt=w.load_prompt("v1"),
        resume_payload=build_resume_payload(w.resume),
        posting_payload=build_posting_payload(postings[args.posting_id]),
        state_ids=[p.posting_id for p in w.handcheck_postings],
        model_id=w.config.model.model_id,
        executable=w.config.model.executable,
        repo_snapshot=_repo_snapshot(w),
    )


def _surfaces_run(w: Wiring, args: argparse.Namespace) -> Any:  # noqa: ANN401
    return surfaces.cmd_run(
        w.context,
        surface=args.surface,
        runner=w.runner,
        resolve_dir=w.out.resolve_for_write,
        executable=w.config.model.executable,
        which=w.which,
        base_env=dict(os.environ),
        fetcher=w.fetcher() if args.surface == "c" and not args.dry_run else None,
        dry_run=args.dry_run,
    )


def _surfaces_capture(w: Wiring, args: argparse.Namespace) -> Any:  # noqa: ANN401
    return surfaces.cmd_capture(
        w.context,
        resolve_dir=w.out.resolve_for_write,
        repo_snapshot=_repo_snapshot(w),
        home=str(Path.home()),
        surfaces=(args.surface,) if args.surface else surfaces.SURFACES,
    )


# --- registration ----------------------------------------------------------------


def register(
    subparsers: Subparsers, *, wiring: WiringFactory = _default_wiring
) -> None:
    """Adds ``jsa exp ...`` to the top-level parser.

    Args:
        subparsers: The top-level subparsers object.
        wiring: Builds the dependencies for a parsed command (tests inject fakes).
    """
    exp = subparsers.add_parser(
        "exp", help="experiment harnesses (sampling, prompt, surfaces)"
    )
    groups = exp.add_subparsers(dest="exp_group", required=True)

    sample = groups.add_parser("sampling", help="Chapter 1: sampling report")
    sample_actions = sample.add_subparsers(dest="exp_action", required=True)
    run = sample_actions.add_parser(
        "run", help="n fresh first-reply calls per §13 posting"
    )
    run.add_argument("--n", type=int, default=4)
    run.set_defaults(handler=_handler(_sampling_run, wiring))
    table = sample_actions.add_parser("table", help="write spread.json and tables")
    table.set_defaults(handler=_handler(_sampling_table, wiring))

    prompt = groups.add_parser("prompt", help="Chapter 2: prompt experiment")
    prompt_actions = prompt.add_subparsers(dest="exp_action", required=True)
    for name, action, text in (
        ("select", _prompt_select, "draw dev and held-out sets (seed 20261029)"),
        ("seal", _prompt_seal, "validate hand labels and write SEAL.json"),
        (
            "freeze",
            _prompt_freeze,
            "check the one-section v2 diff and write FREEZE.json",
        ),
        ("score", _prompt_score, "re-verify SEAL, reveal strata, write metrics"),
    ):
        parser = prompt_actions.add_parser(name, help=text)
        parser.set_defaults(handler=_handler(action, wiring))
    prompt_run = prompt_actions.add_parser(
        "run", help="run one (prompt, set) cell once"
    )
    prompt_run.add_argument(
        "--prompt", choices=prompt_experiment.PROMPTS, required=True
    )
    prompt_run.add_argument("--set", choices=("dev", "heldout"), required=True)
    prompt_run.set_defaults(handler=_handler(_prompt_run, wiring))

    surf = groups.add_parser("surfaces", help="Chapter 3: action-surface comparison")
    surf_actions = surf.add_subparsers(dest="exp_action", required=True)
    prepare = surf_actions.add_parser(
        "prepare", help="create sandboxes and before-trees"
    )
    prepare.add_argument("--posting-id", default=HANDCHECK_IDS[0])
    prepare.set_defaults(handler=_handler(_surfaces_prepare, wiring))
    surf_run = surf_actions.add_parser("run", help="run one surface once")
    surf_run.add_argument("surface", choices=surfaces.SURFACES)
    surf_run.add_argument(
        "--dry-run", action="store_true", help="print the argv only; make no call"
    )
    surf_run.set_defaults(handler=_handler(_surfaces_run, wiring))
    capture = surf_actions.add_parser("capture", help="after-trees, diffs and facts")
    capture.add_argument("--surface", choices=surfaces.SURFACES)
    capture.set_defaults(handler=_handler(_surfaces_capture, wiring))
