"""Command line for the JS2 loop.

    python -m jsagent run --config boards.json
    python -m jsagent run --config boards.json --state state/seen.json --no-claude
    python -m jsagent reset-state --state state/seen.json --approve reset-state
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from . import loop, resume as resume_mod
from .policy import ROOT, Policy, Refused


def write_report(policy: Policy, run_dir: Path, run_id: str, config: str, out: dict) -> Path:
    lines = [f"# Loop run {run_id}", "", f"- Config: `{config}`", f"- **Exit: {out['status']}**"]
    if out.get("reason"):
        lines.append(f"- Reason: {out['reason']}")
    if "requests_sent" in out:
        lines.append(f"- HTTP requests sent: {out['requests_sent']}")
    lines += ["", "| board | status | postings | new | note |", "|---|---|---|---|---|"]
    for r in out["boards"]:
        seeded = " (SEEDED file)" if r.get("seeded") else ""
        if r["status"] == "ok":
            note = "baseline: none reported as new" if r.get("baseline") else ""
            lines.append(f"| {r['board']}{seeded} | ok | {r['postings']} | {len(r['new'])} | {note} |")
        else:
            lines.append(f"| {r['board']}{seeded} | **{r['status']}** | — | **no result** | {r.get('reason', '')} |")
    news = [(r["board"], row) for r in out["boards"] for row in r.get("new", [])]
    if news:
        lines += ["", "## New postings", "",
                  "**Record** = the rule (recomputable). **Judgment** = Claude under prompt contract v2, an opinion.", ""]
        for board, row in news:
            rec, jud = row["record"], row["judgment"]
            j = jud.get("judgment") if jud.get("valid") else None
            lines += [f"**{board} — {rec['title']}** (`{rec['id']}`, {rec['location'] or 'no location'})", "",
                      f"- Record (rule): {rec['verdict']}. {rec['justification']}",
                      "- Judgment (Claude" + (f", {', '.join(jud.get('models_used') or [])}, {jud.get('started_at')}" if j else "")
                      + "): " + (f"{j['verdict']}, {j['confidence']} confidence. {j['justification']}" if j
                                 else "none: " + "; ".join(jud.get("errors", []))), ""]
    path = policy.check_write(run_dir / "report.md")
    path.write_text("\n".join(lines) + "\n")
    return path


def cmd_run(a) -> int:
    approvals = set(a.approve or [])
    policy = Policy(ROOT, approvals)
    run_id = dt.datetime.now().strftime("%Y-%m-%dT%H%M%S") + (f"-{a.label}" if a.label else "")
    run_dir = ROOT / a.runs_dir / run_id
    n = 2
    while run_dir.exists():
        run_dir = ROOT / a.runs_dir / f"{run_id}-{n}"
        n += 1
    try:
        config = json.loads(policy.check_read(a.config).read_text())
        resume = resume_mod.load(policy.check_read(a.resume))
    except (Refused, OSError, json.JSONDecodeError, resume_mod.ResumeInvalid) as e:
        print(f"exit: error — {e}")
        return 3
    budgets = loop.Budgets(**config.get("budgets", {}))
    out = loop.run(config["boards"], resume, policy, ROOT / a.state, run_dir, budgets,
                   use_claude=not a.no_claude, prompt=a.prompt)
    policy.check_write(run_dir / "run.json").write_text(json.dumps(
        {k: v for k, v in out.items() if k != "trace"}, indent=2, ensure_ascii=False, default=str) + "\n")
    report = write_report(policy, run_dir, run_dir.name, a.config, out)
    print(f"run {run_dir.name}: exit {out['status']}")
    for r in out["boards"]:
        print(f"  {r['board']:<40} {r['status']:<8} " + (f"{r['postings']} postings, {len(r['new'])} new" if r['status'] == 'ok'
                                                           else f"NO RESULT — {r.get('reason')}"))
    print(f"  report: {report.relative_to(ROOT)}")
    return {"finished": 0, "incomplete": 1, "budget-exhausted": 2}.get(out["status"], 3)


def cmd_reset(a) -> int:
    policy = Policy(ROOT, set(a.approve or []))
    try:
        path = policy.check_reset_state(ROOT / a.state)
    except Refused as e:
        print(f"refused: {e}")
        return 4
    if path.exists():
        path.unlink()
    print(f"state reset (approved: reset-state): {path.relative_to(ROOT)}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="jsagent")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--config", default="boards.json")
    r.add_argument("--resume", default="persona/priya-nair.resume.json")
    r.add_argument("--state", default="state/seen.json")
    r.add_argument("--runs-dir", default="runs")
    r.add_argument("--label")
    r.add_argument("--prompt", default="v2")
    r.add_argument("--no-claude", action="store_true")
    r.add_argument("--approve", action="append")
    s = sub.add_parser("reset-state")
    s.add_argument("--state", required=True)
    s.add_argument("--approve", action="append")
    a = p.parse_args(argv)
    return cmd_run(a) if a.cmd == "run" else cmd_reset(a)


if __name__ == "__main__":
    sys.exit(main())
