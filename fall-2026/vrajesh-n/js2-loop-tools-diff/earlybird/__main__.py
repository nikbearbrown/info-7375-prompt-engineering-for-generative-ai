"""CLI.

python -m earlybird run (--live | --replay YYYY-MM-DD) --label NAME [--only k1,k2] [--max-requests N] ...
python -m earlybird check --trace reports/NAME-trace.jsonl [--state data/state/seen.json]
python -m earlybird boards (list | add PLATFORM NAME | remove KEY)     # add/remove ask you to type yes
"""
import argparse
import json
from datetime import date
from pathlib import Path

from . import Refused, boards, check, gate, loop, report, watch
from .policy import Policy
from .resume import load_resume
from .tools import Tools, Trace

ROOT = Path(__file__).resolve().parent.parent
BOARDS_FILE = "config/boards.json"


def cmd_run(a):
    policy = Policy(ROOT)
    try:
        budget = gate.Budget(boards=a.max_boards, requests=a.max_requests, seconds=a.max_seconds)
        resume = load_resume(policy.check_read(a.resume))
    except Refused as e:
        print(f"REFUSED: {e}")
        return 2
    day = date.today().isoformat() if a.live else a.replay
    trace = Trace(budget)
    tools = Tools(policy, budget, trace, day, replay=not a.live)
    board_list = boards.load(tools.read_text(a.boards))
    if a.only:
        wanted = a.only.split(",")
        board_list = [b for b in board_list if b["key"] in wanted]
    state_file = policy.check_read(a.state)
    state = watch.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else watch.empty_state()

    result = loop.run(board_list, tools, budget, trace, state, resume, day, a.label)

    source = "live fetch" if a.live else f"replay of saved responses in data/raw/{day}/"
    if result["exit"] != "error":
        tools.write_text(a.state, watch.dumps(state))
    tools.write_text(f"reports/{a.label}-trace.jsonl", trace.jsonl())
    tools.write_text(f"reports/{a.label}.json", json.dumps(result, indent=2, ensure_ascii=False))
    tools.write_text(f"reports/{a.label}.md", report.markdown(result, source))
    for b in result["boards"]:
        if b["status"] == "ok":
            print(f"  {b['key']:24} ok     {b['postings']:4} postings, "
                  f"{'baseline' if b['baseline'] else str(b['new']) + ' new'}, {b['relevant']} relevant")
        else:
            print(f"  {b['key']:24} {b['status'].upper():6} {b['error']}")
    for k in result["not_attempted"]:
        print(f"  {k:24} not attempted")
    print(f"{a.label}: exit {result['exit']}" + (f" ({result['reason']})" if result["reason"] else "")
          + f" | budget {gate.Budget.describe(result['budget'])} | trace reports/{a.label}-trace.jsonl")
    return loop.EXIT_CODES[result["exit"]]


def cmd_check(a):
    out = check.check(ROOT, ROOT / a.trace, ROOT / a.state)
    print(f"independent check of {a.trace} (run said exit {out['exit_claimed']}):")
    for r in out["boards"]:
        mark = "ok " if r["claimed"] == r["recounted"] else "BAD"
        print(f"  {mark} {r['board']:24} trace {r['claimed']:>4} | recount of raw file {r['recounted']}")
    for p in out["problems"]:
        print(f"  PROBLEM: {p}")
    print(f"verdict: {out['verdict']}")
    return 0 if out["verdict"] == "PASS" else 4


def change_boards(root, action, ask=input, platform=None, name=None, key=None):
    """Add or remove a board. The write needs the owner to type yes (GATE.md permission policy)."""
    policy = Policy(root)
    current = boards.load(policy.check_read(BOARDS_FILE).read_text(encoding="utf-8"))
    if action == "add":
        new_key = f"{platform}:{name}"
        if any(b["key"] == new_key for b in current):
            print(f"{new_key} is already watched; nothing to change")
            return 0
        updated = current + [{"key": new_key, "platform": platform, "name": name}]
        print(f"Proposed change to {BOARDS_FILE}: ADD {new_key} -> {boards.url(updated[-1])}")
    else:
        updated = [b for b in current if b["key"] != key]
        if len(updated) == len(current):
            print(f"{key} is not in the list; nothing to change")
            return 0
        print(f"Proposed change to {BOARDS_FILE}: REMOVE {key}")
    boards.load(json.dumps(updated))  # validate before asking
    answer = ask("Type yes to approve: ")
    try:
        path = policy.check_write(BOARDS_FILE, approval=answer)
    except Refused as e:
        print(f"REFUSED: {e}")
        return 2
    path.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    print(f"approved and written: {len(current)} -> {len(updated)} boards")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="earlybird")
    sub = ap.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run")
    src = run.add_mutually_exclusive_group(required=True)
    src.add_argument("--live", action="store_true", help="fetch every board now and save each raw response")
    src.add_argument("--replay", metavar="YYYY-MM-DD", help="re-run on the responses saved for that day")
    run.add_argument("--label", required=True)
    run.add_argument("--only", help="comma-separated board keys (default: all in config/boards.json)")
    run.add_argument("--boards", default=BOARDS_FILE)
    run.add_argument("--state", default="data/state/seen.json")
    run.add_argument("--resume", default="data/resume/rohan-desai.example.json")
    run.add_argument("--max-boards", type=int, default=gate.MAX_BOARDS, help="may only lower GATE.md's limit")
    run.add_argument("--max-requests", type=int, default=gate.MAX_REQUESTS, help="may only lower GATE.md's limit")
    run.add_argument("--max-seconds", type=float, default=gate.MAX_SECONDS, help="may only lower GATE.md's limit")
    chk = sub.add_parser("check")
    chk.add_argument("--trace", required=True)
    chk.add_argument("--state", default="data/state/seen.json")
    bd = sub.add_parser("boards")
    bsub = bd.add_subparsers(dest="action", required=True)
    bsub.add_parser("list")
    add = bsub.add_parser("add")
    add.add_argument("platform", choices=sorted(boards.URLS))
    add.add_argument("name")
    rm = bsub.add_parser("remove")
    rm.add_argument("key")
    a = ap.parse_args(argv)

    if a.cmd == "run":
        return cmd_run(a)
    if a.cmd == "check":
        return cmd_check(a)
    if a.action == "list":
        for b in boards.load((ROOT / BOARDS_FILE).read_text(encoding="utf-8")):
            print(f"{b['key']:26} {boards.url(b)}")
        return 0
    return change_boards(ROOT, a.action, platform=getattr(a, "platform", None),
                         name=getattr(a, "name", None), key=getattr(a, "key", None))


if __name__ == "__main__":
    raise SystemExit(main())
