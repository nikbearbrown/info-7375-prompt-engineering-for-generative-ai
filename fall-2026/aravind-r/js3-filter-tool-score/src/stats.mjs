// Exact (Clopper-Pearson) binomial interval, by bisection on the binomial CDF.
// Used for every sample-based error figure: an estimate with an interval, never a rate.
function logChoose(n, k) { let s = 0; for (let i = 1; i <= k; i++) s += Math.log(n - k + i) - Math.log(i); return s; }
export function binomCdf(x, n, p) { // P(X <= x)
  if (x < 0) return 0; if (x >= n) return 1;
  if (p <= 0) return 1; if (p >= 1) return 0;
  let s = 0; for (let k = 0; k <= x; k++) s += Math.exp(logChoose(n, k) + k * Math.log(p) + (n - k) * Math.log1p(-p));
  return Math.min(1, s);
}
function bisect(f, lo = 0, hi = 1) { for (let i = 0; i < 200; i++) { const m = (lo + hi) / 2; if (f(m)) hi = m; else lo = m; } return (lo + hi) / 2; }
export function clopperPearson(x, n, conf = 0.95) {
  if (!Number.isInteger(x) || !Number.isInteger(n) || n <= 0 || x < 0 || x > n) throw new Error(`bad counts x=${x} n=${n}`);
  const a = (1 - conf) / 2;
  const lower = x === 0 ? 0 : bisect(p => 1 - binomCdf(x - 1, n, p) >= a);   // smallest p with P(X>=x) >= a
  const upper = x === n ? 1 : bisect(p => binomCdf(x, n, p) <= a);          // smallest p with P(X<=x) <= a
  return { x, n, conf, estimate: x / n, lower, upper };
}
