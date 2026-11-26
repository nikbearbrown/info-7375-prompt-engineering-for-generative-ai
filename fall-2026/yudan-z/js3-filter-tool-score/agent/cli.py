"""One bounded run over the configured boards (GATE.md). Prints and saves the exit status, the per-board
results, the trace and the raw responses.

  python -m agent.cli --workdir runs/live
  python -m agent.cli --workdir runs/live --approve reset-state:greenhouse/pinterest --reset-state greenhouse/pinterest
Exit codes: 0 finished · 2 error · 3 incomplete · 4 budget-exhausted
"""
import argparse
import json
import os
import sys

from agent import loop, persona, policy, tools
from agent.tools import Tools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def to_markdown(res, boards_file):
    lines = [f"# Run {res['run']} — exit `{res['exit']}`", "",
             f"Boards file: `{boards_file}` · budget used: {res['budget']['boards']} boards, "
             f"{res['budget']['requests']} requests, {res['budget']['seconds']} s "
             f"(limits {res['budget']['limits']})", ""]
    if res["stop_reason"]:
        lines += [f"Stopped: {res['stop_reason']}", ""]
    lines += ["| System | Board | Status | Postings | New | Note |", "|---|---|---|---|---|---|"]
    for b in res["boards"]:
        note = "baseline" if b.get("baseline") else (b.get("error", "") if b["status"] != "ok" else "")
        lines.append(f"| {b['system']} | {b['board']} | {b['status']} | {b.get('postings', '—')} | "
                     f"{b.get('new', '—')} | {note} |")
    for name in res["not_reached"]:
        lines.append(f"| | {name} | not reached | — | — | |")
    for b in res["boards"]:
        for p in b.get("new_postings", []):
            r = p.get("rule", {})
            lines.append("")
            lines.append(f"- **{b['board']} {p['id']}** {p['title']} ({p['location']}): rule (record) "
                         f"**{r.get('verdict', '—')}**; failed checks: "
                         + (", ".join(x["check"] for x in r.get("reasons", []) if x.get("result") == "fail") or "none"))
    return "\n".join(lines) + "\n"


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--boards", default=os.path.join(ROOT, "config", "boards.json"))
    ap.add_argument("--resume", default=os.path.join(ROOT, "persona", "resume.json"))
    ap.add_argument("--approve", action="append", default=[], help="an approval key, e.g. reset-state:greenhouse/pinterest")
    ap.add_argument("--reset-state", action="append", default=[], help="system/board whose seen ids to reset (needs --approve)")
    for k in loop.LIMITS:
        ap.add_argument("--" + k.replace("_", "-"), type=float if k == "max_seconds" else int, default=None,
                        help=f"lower the GATE budget (max {loop.LIMITS[k]})")
    a = ap.parse_args(argv)

    hosts = json.load(open(os.path.join(ROOT, "config", "allowlist.json"), encoding="utf-8"))["hosts"]
    pol = policy.Policy(ROOT, hosts, write_dir="runs", approvals=a.approve)
    workdir = os.path.abspath(a.workdir)
    try:
        # refuse a workdir outside runs/ before any request: a fetched board must have somewhere to be saved
        pol.check_write(os.path.join(workdir, "probe"))
        resume = persona.validate_resume(json.load(open(a.resume, encoding="utf-8")))
        limits = {k: getattr(a, k) for k in loop.LIMITS if getattr(a, k) is not None}
        loop.Budget(**limits)                                     # refuses a raised budget before anything runs
        for sb in a.reset_state:
            Tools(pol, loop.Budget(), trace=[]).reset_state(
                os.path.join(workdir, "state", sb.replace("/", "-") + ".json"), f"reset-state:{sb}")
            print(f"• reset seen ids for {sb} (approved)")
    except (persona.PersonaError, ValueError, policy.Refused) as e:
        print(f"✗ STOP: {e}", file=sys.stderr)
        return 2
    boards = [tuple(b) for b in json.load(open(a.boards, encoding="utf-8"))["boards"]]

    res = loop.run(boards, workdir, pol, resume=resume, fetcher=tools.http_get,
                   on_board=lambda b: print(f"  · {b['system']}/{b['board']}: {b['status']}"
                                            + (f", {b['postings']} postings, {b['new']} new"
                                               + (" (baseline)" if b.get("baseline") else "")
                                               if b["status"] == "ok" else f" — {b.get('error')}")),
                   **limits)
    out = {k: v for k, v in res.items() if k != "trace"}
    out["boards_file"] = os.path.relpath(a.boards, ROOT).replace(os.sep, "/")
    base = os.path.join(workdir, f"run-{res['run']}")
    t = Tools(pol, loop.Budget(), trace=[])
    t.write_new(base + ".json", json.dumps(out, indent=1, ensure_ascii=False, default=str).encode("utf-8"))
    t.write_new(base + ".md", to_markdown(res, out["boards_file"]).encode("utf-8"))
    print(f"{'✓' if res['exit'] == 'finished' else '!'} run {res['run']}: exit {res['exit']} "
          f"(code {res['exit_code']}) · requests {res['budget']['requests']}/{res['budget']['limits']['max_requests']}"
          f" · {res['budget']['seconds']} s" + (f" · {res['stop_reason']}" if res["stop_reason"] else ""))
    for name in res["not_reached"]:
        print(f"  · {name}: not reached")
    return res["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
