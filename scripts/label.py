"""Hand-label the postings in labels/labels.csv, one at a time (adapted from my JS1 label.py).

Shows only the posting's own title, location, link and whole description: never a filter verdict, score or Claude output,
so the label stays mine. Read labels/LABELING_RULE.md first. Labels are saved after every answer.

    python3 scripts/label.py           # next unlabeled posting
    python3 scripts/label.py --redo    # second pass over all: Enter keeps the current label

Keys: r = relevant, n = not_relevant, s = skip for now, q = save and quit.
"""
import csv
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import re  # noqa: E402

from jsagent import rule, snapshot  # noqa: E402

LABELS = ROOT / "labels" / "labels.csv"
# Quoted posting text only, never the filter's reading: EVERY years phrase (not just the first one F4 uses), and every
# sentence that mentions sponsorship, visas or work authorization (Ethan's request, 2026-11-25, before any label).
_VISA = re.compile(r"sponsor|\bvisas?\b|immigration|H-?1B|work authori[sz]ation|authori[sz]ed to work|work permit", re.I)
_SENT = re.compile(r"(?<=[.!?])\s+")


def years_mentions(content):
    out = []
    for m in rule.YEARS_RE.finditer(content):
        out.append("..." + content[max(0, m.start() - 60):m.end() + 60].strip() + "...")
    return out


def visa_mentions(content):
    return [s.strip() for s in _SENT.split(content) if _VISA.search(s)]


def show_list(name, items):
    print(f"{name}:")
    if not items:
        print("  (none mentioned in the posting)")
    for x in items:
        print(textwrap.fill(x, 78, initial_indent="  - ", subsequent_indent="    "))


def main():
    rows = list(csv.DictReader(LABELS.open()))
    fields = list(rows[0].keys())
    postings, _ = snapshot.load()
    ps = {(p["board"], p["id"]): p for p in postings}

    def save():
        with LABELS.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    redo = "--redo" in sys.argv
    todo = rows if redo else [r for r in rows if r["human_label"] not in ("relevant", "not_relevant")]
    done = len(rows) - sum(1 for r in rows if r["human_label"] not in ("relevant", "not_relevant"))
    print(f"{done} of {len(rows)} labeled; {len(todo)} to go.\n")
    for i, row in enumerate(todo, 1):
        p = ps[(row["board"], row["posting_id"])]
        print("\n" * 2 + "=" * 78)
        print(f"[{i}/{len(todo)}]  #{row['n']}  {p['board']}  id={p['id']}")
        print(f"TITLE:    {p['title']}\nLOCATION: {p['location']['name'] or '(none)'}\nURL:      {p['absolute_url']}")
        show_list("YEARS MENTIONED (every phrase, quoted)", years_mentions(p["content"]))
        show_list("SPONSORSHIP / VISA / WORK AUTHORIZATION (quoted)", visa_mentions(p["content"]))
        print("\nFULL DESCRIPTION:")
        print(textwrap.fill(p["content"], 78) if p["content"] else "(no description in the posting)")
        if redo:
            print(f"\nCURRENT: {row['human_label'] or '(none)'} | note: {row['label_note'] or '(none)'}")
        while True:
            k = input("\nLabel (r/n/s/q" + (", Enter = keep" if redo else "") + "): ").strip().lower()
            if redo and k == "" and row["human_label"] in ("relevant", "not_relevant"):
                note = input("Note (Enter = keep current): ").strip()
                if note:
                    row["label_note"] = note
                    save()
                break
            if k in ("r", "n"):
                row["human_label"] = "relevant" if k == "r" else "not_relevant"
                row["label_note"] = input("One-line reason (which résumé/posting facts decided it): ").strip()
                save()
                break
            if k == "s":
                break
            if k == "q":
                save()
                sys.exit("saved")
    save()
    print("done; labels saved to", LABELS.relative_to(ROOT))


if __name__ == "__main__":
    main()
