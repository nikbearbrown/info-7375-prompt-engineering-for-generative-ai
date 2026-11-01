"""Prompt experiment (Chapter 2): score a prompt contract against hand labels.

    python experiments/prompt_experiment.py --prompt prompts/judge_baseline.md --set dev
    python experiments/prompt_experiment.py --prompt prompts/judge_revision.md --set dev
    python experiments/prompt_experiment.py --prompt prompts/judge_baseline.md --set heldout --final
    python experiments/prompt_experiment.py --prompt prompts/judge_revision.md --set heldout --final

It refuses to run until every hand label in the chosen set is filled in (labels come first),
and refuses the held-out set without --final (the held-out set is only for the end).
A case passes only if Claude's reply is valid AND its verdict equals the hand label.
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent import claude_judge, rule  # noqa: E402
from agent.config import ROOT  # noqa: E402
from agent.postings import load_postings  # noqa: E402
from agent.resume import load_resume  # noqa: E402

HERE = Path(__file__).resolve().parent
LABELS = HERE / "labels.csv"
RAW = ROOT / "evidence" / "raw" / "20261031T233955Z_figma_live.json"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", type=Path, required=True)
    ap.add_argument("--set", choices=("dev", "heldout"), required=True)
    ap.add_argument("--final", action="store_true", help="required for the held-out set")
    args = ap.parse_args()
    if args.set == "heldout" and not args.final:
        sys.exit("refused: the held-out set is only run at the end; pass --final when you are done with dev")

    with LABELS.open(encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["set"] == args.set]
    unlabeled = [r["id"] for r in rows if r["hand_label"].strip() not in claude_judge.VERDICTS]
    if unlabeled:
        sys.exit(f"refused: hand_label missing or not relevant/not_relevant for ids {unlabeled}")

    resume = load_resume(ROOT / "data" / "resume_jack_spencer.json")
    by_id = {p["id"]: p for p in load_postings(RAW)}
    postings = [by_id[int(r["id"])] for r in rows]
    hand = {int(r["id"]): r["hand_label"].strip() for r in rows}
    template = args.prompt.read_text(encoding="utf-8")
    replies = claude_judge.judge_all(postings, resume, template)

    cases, passed, rule_agree = [], 0, 0
    for p in postings:
        c, r = replies[p["id"]], rule.judge(p, resume)
        ok = c["valid"] and c["verdict"] == hand[p["id"]]
        passed += ok
        rule_agree += r["verdict"] == hand[p["id"]]
        cases.append({"id": p["id"], "title": p["title"], "hand_label": hand[p["id"]],
                      "claude": c["verdict"] if c["valid"] else f"INVALID ({c['rejection']})",
                      "pass": ok, "rule": r["verdict"], "reply": c})

    stamp = datetime.now(timezone.utc)
    out = HERE / "results" / f"{args.prompt.stem}_{args.set}_{stamp:%Y%m%dT%H%M%SZ}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"prompt": args.prompt.as_posix(), "set": args.set,
                               "run_at_utc": stamp.isoformat(timespec="seconds"),
                               "passed": passed, "total": len(cases), "rule_agrees_with_hand": rule_agree,
                               "cases": cases}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"{args.prompt.name} on {args.set}: {passed}/{len(cases)} pass   (rule vs hand: {rule_agree}/{len(cases)})")
    for c in cases:
        print(f"  {'PASS' if c['pass'] else 'FAIL'}  {c['id']}  hand={c['hand_label']:13} "
              f"claude={c['claude'][:40]:40} rule={c['rule']}  {c['title'][:45]}")
    print(f"saved {out}")


if __name__ == "__main__":
    main()
