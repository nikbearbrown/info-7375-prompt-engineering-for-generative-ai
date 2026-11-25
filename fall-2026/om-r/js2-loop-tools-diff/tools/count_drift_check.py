"""Independent posting-count drift check (FINISHED-WRONG-ANSWER.md).

Deliberately standalone: standard library only, imports nothing from
agent/, and nothing in agent/ imports it. It is not part of the loop's
reporting path. It reads two saved board responses directly from disk and
compares their TOTAL posting counts - something the loop's repeat rule
(new-vs-seen ids) never looks at.

    python3 tools/count_drift_check.py BEFORE.json AFTER.json [--max-drop 0.5]

Exit 0: counts look consistent. Exit 1: SUSPICIOUS - investigate by hand
before trusting the loop's "0 new" for this board.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def count_postings(path):
    data = json.loads(Path(path).read_bytes())
    if isinstance(data, dict) and isinstance(data.get("jobs"), list):  # Greenhouse
        return len(data["jobs"]), "greenhouse", (data.get("meta") or {}).get("total")
    if isinstance(data, list):  # Lever (one page)
        return len(data), "lever", None
    raise ValueError(f"{path}: not a Greenhouse or Lever response shape")


def describe(path):
    n, shape, meta_total = count_postings(path)
    label = "  [SEEDED - constructed, NOT live data]" if "SEEDED" in Path(path).name else ""
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]
    print(f"  {path}{label}")
    print(f"    shape={shape}  postings={n}  meta.total={meta_total}  sha256={digest}")
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--max-drop", type=float, default=0.5,
                    help="flag if the count falls by more than this fraction (default 0.5)")
    args = ap.parse_args(argv)

    print("independent count check (standalone; not part of the loop)")
    print("before:")
    n_before = describe(args.before)
    print("after:")
    n_after = describe(args.after)

    if n_before == 0:
        print("\nOK: no earlier postings to compare against")
        return 0
    drop = (n_before - n_after) / n_before
    print(f"\nchange: {n_before} -> {n_after}  ({drop:.0%} drop)")
    if n_after == 0 or drop > args.max_drop:
        print(f"SUSPICIOUS: this board's total posting count dropped from {n_before} to {n_after} "
              f"between runs. Investigate by hand (re-fetch, check the board's public page) "
              f"before trusting the loop's '0 new' result for this run.")
        return 1
    print("OK: count change within threshold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
