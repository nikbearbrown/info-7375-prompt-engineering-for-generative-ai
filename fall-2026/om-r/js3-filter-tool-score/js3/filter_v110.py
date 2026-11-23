"""Filter v1.1.0-CANDIDATE = FILTER.md v1.0.0 rules 1-3 (js3/filter.py,
unchanged) + candidate rule 4 (js3/rule4.py). A versioned addition under
measurement (EXPERIMENT.md), not an edit to v1.0.0 and not in FILTER.md
unless promoted.

Rule 3 still runs first: no content, no verdict, and rule 4 is not
evaluated. Otherwise a rule-4 fire adds a "rule 4: ..." reason, so a
v1.0.0 "relevant" posting becomes "rejected". Eligibility flags are carried
on the result and never change the bucket.
"""
from js3 import filter as v100
from js3 import rule4

VERSION = "1.1.0-candidate"
BUCKETS = v100.BUCKETS


def classify(posting):
    r = v100.classify(posting)
    r["filter_version"] = VERSION
    r["v1.0.0_bucket"] = r["bucket"]
    if r["bucket"] == "insufficient_data":
        r.update({"rule4_fires": None, "eligibility_flags": []})
        return r
    c = rule4.check(posting)
    r.update({"rule4_fires": c["fires"], "year_minimums": c["year_minimums"],
              "seniority_title_word": c["seniority_title_word"], "management_phrase": c["management_phrase"],
              "eligibility_flags": c["eligibility_flags"]})
    r["reasons"] += c["reasons"]
    r["bucket"] = "rejected" if r["reasons"] else "relevant"
    return r


def run_filter(postings):
    results = [classify(p) for p in postings]
    out = {"filter_version": VERSION, "results": results, **{b: [] for b in BUCKETS}}
    for r in results:
        out[r["bucket"]].append(r)
    return out
