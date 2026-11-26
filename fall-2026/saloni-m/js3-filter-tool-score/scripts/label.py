"""Saloni's hand labels. Run it in a terminal; it saves after every answer, so you can stop anytime.

    python3 scripts/label.py labels/audit_sheet.csv
    python3 scripts/label.py labels/heldout_sheet.csv
    python3 scripts/label.py labels/claims_sheet.csv      # agree/disagree with the checker's claim labels

    python3 scripts/label.py labels/audit_sheet.csv labels/heldout_sheet.csv   # both, one after the other

Postings: y = worth Priya's time, n = not, ? = I cannot tell from the posting, f = show the full text.
One key per row saves it. Add + (y+, n+, ?+) to also type a note for that row.
The sheet never shows the filter's decision or score (blind labeling). Rule: labels/LABELING-RULE.md.
"""
import csv
import datetime as dt
import os
import subprocess
import sys
import textwrap

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from js3.collect import latest_snapshot, load_postings  # noqa: E402

REQ_HEADS = ("you might", "you may be a good fit", "qualifications", "requirements", "you have", "you'll need",
             "what you bring", "we're looking for", "we’re looking for", "you should", "about you", "minimum")


def excerpt(text, head=900, req=1800):
    low = text.lower()
    starts = [low.find(h) for h in REQ_HEADS if low.find(h) > head]
    out = text[:head]
    if starts:
        s = min(starts)
        out += f"\n\n[… skipped to requirements, char {s} of {len(text)} …]\n\n" + text[s:s + req]
    elif len(text) > head:
        out += f"\n[… {len(text) - head} more chars; press f for all …]"
    return out


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        return rows, (rows and list(rows[0].keys())) or []


def save(path, rows, cols):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def ask(prompt, allowed):
    """Returns (key, wants_note). A trailing + asks for a note."""
    while True:
        a = input(prompt).strip().lower()
        note = a.endswith("+") and len(a) > 1
        a = a[:-1] if note else a
        if a in allowed:
            return a, note


def main(path):
    rows, cols = read(path)
    claims_mode = "checker_label" in cols
    posts = {p["uid"]: p for p in load_postings(latest_snapshot())}
    todo = [r for r in rows if not r.get("hand_label")]
    print(f"{len(todo)} of {len(rows)} rows to label in {os.path.relpath(path, HERE)}. q to stop.\n")
    for r in todo:
        p = posts[r["uid"]]
        print("=" * 100)
        print(f"row {r['row']}  {p['title']}  |  {p.get('location')}  |  {p.get('department')}  |  {p['board']}")
        print("-" * 100)
        if claims_mode:
            print(f"CLAIM ({r['kind']}): {r['claim']}\nTERM: {r['term']}\nQUOTE: {r['quote']!r}\n"
                  f"CHECKER SAYS: {r['checker_label']}  ({r['checker_why']})")
            keys = {"a": "agree", "d": "disagree", "f": None, "q": None}
            prompt = "a = agree with the checker, d = disagree, f = full text, q = quit  (+ for a note): "
        else:
            print(textwrap.indent(excerpt(p["text"]), "  "))
            keys = {"y": "worth_time", "n": "not_worth_time", "?": "cannot_tell", "f": None, "q": None}
            prompt = f"[{todo.index(r) + 1}/{len(todo)}] worth Priya's time?  y / n / ? / f (full text) / q   (+ for a note): "
        while True:
            a, wants_note = ask(prompt, keys)
            if a == "f":
                subprocess.run(["less"], input=p["text"].encode())
                continue
            break
        if a == "q":
            break
        r["hand_label"] = keys[a]
        r["note"] = input("note: ").strip() if wants_note else r.get("note", "")
        r["labelled_at"] = dt.datetime.now().isoformat(timespec="seconds")
        save(path, rows, cols)
    left = sum(1 for r in rows if not r.get("hand_label"))
    print(f"\nsaved. {left} rows still unlabelled.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for sheet in sys.argv[1:]:
        main(sheet)
        with open(sheet, newline="", encoding="utf-8") as f:
            if any(not r.get("hand_label") for r in csv.DictReader(f)):
                break  # stopped with q: don't start the next sheet
