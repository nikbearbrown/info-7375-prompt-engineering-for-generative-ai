"""Prompt experiment (Chapter 2): run one prompt contract on one split, compare Claude's verdict with my hand label.

  python -m experiment.run_experiment --prompt contract_v1.txt --split dev
  python -m experiment.run_experiment --prompt contract_v2.txt --split held-out

Every call is a fresh `claude -p` conversation. Invalid answers count as failures (never repaired).
Writes experiment/results/<prompt>-<split>.json with every raw answer.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from agent import judge  # noqa: E402


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--split", required=True, choices=["dev", "held-out"])
    a = ap.parse_args(argv)
    E = os.path.join(ROOT, "experiment")
    resume = json.load(open(os.path.join(ROOT, "persona", "resume.json"), encoding="utf-8"))
    split = [p for p in json.load(open(os.path.join(E, "split.json"), encoding="utf-8"))["postings"] if p["split"] == a.split]
    labels = {l["n"]: l["label"] for l in json.load(open(os.path.join(E, "labels.json"), encoding="utf-8"))["labels"]}
    rows = []
    for p in split:
        posting = json.load(open(os.path.join(E, "postings", f"{p['board']}-{p['id']}.json"), encoding="utf-8"))
        out = judge.judge(posting, resume, a.prompt)
        ok = out["status"] == "valid" and out["verdict"] == labels[p["n"]]
        rows.append({"n": p["n"], "title": p["title"], "hand_label": labels[p["n"]], "claude_verdict": out.get("verdict"),
                     "status": out["status"], "match": ok, "justification": out.get("justification"),
                     "error": out.get("error"), "raw": out["raw"]})
        print(f"  {p['n']:>2} hand={labels[p['n']]:<12} claude={str(out.get('verdict')):<12} {out['status']:<7} {'✓' if ok else '✗'}  {p['title'][:50]}")
    passed = sum(r["match"] for r in rows)
    res = {"prompt": a.prompt, "split": a.split, "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "model_via": "Claude Code CLI `claude -p`, one fresh conversation per posting", "passed": passed, "total": len(rows),
           "invalid": sum(r["status"] != "valid" for r in rows), "rows": rows}
    os.makedirs(os.path.join(E, "results"), exist_ok=True)
    with open(os.path.join(E, "results", f"{a.prompt.replace('.txt', '')}-{a.split}.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    print(f"✓ {a.prompt} on {a.split}: {passed}/{len(rows)} match my hand labels · invalid {res['invalid']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
