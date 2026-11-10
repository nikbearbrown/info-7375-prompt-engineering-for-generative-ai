"""Command line. `python3 -m agent watch` (one real run), `watch --wrong-version 3` (the labelled demonstration),
`check RUN_DIR` (the independent check)."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import check, config, loop, resume, wrong_versions
from .policy import Policy


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m agent")
    commands = parser.add_subparsers(dest="command", required=True)
    w = commands.add_parser("watch", help="one bounded run over config/boards.json")
    w.add_argument("--wrong-version", type=int, choices=sorted(wrong_versions.VERSIONS),
                   help="run a deliberate wrong version (labelled WRONG, its own state file); for the demonstration only")
    c = commands.add_parser("check", help="compare a run's report with its saved raw responses")
    c.add_argument("run_dir")
    args = parser.parse_args(argv)

    policy = Policy()
    if args.command == "check":
        problems, notes = check.check(Path(args.run_dir).resolve(), config.ROOT, policy)
        for note in notes:
            print(f"note: {note}")
        if problems:
            print("CHECK FAILED")
            for p in problems:
                print(f"- {p}")
            return 1
        print("check passed: the report matches the saved raw responses")
        return 0

    persona = resume.load(policy.check_read(config.RESUME))  # refuses a non-fictional résumé before any request
    now = datetime.now(timezone.utc).replace(microsecond=0)
    tag = f"-WRONG-V{args.wrong_version}" if args.wrong_version else ""
    state_path = config.STATE.with_name(f"seen_ids{tag}.json") if tag else config.STATE
    if tag and not state_path.exists():
        state_path = config.STATE  # start the demonstration from the real state, but never write back to it
    state = json.loads(policy.check_read(state_path).read_text(encoding="utf-8")) if state_path.exists() else {}
    hooks = wrong_versions.VERSIONS[args.wrong_version] if args.wrong_version else None

    boards, budgets = (json.loads(policy.check_read(config.CONFIG_DIR / f"{n}.json").read_text(encoding="utf-8"))
                       for n in ("boards", "budgets"))
    result = loop.run(boards, budgets, policy, persona, state, config.RAW_DIR,
                      now=now, hooks=hooks, tag=tag)

    run_dir = config.RUNS_DIR / f"{now.strftime('%Y%m%dT%H%M%SZ')}{tag}"
    label = f" (WRONG VERSION {args.wrong_version}, deliberate: see FINISHED-WRONG.md)" if tag else ""
    policy.write_text(run_dir / "trace.jsonl", loop.trace_jsonl(result))
    policy.write_text(run_dir / "report.json", json.dumps(loop.summary(result), indent=2, ensure_ascii=False) + "\n")
    policy.write_text(run_dir / "report.md", loop.report_markdown(result, label))
    if result.status != "error":
        state.setdefault("runs", []).append({"at": result.started_at, "status": result.status, "run": run_dir.name})
        policy.write_text(config.STATE.with_name(f"seen_ids{tag}.json"), json.dumps(state, indent=2) + "\n")
    print(loop.report_markdown(result, label))
    print(f"(trace, report and raw responses saved under {run_dir.relative_to(config.ROOT)}/ and evidence/raw/)")
    return 0 if result.status == "finished" else 3


if __name__ == "__main__":
    sys.exit(main())
