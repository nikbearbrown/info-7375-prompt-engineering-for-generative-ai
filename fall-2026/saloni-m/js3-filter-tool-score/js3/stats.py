"""Exact (Clopper-Pearson) binomial interval, standard library only."""
import math


def _binom_cdf(k, n, p):
    if p <= 0:
        return 1.0
    if p >= 1:
        return 0.0 if k < n else 1.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def _bisect(f, lo=0.0, hi=1.0, iters=100):
    for _ in range(iters):
        mid = (lo + hi) / 2
        if f(mid):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def clopper_pearson(k, n, conf=0.95):
    """Two-sided exact interval for k successes in n trials."""
    if n == 0:
        return (0.0, 1.0)
    a = (1 - conf) / 2
    lower = 0.0 if k == 0 else _bisect(lambda p: _binom_cdf(k - 1, n, p) > 1 - a)
    upper = 1.0 if k == n else _bisect(lambda p: _binom_cdf(k, n, p) > a)
    return (lower, upper)
