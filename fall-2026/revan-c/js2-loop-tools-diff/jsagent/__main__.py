"""CLI: python -m jsagent run --board klaviyo --resume resumes/aarav-patel.json [...]"""
import argparse
import json
import sys

from .fetch import FetchRefused
from .resume import ResumeError
from .run import RunError, run_once


def _failed(record):
    return [e["condition"] for e in record["rule_justification"] if not e["passed"]]


def print_summary(result):
    print(f"mode={result['mode'].upper()}  source={result['source']}")
    print(f"postings in response={result['postings_in_response']}  baseline={result['baseline']}  "
          f"new={result['new_count']}  run file={result['run_file']}")
    if result["baseline"]:
        print("Baseline run: ids saved, none reported as new.")
    for r in result["new_postings"]:
        failed = _failed(r)
        rule = r["rule_verdict"] + (f" (failed: {', '.join(failed)})" if failed else "")
        print(f"\n[{r['posting_id']}] {r['title']} | {r['location']}")
        print(f"  RULE (record):      {rule}")
        print(f"  CLAUDE ({r['claude_label']}): {r['claude_verdict']}")
        print(f"  authorization_flag={r['authorization_flag']}  e_verify={r['e_verify']}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="jsagent")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="one watch run")
    run.add_argument("--board", required=True)
    run.add_argument("--resume", required=True)
    run.add_argument("--seeded-response", help="saved Greenhouse JSON used instead of a live fetch")
    run.add_argument("--state", default="state/seen_ids.json")
    run.add_argument("--runs-dir", default="runs")
    run.add_argument("--evidence-dir", default="evidence")
    run.add_argument("--no-claude", action="store_true", help="skip the Claude judge")
    run.add_argument("--model", default=None)
    run.add_argument("--effort", default=None)
    run.add_argument("--prompt", default=None, help="system prompt file for the Claude judge")
    run.add_argument("--json", action="store_true", help="also print full records as JSON")
    args = parser.parse_args(argv)

    from .claude_judge import MISSING_CREDENTIALS, credentials_present

    judge = None
    if not args.no_claude and not credentials_present():
        # Checked before fetching: a run without credentials would advance state with no Claude verdicts.
        print(f"{MISSING_CREDENTIALS} (Or pass --no-claude.) State not advanced.", file=sys.stderr)
        return 5
    if not args.no_claude:
        from .claude_judge import DEFAULT_EFFORT, DEFAULT_MODEL, DEFAULT_PROMPT, make_claude_judge
        judge = make_claude_judge(args.model or DEFAULT_MODEL, args.effort or DEFAULT_EFFORT,
                                  args.prompt or DEFAULT_PROMPT)
    try:
        result = run_once(args.board, args.resume, seeded_response=args.seeded_response,
                          state_path=args.state, runs_dir=args.runs_dir,
                          evidence_dir=args.evidence_dir, claude_judge=judge)
    except FetchRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except ResumeError as exc:
        print(f"RÉSUMÉ REFUSED: {exc}", file=sys.stderr)
        return 3
    except RunError as exc:
        print(f"RUN STOPPED (state not advanced): {exc}", file=sys.stderr)
        return 4

    print_summary(result)
    if args.json:
        print(json.dumps(result["new_postings"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
