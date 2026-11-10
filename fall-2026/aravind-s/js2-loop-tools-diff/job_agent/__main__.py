"""Command line: python3 -m job_agent run | run-one | check-resume.

run      the loop over the boards in boards.json (GATE.md). Exit 0 finished, 1 incomplete,
         4 budget-exhausted, 2 broken input, 3 refused.
run-one  layer 1's watch of the one OpenAI board (CONTRACT.md), kept as it was. Exit 0 done,
         1 no answer, 2 broken input, 3 refused.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import CONTRACT_VERSION, claude_judge, gate, loop, policy, resume, watch
from .errors import BrokenInput, NoAnswer, Refused
from .judges import PROMPTS, Judges

REPO = Path(__file__).resolve().parent.parent
DEFAULT_RESUME = REPO / "persona" / "jane-doe.json"
DEFAULT_BOARDS = REPO / "boards.json"
DEFAULT_STATE_DIR = REPO / "state"
DEFAULT_STATE = DEFAULT_STATE_DIR / "seen.json"
DEFAULT_RUNS = REPO / "runs"


def files_policy(repo: Path = REPO) -> policy.Files:
    """GATE.md, Permission policy: writes only in runs/ and state/; reads in the folders the loop needs."""
    return policy.Files(repo, write_roots=["runs", "state"],
                        read_roots=["persona", "prompts", "boards.json", "boards", "state", "runs"])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m job_agent", description="Job-Search Agent, layers 1 and 2.")
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run", help="one run of the loop over the boards in the list (GATE.md)")
    run.add_argument("--boards", type=Path, default=DEFAULT_BOARDS)
    run.add_argument("--resume", type=Path, default=DEFAULT_RESUME)
    run.add_argument("--state", type=Path, default=DEFAULT_STATE_DIR, help="the folder of board states")
    run.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    run.add_argument("--replay", type=Path, help="a saved run folder: read its saved answers instead of fetching; "
                     "labeled as a replay, and it needs its own --state and --runs inside state/ and runs/")
    run.add_argument("--approve", metavar="REASON", help="approve a write GATE.md allows only with approval "
                     "(replacing or deleting a board's state); the reason goes into the trace")
    for name in ("boards", "requests", "claude-calls", "seconds"):
        run.add_argument(f"--max-{name}", type=int, help="lower this budget for one run (raising it is refused)")
    run.add_argument("--prompt", type=Path, default=PROMPTS / "baseline.txt", help="the Claude judge's prompt contract")
    run.add_argument("--model", default=claude_judge.DEFAULT_MODEL, help="the Claude judge's model")

    one = commands.add_parser("run-one", help="layer 1: one run of the watch on the OpenAI board (CONTRACT.md)")
    one.add_argument("--resume", type=Path, default=DEFAULT_RESUME)
    one.add_argument("--state", type=Path, default=DEFAULT_STATE)
    one.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    one.add_argument("--replay", type=Path, help="read a saved response instead of fetching; labeled as a replay, "
                     "and it needs its own --state and --runs")
    one.add_argument("--prompt", type=Path, default=PROMPTS / "baseline.txt", help="the Claude judge's prompt contract")
    one.add_argument("--model", default=claude_judge.DEFAULT_MODEL, help="the Claude judge's model")

    check = commands.add_parser("check-resume", help="validate a résumé and run nothing else")
    check.add_argument("path", type=Path, nargs="?", default=DEFAULT_RESUME)
    args = parser.parse_args(argv)
    try:
        if args.command == "check-resume":
            resume.load(args.path)
            print(f"{args.path.name}: a valid fictional persona for contract v{CONTRACT_VERSION}")
            return 0
        if args.command == "run-one":
            return _run_one(args)
        return _run_loop(args)
    except Refused as exc:
        print(exc, file=sys.stderr)
        return gate.REFUSED_CODE
    except BrokenInput as exc:
        print(f"stopped: {exc}", file=sys.stderr)
        return gate.BROKEN_INPUT_CODE
    except NoAnswer as exc:  # layer 1 only: nothing was saved, the state is unchanged
        print(f"stopped: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:  # a file the run needed could not be read or written; the state is unchanged
        print(f"stopped: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1 if args.command == "run-one" else gate.BROKEN_INPUT_CODE


def _run_loop(args) -> int:
    budgets = gate.Budgets().lowered(boards=args.max_boards, requests=args.max_requests,
                                     claude_calls=args.max_claude_calls, seconds=args.max_seconds)
    if args.replay is not None and (_same(args.state, DEFAULT_STATE_DIR) or _same(args.runs, DEFAULT_RUNS)):
        raise Refused("refused: a replay needs its own --state and --runs, so it never mixes with the live runs")
    summary = loop.run(boards_path=args.boards, resume_path=args.resume, state_root=args.state, runs_root=args.runs,
                       files=files_policy(), judges=Judges(prompt=args.prompt, model=args.model), budgets=budgets,
                       approve=args.approve or None, replay=args.replay)
    return summary["exit_code"]


def _run_one(args) -> int:
    if args.replay is not None and (_same(args.state, DEFAULT_STATE) or _same(args.runs, DEFAULT_RUNS)):
        raise Refused("refused: a replay needs its own --state and --runs, so it never mixes with the live runs")
    watch.run(resume_path=args.resume, state_path=args.state, runs_root=args.runs, replay=args.replay,
              judge=Judges(prompt=args.prompt, model=args.model))
    return 0


def _same(a: Path, b: Path) -> bool:
    return Path(a).resolve() == Path(b).resolve()


if __name__ == "__main__":
    sys.exit(main())
