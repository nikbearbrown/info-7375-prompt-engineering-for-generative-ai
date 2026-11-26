"""JS3 audit report: compare Isaac's hand labels with the filter's verdicts and write audit/AUDIT.md.

Why it exists: the hand labels are the measurement, and a small sample needs an honest error bar.
Each stratum gets its disagreement count k of n with an exact two-sided 95% Clopper-Pearson
interval, computed here in pure Python (bisection on the binomial CDF) so no statistics library
is needed. It refuses to write anything while a label is missing or misspelled, so AUDIT.md never
quietly counts a blank as agreement.

Run: .venv/bin/python reports/audit_report.py   (after labelling audit/hand_verdicts.csv)
     -> audit/AUDIT.md
Tested by: tests/test_js3_audit.py (fake raw folders under tmp_path; never writes audit/)
"""

import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

LABELS = ("relevant", "not_relevant")
STRATA = ("random_reject", "close_call", "kept")
ALPHA = 0.05
TODO = "(to be written by Isaac)"


def binom_cdf(k: int, n: int, p: float) -> float:
    """P(X <= k) for X ~ Binomial(n, p)."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def _bisect(f, target: float) -> float:
    """p in [0, 1] with f(p) == target, for f decreasing in p."""
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def clopper_pearson(k: int, n: int) -> tuple[float, float]:
    """Exact two-sided 95% interval for a binomial proportion k/n."""
    if n <= 0 or not 0 <= k <= n:
        raise ValueError(f"need 0 <= k <= n and n > 0, got k={k}, n={n}")
    tail = ALPHA / 2
    # lower: P(X >= k | p) = tail, i.e. P(X <= k-1 | p) = 1 - tail.
    lower = 0.0 if k == 0 else _bisect(lambda p: binom_cdf(k - 1, n, p), 1 - tail)
    # upper: P(X <= k | p) = tail.
    upper = 1.0 if k == n else _bisect(lambda p: binom_cdf(k, n, p), tail)
    return lower, upper


def _filter_label(entry: dict) -> str:
    fc = entry.get("failed_check")
    return entry["verdict"] + (f" (cut at {fc})" if fc else "")


def check_labels(rows: list[dict], key: dict) -> list[str]:
    """Messages for every row whose label is missing or not exactly relevant/not_relevant."""
    bad = []
    for row in rows:
        sid = row.get("sample_id", "")
        label = row.get("my_label") or ""
        if sid not in key:
            bad.append(f"{sid}: not in sample_key.json")
        elif label not in LABELS:
            bad.append(f"{sid}: my_label is {label!r}, must be relevant or not_relevant")
    for sid in sorted(set(key) - {row.get("sample_id") for row in rows}):
        bad.append(f"{sid}: missing from hand_verdicts.csv")
    return bad


def audit_md(rows: list[dict], key: dict) -> str:
    by_stratum = {s: [0, 0] for s in STRATA}
    disagreements = []
    for row in sorted(rows, key=lambda r: r["sample_id"]):
        entry = key[row["sample_id"]]
        counts = by_stratum.setdefault(entry["stratum"], [0, 0])
        counts[0] += 1
        if row["my_label"] != entry["verdict"]:
            counts[1] += 1
            disagreements.append(f"| {row['sample_id']} | {entry['title']} | {_filter_label(entry)} | "
                                 f"{row['my_label']}: {(row.get('my_reason') or '').strip()} |")
    lines = ["# Filter audit (hand labels vs the rule filter)", "",
             "k counts the samples where Isaac's label differs from the filter's verdict.", "",
             "| stratum | n | k | k/n | 95% Clopper-Pearson interval |", "|---|---|---|---|---|"]
    notes = []
    for stratum, (n, k) in by_stratum.items():
        if n == 0:
            lines.append(f"| {stratum} | 0 | 0 | - | - |")
            continue
        lo, hi = clopper_pearson(k, n)
        lines.append(f"| {stratum} | {n} | {k} | {k / n:.3f} | {lo:.3f} – {hi:.3f} |")
        if stratum == "random_reject":
            notes.append(f"This is an estimate from {n} random rejects, not a measured rate for all postings.")
    lines += ["", *notes, "", "## Disagreements", ""]
    if disagreements:
        lines += ["| sample | title | filter verdict | Isaac's label and reason |", "|---|---|---|---|", *disagreements]
    else:
        lines.append("None: every label matches the filter.")
    lines += ["", "## False friend", "", TODO, "", "## Rule changes (v2)", "", TODO, ""]
    return "\n".join(lines)


def report(audit_dir: Path, out_dir: Path) -> int:
    audit_dir = Path(audit_dir)
    key = json.loads((audit_dir / "sample_key.json").read_text(encoding="utf-8"))
    with (audit_dir / "hand_verdicts.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    bad = check_labels(rows, key)
    if bad:
        print("hand_verdicts.csv is not ready, AUDIT.md not written:\n  " + "\n  ".join(bad), file=sys.stderr)
        return 1
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "AUDIT.md").write_text(audit_md(rows, key), encoding="utf-8")
    print(f"wrote {out_dir / 'AUDIT.md'} from {len(rows)} labels")
    return 0


def main() -> None:
    sys.exit(report(ROOT / "audit", ROOT / "audit"))


if __name__ == "__main__":
    main()
