"""Exact binomial bounds (Clopper-Pearson) by bisection on the binomial CDF. Standard library only."""
from __future__ import annotations

from math import comb


def cdf(k: int, n: int, p: float) -> float:
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def _solve(f, lo=0.0, hi=1.0, it=200) -> float:
    for _ in range(it):
        mid = (lo + hi) / 2
        if f(mid):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def upper_one_sided(k: int, n: int, alpha: float = 0.05) -> float:
    """Largest p with P(X <= k | n, p) >= alpha. k = 0 gives 1 - alpha**(1/n) (about 9.5 % for n = 30)."""
    if k >= n:
        return 1.0
    return _solve(lambda p: cdf(k, n, p) >= alpha)


def two_sided(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    lo = 0.0 if k == 0 else _solve(lambda p: 1 - cdf(k - 1, n, p) <= alpha / 2)
    hi = 1.0 if k == n else _solve(lambda p: cdf(k, n, p) >= alpha / 2)
    return lo, hi
