"""The rule's verdict on every posting of a saved answer, to see what a change to the rule changes.

Usage (from the repo root):
  python3 tools/rule_verdicts.py <saved answer> --save <file.json>     the verdicts now, saved
  python3 tools/rule_verdicts.py <saved answer> --compare <file.json>  every posting whose verdict differs
  python3 tools/rule_verdicts.py <saved answer> --flips                contract v0.1 against v0.2, posting by posting
<saved answer> is read as in tools/explain_rule.py. The résumé is Jane Doe's.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

from explain_rule import load  # noqa: E402
from job_agent import resume, rule  # noqa: E402


def verdicts(answer: Path) -> dict:
    jane = resume.load(REPO / "persona" / "jane-doe.json")
    _, postings = load(answer)
    out = {}
    for p in postings:
        v = rule.judge(p, jane)
        out[p["id"]] = {"title": p["title"], "verdict": v["verdict"], "deciding_check": v["deciding_check"]}
    return out


def flips(answer: Path) -> list:
    jane = resume.load(REPO / "persona" / "jane-doe.json")
    _, postings = load(answer)
    out = []
    for p in postings:
        old, new = rule.judge(p, jane, contract="0.1"), rule.judge(p, jane, contract="0.2")
        if old["verdict"] != new["verdict"]:
            out.append((p, old, new))
    return out


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) == 2 and args[1] == "--flips":
        changed = flips(Path(args[0]))
        print(f"{len(changed)} verdicts differ between contract v0.1 and v0.2")
        for p, old, new in changed:
            print(f"- {p['title']} ({p['id']}): {old['verdict']} -> {new['verdict']}; check 7 now: "
                  f"{new['checks'][-1]['because']}")
        return 0
    if len(args) != 3 or args[1] not in ("--save", "--compare"):
        print("usage: python3 tools/rule_verdicts.py <saved answer> --save|--compare <file.json>")
        return 2
    now = verdicts(Path(args[0]))
    if args[1] == "--save":
        Path(args[2]).write_text(json.dumps(now, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        relevant = sum(1 for v in now.values() if v["verdict"] == "relevant")
        print(f"{len(now)} postings, {relevant} relevant by the rule; saved to {args[2]}")
        return 0
    before = json.loads(Path(args[2]).read_text(encoding="utf-8"))
    changed = [(i, before[i], now[i]) for i in now if i in before and before[i]["verdict"] != now[i]["verdict"]]
    print(f"{len(now)} postings; {len(changed)} verdicts changed")
    for i, old, new in changed:
        print(f"- {old['title']} ({i}): {old['verdict']} -> {new['verdict']} (deciding check {new['deciding_check']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
