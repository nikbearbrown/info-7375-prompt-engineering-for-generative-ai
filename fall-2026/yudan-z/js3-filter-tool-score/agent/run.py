"""One command: watch the board, judge each NEW posting twice (rule = record, Claude = model-judgment), write a report.

  python -m agent.run --workdir runs/live                       # real run against the live board
  python -m agent.run --workdir runs/seeded --from-file F.json  # SEEDED run against a saved response
  add --no-claude to skip the Claude judge (rule only)
"""
import argparse
import json
import os
import sys

from agent import judge, persona, report, rule, watch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", default="pinterest")
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--resume", default=os.path.join(ROOT, "persona", "resume.json"))
    ap.add_argument("--allowlist", default=os.path.join(ROOT, "config", "allowlist.json"))
    ap.add_argument("--from-file", default=None, help="SEEDED: read this saved response instead of the network")
    ap.add_argument("--prompt", default="contract_v1.txt")
    ap.add_argument("--no-claude", action="store_true")
    a = ap.parse_args(argv)

    try:
        resume = persona.validate_resume(json.load(open(a.resume, encoding="utf-8")))
    except persona.PersonaError as e:
        print(f"✗ STOP: {e}", file=sys.stderr)
        return 2
    allow = json.load(open(a.allowlist, encoding="utf-8"))["hosts"]
    fetcher = watch.http_get
    if a.from_file:
        data = open(a.from_file, "rb").read()
        fetcher = lambda url: data      # still passes through the allow-list check in watch.fetch
    try:
        new = watch.run_watch(a.board, a.workdir, allow, fetcher=fetcher)
    except watch.NotAllowed as e:
        print(f"✗ STOP: {e}", file=sys.stderr)
        return 2

    state = json.load(open(os.path.join(a.workdir, "state", "seen_ids.json"), encoding="utf-8"))
    rule_by_id = {j["id"]: rule.judge(j, resume) for j in new}
    claude_by_id = {}
    if not a.no_claude:
        for j in new:
            claude_by_id[j["id"]] = judge.judge(j, resume, a.prompt)
    records = report.assemble(new, rule_by_id, claude_by_id)
    stamp = state["last_run"]
    with open(os.path.join(a.workdir, f"report-{stamp}.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"board": a.board, "run": stamp, "seeded": bool(a.from_file), "baseline": state["baseline_run"],
                   "seen_total": len(state["seen_ids"]), "new": records}, f, indent=1, ensure_ascii=False)
    with open(os.path.join(a.workdir, f"report-{stamp}.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(report.to_markdown(records, a.board, stamp, seeded=bool(a.from_file)))
    kind = "BASELINE" if state["baseline_run"] else "run"
    print(f"✓ {kind} {stamp}{' (SEEDED)' if a.from_file else ''}: {len(state['seen_ids'])} ids seen in total · "
          f"{len(new)} new · rule relevant {sum(r['rule_verdict'] == 'relevant' for r in records)} · "
          f"claude valid {sum(1 for c in claude_by_id.values() if c['status'] == 'valid')}/{len(claude_by_id)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
