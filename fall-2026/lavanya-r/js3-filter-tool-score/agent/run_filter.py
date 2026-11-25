"""Run the filter on every posting in the frozen corpus.

python3 -B -m agent.run_filter                       # config/filter.json
python3 -B -m agent.run_filter --config <file> --out <dir>

Writes <out>/decisions.jsonl (one record per posting, sorted by key) and
<out>/summary.json. Reads only the corpus; fetches nothing.
"""

import argparse
import collections
import json
import pathlib

from agent import corpus, filter as flt

HERE = pathlib.Path(__file__).resolve().parent.parent
CORPUS = HERE / "runs" / "2026-11-24T220432Z-live"


def run(cfg, out_dir):
    posts = corpus.load(CORPUS)
    recs = [flt.evaluate(p, cfg) for p in posts]
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "decisions.jsonl", "w") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    verdicts = collections.Counter(r["verdict"] for r in recs)
    fired = collections.Counter(x for r in recs for x in r["rejected_by"])
    only = collections.Counter(r["rejected_by"][0] for r in recs
                               if len(r["rejected_by"]) == 1)
    passed_hard = [r for r in recs
                   if r["verdict"] == "keep"
                   or r["rejected_by"] == ["below_threshold"]]
    summary = {
        "filter_version": cfg["version"], "corpus": str(CORPUS.relative_to(HERE)),
        "postings": len(recs), "verdicts": dict(verdicts),
        "rule_fired": dict(fired), "only_rule_that_fired": dict(only),
        "passed_hard_rejects": len(passed_hard),
        "score_of_those": dict(sorted(collections.Counter(
            r["score"] for r in passed_hard).items())),
        "cannot_tell": [{"key": r["key"], "title": r["title"],
                         "because": r["cannot_tell_because"]}
                        for r in recs if r["verdict"] == "cannot_tell"],
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    return recs, summary


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(HERE / "config" / "filter.json"))
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    cfg = json.loads(pathlib.Path(a.config).read_text())
    out = pathlib.Path(a.out) if a.out else HERE / "out" / "filter" / f"v{cfg['version']}"
    _, s = run(cfg, out)
    print(json.dumps({k: s[k] for k in ("filter_version", "postings", "verdicts",
                                        "rule_fired", "passed_hard_rejects",
                                        "score_of_those")}, indent=1))
    print("cannot tell:", s["cannot_tell"])
    print("written:", out.relative_to(HERE))


if __name__ == "__main__":
    main()
