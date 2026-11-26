"""The reject audit, computed from Saloni's hand labels. Run after labels/audit_sheet.csv is labelled.

    python3 scripts/audit_report.py [--filter-results out/filter/v1.0/results.jsonl] [--sheet audit]

Prints, per stratum: how many the filter got wrong by Saloni's label, the exact 95% interval for
the random strata, and what that interval does and does not let us say about all rejects.
Also: for every word the filter matched in the audited postings, the hand-label split, so a
false friend (a word that matched for the wrong reason) can be found and named.
"""
import argparse
import collections
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from js3.stats import clopper_pearson  # noqa: E402


def load(sheet):
    with open(os.path.join(HERE, "labels", f"{sheet}_sheet.csv"), newline="", encoding="utf-8") as f:
        labs = {r["uid"]: r for r in csv.DictReader(f)}
    with open(os.path.join(HERE, "labels", f"{sheet}_key.csv"), newline="", encoding="utf-8") as f:
        keys = {r["uid"]: r for r in csv.DictReader(f)}
    return labs, keys


def wrong(decision, hand):
    if hand == "cannot_tell":
        return None
    return (decision == "keep") != (hand == "worth_time")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", default="audit")
    ap.add_argument("--filter-results", default=os.path.join(HERE, "out", "filter", "v1.0", "results.jsonl"))
    a = ap.parse_args(argv)
    labs, keys = load(a.sheet)
    with open(a.filter_results, encoding="utf-8") as f:
        res = {r["uid"]: r for r in map(json.loads, f)}
    unlabelled = [u for u, r in labs.items() if not r["hand_label"]]
    if unlabelled:
        sys.exit(f"{len(unlabelled)} of {len(labs)} rows are unlabelled; run scripts/label.py labels/{a.sheet}_sheet.csv")

    pop_rej = sum(r["decision"] == "reject" for r in res.values())
    pop_keep = len(res) - pop_rej
    out = {"filter_results": os.path.relpath(a.filter_results, HERE), "strata": {}, "errors": []}
    by = collections.defaultdict(list)
    for uid, k in keys.items():
        by[k["stratum"]].append(uid)
    for stratum, uids in sorted(by.items()):
        n = len(uids)
        verdicts = [(u, res[u]["decision"], labs[u]["hand_label"]) for u in uids]
        ct = sum(h == "cannot_tell" for _, _, h in verdicts)
        errs = [(u, d, h) for u, d, h in verdicts if wrong(d, h)]
        judged = n - ct
        s = {"n": n, "cannot_tell": ct, "judged": judged, "filter_wrong": len(errs)}
        if stratum.startswith("random") or stratum.startswith("heldout"):
            lo, hi = clopper_pearson(len(errs), judged)
            s["error_rate_95ci"] = [round(lo, 3), round(hi, 3)]
            pop = pop_rej if "reject" in stratum else pop_keep
            s["if_this_sample_is_typical"] = (f"between {lo * pop:.0f} and {hi * pop:.0f} of the {pop} "
                                              f"{'rejects' if 'reject' in stratum else 'keeps'} could be wrong "
                                              f"(95% exact interval, k={len(errs)}, n={judged}); a sample estimate, not a measured count")
        else:
            s["note"] = "chosen by margin, not at random: no rate is claimed for this stratum"
        out["strata"][stratum] = s
        for u, d, h in errs:
            out["errors"].append({"stratum": stratum, "uid": u, "title": res[u]["title"], "filter": d, "hand": h,
                                  "score": res[u]["score"], "note": labs[u]["note"],
                                  "fired": [(f["rule"], f["matched"]) for f in res[u]["fired"]]})

    word_split = collections.defaultdict(collections.Counter)
    for u in keys:
        for f in res[u]["fired"]:
            if f["rule"] in ("R1", "R3"):
                for w in f["matched"]:
                    word_split[f"{f['rule']}:{w}"][labs[u]["hand_label"]] += 1
    out["matched_word_vs_hand_label"] = {w: dict(c) for w, c in sorted(word_split.items(), key=lambda x: -sum(x[1].values()))}
    print(json.dumps(out, indent=2, ensure_ascii=False))
    dest = os.path.join(HERE, "out", f"{a.sheet}_report.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nwritten: {os.path.relpath(dest, HERE)}")


if __name__ == "__main__":
    main()
