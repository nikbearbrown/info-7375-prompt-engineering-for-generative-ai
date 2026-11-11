"""python3 -m jsagent run [--boards boards.json] [--run-id ID] [--replay MAP] [--approve-overwrite]
   python3 jsagent/check.py runs/<run_id>"""
import argparse
import datetime
import json
import pathlib
import sys

from jsagent import loop, persona, policy, transport

HERE = pathlib.Path(__file__).resolve().parent.parent


def main(argv=None):
    ap = argparse.ArgumentParser(prog="jsagent")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--boards", default="boards.json")
    r.add_argument("--run-id")
    r.add_argument("--runs-dir", default="runs")
    r.add_argument("--replay", help="SEEDED: answer from saved files listed in this map instead of the network")
    r.add_argument("--approve-overwrite", action="store_true", help="your approval to overwrite or delete saved files")
    a = ap.parse_args(argv)
    budgets = loop.load_budgets(HERE / "budgets.json", HERE / "GATE.md")
    files = policy.Files(HERE, HERE / a.runs_dir, approve=a.approve_overwrite)
    # Input files named on the command line go through the read rule (GATE.md section 6), so a
    # path outside this folder is refused before anything runs. Fixed 2026-11-10 after the regrade.
    boards = json.loads(files.read(HERE / a.boards))["boards"]
    view = persona.public_view(persona.load(HERE / "persona" / "alex_morgan.json"))
    run_id = a.run_id or datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if a.replay:
        run_id += "-SEEDED"
    t = transport.Replay(HERE / a.replay, read=files.read) if a.replay else transport.Live()
    rep = loop.run(boards, budgets, t, files, run_id, view)
    print(f"run {run_id}: exit {rep['exit']}  (requests {rep['requests_used']}/{budgets['max_requests']}, "
          f"seconds {rep['seconds_used']}/{budgets['max_seconds']})" + ("  [SEEDED replay]" if a.replay else ""))
    for b in rep["boards"]:
        show = lambda v: "-" if v is None else v
        print(f"  {b['name']:<26} {b['ats']:<10} {b['status']:<17} fetched {show(b['fetched'])!s:<5} new {show(b['new'])!s:<4}"
              + (f" error {b['error']}" if b["error"] else "") + ("  NEEDS REVIEW" if b["needs_review"] else ""))
        for p in b["new_postings"]:
            print(f"      new {p['posting_id']}: {p['title'][:60]} | {p['location'][:30]} -> rule (record): {p['verdict']}")
    print(f"summary: {a.runs_dir}/{run_id}/summary.md   trace: {a.runs_dir}/{run_id}/trace.jsonl")
    return {"finished": 0, "incomplete": 2, "budget-exhausted": 3, "error": 4}[rep["exit"]]


if __name__ == "__main__":
    sys.exit(main())
