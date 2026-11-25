"""One-off rebalance of experiment/labels.csv before any Claude run (seed 7).

Run from the project folder: python3 experiment/rebalance_labels.py

Copies labels.csv to labels_v2_unbalanced.csv, then swaps 3 clearly
non-engineering rows for the only 3 distinct entry/mid-level US
"Software Engineer" postings on the board that are not already labeled:
1 into dev, 2 into heldout. New rows get blank my_label and my_note.
Every other line of labels.csv is left byte-for-byte unchanged.
Refuses to run if labels_v2_unbalanced.csv already exists.
"""

import csv
import io
import json
import random
import shutil
import sys
from pathlib import Path

EXP = Path(__file__).resolve().parent
PROJECT = EXP.parent
sys.path.insert(0, str(PROJECT))

from agent.rule import _check_location  # noqa: E402  (same US check as the agent)

RAW_PATH = PROJECT / "raw" / "klaviyo_20261031T175121.json"
LABELS_PATH = EXP / "labels.csv"
V2_PATH = EXP / "labels_v2_unbalanced.csv"
SEED = 7
SENIOR_WORDS = ["senior", "sr.", "staff", "lead", "principal", "manager"]
N_NEW = {"dev": 1, "heldout": 2}

# Clearly non-engineering rows (HR, sales, product, design, project management),
# classified by hand from their titles. In each set the lowest ids are replaced.
NON_ENGINEERING = {
    7708059003: "product",              # Senior Product Manager, Identity and Access Management
    7806009003: "project management",   # Lead Project Manager
    7984272003: "HR",                   # Head of Global Compensation
    8037134003: "HR",                   # Global Mobility and Immigration Program Lead
    7636105003: "design",               # Senior Product Designer
    7776857003: "sales",                # Account Executive Commercial, Spanish Speaker
}


def candidates(jobs, labeled_ids, labeled_titles):
    """Entry/mid-level US "Software Engineer" postings, one per title, not already labeled."""
    found = {}
    for job in sorted(jobs, key=lambda j: j["id"]):
        title = job["title"]
        lower = title.lower()
        if ("software engineer" in lower
                and not any(w in lower for w in SENIOR_WORDS)
                and _check_location((job.get("location") or {}).get("name") or "")
                and job["id"] not in labeled_ids
                and title not in labeled_titles):
            found.setdefault(title, job)
    return list(found.values())


def csv_line(values, terminator):
    buf = io.StringIO()
    csv.writer(buf, lineterminator="").writerow(values)
    return buf.getvalue() + terminator


def main():
    if V2_PATH.exists():
        sys.exit(f"{V2_PATH.name} already exists; the rebalance has been done. Nothing changed.")

    with LABELS_PATH.open(newline="") as f:
        rows = list(csv.DictReader(f))
    labeled_ids = {int(r["id"]) for r in rows}
    labeled_titles = {r["title"] for r in rows}
    jobs = json.loads(RAW_PATH.read_text())["jobs"]

    pool = candidates(jobs, labeled_ids, labeled_titles)
    needed = sum(N_NEW.values())
    if len(pool) < needed:
        sys.exit(f"only {len(pool)} candidates, need {needed}. Nothing changed.")
    picks = random.Random(SEED).sample(pool, needed)
    new_for = {"dev": picks[:N_NEW["dev"]], "heldout": picks[N_NEW["dev"]:]}

    replace = {}  # old id -> new posting
    for s, new in new_for.items():
        targets = sorted(int(r["id"]) for r in rows if r["set"] == s and int(r["id"]) in NON_ENGINEERING)
        replace.update(zip(targets[:len(new)], new))

    shutil.copyfile(LABELS_PATH, V2_PATH)

    text = LABELS_PATH.read_bytes().decode("utf-8")
    out = []
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        old_id = next(csv.reader([body]))[0]
        if old_id.isdigit() and int(old_id) in replace:
            job = replace[int(old_id)]
            s = next(r["set"] for r in rows if r["id"] == old_id)
            line = csv_line([job["id"], job["title"], job["location"]["name"],
                             job["absolute_url"], s, "", ""], line[len(body):])
        out.append(line)
    LABELS_PATH.write_bytes("".join(out).encode("utf-8"))

    print(f"Candidates ({len(pool)}): " + ", ".join(str(j["id"]) for j in pool))
    print(f"Copied labels.csv -> {V2_PATH.name}")
    for old, job in replace.items():
        s = next(r["set"] for r in rows if int(r["id"]) == old)
        print(f"  {s}: {old} ({NON_ENGINEERING[old]}) -> {job['id']} {job['title']} | {job['location']['name']}")


if __name__ == "__main__":
    main()
