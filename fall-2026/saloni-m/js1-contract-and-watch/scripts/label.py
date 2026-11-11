"""Hand-label the 20 experiment postings (yours to do: Claude must not fill this in).

Shows each posting's title, location, departments and the start of its text, then asks for
r (relevant) / n (not_relevant) and an optional one-line note. Dev postings come first; you can
stop and resume (already-labelled ids are skipped).

    python3 scripts/label.py
"""
import csv
import datetime as dt
import json
import os
import sys
import textwrap

sys.path.insert(0, ".")
from agent.claude_judge import posting_view  # noqa: E402

SET = "labels/experiment_set.json"
OUT = "labels/hand_labels.csv"
FIELDS = ["id", "split", "title", "hand_label", "note", "labelled_at"]

spec = json.load(open(SET, encoding="utf-8"))
jobs = {j["id"]: j for j in json.load(open(spec["source"], encoding="utf-8"))["jobs"]}
done = set()
if os.path.exists(OUT):
    done = {int(r["id"]) for r in csv.DictReader(open(OUT, encoding="utf-8"))}
else:
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, FIELDS).writeheader()

print(open("labels/LABELING-RULE.md", encoding="utf-8").read())
todo = [p for p in sorted(spec["postings"], key=lambda p: p["split"] != "dev") if p["id"] not in done]
for n, p in enumerate(todo, 1):
    v = posting_view(jobs[p["id"]])
    print("\n" + "=" * 78)
    print(f"[{n}/{len(todo)}] {p['split'].upper()}  id {p['id']}\n{v['title']}\n{v['location.name']}  |  {', '.join(v['departments'])}")
    print(textwrap.fill(v["content"][:2500], 78))
    print(f"\nfull posting: {p['url']}")
    label = ""
    while label not in ("r", "n"):
        label = input("relevant for Priya by YOUR labeling rule? [r/n] ").strip().lower()
    note = input("one-line reason (optional): ").strip()
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, FIELDS).writerow({
            "id": p["id"], "split": p["split"], "title": p["title"],
            "hand_label": "relevant" if label == "r" else "not_relevant", "note": note,
            "labelled_at": dt.datetime.now().isoformat(timespec="seconds")})
print(f"\nDone. Labels are in {OUT}.")
