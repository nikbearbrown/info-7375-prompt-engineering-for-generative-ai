"""Run the filter over the frozen corpus.

    python3 -m js3.run_filter --config config/filter-v1.0.json \
        --out out/filter/v1.0

Writes <out>/decisions.jsonl (one line per posting) and <out>/summary.json.
Offline: reads only CORPUS.sha256, the frozen files it lists,
config/boards.json and the filter config.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from js3 import corpus, filter as js3_filter

DECISIONS = ("kept", "rejected", "abstain")


def histogram(scores):
    counts = Counter(scores)
    return {str(s): counts[s] for s in sorted(counts)}


def build_summary(results, corpus_data, config, config_path):
    boards = {}
    for board, info in corpus_data["boards"].items():
        entry = {"status": info["status"], "file": info["file"],
                 "sha256": info["sha256"]}
        if info["status"] == corpus.NOT_EVALUATED:
            entry["reason"] = info["reason"]
        else:
            rows = [r for r in results if r["board"] == board]
            counts = Counter(r["decision"] for r in rows)
            entry["postings"] = len(rows)
            entry.update({d: counts[d] for d in DECISIONS})
            entry["score_histogram"] = histogram(r["score"] for r in rows)
        boards[board] = entry
    totals = Counter(r["decision"] for r in results)
    close = set(config.get("close_call_scores", []))
    return {
        "config_version": config["version"],
        "config_path": str(config_path),
        "config_sha256": corpus.sha256_of(config_path),
        "corpus_hashes": {info["file"]: info["sha256"]
                          for info in corpus_data["boards"].values()
                          if info["file"]},
        "boards": boards,
        "totals": dict({d: totals[d] for d in DECISIONS},
                       postings=len(results)),
        "score_histogram": histogram(r["score"] for r in results),
        "close_calls": sum(1 for r in results if r["score"] in close),
        "note": "Filter decisions only. No posting has been labeled; these "
                "counts say nothing yet about relevance.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--root", default=str(corpus.ROOT),
                        help="folder holding CORPUS.sha256 (default: this "
                             "project)")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    config = js3_filter.load_config(config_path)
    corpus_data = corpus.load(args.root)
    flt = js3_filter.Filter(config)
    results = [flt.evaluate(p) for p in corpus_data["postings"]]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "decisions.jsonl", "w", encoding="utf-8") as handle:
        for row in results:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = build_summary(results, corpus_data, config, config_path)
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", "utf-8")

    for board, entry in summary["boards"].items():
        if entry["status"] == corpus.NOT_EVALUATED:
            print(f"{board}: not evaluated ({entry['reason']})")
        else:
            print(f"{board}: {entry['postings']} postings, "
                  f"kept {entry['kept']}, rejected {entry['rejected']}, "
                  f"abstain {entry['abstain']}")
    print(f"wrote {out / 'decisions.jsonl'} and {out / 'summary.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
