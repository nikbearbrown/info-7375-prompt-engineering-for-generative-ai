"""Run a filter version over data/postings.jsonl and write runs/filter-<version>.jsonl plus a summary.
Usage: python -m agent.run_filter filter/filter-v1.json"""
import collections
import json
import os
import sys

from agent import filter as filt


def main(cfg_path, data="data/postings.jsonl", outdir="runs"):
    cfg = filt.load(cfg_path)
    os.makedirs(outdir, exist_ok=True)
    rows = [json.loads(l) for l in open(data, encoding="utf-8")]
    out = os.path.join(outdir, f"filter-{cfg['version']}.jsonl")
    dec, scores = collections.Counter(), collections.Counter()
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        for p in rows:
            r = filt.score(p, cfg)
            r.update({"title": p["title"], "location": p["location"], "board": p["board"]})
            dec[r["decision"]] += 1
            scores[r["score"]] += 1
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"filter {cfg['version']} on {len(rows)} postings -> {out}")
    print("decisions:", dict(dec))
    print("scores:", dict(sorted(scores.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
