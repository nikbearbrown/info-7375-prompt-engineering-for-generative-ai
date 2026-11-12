"""Choose the 20 experiment postings and the 5 sampling postings from the run-1 baseline,
before any hand label or Claude result exists. Deterministic: same seed, same choice.

Run from the js1-contract-and-watch folder:
    python3 experiments/select_postings.py

Writes experiments/selection.json, labels/labeling-sheet.md, labels/hand_labels.csv.

The sample is stratified by the rule's failure pattern so it holds near-misses, not
600 easy rejections. It is therefore NOT a random sample of the board, and pass rates
on it say nothing about the board as a whole. The labeling sheet shows no rule output.
"""

import csv
import gzip
import json
import random
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jobwatch import board, rule  # noqa: E402
from jobwatch.normalize import decode_entities  # noqa: E402
from jobwatch.resume import validate_resume  # noqa: E402

SEED = 20261028
SOURCE_RUN = "runs/20261028T102612Z-live"
# stratum: (how many to take, how many of those go to the development set)
PLAN = {"R": (6, 3), "S": (3, 2), "T": (3, 1), "E": (3, 2), "L": (2, 1), "M": (3, 1)}
STRATA = {
    "R": "rule: relevant",
    "S": "rule: fails only skills",
    "T": "rule: fails only title_seniority",
    "E": "rule: fails only engineering_role",
    "L": "rule: fails location (with or without skills), title conditions pass",
    "M": "rule: fails two or more conditions including engineering_role",
}
SAMPLING = {"R": 2, "other": 3}


def stratum(failed):
    failed = tuple(failed)
    if not failed:
        return "R"
    if failed == ("skills",):
        return "S"
    if failed == ("title_seniority",):
        return "T"
    if failed == ("engineering_role",):
        return "E"
    if "location" in failed and "engineering_role" not in failed and "title_seniority" not in failed:
        return "L"
    return "M"


class ReadableText(HTMLParser):
    """For the human labeling sheet only: keeps paragraph and list breaks."""

    BLOCKS = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "tr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCKS:
            self.parts.append("\n- " if tag == "li" else "\n")

    def handle_data(self, data):
        self.parts.append(data)

    def text(self):
        lines = [re.sub(r"\s+", " ", line).strip() for line in "".join(self.parts).split("\n")]
        return "\n".join(line for line in lines if line and line != "-")


def readable(content):
    parser = ReadableText()
    parser.feed(decode_entities(content))
    parser.close()
    return parser.text()


def main():
    resume = validate_resume(json.loads((ROOT / "persona/alex_morgan.json").read_text(encoding="utf-8")))
    raw = gzip.decompress((ROOT / SOURCE_RUN / "raw_response.json.gz").read_bytes())
    postings = board.parse_board(raw)
    groups = {key: [] for key in PLAN}
    for posting in postings:
        groups[stratum(rule.rule_verdict(resume, posting)["failed_conditions"])].append(posting)

    rng = random.Random(SEED)
    development, held_out, chosen = [], [], {}
    for key, (take, to_dev) in PLAN.items():
        picked = rng.sample(sorted(groups[key], key=lambda p: p.id), take)
        for i, posting in enumerate(picked):
            chosen[posting.id] = (posting, key)
            (development if i < to_dev else held_out).append(posting.id)

    dev_relevant = [i for i in development if chosen[i][1] == "R"]
    dev_other = [i for i in development if chosen[i][1] != "R"]
    sampling = rng.sample(dev_relevant, SAMPLING["R"]) + rng.sample(dev_other, SAMPLING["other"])

    order = development + held_out
    rng.shuffle(order)

    selection = {
        "seed": SEED,
        "source_run": SOURCE_RUN,
        "board_posting_count": len(postings),
        "strata_sizes_on_board": {k: len(v) for k, v in groups.items()},
        "strata": STRATA,
        "plan": {k: {"take": t, "to_development": d} for k, (t, d) in PLAN.items()},
        "development": sorted(development),
        "held_out": sorted(held_out),
        "sampling": sorted(sampling),
        "labeling_order": order,
        "stratum_by_id": {str(i): chosen[i][1] for i in order},
        "note": ("Chosen by this script before any hand label or Claude result existed. "
                 "Stratified by rule outcome, so not a random sample of the board. "
                 "stratum_by_id is not shown on the labeling sheet."),
    }
    (ROOT / "experiments").mkdir(exist_ok=True)
    (ROOT / "experiments/selection.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")

    labels = ROOT / "labels"
    labels.mkdir(exist_ok=True)
    sheet = [
        "# Labeling sheet: 20 real postings from the run-1 baseline (2026-10-28)",
        "",
        "Real postings from the Anthropic Greenhouse board, retrieved 2026-10-28T10:26:12Z.",
        "Label each one with your labeling rule (labels/LABELING-RULE.md), written before you open this sheet.",
        "Record labels in labels/hand_labels.csv. This sheet shows no rule or Claude output, and it does",
        "not say which postings are development and which are held-out.",
        "",
    ]
    for n, posting_id in enumerate(order, 1):
        posting = chosen[posting_id][0]
        sheet += [
            f"## {n}. Posting {posting.id}",
            "",
            f"- **Title:** {posting.title}",
            f"- **Location:** {posting.location_name or '(empty)'}",
            "",
            "<details><summary>Content</summary>",
            "",
            readable(posting.content),
            "",
            "</details>",
            "",
        ]
    (labels / "labeling-sheet.md").write_text("\n".join(sheet) + "\n", encoding="utf-8")

    with open(labels / "hand_labels.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["n", "posting_id", "title", "label", "failed_conditions", "labeled_at", "notes"])
        for n, posting_id in enumerate(order, 1):
            writer.writerow([n, posting_id, chosen[posting_id][0].title, "", "", "", ""])

    print(f"development: {selection['development']}")
    print(f"held_out:    {selection['held_out']}")
    print(f"sampling:    {selection['sampling']}")


if __name__ == "__main__":
    main()
