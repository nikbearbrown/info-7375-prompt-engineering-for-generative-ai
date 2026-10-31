"""Run from the folder: PYTHONPATH=. python3 experiments/experiment-2/make_label_sheet.py
Writes the blind label sheet (no verdicts, no hints) and a blank CSV for Shreyash."""
import csv
import json
import pathlib

from jsagent import posting

D = pathlib.Path("experiments/experiment-2")
sel = json.loads((D / "selected_postings.json").read_text())
jobs = {j["id"]: j for j in json.loads(pathlib.Path(sel["raw_file"]).read_bytes())["jobs"]}
order = [("development", x["id"]) for x in sel["development"]] + [("held_out", x["id"]) for x in sel["held_out"]]
head = """# Experiment 2: postings to label (20 real Klaviyo postings, fetched 2026-10-31)

Fill in `hand-labels.csv` for each posting, before any Claude call:
- `label`: Relevant or Not Relevant
- `failed_conditions`: the numbers that fail, joined with `;` (for example `3;5`). Leave it empty if Relevant.
- `reason`: a few words, the way your Oscar evidence notes were

This sheet shows no verdict from the rule or from Claude.

**The applicant (Alex Morgan):** Boston, MA, remote OK, 3 years of experience. Skills: Python, Java, TypeScript, FastAPI, React, LangGraph, RAG, PyTorch, SQL, Docker.

**The six conditions (CONTRACT.md section 5, as you decided on 2026-10-31):**
1. The title has one of the phrases Software Engineer, Software Developer, Backend Engineer, Full Stack Engineer, Full Stack Developer, AI Engineer, ML Engineer, Machine Learning Engineer, LLM Engineer. (All 20 here pass, because the postings were picked that way.)
2. The department is one of Engineering, Software Engineering, Machine Learning, AI, Artificial Intelligence, Data Science.
3. Boston, or remote in the US that someone living in Massachusetts can actually do.
4. The ad mentions at least 2 of the skills.
5. The highest minimum years in the mandatory qualifications is 3 or less. If none is stated, this passes.
6. Not Director, Staff, Principal, Manager or Lead in the title; not unpaid, contract-only, or relocation outside Boston.
"""
out = [head]
for i, (split, pid) in enumerate(order, 1):
    p = posting.normalize(jobs[pid], "klaviyo")
    out += [f"## {i}. {p['id']} — {p['title']}", "", f"- set: {split}", f"- departments: {p['departments']}",
            f"- location: {p['location']}", f"- offices: {p['offices']}", f"- link: {p['absolute_url']}", "", p["content"], ""]
(D / "POSTINGS-TO-LABEL.md").write_text("\n".join(out))
with open(D / "hand-labels.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["n", "posting_id", "set", "title", "location", "label", "failed_conditions", "reason"])
    for i, (split, pid) in enumerate(order, 1):
        w.writerow([i, pid, split, jobs[pid]["title"].strip(), jobs[pid]["location"]["name"], "", "", ""])
print("wrote", D / "POSTINGS-TO-LABEL.md", "and", D / "hand-labels.csv")
