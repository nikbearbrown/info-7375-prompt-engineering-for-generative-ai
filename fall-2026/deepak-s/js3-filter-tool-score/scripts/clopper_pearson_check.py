"""Independent recomputation of the exact (Clopper-Pearson) 95% interval, stdlib only.

    python scripts/clopper_pearson_check.py K N

Different numerics from jobwatch/stats.py on purpose: here the bounds are beta quantiles,
    lower = BetaInv(alpha/2; K, N-K+1)        (0 when K = 0)
    upper = BetaInv(1-alpha/2; K+1, N-K)      (1 when K = N)
with the regularized incomplete beta function evaluated by Lentz's continued fraction (math.lgamma
for the prefactor) and inverted by bisection. It does not import jobwatch.
"""
import math
import sys


def _betacf(a, b, x, iters=500, eps=1e-15):
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, iters + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def betainv(q, a, b):
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if betainc(a, b, mid) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def interval(k, n, alpha=0.05):
    lower = 0.0 if k == 0 else betainv(alpha / 2, k, n - k + 1)
    upper = 1.0 if k == n else betainv(1 - alpha / 2, k + 1, n - k)
    return lower, upper


if __name__ == "__main__":
    k, n = int(sys.argv[1]), int(sys.argv[2])
    lo, hi = interval(k, n)
    print(f"k={k} n={n} lower={lo:.6f} upper={hi:.6f}")
