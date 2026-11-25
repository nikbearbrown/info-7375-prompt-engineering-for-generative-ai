"""Run a filter file over the whole JS2 corpus. Offline. Writes out/<version>/decisions.jsonl and summary.json.

    python3 tools/run_filter.py                       # filters/filter-v1.json
    python3 tools/run_filter.py --filter filters/filter-v1.1.json
"""

import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from js3 import corpus, evidence, filter as F  # noqa: E402

HERE = Path(__file__).resolve().parent.parent


def run(filter_path, out_root):
    flt = F.load_filter(filter_path)
    postings = corpus.load()
    recs = [F.apply(p, flt, evidence.claims) for p in postings]
    out = Path(out_root) / flt["version"]
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "decisions.jsonl", "w") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    dec = collections.Counter(r["decision"] for r in recs)
    gate = collections.Counter(g.split()[0] for r in recs for g in r["gates_failed"])
    abst = collections.Counter(r["abstain"].split()[0] for r in recs if r["abstain"])
    by_board = collections.defaultdict(collections.Counter)
    for r in recs:
        by_board[r["board"]][r["decision"]] += 1
    summary = {"filter": flt["version"], "filter_file": str(Path(filter_path or HERE / "filters/filter-v1.json").name),
               "corpus": f"JS2 {corpus.TAG}", "total": len(recs), "decisions": dict(dec),
               "gate_failures (a posting can fail several)": dict(sorted(gate.items())), "abstain": dict(abst),
               "by_board": {b: dict(c) for b, c in by_board.items()}, "boards_with_no_data": corpus.MISSING}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--filter", default=None)
    ap.add_argument("--out", default=str(HERE / "out"))
    a = ap.parse_args()
    print(json.dumps(run(a.filter, a.out), indent=2))
