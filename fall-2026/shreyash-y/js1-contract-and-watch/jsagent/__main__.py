"""Command line:  python3 -m jsagent run --board oscar [--claude-prompt prompts/baseline-v1.md]
                  python3 -m jsagent run --board oscar --from-raw FILE --runs-dir runs-seeded
                  python3 -m jsagent check-persona persona/alex_morgan.json"""
import argparse
import datetime
import functools
import sys

from jsagent import claude_judge, persona, watch


def main(argv=None):
    ap = argparse.ArgumentParser(prog="jsagent")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="one watch run")
    r.add_argument("--board", required=True)
    r.add_argument("--resume", default="persona/alex_morgan.json")
    r.add_argument("--runs-dir", default="runs")
    r.add_argument("--from-raw", help="judge a saved response instead of fetching (a SEEDED run)")
    r.add_argument("--seeded-label", help="what the seeded run stands for")
    r.add_argument("--claude-prompt", help="also ask Claude about each new posting with this prompt")
    r.add_argument("--model", default=claude_judge.DEFAULT_MODEL)
    c = sub.add_parser("check-persona")
    c.add_argument("path")
    a = ap.parse_args(argv)

    if a.cmd == "check-persona":
        errors = persona.validate(__import__("json").load(open(a.path)))
        print("persona OK (fictional, example.com email, 555 phone, all rule fields present)"
              if not errors else "persona REFUSED: " + "; ".join(errors))
        return 1 if errors else 0

    run_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    claude = None
    if a.claude_prompt:
        claude = lambda p, view: claude_judge.judge(a.claude_prompt, view, p,
                                                    f"{a.runs_dir}/claude-calls", "watch", a.model)
    report = watch.run(a.board, a.resume, a.runs_dir, run_at, a.from_raw, a.seeded_label, claude)
    print(f"{report['source']}")
    print(f"fetched {report['fetched']} postings; seen before: {report['seen_before_this_run']}; "
          f"baseline: {report['baseline']}; new: {report['new_count']}; "
          f"gone since last run: {len(report['removed_since_last_run'])}")
    for rec in report["new"]:
        line = f"  {rec['posting_id']}  rule (record): {rec['verdict']:<12}"
        if rec.get("claude"):
            c = rec["claude"]
            line += (f"  Claude (judgment): {c['parsed']['verdict']}" if c["valid"]
                     else f"  Claude output REJECTED: {c['errors'][0]}")
        print(line + f"  {rec['title']} | {rec['location']}")
    print(f"raw response saved: {report['raw_file']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
