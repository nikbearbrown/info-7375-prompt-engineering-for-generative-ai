"""Command line: python3 -m sponsorsql <command> ...

  load SOURCE.xlsx DB.sqlite         verify the workbook checksum, load 18 public fields
  ask --db DB --question "..."       one question through the full loop and the human gate
  prompts --set SET --contract C     write the exact prompt text for every question in a set
  evaluate --db DB --set SET --responses R --contract C --out OUT
  failures --db DB --out OUT         run the deliberate failure cases and the controlled failure
  status                             summarize the ledger of past runs
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from . import agent, evaluate, failures, prompt
from .adapters import ClaudeCLIAdapter, RecordedAdapter
from .config import Budget


def _write_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n",
                          encoding="utf-8")


def cmd_load(args):
    from .load import load
    load(args.source, args.db)


def cmd_ask(args):
    if args.adapter == "recorded":
        if not args.responses:
            sys.exit("--responses is required with --adapter recorded")
        adapter = RecordedAdapter(args.responses)
    else:
        adapter = ClaudeCLIAdapter()
    state = agent.run(args.question, adapter, args.db, args.contract, qid=args.qid,
                      output_shape=args.output or "", budget=Budget(), gate_mode=args.gate,
                      decision_file=args.decision_file, state_dir=args.state, outputs_dir=args.outputs)
    print(f"\nrun {state.run_id}: stop = {state.stop_reason}")
    print(f"adapter: {state.adapter}")
    if state.view_hash:
        print(f"view SHA-256: {state.view_hash}")
    if state.export_path:
        print(f"report written: {state.export_path}")
    print(f"state saved under {args.state}/runs/{state.run_id}.json")


def cmd_prompts(args):
    qset = json.loads(Path(args.set).read_text(encoding="utf-8"))
    contract_text = Path(args.contract).read_text(encoding="utf-8")
    out = {q["id"]: prompt.build(contract_text, q["question"], q.get("output", ""))
           for q in qset["questions"]}
    _write_json(args.out, {"contract": Path(args.contract).name,
                           "contract_sha256": evaluate.sha256_file(args.contract),
                           "question_set": Path(args.set).name, "prompts": out})
    print(f"wrote {len(out)} prompts to {args.out}")


def cmd_evaluate(args):
    report = evaluate.run_set(args.set, args.responses, args.db, args.contract, args.state)
    _write_json(args.out, report)
    print(f"{report['set']}: {report['passes']}/{report['total']} pass "
          f"(policy denials {report['policy_denials_total']}, "
          f"executed SQL failing policy {report['executed_sql_failing_policy']})")
    for r in report["results"]:
        print(f"  {r['id']:4} {'PASS' if r['pass'] else 'FAIL'}  stop={r['stop_reason']}")


def cmd_failures(args):
    report = failures.run_all(args.db)
    _write_json(args.out, report)
    print(f"deliberate failure cases behaving as predicted: {report['passed_as_predicted']}/{report['total']}")
    for c in report["cases"]:
        print(f"  {c['id']:4} {'as predicted' if c['as_predicted'] else 'NOT as predicted'}  "
              f"stop={c['actual_stop']}  caught by {c['caught_by']}")
    cf = report["controlled_failure"]
    if cf:
        print(f"  {cf['id']}   trigger pass={cf['trigger']['pass_against_key']}  "
              f"recovery pass={cf['recovery']['pass_against_key']}  "
              f"{'as predicted' if cf['as_predicted'] else 'NOT as predicted'}")


def cmd_status(args):
    ledger = Path(args.state) / "ledger.jsonl"
    if not ledger.exists():
        print("no runs recorded yet")
        return
    lines = [json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines() if x.strip()]
    print(f"{len(lines)} runs")
    for reason, n in Counter(x["stop_reason"] for x in lines).most_common():
        print(f"  {reason}: {n}")


def main(argv=None):
    here = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(prog="sponsorsql", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("load")
    s.add_argument("source")
    s.add_argument("db")
    s.set_defaults(func=cmd_load)

    s = sub.add_parser("ask")
    s.add_argument("--db", required=True)
    s.add_argument("--question", required=True)
    s.add_argument("--qid", default="adhoc")
    s.add_argument("--output", help="optional output shape for the answer query")
    s.add_argument("--adapter", choices=("recorded", "claude-cli"), default="recorded")
    s.add_argument("--responses", help="recorded replies file (with --adapter recorded)")
    s.add_argument("--contract", default=str(here / "evals" / "PROMPT-CONTRACT-v2.md"))
    s.add_argument("--gate", choices=("interactive", "file", "none"), default="interactive")
    s.add_argument("--decision-file")
    s.add_argument("--state", default=str(here / "state"))
    s.add_argument("--outputs", default=str(here / "outputs"))
    s.set_defaults(func=cmd_ask)

    s = sub.add_parser("prompts")
    s.add_argument("--set", required=True)
    s.add_argument("--contract", required=True)
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_prompts)

    s = sub.add_parser("evaluate")
    s.add_argument("--db", required=True)
    s.add_argument("--set", required=True)
    s.add_argument("--responses", required=True)
    s.add_argument("--contract", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--state", default=str(here / "state"))
    s.set_defaults(func=cmd_evaluate)

    s = sub.add_parser("failures")
    s.add_argument("--db", required=True)
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_failures)

    s = sub.add_parser("status")
    s.add_argument("--state", default=str(here / "state"))
    s.set_defaults(func=cmd_status)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
