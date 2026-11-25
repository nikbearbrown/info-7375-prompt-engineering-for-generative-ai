"""Judge the filter, one sampled posting at a time (JS3 reject audit). Shows the whole posting AND the filter's verdict with its
evidence; you decide whether the filter was right for Evan. Saved after every answer.

    python3 scripts/audit.py

Keys: y = filter right, w = filter wrong, s = skip, q = save and quit.
"""
import csv
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jsagent import snapshot  # noqa: E402

AUDIT = ROOT / "audit" / "audit.csv"


def main():
    rows = list(csv.DictReader(AUDIT.open()))
    fields = list(rows[0].keys())
    ps = {(p["board"], p["id"]): p for p in snapshot.load()[0]}

    def save():
        with AUDIT.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    todo = [r for r in rows if r["ethan_verdict"] not in ("right", "wrong")]
    print(f"{len(rows) - len(todo)} of {len(rows)} judged; {len(todo)} to go.")
    for i, row in enumerate(todo, 1):
        p = ps[(row["board"], row["posting_id"])]
        print("\n" * 2 + "=" * 78)
        print(f"[{i}/{len(todo)}]  #{row['n']}  {row['group'].upper()}  {p['board']}  id={p['id']}")
        print(f"TITLE:    {p['title']}\nLOCATION: {p['location']['name'] or '(none)'}\nURL:      {p['absolute_url']}\n")
        print(textwrap.fill(p["content"], 78) if p["content"] else "(no description in the posting)")
        print(f"\nFILTER SAYS: {row['filter_bucket'].upper()}\n  reason:   {row['filter_reason']}\n  evidence: {row['filter_evidence']}")
        while True:
            k = input("\nIs the filter right for Evan? (y/w/s/q): ").strip().lower()
            if k in ("y", "w"):
                row["ethan_verdict"] = "right" if k == "y" else "wrong"
                row["ethan_note"] = input("One-line reason: ").strip()
                save()
                break
            if k == "s":
                break
            if k == "q":
                save()
                sys.exit("saved")
    save()
    print("done; verdicts saved to", AUDIT.relative_to(ROOT))


if __name__ == "__main__":
    main()
