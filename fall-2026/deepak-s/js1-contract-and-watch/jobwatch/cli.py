"""Entry point and test seam: CONTRACT.md Interfaces.

    cli.main(argv, *, opener=None, anthropic_client=None, now=None) -> int
"""
import argparse
import sys
from datetime import datetime, timezone

from jobwatch.backends import BACKENDS
from jobwatch.errors import OTHER, REFUSED, Stop
from jobwatch.experiment import experiment
from jobwatch.judge import DEFAULT_MODEL
from jobwatch.replay import replay
from jobwatch.run import run
from jobwatch.sample import sample


def build_parser():
    parser = argparse.ArgumentParser(
        prog="python -m jobwatch",
        description="Watch one Greenhouse board for new postings and judge them against a fictional résumé.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run", help="fetch the board (or read --from-file), report new postings, update state")
    r.add_argument("--board", required=True, help="Greenhouse board token, e.g. stripe")
    r.add_argument("--resume", required=True, help="path to a fictional résumé JSON")
    r.add_argument("--from-file", dest="from_file", help="read a saved raw response instead of fetching (seeded)")
    r.add_argument("--prompt", default="prompts/v1.md", help="prompt contract, used only when ANTHROPIC_API_KEY is set")
    r.add_argument("--model", default=DEFAULT_MODEL, help=f"judge model (default {DEFAULT_MODEL})")
    r.add_argument("--judge", default="sdk", choices=BACKENDS,
                   help="judge backend: the anthropic SDK (needs ANTHROPIC_API_KEY) or the local Claude Code CLI")

    p = sub.add_parser("replay", help="rebuild a run's report from its saved files, offline; exit 1 on any difference")
    p.add_argument("run_dir", metavar="RUN_DIR", help="e.g. evidence/runs/<run_id>")

    s = sub.add_parser("sample", help="call the judge n times on each posting from a saved run")
    s.add_argument("--run", required=True, help="saved run whose raw response holds the postings (never fetched)")
    s.add_argument("--posting-id", dest="posting_ids", nargs="+", required=True, metavar="ID")
    s.add_argument("--resume", required=True, help="path to a fictional résumé JSON")
    s.add_argument("--prompt", required=True, help="prompt contract")
    s.add_argument("--n", type=int, default=4, help="calls per posting (default 4)")
    s.add_argument("--model", default=DEFAULT_MODEL, help=f"judge model (default {DEFAULT_MODEL})")
    s.add_argument("--judge", default="sdk", choices=BACKENDS,
                   help="judge backend: the anthropic SDK (needs ANTHROPIC_API_KEY) or the local Claude Code CLI")

    e = sub.add_parser("experiment", help="score prompts and the rule against the hand labels of one set")
    e.add_argument("--set", required=True, choices=("development", "held-out"))
    e.add_argument("--run", required=True, help="saved run whose raw response holds the postings (never fetched)")
    e.add_argument("--resume", required=True, help="path to a fictional résumé JSON")
    e.add_argument("--prompt-a", dest="prompt_a", required=True)
    e.add_argument("--prompt-b", dest="prompt_b", help="required for held-out; optional for development")
    e.add_argument("--model", default=DEFAULT_MODEL, help=f"judge model (default {DEFAULT_MODEL})")
    e.add_argument("--judge", default="sdk", choices=BACKENDS,
                   help="judge backend: the anthropic SDK (needs ANTHROPIC_API_KEY) or the local Claude Code CLI")
    return parser


def _dispatch(args, opener, client, now):
    if args.command == "run":
        return run(args, opener=opener, client=client, now=now)
    if args.command == "replay":
        return replay(args)
    clock = (lambda: now) if now is not None else (lambda: datetime.now(timezone.utc))
    if args.command == "sample":
        return sample(args, client=client, clock=clock)
    return experiment(args, client=client, clock=clock)


def main(argv=None, *, opener=None, anthropic_client=None, now=None):
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else REFUSED
    try:
        return _dispatch(args, opener, anthropic_client, now)
    except Stop as e:
        print(f"jobwatch: {e}", file=sys.stderr)
        return e.code
    except Exception as e:
        print(f"jobwatch: unexpected error: {type(e).__name__}: {e}", file=sys.stderr)
        return OTHER
