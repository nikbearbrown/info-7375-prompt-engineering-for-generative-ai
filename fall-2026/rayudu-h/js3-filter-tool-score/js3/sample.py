"""The draws for the audit (A) and the held-out set (H), and the one fitted number.

Order of draws, all from one seeded random generator: H first (20 kept + 20 rejected), then
from what is left: 30 uniform random rejects, the closest calls on each side of the threshold,
and a random sample of kept postings. No key is in two sets (FILTER.md W5).
"""
from __future__ import annotations

import random

KEPT, REJECTED = "kept", "rejected"


def draw(results: list, seed: int, heldout_kept: int = 20, heldout_rejected: int = 20,
         random_rejects: int = 30, closest_each_side: int = 5, audit_kept: int = 15) -> dict:
    rng = random.Random(seed)
    by_key = {r["key"]: r for r in results}
    kept = sorted(k for k, r in by_key.items() if r["decision"] == KEPT)
    rejected = sorted(k for k, r in by_key.items() if r["decision"] == REJECTED)

    heldout = rng.sample(kept, heldout_kept) + rng.sample(rejected, heldout_rejected)
    used = set(heldout)

    rej_pool = [k for k in rejected if k not in used]
    rand_rej = rng.sample(rej_pool, random_rejects)
    used |= set(rand_rej)

    # closest calls: postings the threshold decided (not an exclusion, not "no skill"), nearest to it
    cand = [k for k in sorted(by_key) if k not in used and by_key[k].get("threshold_decided", True)
            and by_key[k]["decision"] in (KEPT, REJECTED)]
    rng.shuffle(cand)                                       # ties broken at random, reproducibly
    below = sorted((k for k in cand if by_key[k]["margin"] < 0), key=lambda k: -by_key[k]["margin"])
    above = sorted((k for k in cand if by_key[k]["margin"] >= 0), key=lambda k: by_key[k]["margin"])
    closest = below[:closest_each_side] + above[:closest_each_side]
    used |= set(closest)

    kept_pool = [k for k in kept if k not in used]
    kept_sample = rng.sample(kept_pool, min(audit_kept, len(kept_pool)))

    return {"seed": seed, "heldout": heldout, "audit_random_rejects": rand_rej,
            "audit_closest": closest, "audit_kept": kept_sample,
            "population": {"kept": len(kept), "rejected": len(rejected),
                           "rejected_after_heldout": len(rej_pool), "closest_candidates": len(cand)}}


def fit_threshold(labels: dict, results_by_key: dict, heldout: set, current: float = 3.0) -> dict:
    """Fit the threshold on AUDIT labels only. labels: key -> 'relevant' | 'not relevant' | "can't tell".

    Only postings the threshold decided are informative; exclusions and "no skill" stay rejected.
    Ties in accuracy go to the value closest to the current threshold (the smallest change).
    """
    leaked = set(labels) & set(heldout)
    if leaked:
        raise ValueError(f"held-out ids must never be used for fitting: {sorted(leaked)[:3]}")
    rows = [(results_by_key[k]["score"], lab == "relevant") for k, lab in labels.items()
            if lab in ("relevant", "not relevant") and results_by_key[k].get("threshold_decided", True)]
    if not rows:
        raise ValueError("no usable labels")
    candidates = sorted({s for s, _ in rows} | {current})
    table = []
    for t in candidates:
        correct = sum(1 for s, rel in rows if (s >= t) == rel)
        table.append({"threshold": t, "correct": correct, "n": len(rows)})
    best = max(table, key=lambda r: (r["correct"], -abs(r["threshold"] - current)))
    return {"threshold": best["threshold"], "correct": best["correct"], "n": len(rows), "table": table}
