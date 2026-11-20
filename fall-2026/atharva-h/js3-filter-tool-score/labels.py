"""Draw the hand-label sample from the frozen corpus, before any filter verdict exists.

    python3 labels.py draw      write state/labels/labels.csv (to fill in), postings.md, and split.json

The permission policy allows writes only in runs/ and state/, so the label files live in state/labels/.

The sample (FILTER.md v1.0, "How the filter will be measured"):
- every posting whose title has a role phrase, at any seniority;
- 30 random postings whose title has a bare "analyst" (no role phrase);
- 40 random other postings.
Each stratum is then split 2:1 into tuning and held-out. One seed drives every random choice, so
the draw can be repeated exactly. The role phrases are frozen here at v1.0 on purpose: a later
filter version may change its phrases, but the labeled sample must not move.
"""
import csv
import io
import json
import random
import re
import sys

import corpus
from policy import Policy
from tools import Tools

SEED = 20261120
ROLE_V1 = re.compile(r"\b(data analyst|bi analyst|business intelligence analyst|business analyst|reporting analyst|"
                     r"analytics analyst)\b", re.I)
ANALYST = re.compile(r"\banalyst\b", re.I)
SIZES = {"bare-analyst": 30, "other": 40}
COLUMNS = ["n", "key", "title", "location", "url", "label", "reason"]


def stratum(p):
    title = p["title"] or ""
    if ROLE_V1.search(title):
        return "role-phrase"
    return "bare-analyst" if ANALYST.search(title) else "other"


def draw(postings, seed=SEED):
    rng = random.Random(seed)
    groups = {"role-phrase": [], "bare-analyst": [], "other": []}
    for p in sorted(postings, key=lambda p: p["key"]):
        groups[stratum(p)].append(p)
    sample = {"role-phrase": groups["role-phrase"]}
    for name, size in SIZES.items():
        sample[name] = rng.sample(groups[name], min(size, len(groups[name])))
    split = {}
    for name, items in sample.items():
        keys = [p["key"] for p in items]
        rng.shuffle(keys)
        cut = round(len(keys) * 2 / 3)
        split.update({k: "tuning" for k in keys[:cut]})
        split.update({k: "held-out" for k in keys[cut:]})
    chosen = [p for items in sample.values() for p in items]
    rng.shuffle(chosen)  # the sheet's order hides the stratum
    return chosen, split, {name: len(groups[name]) for name in groups}, {name: len(v) for name, v in sample.items()}


def main(argv):
    if argv[1:] != ["draw"]:
        print(__doc__)
        return 2
    tools = Tools(Policy())
    run, postings = corpus.load(tools)
    chosen, split, population, sizes = draw(postings)
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    for n, p in enumerate(chosen, 1):
        writer.writerow({"n": n, "key": p["key"], "title": p["title"], "url": p["url"], "label": "", "reason": "",
                         "location": "; ".join(dict.fromkeys(p["locations"])) or "not given"})
    md = [f"# Postings to label ({len(chosen)})", "",
          "For each one, decide: would Riley Navarro (fictional, entry-level Data/BI/Business Analyst, 0-2 years, "
          "US or US remote, needs sponsorship) apply? Write `yes` or `no` in the `label` column of `labels.csv`, "
          "with a one-line reason. This sheet shows no filter verdict.", ""]
    for n, p in enumerate(chosen, 1):
        md += [f"## {n}. {p['title']}", "",
               f"- **Key:** `{p['key']}`",
               f"- **Location:** {p['location'] or 'not given'}" + (
                   f" (also: {'; '.join(l for l in p['locations'][1:] if l != p['location'])})"
                   if len(set(p["locations"])) > 1 else ""),
               f"- **Department:** {p['department'] or 'not given'}",
               f"- **Link:** {p['url']}", "", p["text"] or "_No description text in the response._", ""]
    meta = {"corpus": run, "seed": SEED, "rule": "FILTER.md v1.0: every role-phrase title, 30 random bare-analyst, "
            "40 random other; each stratum split 2:1 tuning/held-out", "population": population, "sample": sizes,
            "split": split}
    tools.write_text("state/labels/labels.csv", out.getvalue())
    tools.write_text("state/labels/postings.md", "\n".join(md) + "\n")
    tools.write_text("state/labels/split.json", json.dumps(meta, indent=1) + "\n")
    print(f"drew {len(chosen)} from {run}: population {population}, sample {sizes}")
    print(f"held-out: {sum(v == 'held-out' for v in split.values())}, tuning: {sum(v == 'tuning' for v in split.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
