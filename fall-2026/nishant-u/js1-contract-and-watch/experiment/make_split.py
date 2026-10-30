"""Choose 20 postings from the baseline response, split them 10 dev / 10 held-out, and build a
blank labeling kit. Run once, from this folder:

    python3 experiment/make_split.py

It refuses to run again once heldout_ids.json exists, so the sealed split cannot be redrawn.
It writes no rule or Claude verdicts.
"""
import csv
import hashlib
import html
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "runs" / "2026-10-29-1" / "raw.json"
RAW_SHA256 = "3c10b536e3805bb5a4fca46800ac5caf4c521fa84c9beec30a8ab0beb995c2b7"
OUT = ROOT / "experiment"
KIT = OUT / "labeling"
SEED = 20261029
PER_GROUP = 10
# Only used to balance the sample: about half the chosen titles look like data roles.
DATA_TITLE = re.compile(r"(?<!\w)(data|analytics|analyst|scientist|machine learning|ML)(?!\w)", re.I)


def readable_text(content):
    """HTML removed, keeping paragraph and list breaks so the file is readable."""
    text = html.unescape(content or "")
    text = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h[1-6]|ul|ol|tr)>", "\n", text)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    lines = (re.sub(r"[ \t\xa0]+", " ", line).strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


def write_ids(path, ids):
    data = (json.dumps(sorted(ids)) + "\n").encode("utf-8")
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def main():
    if (OUT / "heldout_ids.json").exists():
        sys.exit("refused: experiment/heldout_ids.json already exists; the split is sealed")
    body = RAW.read_bytes()
    if hashlib.sha256(body).hexdigest() != RAW_SHA256:
        sys.exit("refused: raw.json does not match the baseline sha256")
    jobs = sorted(json.loads(body.decode("utf-8"))["jobs"], key=lambda j: j["id"])

    rng = random.Random(SEED)
    looks_data = [j for j in jobs if DATA_TITLE.search(j["title"])]
    others = [j for j in jobs if not DATA_TITLE.search(j["title"])]
    dev, heldout = [], []
    for group in (looks_data, others):
        chosen = rng.sample(group, PER_GROUP)
        rng.shuffle(chosen)
        dev += chosen[:PER_GROUP // 2]
        heldout += chosen[PER_GROUP // 2:]

    OUT.mkdir(exist_ok=True)
    KIT.mkdir(exist_ok=True)
    dev_sha = write_ids(OUT / "dev_ids.json", [j["id"] for j in dev])
    heldout_sha = write_ids(OUT / "heldout_ids.json", [j["id"] for j in heldout])

    rows = sorted([(j, "dev") for j in dev] + [(j, "heldout") for j in heldout], key=lambda r: r[0]["id"])
    with open(KIT / "labels.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["posting_id", "set", "title", "location", "my_label", "my_failed_check", "my_notes"])
        for job, split in rows:
            writer.writerow([job["id"], split, job["title"], job["location"]["name"], "", "", ""])
    for job, _ in rows:
        (KIT / f"{job['id']}.txt").write_text(
            f"Posting id: {job['id']}\nTitle: {job['title']}\nLocation: {job['location']['name']}\n"
            f"\n--- Content (HTML removed) ---\n{readable_text(job.get('content'))}\n",
            encoding="utf-8")

    print(json.dumps({"seed": SEED, "pool": len(jobs), "looks_data_pool": len(looks_data),
                      "other_pool": len(others), "dev": len(dev), "heldout": len(heldout),
                      "dev_ids_sha256": dev_sha, "heldout_ids_sha256": heldout_sha}, indent=2))


if __name__ == "__main__":
    main()
