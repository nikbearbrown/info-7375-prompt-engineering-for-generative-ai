"""Chapter 2 prompt experiment: run one prompt over one labeled set and score it against my hand labels.

Usage: python experiments/prompt_experiment.py baseline dev
       python experiments/prompt_experiment.py revision dev
       python experiments/prompt_experiment.py baseline heldout --final   (only at the very end)
A rejected (invalid) answer counts as a fail.
"""
import argparse
from datetime import datetime

from common import RESUME, ROOT, labels, postings, save
from earlybird import claude_judge, rule


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", choices=["baseline", "revision"])
    ap.add_argument("set", choices=["dev", "heldout"])
    ap.add_argument("--final", action="store_true", help="required to touch the held-out set")
    a = ap.parse_args()
    if a.set == "heldout" and not a.final:
        raise SystemExit("held-out set is locked until the end; pass --final once both prompts are frozen")
    rows = [r for r in labels() if r["set"] == a.set]
    if any(r["hand_label"] not in ("relevant", "not_relevant") for r in rows):
        raise SystemExit("every row in this set needs a hand_label first")
    ps = postings()
    template = claude_judge.load_prompt(ROOT / f"experiments/prompts/{a.prompt}.txt")
    results = []
    for r in rows:
        p = ps[r["posting_id"]]
        j = claude_judge.judge(p, RESUME, template)
        got = j["verdict"] if j["valid"] else "REJECTED"
        results.append({"posting_id": p["id"], "title": p["title"], "hand_label": r["hand_label"],
                        "rule": rule.judge(p, RESUME)["verdict"], "claude": got, "pass": got == r["hand_label"],
                        "judgment": j})
        print(f"{'PASS' if got == r['hand_label'] else 'FAIL'}  {p['title'][:50]:50} hand={r['hand_label']} claude={got}")
    passed = sum(x["pass"] for x in results)
    rule_passed = sum(x["rule"] == x["hand_label"] for x in results)
    print(f"{a.prompt} on {a.set}: claude {passed}/{len(results)}, written rule {rule_passed}/{len(results)}")
    save(f"{a.prompt}-{a.set}.json", {"run_at": datetime.now().isoformat(timespec="seconds"), "prompt": a.prompt,
                                      "set": a.set, "claude_pass": passed, "rule_pass": rule_passed,
                                      "n": len(results), "results": results})


if __name__ == "__main__":
    main()
