"""Chapter 1 sampling: ask Claude the same contract about the same posting in N fresh conversations.

Usage: python experiments/sampling.py --n 4 ID1 ID2 ID3 ID4 ID5
Every call is a separate `claude -p` process with no session, tools, or settings.
"""
import argparse
from collections import Counter
from datetime import datetime

from common import RESUME, ROOT, labels, postings, save
from earlybird import claude_judge, rule


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--prompt", default=str(ROOT / "experiments/prompts/baseline.txt"))
    a = ap.parse_args()
    ps, hand = postings(), {r["posting_id"]: r["hand_label"] for r in labels()}
    template = claude_judge.load_prompt(a.prompt)
    out = {"started": datetime.now().isoformat(timespec="seconds"), "prompt": a.prompt, "n": a.n, "postings": []}
    for pid in a.ids:
        p = ps[pid]
        calls = [claude_judge.judge(p, RESUME, template) for _ in range(a.n)]
        verdicts = [c["verdict"] if c["valid"] else "REJECTED" for c in calls]
        row = {"posting_id": pid, "title": p["title"], "hand_label": hand.get(pid) or None,
               "rule": rule.judge(p, RESUME)["verdict"], "verdicts": verdicts, "calls": calls}
        out["postings"].append(row)
        print(f"{p['title'][:50]:50} hand={row['hand_label']} rule={row['rule']} claude={dict(Counter(verdicts))}")
    save("sampling.json", out)


if __name__ == "__main__":
    main()
