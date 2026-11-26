"""The reject audit (brief Step 2.1): compare Siddi's blind labels with filter v1 on the audit items, and say what a
sample this size can and cannot show (exact Clopper-Pearson intervals, standard library only).

Usage: python tools/audit_report.py   -> prints tables and writes output/audit/audit.json"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from js3 import policy  # noqa: E402

RUN = "2026-11-26T02-59-56Z"


def binom_cdf(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    def solve(f, lo=0.0, hi=1.0):
        for _ in range(100):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) else (lo, mid)
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(lambda p: 1 - binom_cdf(k - 1, n, p) < alpha / 2)
    upper = 1.0 if k == n else solve(lambda p: binom_cdf(k, n, p) > alpha / 2)
    return lower, upper


def main() -> int:
    labels = {x["key"]: x for x in map(json.loads, policy.check_read("labels/hand_labels.jsonl")
                                         .read_text(encoding="utf-8").splitlines()) if x}
    manifest = json.loads(policy.check_read("labels/sheet-manifest.json").read_text(encoding="utf-8"))
    results = {f"{r['board']}:{r['id']}": r for r in map(json.loads, policy.check_read(
        f"output/filter/filter-v1/{RUN}/results.jsonl").read_text(encoding="utf-8").splitlines()) if r}
    total_rejects = sum(r["verdict"] == "reject" for r in results.values())
    groups: dict[str, list] = {}
    for it in manifest["items"]:
        for role in it["roles"]:
            groups.setdefault(role, []).append(it["key"])
    out = {"total_rejects": total_rejects, "groups": {}}
    for role in ("random_reject", "close_call", "kept", "held_out_A", "held_out_B"):
        rows = []
        for k in groups.get(role, []):
            r, lab = results[k], labels[k]
            wrong = (r["verdict"] == "keep") != (lab["label"] == "relevant")
            rows.append({"key": k, "title": r["title"], "location": r["location"], "filter": r["verdict"],
                         "reasons": r["reasons"], "score": r["score"], "hand": lab["label"], "reason": lab["reason"],
                         "filter_wrong": wrong})
        n, k_wrong = len(rows), sum(x["filter_wrong"] for x in rows)
        lo, hi = clopper_pearson(k_wrong, n) if n else (None, None)
        out["groups"][role] = {"n": n, "filter_wrong": k_wrong, "ci95": [lo, hi], "rows": rows}
        print(f"\n## {role}: filter wrong on {k_wrong} of {n}" + (f"  (95% CI {lo:.1%}-{hi:.1%})" if n else ""))
        for x in rows:
            flag = "WRONG" if x["filter_wrong"] else "ok   "
            print(f"  {flag} filter={x['filter']:6} hand={x['hand']:12} score={x['score']} {x['title'][:50]} | "
                  f"{x['location'][:25]} | {','.join(x['reasons'])} | {x['reason'][:60]}")
    rr = out["groups"]["random_reject"]
    if rr["n"]:
        hi = rr["ci95"][1]
        print(f"\nRandom rejects: {rr['filter_wrong']}/{rr['n']} wrong. Of {total_rejects} rejects, the 95% upper bound "
              f"allows up to {hi:.1%}, i.e. about {math.floor(hi * total_rejects)} postings, to be wrongly rejected.")
    policy.write_bytes("output/audit/audit.json", (json.dumps(out, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
