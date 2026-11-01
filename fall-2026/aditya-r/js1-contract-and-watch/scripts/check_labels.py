"""Validate the hand-label files without changing them.

    .venv/bin/python scripts/check_labels.py

Checks ids against the sample manifest, missing values and allowed values. Prints no groups,
no RECORDs and no model output.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = {"relevant", "not_relevant"}


def main():
    manifest = json.loads((ROOT / "experiments/sample/manifest.json").read_text())
    problems = 0
    for split, key in (("dev", "dev_ids"), ("heldout", "heldout_ids")):
        rows = list(csv.DictReader(open(ROOT / f"labeling/{split}_labels.csv", newline="")))
        ids = [r["posting_id"].strip() for r in rows]
        expected = {str(i) for i in manifest[key]}
        issues = []
        if set(ids) != expected or len(ids) != len(expected):
            issues.append(f"ids differ from the sample (missing {sorted(expected - set(ids))}, unexpected {sorted(set(ids) - expected)}, rows {len(ids)})")
        for r in rows:
            label = r["label"].strip()
            if not label:
                issues.append(f"{r['posting_id']}: label missing")
            elif label not in ALLOWED:
                issues.append(f"{r['posting_id']}: label {label!r} is not exactly 'relevant' or 'not_relevant'")
        filled = sum(1 for r in rows if r["label"].strip() in ALLOWED)
        print(f"{split}: {filled}/{len(expected)} valid labels" + ("" if not issues else ""))
        for i in issues:
            print("   -", i)
        problems += len(issues)
    print("OK" if not problems else f"{problems} problem(s); files were not modified")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
