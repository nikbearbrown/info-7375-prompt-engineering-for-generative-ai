"""Hand-label the 20 postings in labels.csv, one at a time. Shows the posting only:
never the rule verdict or any Claude output, so your label stays yours.

    python3 experiments/prompt_experiment/label.py

Keys: r = relevant, n = not_relevant, s = skip for now, q = save and quit.
Read LABELING_RULE.md first. Labels are saved after every answer.

    python3 experiments/prompt_experiment/label.py --redo   # second pass over all 20: Enter keeps the current label
"""
import csv
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import LABELS, load_postings  # noqa: E402

rows = list(csv.DictReader(LABELS.open()))
fields = list(rows[0].keys())
ps = load_postings()


def save():
    with LABELS.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


REDO = "--redo" in sys.argv
todo = rows if REDO else [r for r in rows if r["human_label"] not in ("relevant", "not_relevant")]
print(f"{len(todo)} of {len(rows)} postings still need a label.\n")
for i, row in enumerate(todo, 1):
    p = ps[row["posting_id"]]
    print("=" * 78)
    print(f"[{i}/{len(todo)}] {row['split'].upper()}  {p['board']}  id={p['id']}")
    print(f"TITLE:    {p['title']}\nLOCATION: {p['location']['name']}\nURL:      {p['absolute_url']}\n")
    print(textwrap.fill(p["content"], 78))  # whole posting: requirements are often past char 6000
    if REDO:
        print(f"\nCURRENT: {row['human_label'] or '(none)'} | note: {row['label_note'] or '(none)'}")
    while True:
        k = input("\nLabel (r/n/s/q" + (", Enter = keep" if REDO else "") + "): ").strip().lower()
        if REDO and k == "" and row["human_label"] in ("relevant", "not_relevant"):
            new_note = input("Note (Enter = keep current): ").strip()
            if new_note:
                row["label_note"] = new_note
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
print("done; labels saved to", LABELS)
