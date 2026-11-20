"""Run from the folder: PYTHONPATH=. python3 labels/make_label_sheet.py
Writes labels/POSTINGS-TO-LABEL.md (the 20 selected postings as plain text, no verdicts and
no hints) and a blank labels/hand-labels.csv for Shreyash to fill in by hand."""
import csv
import json
import pathlib

from jsagent import posting

sel = json.loads(pathlib.Path("experiments/selected_postings.json").read_text())
jobs = {j["id"]: j for j in json.loads(pathlib.Path(sel["raw_file"]).read_bytes())["jobs"]}
order = [("development", x["id"]) for x in sel["development"]] + [("held_out", x["id"]) for x in sel["held_out"]]

out = ["# Postings to label (20 real Oscar postings from run 1, 2026-10-28)", "",
       "Read each one and fill in `labels/hand-labels.csv` using LABELING-RULE.md. "
       "This sheet shows no verdict from the rule or from Claude.", ""]
for i, (split, pid) in enumerate(order, 1):
    p = posting.normalize(jobs[pid], "oscar")
    out += [f"## {i}. {p['id']} — {p['title']}", "",
            f"- set: {split}", f"- departments: {p['departments']}", f"- location: {p['location']}",
            f"- offices: {p['offices']}", f"- link: {p['absolute_url']}", "", p["content"], ""]
pathlib.Path("labels/POSTINGS-TO-LABEL.md").write_text("\n".join(out))

with open("labels/hand-labels.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["n", "posting_id", "set", "title", "label", "failed_conditions", "note"])
    for i, (split, pid) in enumerate(order, 1):
        w.writerow([i, pid, split, jobs[pid]["title"].strip(), "", "", ""])
print("wrote labels/POSTINGS-TO-LABEL.md and labels/hand-labels.csv")
