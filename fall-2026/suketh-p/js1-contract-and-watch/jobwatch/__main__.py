"""Command line: python3 -m jobwatch run|rule ... (see README.md for the exact commands)."""

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

from jobwatch import board, net, rule, transports
from jobwatch.errors import AgentError, InputError
from jobwatch.resume import validate_resume
from jobwatch.run import run_once


def read_resume(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise InputError("résumé file could not be read as JSON") from None


def read_saved(path):
    """Bytes of a saved response; a .gz file is decompressed (the repo stores raw responses gzipped)."""
    data = Path(path).read_bytes()
    return gzip.decompress(data) if str(path).endswith(".gz") else data


def replay(path):
    """A saved earlier response, served as if fetched. Runs that use it are labelled seeded."""
    def fetch():
        return net.FetchResult(read_saved(path), net.BOARD_URL, 200, "application/json (saved file)", net.utc_now())
    return fetch


def cmd_run(args):
    seeded = args.from_file is not None
    summary = run_once(
        fetch=replay(args.from_file) if seeded else net.fetch_board,
        resume=read_resume(args.resume),
        state_path=args.state,
        out_dir=args.out,
        send=transports.get(args.judge, args.model),
        mode="seeded" if seeded else "live",
        source=f"saved earlier response {args.from_file}" if seeded else "live GET of the board endpoint",
    )
    kind = "SEEDED replay" if seeded else "live fetch"
    first = "baseline (first run): 0 reported as new" if summary["baseline"] else f"{len(summary['new_ids'])} new since last run"
    print(f"{summary['run_id']}: {kind}, {summary['posting_count']} postings, {first}")
    for a in summary["assessments"]:
        print(f"  {a['posting_id']} {a['title']} | rule (record): {a['rule_verdict']['verdict']} "
              f"| Claude (model judgment): {a['claude_verdict']['verdict']}"
              f"{'' if a['verdicts_agree'] else ' | DISAGREE'}")
    print(f"  evidence: {summary['run_dir']}")


def cmd_rule(args):
    resume = validate_resume(read_resume(args.resume))
    postings = {p.id: p for p in board.parse_board(read_saved(args.raw))}
    if args.id not in postings:
        raise InputError(f"posting {args.id} is not in {args.raw}")
    print(json.dumps(rule.rule_verdict(resume, postings[args.id]), indent=2, ensure_ascii=False))


def cmd_verify(args):
    """Check that a run's saved raw response (plain or .gz) is byte-for-byte what retrieval.json recorded."""
    run_dir = Path(args.run_dir)
    recorded = json.loads((run_dir / "retrieval.json").read_text(encoding="utf-8"))
    plain, packed = run_dir / "raw_response.json", run_dir / "raw_response.json.gz"
    source = plain if plain.exists() else packed
    body = read_saved(source)
    digest = hashlib.sha256(body).hexdigest()
    if digest != recorded["sha256"] or len(body) != recorded["bytes"]:
        raise InputError(f"{source} does not match retrieval.json (sha256 {digest}, {len(body)} bytes)")
    print(f"OK {source}: {len(body)} bytes, sha256 {digest} matches retrieval.json "
          f"({recorded['mode']}, retrieved {recorded['retrieved_at']})")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m jobwatch",
                                     description="Job-Search Agent 1: one board, one fictional résumé, new postings only.")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="fetch the board (or replay a saved response) and report new postings")
    run.add_argument("--resume", required=True, help="fictional persona résumé (JSON)")
    run.add_argument("--state", required=True, type=Path, help="state file of seen posting ids")
    run.add_argument("--out", required=True, type=Path, help="directory for run evidence")
    run.add_argument("--from-file", type=Path, help="replay a saved earlier response; the run is labelled SEEDED")
    run.add_argument("--judge", choices=transports.CHOICES, default=transports.DEFAULT, help="how Claude is reached")
    run.add_argument("--model", default=transports.DEFAULT_MODEL, help="Claude model id")
    run.set_defaults(func=cmd_run)

    recompute = sub.add_parser("rule", help="recompute the rule record for one posting in a saved response")
    recompute.add_argument("--resume", required=True)
    recompute.add_argument("--raw", required=True, type=Path)
    recompute.add_argument("--id", required=True, type=int)
    recompute.set_defaults(func=cmd_rule)

    verify = sub.add_parser("verify", help="check a run's saved raw response against its recorded sha256")
    verify.add_argument("run_dir", type=Path)
    verify.set_defaults(func=cmd_verify)

    args = parser.parse_args(argv)
    try:
        args.func(args)
    except AgentError as error:
        print(f"error ({type(error).__name__}): {error}", file=sys.stderr)
        print("state file unchanged", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
