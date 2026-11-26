"""Reject audit and single-change comparisons on Aditya's DEV labels (FILTER.md §5, amendment A3).

  .venv/bin/python -m js3.audit        -> audit/audit_results.json (and a printed summary)

Error = the filter's verdict disagrees with a decided label (yes/no). `unsure` labels are counted separately,
never as right or wrong. The dev groups are stratified, so nothing here is a population rate except the
uniform 30-reject group, and that one only as an interval.
"""
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from .corpus import load_corpus
from .filter import load_filter, score_posting

ROOT = Path(__file__).resolve().parent.parent
CANDIDATES = [  # (label, filter file, threshold override or None, what changed)
    ("v1.0 baseline", "v1.0", None, "-"),
    ("C-a", "cand-a_boilerplate", None, "filter file: topic ignores board boilerplate segments"),
    ("C-b", "cand-b_years", None, "filter file: years bands -> only N>=5 gives -1"),
    ("C-e", "cand-e_earlycareer3", None, "filter file: early-career +1 -> +3"),
    ("C-t", "v1.0", 5, "setting: threshold 6 -> 5"),
    ("C-r", "cand-r_roles", None, "filter file: add 'forward deployed engineer', 'solutions engineer' to R-adjacent"),
    ("C-a+C-b+C-e", "cand-abe_combined", None, "three filter-file changes together (not one-at-a-time)"),
]


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(k, n, alpha=0.05):
    """Exact two-sided 95% interval for k successes in n, by bisection (standard library only)."""
    def solve(f):
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) else (lo, mid)
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(lambda p: 1 - binom_cdf(k - 1, n, p) < alpha / 2)
    upper = 1.0 if k == n else solve(lambda p: binom_cdf(k, n, p) > alpha / 2)
    return round(lower, 4), round(upper, 4)


def confusion(rows, verdicts):
    m = Counter()
    for r in rows:
        v = verdicts[r["key"]]
        if r["label"] == "unsure":
            m[f"unsure_{v}"] += 1
        else:
            y, k = r["label"] == "yes", v == "keep"
            m["TP" if y and k else "FN" if y else "FP" if k else "TN"] += 1
    return dict(m)


def run(labels_path=ROOT / "labels" / "dev_labels.csv", audited="v1.0", random_group="D-random-reject",
        out_name="audit_results.json", candidates=True):
    corpus = load_corpus()
    with labels_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    base_cfg = load_filter(audited)
    base = {r["key"]: score_posting(corpus[r["key"]], base_cfg) for r in rows}
    by_group = defaultdict(list)
    for r in rows:
        for g in r["group"].split("+"):
            by_group[g].append(r)
    groups = {}
    for g, rs in sorted(by_group.items()):
        groups[g] = {"n": len(rs), "labels": dict(Counter(r["label"] for r in rs)),
                     audited: confusion(rs, {r["key"]: base[r["key"]]["verdict"] for r in rs}),
                     "errors": [{"sheet_id": r["sheet_id"], "label": r["label"], audited: base[r["key"]]["verdict"],
                                 "arithmetic": base[r["key"]].get("arithmetic"),
                                 "score": base[r["key"]]["score"], "title": corpus[r["key"]]["title"], "reason": r["reason"]}
                                for r in rs if (r["label"] == "yes") != (base[r["key"]]["verdict"] == "keep") and r["label"] != "unsure"]}
    rr = by_group.get(random_group, [])
    decided = [r for r in rr if r["label"] != "unsure"]
    yes = sum(r["label"] == "yes" for r in rr)
    uns = sum(r["label"] == "unsure" for r in rr)
    rejects_total = sum(1 for p in corpus.values() if score_posting(p, base_cfg)["verdict"] == "reject")
    random_estimate = {
        "sample": len(rr), "yes": yes, "unsure": uns, "no": len(rr) - yes - uns,
        "miss_rate_decided": f"{yes}/{len(decided)}", "ci95_decided": clopper_pearson(yes, len(decided)),
        "worst_case_unsure_as_miss": f"{yes + uns}/{len(rr)}", "ci95_worst_case": clopper_pearson(yes + uns, len(rr)),
        f"{audited}_rejects_in_corpus": rejects_total}
    comps = []
    for label, fv, thr, what in (CANDIDATES if candidates else []):
        cfg = load_filter(fv)
        if thr is not None:
            cfg["threshold"] = thr
        res = {r["key"]: score_posting(corpus[r["key"]], cfg) for r in rows}
        flips = [{"sheet_id": r["sheet_id"], "label": r["label"], "from": base[r["key"]]["verdict"],
                  "to": res[r["key"]]["verdict"], "title": corpus[r["key"]]["title"],
                  "v1.0": base[r["key"]].get("arithmetic"), "candidate": res[r["key"]].get("arithmetic")}
                 for r in rows if res[r["key"]]["verdict"] != base[r["key"]]["verdict"]]
        corpus_keeps = sum(score_posting(p, cfg)["verdict"] == "keep" for p in corpus.values())
        comps.append({"label": label, "filter": fv, "threshold": cfg["threshold"], "change": what,
                      "confusion": confusion(rows, {k: v["verdict"] for k, v in res.items()}),
                      "corpus_keeps": corpus_keeps, "flips": flips})
    out = {"labels": str(Path(labels_path).resolve().relative_to(ROOT)), "audited_filter": audited, "n": len(rows),
           "label_counts": dict(Counter(r["label"] for r in rows)), "groups": groups,
           "random_reject_estimate": random_estimate, "comparisons": comps}
    (ROOT / "audit").mkdir(exist_ok=True)
    (ROOT / "audit" / out_name).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    return out


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["a4"]:  # fresh audit of frozen v1.1 (amendment A4); no candidate rules
        o = run(ROOT / "labels" / "audit_a4_labels.csv", "v1.1", "A4-random-reject", "audit_a4_results.json", False)
        print(json.dumps(o["random_reject_estimate"], indent=1))
        for g, v in o["groups"].items():
            print(g, v["n"], v["labels"], v["v1.1"], [e["sheet_id"] for e in v["errors"]])
        sys.exit(0)
    o = run()
    print(json.dumps(o["random_reject_estimate"], indent=1))
    for c in o["comparisons"]:
        m = c["confusion"]
        print(f"{c['label']:<14} TP {m.get('TP',0)} FP {m.get('FP',0)} FN {m.get('FN',0)} TN {m.get('TN',0)} "
              f"unsure kept {m.get('unsure_keep',0)} | corpus keeps {c['corpus_keeps']} | flips {len(c['flips'])}")
