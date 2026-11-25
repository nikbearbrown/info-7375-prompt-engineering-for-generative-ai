"""Entry point and test seam.

    cli.main(argv, *, opener=None, anthropic_client=None, now=None, clock=None, sleep=None, approver=None) -> int

JS2 subcommands (GATE.md):
    loop --config config/boards.json [--interactive]
    verify runs/<run-id>
    replay runs/<run-id>          (a JS2 loop run; JS1 runs under evidence/runs/ replay as in JS1)

JS1 subcommands (run, replay of evidence/runs/, sample, experiment) are kept unchanged. Their
modules, including the Claude judge, are imported only when one of them is used, so the loop
and verify never import the judge (GATE.md section 5, "read environment secrets").
"""
import argparse
import sys

JS2_COMMANDS = ("loop", "verify")
OTHER = 1
REFUSED = 2


def _is_loop_replay(argv):
    if len(argv) < 2 or argv[0] != "replay":
        return False
    first = argv[1].replace("\\", "/").lstrip("./").split("/")[0]
    return first == "runs"


def build_js2_parser():
    parser = argparse.ArgumentParser(prog="python -m jobwatch",
                                     description="JS2: a bounded loop over several job boards.")
    sub = parser.add_subparsers(dest="command", required=True)
    lp = sub.add_parser("loop", help="run the bounded loop over the boards in --config")
    lp.add_argument("--config", required=True, help="e.g. config/boards.json")
    lp.add_argument("--interactive", action="store_true",
                    help="ask y/N on a TTY for actions that need approval (GATE.md section 5)")
    vp = sub.add_parser("verify", help="independent check of a loop run (GATE.md section 7)")
    vp.add_argument("run_dir", metavar="RUN_DIR")
    rp = sub.add_parser("replay", help="rebuild a JS2 loop run's summary offline; exit 1 on any difference")
    rp.add_argument("run_dir", metavar="RUN_DIR")
    return parser


def tty_approver():
    """GATE.md section 5, Approval mechanism: only on a TTY, only the answer "y" approves."""
    if not sys.stdin.isatty():
        return None

    def ask(action):
        print(f"jobwatch needs approval: {action}. Approve? [y/N] ", end="", flush=True)
        return sys.stdin.readline().strip() == "y"

    return ask


def _main_js2(argv, opener, now, clock, sleep, approver):
    try:
        args = build_js2_parser().parse_args(argv)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else REFUSED
    if args.command == "verify":
        from jobwatch import verify

        return verify.main([args.run_dir])
    if args.command == "replay":
        from jobwatch import loop_replay

        try:
            return loop_replay.main(args.run_dir)
        except Exception as e:
            print(f"jobwatch: replay failed: {type(e).__name__}: {e}", file=sys.stderr)
            return OTHER
    from jobwatch.loop import run_loop

    kw = {}
    if clock is not None:
        kw["clock"] = clock
    if sleep is not None:
        kw["sleep"] = sleep
    if approver is None and args.interactive:
        approver = tty_approver()
    label = "live" if opener is None else "SEEDED"
    return run_loop(args.config, transport=opener, now=now, approver=approver, label=label, **kw)


def build_parser():
    """The JS1 parser, unchanged."""
    from jobwatch.backends import BACKENDS
    from jobwatch.judge import DEFAULT_MODEL

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
    from datetime import datetime, timezone

    if args.command == "run":
        from jobwatch.run import run

        return run(args, opener=opener, client=client, now=now)
    if args.command == "replay":
        from jobwatch.replay import replay

        return replay(args)
    clock = (lambda: now) if now is not None else (lambda: datetime.now(timezone.utc))
    if args.command == "sample":
        from jobwatch.sample import sample

        return sample(args, client=client, clock=clock)
    from jobwatch.experiment import experiment

    return experiment(args, client=client, clock=clock)


def main(argv=None, *, opener=None, anthropic_client=None, now=None, clock=None, sleep=None, approver=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if (argv and argv[0] in JS2_COMMANDS) or _is_loop_replay(argv):
        return _main_js2(argv, opener, now, clock, sleep, approver)
    from jobwatch.errors import Stop

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
