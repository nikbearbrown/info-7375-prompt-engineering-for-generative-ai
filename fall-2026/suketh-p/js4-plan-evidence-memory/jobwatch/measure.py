"""Comparing the filter's decisions with the student's hand labels.

A decision "reaches" Alex when the fate is kept or review (FILTER.md: review "keeps it visible"),
and is "rejected" otherwise. A label is "yes", "no" or "cannot tell". Agreement counts yes+reaches
and no+rejected. A false inclusion is no+reaches; a false exclusion is yes+rejected. "Cannot tell"
labels are counted apart and are never scored as agreement or disagreement.

clopper_pearson gives the exact two-sided binomial interval, for statements such as "k of the 30
randomly drawn rejects were relevant": it bounds the share of relevant postings in the pool the
30 were drawn from, under random sampling, and says nothing about other pools or other days."""

import math


def decision(record):
    return "reaches" if record["fate"] in ("kept", "review") else "rejected"


def compare(labels, records):
    """labels: {(board, key): "yes"|"no"|"cannot tell"}; records: {(board, key): filter record}."""
    rows = []
    for key, label in sorted(labels.items()):
        d = decision(records[key])
        if label == "cannot tell":
            outcome = "cannot tell"
        elif (label == "yes") == (d == "reaches"):
            outcome = "agree"
        else:
            outcome = "false inclusion" if d == "reaches" else "false exclusion"
        rows.append({"board": key[0], "key": key[1], "label": label, "decision": d, "outcome": outcome,
                     "fate": records[key]["fate"], "score": records[key]["score"]})
    return rows


def summary(rows):
    counts = {k: sum(r["outcome"] == k for r in rows) for k in ("agree", "false inclusion", "false exclusion", "cannot tell")}
    counts["labelled"] = len(rows)
    counts["decided"] = len(rows) - counts["cannot tell"]
    return counts


def _binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(k, n, alpha=0.05):
    """Exact two-sided (1 - alpha) interval for a binomial proportion, by bisection on the CDF."""
    if not 0 <= k <= n or n == 0:
        raise ValueError("need 0 <= k <= n and n > 0")

    def bisect(too_small):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if too_small(mid):
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    # upper: the p where P(X <= k) falls to alpha/2; lower: the p where P(X >= k) rises to alpha/2
    upper = 1.0 if k == n else bisect(lambda p: _binom_cdf(k, n, p) > alpha / 2)
    lower = 0.0 if k == 0 else bisect(lambda p: 1 - _binom_cdf(k - 1, n, p) < alpha / 2)
    return lower, upper
