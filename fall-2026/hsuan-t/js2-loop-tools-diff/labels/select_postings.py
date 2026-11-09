"""Picks the 20 real postings Isaac hand-labels for the prompt experiment (brief Step 4.2, R23).

Why a script and not hand-picking: the sample must not be chosen by looking at answers. Run 2's
20 new postings are all obvious not_relevant (sales, intern), which can't tell two prompts apart,
so the sample mixes difficulty on purpose, by a fixed rule and a fixed random seed that anyone can
re-run: every posting the rule keeps or cuts late (relevant, skills, years), 10 random engineering
titles cut only by location, and 5 random postings cut by title as clear negatives.

The groups come from the CONTRACT rule as of commit ab1e292 in my working repo (see `evidence/git-history.txt`), when the 20 were picked. Check 2 changed
afterwards (no location -> pass, D21), which moves a few postings between groups, so re-running this
file today picks a different set: check out ab1e292 to reproduce the committed postings_to_label.md.

Writes the posting text only. The rule's and Claude's verdicts are deliberately left out, so the
labels are Isaac's own reading. Run: .venv/bin/python labels/select_postings.py
"""

import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from job_agent import inputs                      # noqa: E402
from job_agent.common.paths import Paths          # noqa: E402
from job_agent.judges import rule                 # noqa: E402
from job_agent.judges.words import strip_html     # noqa: E402
from job_agent.watch.boards import greenhouse     # noqa: E402

RAW = ROOT / "evidence/raw/2026-10-31T214118Z/stripe_content.json"   # Run 2, live 2026-10-31
SEED = 20261031
OUT = ROOT / "labels"


def strata(posts, criteria):
    """Group postings by where the CONTRACT rule stops; used only to mix difficulty, never shown."""
    groups = {"late": [], "location": [], "title": []}
    for p in posts:
        r = rule.judge(p, criteria)
        if r.failed_check in ("1a", "1b"):
            groups["title"].append(p)
        elif r.failed_check == "2":
            groups["location"].append(p)
        else:                       # relevant, or cut at skills / years / visa / salary
            groups["late"].append(p)
    return groups


def main() -> None:
    paths = Paths()
    criteria = inputs.load_criteria(paths.default_resume, paths.default_profile, paths)
    posts = sorted(greenhouse.parse(RAW.read_bytes()), key=lambda p: p.id)   # sorted: same input order every run
    g = strata(posts, criteria)
    rng = random.Random(SEED)
    picked = g["late"] + rng.sample(g["location"], 10) + rng.sample(g["title"], 5)
    assert len(picked) == 20, f"expected 20, got {len(picked)} (late group has {len(g['late'])})"
    rng.shuffle(picked)            # so the order doesn't reveal which group a posting came from

    urls = greenhouse_urls()
    lines = ["# 20 postings to label", "",
             f"Source: `{RAW.relative_to(ROOT)}` (Run 2, live 2026-10-31). Picked by `labels/select_postings.py` (seed {SEED}).",
             "Label each one in `labels/labels.csv` using `labels/LABELING_RULE.md`. Verdicts are not shown on purpose.", ""]
    for i, p in enumerate(picked, 1):
        lines += [f"## {i}. {p.title}  (posting_id {p.id})", "",
                  f"- **location.name:** {p.location}", f"- **link:** {urls.get(p.id, '')}", "",
                  strip_html(p.content).strip(), "", "---", ""]
    (OUT / "postings_to_label.md").write_text("\n".join(lines))

    with open(OUT / "labels.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "posting_id", "title", "label", "reason"])   # label: relevant / not_relevant
        for i, p in enumerate(picked, 1):
            w.writerow([i, p.id, p.title, "", ""])
    print(f"wrote {OUT / 'postings_to_label.md'} and {OUT / 'labels.csv'}: {len(picked)} postings")


def greenhouse_urls() -> dict[int, str]:
    """The public job page, for reading the posting on Stripe's site if the plain text is hard to read."""
    import json
    return {j["id"]: j.get("absolute_url", "") for j in json.loads(RAW.read_bytes())["jobs"]}


if __name__ == "__main__":
    main()
