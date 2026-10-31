"""Write LABELS.md: the 20 selected postings in full, for labeling by hand with the rule.

    python3 experiments/make_label_sheet.py

The sheet shows no rule or Claude verdicts, so the hand labels are not anchored to them.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from rule import description_text  # noqa: E402

POOL = os.path.join(HERE, "label_pool")


def load_postings():
    with open(os.path.join(POOL, "selection.json"), encoding="utf-8") as f:
        selection = json.load(f)["postings"]
    raws = {}
    for s in selection:
        if s["board"] not in raws:
            with open(os.path.join(POOL, "raw", f"{s['board']}.json"), encoding="utf-8") as f:
                raws[s["board"]] = {j["id"]: j for j in json.load(f)["jobs"]}
    return [(s, raws[s["board"]][s["id"]]) for s in selection]


def main():
    rows = load_postings()
    out = ["# Hand labels — prompt experiment", "",
           "Label each posting with the rule in `CONTRACT.md` before looking at any rule or Claude verdict.",
           "Write `relevant`, `not_relevant`, or `needs_human` in the **Label** column, and the check that",
           "decided it (title, seniority, location, sponsorship, experience) in **Deciding check**.", "",
           "| # | Set | Posting id | Title | Label | Deciding check |", "|---|---|---|---|---|---|"]
    for i, (s, _) in enumerate(rows, 1):
        out.append(f"| {i} | {s['set']} | {s['id']} | {s['title']} |  |  |")
    out.append("")
    for i, (s, job) in enumerate(rows, 1):
        offices = "; ".join(filter(None, (f"{o.get('name')} ({o.get('location')})" for o in job.get("offices") or []))) or "none"
        out += [f"## {i}. {job['title']} — {s['board']} ({s['set']})", "",
                f"- Posting id: {job['id']}", f"- location.name: {(job.get('location') or {}).get('name')}",
                f"- offices: {offices}", f"- URL: {job.get('absolute_url')}", "",
                "<details><summary>Description</summary>", "", description_text(job.get("content")), "",
                "</details>", ""]
    with open(os.path.join(POOL, "LABELS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"wrote {os.path.relpath(os.path.join(POOL, 'LABELS.md'))} with {len(rows)} postings")


if __name__ == "__main__":
    main()
