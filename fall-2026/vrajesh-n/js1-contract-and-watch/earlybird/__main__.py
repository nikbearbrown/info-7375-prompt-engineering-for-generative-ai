"""CLI: python -m earlybird run (--snapshot FILE --day YYYY-MM-DD | --live) [--claude] --label NAME"""
import argparse
import json
from datetime import date
from pathlib import Path

from . import Refused, claude_judge, fetch, rule, validate
from .resume import load_resume
from .watch import watch

ROOT = Path(__file__).resolve().parent.parent


def write_report(label, day, source, rows):
    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    (out / f"{label}.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [f"# Early Bird report: {label}", "", f"- Run on: {date.today().isoformat()}",
             f"- Board day: {day}", f"- Source: {source}", f"- New postings: {len(rows)}", ""]
    for r in rows:
        rec, jud = r["record"], r.get("judgment")
        lines += [f"## {rec['title']}", f"`{rec['posting_id']}`", "",
                  f"- **Record (written rule, recomputable):** {rec['verdict']} - {rec['justification']} "
                  f"(resume: {', '.join(rec['resume_fields'])}; posting: {', '.join(rec['posting_fields'])})"]
        if jud is None:
            lines.append("- **Judgment (Claude):** not requested")
        elif jud["valid"]:
            lines.append(f"- **Judgment (Claude {jud['model']}, {jud['date']}; a model's opinion, not a fact):** "
                         f"{jud['verdict']} - {jud['justification']}")
        else:
            lines.append(f"- **Judgment (Claude):** rejected by validator, not shown ({'; '.join(jud['errors'])})")
        lines.append("")
    (out / f"{label}.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="earlybird")
    sub = ap.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run")
    run.add_argument("--board", default="commure", choices=sorted(fetch.BOARDS))
    src = run.add_mutually_exclusive_group(required=True)
    src.add_argument("--snapshot", help="replay a saved raw response instead of fetching")
    src.add_argument("--live", action="store_true", help="fetch the board now and save the raw response")
    run.add_argument("--day", help="board day of the snapshot (YYYY-MM-DD)")
    run.add_argument("--label", required=True)
    run.add_argument("--resume", default=str(ROOT / "data/resume/rohan-desai.example.json"))
    run.add_argument("--state", default=str(ROOT / "data/state/seen.json"))
    run.add_argument("--claude", action="store_true", help="also ask Claude for a labeled judgment")
    run.add_argument("--prompt", default=str(ROOT / "experiments/prompts/baseline.txt"))
    a = ap.parse_args(argv)

    try:
        resume = load_resume(a.resume)
        if a.live:
            day = date.today().isoformat()
            body = fetch.fetch(fetch.BOARDS[a.board])
            path = fetch.save_raw(body, ROOT / "data/raw", day, a.board)
            source = f"live fetch of {fetch.BOARDS[a.board]}, saved to {path.relative_to(ROOT).as_posix()}"
        else:
            if not a.day:
                ap.error("--snapshot needs --day")
            day, body = a.day, Path(a.snapshot).read_bytes()
            source = f"saved response {Path(a.snapshot).as_posix()} (replayed, fetched on {day})"
    except Refused as e:
        print(f"REFUSED: {e}")
        return 2

    postings = json.loads(body)["jobs"]
    if not postings:
        print("FAILURE (CONTRACT.md): zero postings fetched")
        return 1
    new = watch(postings, a.state, a.board, day, a.label)
    template = claude_judge.load_prompt(a.prompt) if a.claude else None
    rows = []
    for p in new:
        rec = rule.judge(p, resume)
        assert not validate.errors(rec, p, resume), rec
        rows.append({"record": rec, "judgment": claude_judge.judge(p, resume, template) if a.claude else None})
    write_report(a.label, day, source, rows)
    print(f"{a.label}: {len(postings)} postings, {len(new)} new "
          f"({sum(r['record']['verdict'] == 'relevant' for r in rows)} relevant by the rule)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
