"""Tables for SAMPLING-REPORT.md and BASELINE-DEV.md, built from the saved results.json files.

    python3 experiment/report_dev.py sampling       # prints the sampling tables
    python3 experiment/report_dev.py baseline-dev   # prints the baseline-dev table
    python3 experiment/report_dev.py revision1-dev  # prints the revision-1 dev tables
    python3 experiment/report_dev.py baseline-heldout | revision1-heldout   # the held-out tables

It reads only saved results: no Claude call.
"""
import json
import math
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(x, n, alpha=0.05):
    """Exact 95% interval for a binomial proportion, by bisection on the binomial tail."""
    def solve(f):
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) else (lo, mid)
        return (lo + hi) / 2
    lower = 0.0 if x == 0 else solve(lambda p: 1 - binom_cdf(x - 1, n, p) < alpha / 2)
    upper = 1.0 if x == n else solve(lambda p: binom_cdf(x, n, p) > alpha / 2)
    return lower, upper


def cell(text):
    return str(text).replace("|", "/").replace("\n", " ")


def support_summary(row):
    if not row["citations"]:
        return "none"
    n = sum(c["support"] == "supported" for c in row["citations"])
    return f"{n}/{len(row['citations'])}"


def unsupported(row):
    return "; ".join(f"`{c.get('posting_field')}` {c.get('quote')!r}" for c in row["citations"]
                     if c["support"] != "supported")


def call_table(rows, with_call):
    head = ["posting_id"] + (["call"] if with_call else []) + [
        "date (UTC)", "session_id", "model", "my label", "Claude verdict", "valid?", "citations supported", "pass"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        meta = r["meta"] or {}
        valid = "valid" if r["valid"] else "invalid: " + cell("; ".join(r["errors"]))
        lines.append("| " + " | ".join([str(r["posting_id"])] + ([str(r["call"])] if with_call else []) + [
            meta.get("date") or "-", f"`{meta.get('session_id')}`", str(meta.get("model")), r["my_label"],
            str(r["verdict"]), valid, support_summary(r), "yes" if r["passed"] else "no"]) + " |")
    return lines


def sampling(result):
    rows = result["rows"]
    lines = ["## Every call", ""] + call_table(rows, True)
    lines += ["", "## Spread per posting", "",
              "| posting_id | my label | verdicts (4 calls) | valid | all citations supported | agrees with my label |",
              "|---|---|---|---|---|---|"]
    for pid in result["posting_ids"]:
        mine = [r for r in rows if r["posting_id"] == pid]
        n = len(mine)
        verdicts = Counter(str(r["verdict"]) for r in mine)
        spread = ", ".join(f"{k} {v}/{n}" for k, v in verdicts.most_common())
        lines.append(f"| {pid} | {mine[0]['my_label']} | {spread} | {sum(r['valid'] for r in mine)}/{n} | "
                     f"{sum(r['supported'] for r in mine)}/{n} | {sum(r['passed'] for r in mine)}/{n} |")
    lines += unsupported_section(rows)
    return lines


def baseline(result):
    rows = result["rows"]
    passed = sum(r["passed"] for r in rows)
    where = "Held-out" if result["mode"].endswith("heldout") else "Dev"
    low, high = clopper_pearson(passed, len(rows))
    lines = ["## Every call", ""] + call_table(rows, False)
    lines += ["", f"**{where} pass rate: {passed}/{len(rows)}** (pass = valid AND verdict equals my label); "
                  f"95% Clopper-Pearson interval {low:.1%} to {high:.1%}.",
              f"Valid: {sum(r['valid'] for r in rows)}/{len(rows)}. "
              f"All citations supported: {sum(r['supported'] for r in rows)}/{len(rows)}."]
    if result.get("schema") == "revision-1":
        lines += failed_check_section(rows)
    lines += unsupported_section(rows)
    return lines


def failed_check_section(rows):
    agree = sum(r["failed_check_agrees"] for r in rows)
    lines = ["", "## failed_check vs the rule judge (declared second measure)", "",
             f"**failed_check agreement with the rule judge: {agree}/{len(rows)}** (counted only when valid).", "",
             "| posting_id | Claude failed_check | rule failed_check | agrees | my failed check (not a declared measure) |",
             "|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['posting_id']} | {r.get('failed_check') or 'null'} | {r['rule_failed_check'] or 'null'} | "
                     f"{'yes' if r['failed_check_agrees'] else 'no'} | {r['my_failed_check'] or '-'} |")
    return lines


def unsupported_section(rows):
    bad = [r for r in rows if r["citations"] and not r["supported"]]
    if not bad:
        return ["", "No unsupported citations."]
    lines = ["", "## Unsupported citations", "", "| posting_id | call | quote not found in the cited field |",
             "|---|---|---|"]
    for r in bad:
        lines.append(f"| {r['posting_id']} | {r['call']} | {cell(unsupported(r))} |")
    return lines


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    path = {"sampling": HERE / "sampling", "baseline-dev": HERE / "runs" / "baseline-dev",
            "revision1-dev": HERE / "runs" / "revision1-dev",
            "baseline-heldout": HERE / "runs" / "baseline-heldout",
            "revision1-heldout": HERE / "runs" / "revision1-heldout"}.get(mode)
    if not path:
        raise SystemExit("usage: report_dev.py sampling | baseline-dev | revision1-dev | baseline-heldout | "
                         "revision1-heldout")
    result = json.loads((path / "results.json").read_text(encoding="utf-8"))
    print("\n".join(sampling(result) if mode == "sampling" else baseline(result)))
