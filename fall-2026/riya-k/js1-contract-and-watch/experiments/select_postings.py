"""Pick the 20 postings to hand-label, reproducibly (seed 7375), from the 2026-10-31 live snapshot.

Strata (positives are rare on this board, so likely candidates are oversampled):
  8 random from: title has a CONTRACT.md title word and no seniority word
  4 random from: early-career title (Intern, New Grad, University, Associate, Graduate) and no seniority word
  8 random from: everything else
Then a random 10/10 split into development and held-out. The first 5 development postings are the sampling set.
(A first draw of 10 title-word + 10 random gave 17 senior or non-US postings; it was discarded before
any labeling or Claude call. See FRICTIONAL.md.)
    python3 experiments/select_postings.py
"""

import json
import random
import re
from pathlib import Path

from jsagent import rules

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "snapshots" / "databricks-2026-10-31T233230Z-live.json"


def requirements_excerpt(content, n=900):
    text = rules.plain_text(content)
    m = re.search(r"(What we look for|What you.ll need|Qualifications|Requirements|You will have|Minimum)", text, re.I)
    return text[m.start(): m.start() + n] if m else text[:n]


def main():
    jobs = json.loads(SNAPSHOT.read_text())["jobs"]
    rng = random.Random(7375)
    has = lambda words, t: any(rules.find_word(w, t) for w in words)
    early_words = ["Intern", "Internship", "New Grad", "University", "Associate", "Graduate"]
    senior = lambda t: has(rules.SENIORITY_WORDS, t)
    a = [j for j in jobs if has(rules.TITLE_WORDS, j["title"]) and not senior(j["title"])]
    b = [j for j in jobs if has(early_words, j["title"]) and not senior(j["title"]) and j not in a]
    c = [j for j in jobs if j not in a and j not in b]
    picked = rng.sample(a, 8) + rng.sample(b, 4) + rng.sample(c, 8)
    rng.shuffle(picked)
    rows = [{"n": i + 1, "id": j["id"], "set": "dev" if i < 10 else "heldout", "sampling": i < 5,
             "title": j["title"], "location": j["location"]["name"], "url": j["absolute_url"]}
            for i, j in enumerate(picked)]
    (ROOT / "labels" / "selection.json").write_text(json.dumps(rows, indent=1) + "\n")
    by_id = {j["id"]: j for j in picked}
    md = ["# Labeling sheet (20 real postings, Databricks live snapshot 2026-10-31)", "",
          "Labeling rule (CONTRACT.md): relevant if Arya could apply honestly today: the role matches her",
          "AI/ML/data target, it is not senior, and she has at least 2 of the core skills the posting asks for.", "",
          "Arya's shipped skills: Python, SQL, Databricks, Unity Catalog, Power BI, LangGraph, MLflow, Mem0, Delta Lake, AWS.",
          "Experience: one 8-month AI Engineer co-op. Location: Boston, open to remote.", ""]
    for r in rows:
        md += [f"## {r['n']}. {r['title']}  ({r['set']})", f"- id {r['id']} · {r['location']} · {r['url']}", "",
               "> " + requirements_excerpt(by_id[r["id"]]["content"]), ""]
    (ROOT / "labels" / "labeling_sheet.md").write_text("\n".join(md))
    for r in rows:
        print(f"{r['n']:>2}. [{r['set']}] {r['title']} | {r['location']}")


if __name__ == "__main__":
    main()
