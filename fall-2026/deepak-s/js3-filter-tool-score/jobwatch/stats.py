"""Exact (Clopper-Pearson) binomial interval, standard library only (CLAUDE.md: any rate from a
sample comes with its exact 95% interval and the sample size).

Method: the interval is [pL, pU] with P(X >= k | n, pL) = alpha/2 (pL = 0 when k = 0) and
P(X <= k | n, pU) = alpha/2 (pU = 1 when k = n). Each bound is found by bisection on p over exact
binomial sums computed with math.comb. scripts/clopper_pearson_check.py recomputes the same
interval independently, from beta quantiles via a continued-fraction incomplete beta function.
"""
from math import comb


def binom_cdf(k, n, p):
    """P(X <= k) for X ~ Binomial(n, p)."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def _bisect(f, lo=0.0, hi=1.0, iters=200):
    """Root of a function that is decreasing in p on [lo, hi]."""
    for _ in range(iters):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def clopper_pearson(k, n, alpha=0.05):
    if not 0 <= k <= n or n <= 0:
        raise ValueError("need 0 <= k <= n and n > 0")
    a = alpha / 2
    lower = 0.0 if k == 0 else _bisect(lambda p: a - (1 - binom_cdf(k - 1, n, p)))
    upper = 1.0 if k == n else _bisect(lambda p: binom_cdf(k, n, p) - a)
    return lower, upper
