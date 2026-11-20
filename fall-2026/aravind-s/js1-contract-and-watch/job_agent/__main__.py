"""Command line: python3 -m job_agent run | check-resume. Exit 0 done, 1 no answer, 2 broken input, 3 refused."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import CONTRACT_VERSION, claude_judge, resume, watch
from .errors import BrokenInput, NoAnswer, Refused
from .judges import PROMPTS, Judges

REPO = Path(__file__).resolve().parent.parent
DEFAULT_RESUME = REPO / "persona" / "jane-doe.json"
DEFAULT_STATE = REPO / "state" / "seen.json"
DEFAULT_RUNS = REPO / "runs"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m job_agent", description="Job-Search Agent, layer 1 (JS1).")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="one run: fetch the board, save it, report what is new since the last run")
    run.add_argument("--resume", type=Path, default=DEFAULT_RESUME)
    run.add_argument("--state", type=Path, default=DEFAULT_STATE)
    run.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    run.add_argument("--replay", type=Path, help="read a saved response instead of fetching; labeled as a replay, "
                     "and it needs its own --state and --runs")
    run.add_argument("--prompt", type=Path, default=PROMPTS / "baseline.txt", help="the Claude judge's prompt contract")
    run.add_argument("--model", default=claude_judge.DEFAULT_MODEL, help="the Claude judge's model")
    check = commands.add_parser("check-resume", help="validate a résumé and run nothing else")
    check.add_argument("path", type=Path, nargs="?", default=DEFAULT_RESUME)
    args = parser.parse_args(argv)
    try:
        if args.command == "check-resume":
            resume.load(args.path)
            print(f"{args.path.name}: a valid fictional persona for contract v{CONTRACT_VERSION}")
            return 0
        if args.replay is not None and (_same(args.state, DEFAULT_STATE) or _same(args.runs, DEFAULT_RUNS)):
            raise Refused("refused: a replay needs its own --state and --runs, so it never mixes with the live runs")
        watch.run(resume_path=args.resume, state_path=args.state, runs_root=args.runs, replay=args.replay,
                  judge=Judges(prompt=args.prompt, model=args.model))
        return 0
    except Refused as exc:
        print(exc, file=sys.stderr)
        return 3
    except BrokenInput as exc:
        print(f"stopped: {exc}", file=sys.stderr)
        return 2
    except NoAnswer as exc:  # nothing was saved, the state is unchanged
        print(f"stopped: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:  # a file the run needed could not be read or written; the state is unchanged
        print(f"stopped: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


def _same(a: Path, b: Path) -> bool:
    return a.resolve() == b.resolve()


if __name__ == "__main__":
    sys.exit(main())
