"""CLI: python3 -m jobwatch run --board stripe --resume personas/maya-sehgal.resume.json"""
import argparse
import pathlib
import sys

from . import fetch, resume, state, watch


def main(argv=None):
    ap = argparse.ArgumentParser(prog="jobwatch")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="one watch run")
    r.add_argument("--board", default="stripe")
    r.add_argument("--resume", default="personas/maya-sehgal.resume.json")
    r.add_argument("--state", default="runs/state.json")
    r.add_argument("--runs-dir", default="runs")
    r.add_argument("--claude", action="store_true", help="also ask Claude (claude CLI) for a labeled judgment")
    r.add_argument("--model", default="sonnet")
    r.add_argument("--prompt", default="prompts/judge_v1.txt")
    r.add_argument("--seeded-raw", help="SEEDED run: read this saved response instead of fetching")
    a = ap.parse_args(argv)

    judge = None
    if a.claude:
        from . import claude_judge
        judge = claude_judge.make_judge(pathlib.Path(a.prompt), model=a.model)
    seeded = pathlib.Path(a.seeded_raw).read_bytes() if a.seeded_raw else None
    try:
        rec = watch.run(a.board, a.resume, a.state, a.runs_dir, claude_judge=judge,
                        seeded_raw=seeded, seeded_from=a.seeded_raw)
    except (fetch.FetchError, fetch.HostNotAllowed, resume.ResumeError, state.StateError) as e:
        print(f"run refused/failed, state file not changed: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    c = rec["counts"]
    kind = "SEEDED " if rec["seeded"] else ""
    kind += "baseline " if rec["baseline"] else ""
    print(f"{kind}run {rec['run_time']}: fetched {c['fetched']}, new {c['new']}, "
          f"relevant(rule) {c['relevant_rule']}, skipped {c['skipped']}, relevant(Claude) {c['relevant_claude']}, "
          f"invalid(Claude) {c['invalid_claude']}")
    print(f"report: {rec['report_path']}\nrecord: {rec['record_path']}\nraw: {rec['raw_response_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
