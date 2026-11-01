"""Sampling report (Chapter 1): ask Claude the same contract about the same posting several times, each in a
fresh conversation (`claude -p`), and record every verdict.

  python -m experiment.sampling --ns 1 3 4 9 10 --times 4

Postings come from the development split only, so the held-out set stays unseen until the end.
"""
import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from agent import judge  # noqa: E402


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", type=int, nargs="+", required=True)
    ap.add_argument("--times", type=int, default=4)
    ap.add_argument("--prompt", default="contract_v1.txt")
    a = ap.parse_args(argv)
    E = os.path.join(ROOT, "experiment")
    resume = json.load(open(os.path.join(ROOT, "persona", "resume.json"), encoding="utf-8"))
    split = {p["n"]: p for p in json.load(open(os.path.join(E, "split.json"), encoding="utf-8"))["postings"]}
    labels = {l["n"]: l["label"] for l in json.load(open(os.path.join(E, "labels.json"), encoding="utf-8"))["labels"]}
    out = []
    for n in a.ns:
        p = split[n]
        assert p["split"] == "dev", "sampling uses development postings only"
        posting = json.load(open(os.path.join(E, "postings", f"{p['board']}-{p['id']}.json"), encoding="utf-8"))
        runs = []
        for k in range(a.times):
            r = judge.judge(posting, resume, a.prompt)
            runs.append({"try": k + 1, "verdict": r.get("verdict"), "status": r["status"],
                         "justification": r.get("justification"), "error": r.get("error"), "raw": r["raw"],
                         "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        c = Counter(x["verdict"] or "invalid" for x in runs)
        out.append({"n": n, "title": p["title"], "hand_label": labels[n], "counts": dict(c), "runs": runs})
        print(f"  {n:>2} {p['title'][:48]:<48} hand={labels[n]:<12} verdicts={dict(c)}")
    with open(os.path.join(E, "results", "sampling.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"prompt": a.prompt, "times": a.times, "model_via": "Claude Code CLI `claude -p`, fresh conversation per try",
                   "postings": out}, f, indent=1, ensure_ascii=False)
    print("✓ sampling written to experiment/results/sampling.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
