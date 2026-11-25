"""Draw the hand-label sample from the frozen corpus, before any filter verdict exists.

    python3 labels.py draw      write state/labels/labels.csv (to fill in), postings.md, and split.json
    python3 labels.py draw-v1.1 the same for the v1.1 supplement boards: labels_v1_1.csv, postings_v1_1.md,
                                split_v1_1.json

The permission policy allows writes only in runs/ and state/, so the label files live in state/labels/.

The sample (FILTER.md v1.0, "How the filter will be measured"):
- every posting whose title has a role phrase, at any seniority;
- 30 random postings whose title has a bare "analyst" (no role phrase);
- 40 random other postings.
FILTER.md v1.1 adds a supplement sample, drawn only from the supplement boards: every posting the v1.1 probe
rule flags as a candidate, every role-phrase title, 10 random bare-"analyst", and 10 random others.
Each stratum is then split 2:1 into tuning and held-out. One seed drives every random choice, so
the draw can be repeated exactly. The role phrases are frozen here at v1.0 on purpose: a later
filter version may change its phrases, but the labeled sample must not move.
"""
import csv
import importlib.util
import io
import os
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
SIZES_V11 = {"bare-analyst": 10, "other": 10}


def _probe_rule():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe", "probe_v1_1.py")
    spec = importlib.util.spec_from_file_location("probe_v1_1", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.candidate
COLUMNS = ["n", "key", "title", "location", "url", "label", "reason"]


def stratum(p, candidate=None):
    title = p["title"] or ""
    if candidate and candidate(p):
        return "probe-candidate"
    if ROLE_V1.search(title):
        return "role-phrase"
    return "bare-analyst" if ANALYST.search(title) else "other"


def draw(postings, seed=SEED, sizes=SIZES, candidate=None):
    rng = random.Random(seed)
    groups = {"probe-candidate": [], "role-phrase": [], "bare-analyst": [], "other": []}
    for p in sorted(postings, key=lambda p: p["key"]):
        groups[stratum(p, candidate)].append(p)
    if not candidate:
        del groups["probe-candidate"]
    sample = {name: groups[name] for name in groups if name not in sizes}
    for name, size in sizes.items():
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
    if argv[1:] not in (["draw"], ["draw-v1.1"]):
        print(__doc__)
        return 2
    v11 = argv[1] == "draw-v1.1"
    tools = Tools(Policy())
    run, postings = corpus.load(tools)
    if v11:
        postings = [p for p in postings if p["corpus"] == "v1.1 supplement"]
        chosen, split, population, sizes = draw(postings, sizes=SIZES_V11, candidate=_probe_rule())
    else:
        chosen, split, population, sizes = draw([p for p in postings if p["corpus"] == "v1.0"])
    suffix = "_v1_1" if v11 else ""
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
    rule = ("FILTER.md v1.1: on the supplement boards, every probe-rule candidate, every role-phrase title, 10 random "
            "bare-analyst, 10 random other" if v11 else
            "FILTER.md v1.0: every role-phrase title, 30 random bare-analyst, 40 random other")
    meta = {"corpus": sorted({p["corpus"] for p in chosen}), "run": run, "seed": SEED,
            "rule": rule + "; each stratum split 2:1 tuning/held-out", "population": population, "sample": sizes,
            "split": split}
    tools.write_text(f"state/labels/labels{suffix}.csv", out.getvalue())
    tools.write_text(f"state/labels/postings{suffix}.md", "\n".join(md) + "\n")
    tools.write_text(f"state/labels/split{suffix}.json", json.dumps(meta, indent=1) + "\n")
    print(f"drew {len(chosen)} from {run}: population {population}, sample {sizes}")
    print(f"held-out: {sum(v == 'held-out' for v in split.values())}, tuning: {sum(v == 'tuning' for v in split.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
