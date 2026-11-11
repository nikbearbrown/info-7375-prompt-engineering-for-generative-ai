"""Command line for the loop.

Two modes, both first-class: `--live` fetches the allow-listed hosts, and
`--replay-from DIR` reads saved responses so a TA can reproduce every run in
this repository, including the deliberate failure and the finished-wrong-answer
demonstration, from a fresh clone with no network. The mode is recorded in the
run report; a replay can never be mistaken for a live fetch.

Deliberately absent: any flag that widens a budget or an allow-list. GATE.md §2
says a budget changes only by a written decision, and a limit any caller can
raise is not a limit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from . import loop as loop_mod
from . import report as report_mod
from . import resume as resume_mod
from . import state as state_mod
from .errors import AgentError, PolicyRefusal
from .policy import Policy
from .trace import Trace

ROOT = Path(__file__).resolve().parents[1]


def _sha256_of_file(path) -> str | None:
    path = Path(path)
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cmd_watch(args) -> int:
    plan_doc = json.loads(Path(args.boards).read_text(encoding="utf-8"))
    plan = plan_doc["boards"]
    budget = loop_mod.Budget.from_file(args.budget)

    policy = Policy(
        project_root=ROOT,
        output_root=Path(args.output_root).resolve(),
        approve_overwrite=args.approve_overwrite,
    )
    policy.check_read(Path(args.resume).resolve())
    resume = resume_mod.load(args.resume)

    state, is_first_run = state_mod.load(args.state)
    state_before = _sha256_of_file(args.state)

    runs_dir = Path(args.runs_dir)
    trace = Trace(path=runs_dir / f"trace-{loop_mod.utc_stamp()}.jsonl", policy=policy)

    fetcher = (
        loop_mod.replay_fetcher(args.replay_from) if args.replay_from else loop_mod.http_fetch
    )
    mode = f"replay:{args.replay_from}" if args.replay_from else "live"

    try:
        result = loop_mod.run(
            plan,
            policy=policy,
            budget=budget,
            raw_dir=Path(args.raw_dir),
            trace=trace,
            fetcher=fetcher,
            timeout=args.timeout,
        )
    except PolicyRefusal as exc:
        print(
            f"[ERROR] complete=False  exit_status=error\n"
            f"  policy refusal aborted the run: {type(exc).__name__}: {exc}\n"
            f"  trace: {trace.path}\n"
            f"  ESCALATE: no posting list is emitted for an aborted run.",
            file=sys.stderr,
        )
        return 3

    observed = [o for o in result.outcomes if o.observed]
    all_postings = [p for o in observed for p in o.postings]
    new = state_mod.new_postings(all_postings, state)
    entries = report_mod.judge_new(new, resume)

    # Only observed boards get a count written to the state file.
    board_counts = {o.board: len(o.postings) for o in observed}
    if not args.dry_run:
        state_mod.save(
            args.state,
            state,
            postings=all_postings,
            board_counts=board_counts,
            policy=policy,
        )
    state_after = state_before if args.dry_run else _sha256_of_file(args.state)

    report = report_mod.build(
        result,
        policy=policy,
        mode=mode,
        label=args.label,
        new_entries=entries,
        is_first_run=is_first_run,
        state_before_sha=state_before,
        state_after_sha=state_after,
        state_path=args.state,
    )
    out = report_mod.write(report, runs_dir, policy=policy)
    print(report_mod.human_summary(report))
    print(f"\n  run report: {out}")
    print(f"  trace:      {trace.path}")

    return 0 if report["exit_status"] == "finished" else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python3 -m agent",
        description="Job-Search Agent 2: a bounded loop over several boards, "
        "under a permission policy enforced in code.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    w = sub.add_parser("watch", help="run the loop once")
    w.add_argument("--boards", default="config/boards.json")
    w.add_argument("--budget", default="config/budget.json")
    w.add_argument("--resume", default="data/resume.persona.json")
    w.add_argument("--state", default="evidence/state/seen.json")
    w.add_argument("--raw-dir", default="evidence/raw")
    w.add_argument("--runs-dir", default="evidence/runs")
    w.add_argument("--output-root", default="evidence")
    w.add_argument(
        "--replay-from",
        help="read saved responses from this directory instead of the network",
    )
    w.add_argument("--label", help="recorded in the run report, e.g. 'SEEDED: empty board'")
    w.add_argument(
        "--approve-overwrite",
        action="store_true",
        help="permit replacing an existing file under evidence/raw/ (GATE.md §5.3)",
    )
    w.add_argument("--dry-run", action="store_true", help="do not write the state file")
    w.add_argument("--timeout", type=float, default=20.0)
    w.set_defaults(func=cmd_watch)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except AgentError as exc:
        print(f"REFUSED ({type(exc).__name__}): {exc}", file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":  # python3 -m agent.cli, which otherwise exits 0 in silence
    raise SystemExit(main())
