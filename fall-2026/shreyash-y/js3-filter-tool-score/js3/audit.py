"""The reject audit (FILTER.md answer 1; Lectern's two-part audit, adapted) and the held-out set.

draw():   from the filter v1 results, draw with a fixed seed, BEFORE any hand label exists:
  H  held-out set, for the one-change-at-a-time experiments only (SCORE.md): 3 of the 5 kept,
     3 of the 6 Klaviyo closest calls that fail only experience, 8 of the 35 Palantir closest calls
     that fail only location, and 10 rejects that are not closest calls.
  A  audit set: a uniform random sample of 30 rejects (the only part that supports a rate), the
     closest calls not held out (all 6 others outside Palantir, and 9 of the remaining 27 Palantir
     location-only ones), and the 2 kept postings not held out.
  The 18 Palantir location-only closest calls left over are counted, not labeled: they differ only
  in title and city. Both sets go into ONE blind sheet in a shuffled order: the labeler never sees
  which set an item is in or what the filter decided.
report(): reads Shreyash's verdicts and compares them with the filter, part by part.
"""
import hashlib
import json
import math
import pathlib
import random

HERE = pathlib.Path(__file__).resolve().parent.parent
SEED = 7375


def load_records(path=HERE / "results" / "filter-v1" / "records.jsonl"):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def strata(records):
    kept = sorted(r["key"] for r in records if r["verdict"] == "Relevant")
    unsure = sorted(r["key"] for r in records if r["verdict"] == "I cannot tell")
    rejects = sorted(r["key"] for r in records if r["verdict"] == "Not Relevant")
    cc = [r for r in records if r["closest_call"]]
    cc_pal = sorted(r["key"] for r in cc if r["board"] == "palantir" and r["failed"] == [3])
    cc_r5_kl = sorted(r["key"] for r in cc if r["board"] == "klaviyo" and r["failed"] == [5])
    cc_other = sorted(r["key"] for r in cc if r["key"] not in set(cc_pal) | set(cc_r5_kl))
    return {"kept": kept, "unsure": unsure, "rejects": rejects, "cc_palantir_location": cc_pal,
            "cc_klaviyo_experience": cc_r5_kl, "cc_other": cc_other,
            "closest_calls": sorted(r["key"] for r in cc)}


def draw(records, seed=SEED):
    s = strata(records)
    rng = random.Random(seed)
    non_cc_rejects = sorted(set(s["rejects"]) - set(s["closest_calls"]))
    h = {"kept": sorted(rng.sample(s["kept"], 3)),
         "cc_klaviyo_experience": sorted(rng.sample(s["cc_klaviyo_experience"], 3)),
         "cc_palantir_location": sorted(rng.sample(s["cc_palantir_location"], 8)),
         "rejects_not_closest": sorted(rng.sample(non_cc_rejects, 10))}
    held = set().union(*h.values())
    pal_left = sorted(set(s["cc_palantir_location"]) - held)
    a = {"random_rejects": sorted(rng.sample(sorted(set(s["rejects"]) - held), 30)),
         "closest_calls": sorted(set(s["cc_other"]) | (set(s["cc_klaviyo_experience"]) - held)
                                 | set(rng.sample(pal_left, 9))),
         "kept": sorted(set(s["kept"]) - held),
         "unsure": s["unsure"]}
    in_a = set().union(*a.values())
    assert not (in_a & held), "audit and held-out sets must not overlap"
    order = sorted(in_a | held)
    rng.shuffle(order)
    not_labeled = sorted(set(s["cc_palantir_location"]) - in_a - held)
    return {"seed": seed, "filter_version": records[0]["filter_version"], "strata_sizes": {k: len(v) for k, v in s.items()},
            "held_out": h, "audit": a, "closest_calls_not_labeled": not_labeled,
            "label_order": order, "items": len(order)}


def wilson(k, n, z=1.96):
    """95% Wilson score interval for k successes in n draws."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def clopper_pearson_upper(k, n, alpha=0.05):
    """One-sided upper bound: the largest miss rate under which seeing k or fewer in n has
    probability >= alpha (bisection on the binomial tail; stdlib only)."""
    def tail(p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
    lo, hi = k / n if n else 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if tail(mid) > alpha:
            lo = mid
        else:
            hi = mid
    return hi


def file_sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
