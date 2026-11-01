"""Pick the 20 real postings for hand-labeling and split them 10 development / 10 held-out.

    python3 make_labeling_set.py evidence/raw/<live response>.json.gz

Selection (fixed, seed 7375), three strata, each split evenly between dev and held-out at random:
  A (all 6)  US-located, title names an early-career term (intern / new grad / early career) AND
             engineering ("Engineer"/"Engineering") — the boundary cases for the rule;
  B (6)      rule role AND level true, but not US-located;
  C (8)      rule role true, level false (experienced engineering roles).
A uniform random draw was tried first: it contained no US early-career posting at all, so every
label would likely have been NOT RELEVANT and the pass rate would say nothing.
Writes labeling/postings/<NN>-<id>.md (title, location, link, full description text) and a blank
labeling/labels.csv. Rule verdicts are deliberately NOT written anywhere in labeling/.
"""

import csv
import random
import re
import sys
from pathlib import Path

from jsagent import rule
from jsagent.resume import load_resume, skill_fields
from jsagent.watch import load_raw, parse_jobs

HERE = Path(__file__).resolve().parent
SEED = 7375


def main(raw_path):
    jobs = parse_jobs(load_raw(raw_path))
    skills = skill_fields(load_resume(HERE / "persona" / "rohan-desai.resume.example.json"))
    a, b, c_ = [], [], []
    for job in sorted(jobs, key=lambda j: j["id"]):
        c = rule.judge(job, skills)["conditions"]
        early = re.search(r"\b(intern|internship|new grad|early career)\b", job["title"], re.I)
        if c["location"]["passed"] and early and re.search(r"\bengineer", job["title"], re.I):
            a.append(job)
        elif c["role"]["passed"] and c["level"]["passed"]:
            b.append(job)
        elif c["role"]["passed"]:
            c_.append(job)
    rng = random.Random(SEED)
    strata = [rng.sample(a, 6), rng.sample(b, 6), rng.sample(c_, 8)]
    for s in strata:
        rng.shuffle(s)
    rows = ([("dev", j) for s in strata for j in s[:len(s) // 2]] +
            [("heldout", j) for s in strata for j in s[len(s) // 2:]])

    out = HERE / "labeling" / "postings"
    out.mkdir(parents=True, exist_ok=True)
    with open(HERE / "labeling" / "labels.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "set", "posting_id", "title", "location", "my_label", "my_note"])
        for n, (split, job) in enumerate(rows, 1):
            w.writerow([n, split, job["id"], job["title"].strip(), rule.location_name(job), "", ""])
            (out / f"{n:02d}-{job['id']}.md").write_text(
                f"# {n:02d} · {job['title'].strip()}\n\n"
                f"- posting_id: {job['id']} · set: {split}\n- location.name: {rule.location_name(job)}\n"
                f"- departments: {', '.join(rule.departments(job)) or '—'}\n- link: {job.get('absolute_url')}\n"
                f"- source: {Path(raw_path).name}\n\n## Description (HTML removed)\n\n{rule.description_text(job)}\n")
    print(f"strata sizes A={len(a)} B={len(b)} C={len(c_)}; wrote {len(rows)} postings to labeling/")


if __name__ == "__main__":
    main(sys.argv[1])
