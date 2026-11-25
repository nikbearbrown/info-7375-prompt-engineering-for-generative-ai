"""Score every corpus posting with one filter version.

  .venv/bin/python -m js3.run --filter v1.0 [--threshold N]
  -> runs/<label>/scores.csv  (key, board, title, score, verdict, arithmetic)  and  runs/<label>/summary.json

--threshold overrides the filter file's threshold (a *setting* change; recorded in the label and summary).
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from .corpus import load_corpus
from .filter import load_filter, score_posting

ROOT = Path(__file__).resolve().parent.parent


def score_all(cfg, corpus=None):
    corpus = corpus or load_corpus()
    return {k: score_posting(p, cfg) for k, p in sorted(corpus.items())}, corpus


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--filter", default="v1.0")
    ap.add_argument("--threshold", type=int)
    ap.add_argument("--label")
    a = ap.parse_args(argv)
    cfg = load_filter(a.filter)
    if a.threshold is not None:
        cfg["threshold"] = a.threshold
    label = a.label or (a.filter + (f"_threshold{a.threshold}" if a.threshold is not None else ""))
    results, corpus = score_all(cfg)
    out = ROOT / "runs" / label
    out.mkdir(parents=True, exist_ok=True)
    with (out / "scores.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["key", "board", "title", "score", "verdict", "arithmetic"])
        for k, r in results.items():
            w.writerow([k, corpus[k]["board"], corpus[k]["title"], r["score"], r["verdict"], r.get("arithmetic", r.get("reason"))])
    verdicts = Counter(r["verdict"] for r in results.values())
    by_board = {b: dict(Counter(r["verdict"] for k, r in results.items() if corpus[k]["board"] == b))
                for b in sorted({p["board"] for p in corpus.values()})}
    hist = Counter(r["score"] for r in results.values() if r["score"] is not None)
    summary = {"filter": cfg["version"], "threshold": cfg["threshold"], "label": label,
               "postings": len(results), "verdicts": dict(verdicts), "verdicts_by_board": by_board,
               "score_histogram": {str(s): hist[s] for s in sorted(hist)},
               "cannot_tell": [k for k, r in results.items() if r["verdict"] == "cannot_tell"]}
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
