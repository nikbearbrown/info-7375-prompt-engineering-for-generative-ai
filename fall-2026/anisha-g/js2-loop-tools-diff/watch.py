"""Job-Search Agent 2 - a bounded, policy-checked watch over several boards.
  python3 watch.py run                         # one live run over boards.json
  python3 watch.py run --wrong empty_as_zero   # the FINISHED-WRONG demo (a deliberately wrong version; labelled WRONG-DEMO)
  python3 watch.py check reports/job-watch/runs/<run-id> [--live]   # independent check of a saved run"""
import argparse, importlib, json, sys
from pathlib import Path
from watcher.loop import Budget
from watcher.fetch import make_fetch
from watcher.store import Store
from watcher.policy import NeedsApproval, Blocked
from watcher.check import check_run, curl_count

HERE = Path(__file__).resolve().parent

def cmd_run(a):
    store = Store(HERE, label=("WRONG-DEMO-" + a.wrong) if a.wrong else "live")
    try:
        boards = json.loads((HERE / a.boards).read_text())["boards"]
        if not isinstance(boards, list): raise ValueError("'boards' must be a list")
    except Exception as e:                       # GATE 1 'Error': the run could not start -> still report it
        r = {"exit": "error", "why": f"the run could not start: cannot read {a.boards}: {e}", "boards": [], "run_id": store.run_id}
        store.write(store.run_dir / "trace.json", json.dumps(r, indent=1))
        print(f"{store.run_id}: exit=error ({r['why']})"); sys.exit(1)
    loop = importlib.import_module(f"wrong_versions.{a.wrong}" if a.wrong else "watcher.loop")
    seen, seen_file = store.load_seen()
    r = loop.run(boards, make_fetch(store.policy), budget=Budget(), seen=seen, on_raw=store.save_raw)
    r.update(run_id=store.run_id, state_read=seen_file, wrong_version=a.wrong,
             label=("DELIBERATELY WRONG VERSION - for the finished-wrong demo only" if a.wrong else "real run"))
    if not a.wrong:                                    # the wrong demo never touches the real state
        for b in r["boards"]:
            if b["status"] == "ok": seen.setdefault(b["board"], set()).update(b.pop("all_ids"))   # keep every id ever seen
        r["state_written"] = store.save_seen(seen).name
    for b in r["boards"]: b.pop("all_ids", None)
    try:
        store.write(store.run_dir / "trace.json", json.dumps(r, indent=1))
    except NeedsApproval as e:
        if input(f"{e}. Overwrite? [y/N] ").strip().lower() != "y": sys.exit("not overwritten")
        store.write(store.run_dir / "trace.json", json.dumps(r, indent=1), approved=True)
    print(f"{store.run_id}: exit={r['exit']} ({r['why']}); boards checked {r['boards_checked']}, new jobs {r['new_count']}, "
          f"requests {r['used']['requests']}/{r['budget']['requests']}, seconds {r['used']['seconds']}/{r['budget']['seconds']}")
    for b in r["boards"]:
        print(f"  {b['board']:<34} {b['status']:<12} jobs={b['jobs']} new={None if b['new'] is None else len(b['new'])} {b['error']}")
    for n in r["notes"]: print("  note:", n)
    print("  trace:", (store.run_dir / "trace.json").relative_to(HERE))

def cmd_check(a):
    p = check_run(a.run_dir, live=curl_count if a.live else None)
    print("INDEPENDENT CHECK:", "PASS - every 'ok' board matches its raw response" if not p else f"FAIL - {len(p)} problem(s)")
    for x in p: print("  -", x)
    sys.exit(1 if p else 0)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--boards", default="boards.json"); r.add_argument("--wrong", choices=["empty_as_zero", "retry_ignores_budget", "lever_reads_nothing"])
    c = sub.add_parser("check"); c.add_argument("run_dir"); c.add_argument("--live", action="store_true")
    a = ap.parse_args(); {"run": cmd_run, "check": cmd_check}[a.cmd](a)
