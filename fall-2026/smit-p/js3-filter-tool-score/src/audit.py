"""The reject audit: draw the samples, then score the filter against the hand verdicts.

    python3 src/audit.py sample --run-id live-20261114     # writes audit/sample.json (before judging)
    python3 src/audit.py score  --run-id live-20261114     # needs audit/hand-verdicts.json

Strata (a posting can be in more than one):
  random_reject  30 rejects drawn uniformly at random (seed 7375) from ALL rejects
  kept           every kept posting
  close_call     every posting that passed the title rules (R1, R2) but was then rejected
  near_miss      every R1 reject whose title says Engineer/Developer and has no seniority word
Each posting is also assigned to dev or held_out (seed 7375) before any hand verdict exists.
"""
import argparse
import collections
import json
import math
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filter as flt  # noqa: E402
from postings import ROOT, load_run  # noqa: E402

SEED = 7375
N_RANDOM = 30
AUDIT = os.path.join(ROOT, "audit")


def fact_card(p):
    """What a person needs to judge relevance by hand, taken from the posting, not from the filter."""
    status, quote, sentence = flt.years_requirement(p["text"])
    return {"board": p["board"], "id": p["id"], "title": p["title"], "location": p["location"],
            "country": p["country"], "url": p["url"],
            "experience_sentence": sentence or "(no years-of-experience sentence found)",
            "has_description": bool((p["text"] or "").strip())}


def sample(run_id, version):
    postings, _, _ = load_run(run_id)
    by_id = {(p["board"], p["id"]): p for p in postings}
    with open(os.path.join(ROOT, "runs", run_id, f"verdicts-v{version}.json"), encoding="utf-8") as f:
        verdicts = json.load(f)["verdicts"]
    rng = random.Random(SEED)
    rejects = [v for v in verdicts if v["verdict"] == "reject"]
    strata = collections.defaultdict(list)
    for v in rng.sample(rejects, N_RANDOM):
        strata[(v["board"], v["posting_id"])].append("random_reject")
    for v in verdicts:
        key = (v["board"], v["posting_id"])
        if v["verdict"] == "keep":
            strata[key].append("kept")
        elif v["rule"] in ("R3", "R4", "R5", "R6") or v["verdict"] == "cannot_tell":
            strata[key].append("close_call")
        elif (v["rule"] == "R1" and re.search(r"engineer|developer", v["title"], re.I)
              and not any(flt.find_whole(w, v["title"]) for w in flt.SENIORITY_WORDS)):
            strata[key].append("near_miss")
    keys = sorted(strata)
    split_rng = random.Random(SEED + 1)
    items = []
    for key in keys:
        v = next(x for x in verdicts if (x["board"], x["posting_id"]) == key)
        items.append({**fact_card(by_id[key]), "strata": strata[key],
                      "split": "dev" if split_rng.random() < 0.5 else "held_out",
                      "filter_v1_0": {"verdict": v["verdict"], "rule": v["rule"], "skills": v["skills"]}})
    os.makedirs(AUDIT, exist_ok=True)
    out = {"run_id": run_id, "filter_version": version, "seed": SEED, "n_rejects_total": len(rejects),
           "n_postings_total": len(verdicts), "items": items}
    with open(os.path.join(AUDIT, "sample.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    return out


def clopper_pearson(k, n, alpha=0.05):
    """Exact two-sided 95% interval for a binomial proportion, by bisection (no scipy)."""
    def cdf(x, p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x + 1))

    def root(g, target, increasing):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if (g(mid) < target) == increasing:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    # lower: P(X >= k | p) = alpha/2 (rises with p); upper: P(X <= k | p) = alpha/2 (falls with p)
    lower = 0.0 if k == 0 else root(lambda p: 1 - cdf(k - 1, p), alpha / 2, increasing=True)
    upper = 1.0 if k == n else root(lambda p: cdf(k, p), alpha / 2, increasing=False)
    return lower, upper


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sample"])
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--version", default=flt.FILTER_VERSION)
    a = ap.parse_args()
    out = sample(a.run_id, a.version)
    c = collections.Counter(s for i in out["items"] for s in i["strata"])
    print(f"{len(out['items'])} postings to judge by hand; strata {dict(c)}; "
          f"split {dict(collections.Counter(i['split'] for i in out['items']))}")


if __name__ == "__main__":
    main()
