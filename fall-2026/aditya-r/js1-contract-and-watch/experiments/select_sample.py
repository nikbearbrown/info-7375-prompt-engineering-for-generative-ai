"""Build the diagnostic sample and the labeling sheets (see experiments/SAMPLE_PROCEDURE.md).

Prints only counts and ids, never held-out content.
"""
import csv
import hashlib
import html
import itertools
import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.board import load_jobs_file  # noqa: E402
from agent.resume import load_resume  # noqa: E402
from agent.rules import SKILL_FIELDS, _TextExtractor, evaluate, normalize  # noqa: E402

SEED = 7375
SNAPSHOT = ROOT / "evidence/snapshots/databricks_20261030T203900Z.json"
RESUME = ROOT / "resume/priya-nair.resume.example.json"
OUT = ROOT / "experiments/sample"
LABELING = ROOT / "labeling"
TARGETS = {"R": (3, 2), "N": (3, 4), "O": (4, 4)}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def group_of(record):
    if record["verdict"] == "relevant":
        return "R"
    if record["checks"]["A_role_phrase"]["pass"]:
        return "N"
    return "O"


def readable(content):
    """Description for human reading: block tags become line breaks."""
    markup = html.unescape(content or "")
    markup = re.sub(r"(?i)<\s*(br|/p|/li|/h[1-6]|/div|/ul|/ol)\b[^>]*>", "\n", markup)
    markup = re.sub(r"(?i)<\s*li\b[^>]*>", "\n- ", markup)
    p = _TextExtractor()
    p.feed(markup)
    p.close()
    lines = [" ".join(line.split()) for line in "".join(p.parts).split("\n")]
    return "\n".join(line for line in lines if line)


def main():
    resume = load_resume(RESUME)
    jobs = load_jobs_file(SNAPSHOT)
    rng = random.Random(SEED)

    clusters = defaultdict(lambda: defaultdict(list))  # group -> title key -> [jobs]
    for job in jobs:
        clusters[group_of(evaluate(job, resume))][normalize(job.get("title"))].append(job)

    dev, held, groups, adjustments = [], [], {}, []

    # Step 4: all R postings, cluster-preserving 3/2 split.
    r_keys = sorted(clusters["R"])
    options = []
    for mask in itertools.product((0, 1), repeat=len(r_keys)):
        n_dev = sum(len(clusters["R"][k]) for k, m in zip(r_keys, mask) if m == 0)
        options.append((abs(n_dev - TARGETS["R"][0]), mask))
    best = min(d for d, _ in options)
    if best:
        adjustments.append(f"R: no exact 3/2 cluster split; used split {best} posting(s) off target")
    mask = rng.choice(sorted(m for d, m in options if d == best))
    used = set()
    for key, m in zip(r_keys, mask):
        used.add(key)
        for job in sorted(clusters["R"][key], key=lambda j: j["id"]):
            (dev if m == 0 else held).append(job)
            groups[job["id"]] = "R"

    # Steps 5-6: one posting per distinct cluster.
    for g in ("N", "O"):
        n_dev, n_held = TARGETS[g]
        keys = sorted(k for k in clusters[g] if k not in used)
        picked = rng.sample(keys, n_dev + n_held)
        chosen = []
        for key in picked:
            used.add(key)
            job = rng.choice(sorted(clusters[g][key], key=lambda j: j["id"]))
            chosen.append(job)
            groups[job["id"]] = g
        rng.shuffle(chosen)
        dev.extend(chosen[:n_dev])
        held.extend(chosen[n_dev:])

    # Step 7: hide group order.
    rng.shuffle(dev)
    rng.shuffle(held)

    sampling_rng = random.Random(SEED + 1)
    sampling = []
    for g, k in (("R", 2), ("N", 2), ("O", 1)):
        pool = sorted(j["id"] for j in dev if groups[j["id"]] == g)
        sampling.extend(sampling_rng.sample(pool, min(k, len(pool))))

    OUT.mkdir(parents=True, exist_ok=True)
    LABELING.mkdir(parents=True, exist_ok=True)
    for name, split in (("dev", dev), ("heldout", held)):
        (OUT / f"{name}_postings.json").write_text(json.dumps(split, ensure_ascii=False, indent=1))
        write_sheet(name, split, resume)

    manifest = {
        "procedure": "experiments/SAMPLE_PROCEDURE.md",
        "seed": SEED,
        "snapshot": str(SNAPSHOT.relative_to(ROOT)),
        "snapshot_sha256": sha256(SNAPSHOT),
        "resume_sha256": sha256(RESUME),
        "pool_size": len(jobs),
        "group_pool_sizes": {g: sum(len(v) for v in clusters[g].values()) for g in "RNO"},
        "dev_ids": [j["id"] for j in dev],
        "heldout_ids": [j["id"] for j in held],
        "groups": {str(k): v for k, v in groups.items()},
        "sampling_ids": sampling,
        "adjustments": adjustments,
        "file_sha256": {
            p: sha256(ROOT / p)
            for p in (
                "experiments/sample/dev_postings.json",
                "experiments/sample/heldout_postings.json",
                "labeling/dev_sheet.md",
                "labeling/heldout_sheet.md",
            )
        },
        "note": "Groups are derived from the deterministic RECORD. Do not open this file while labeling.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print("pool group sizes:", manifest["group_pool_sizes"])
    for name, split in (("dev", dev), ("heldout", held)):
        counts = {g: sum(groups[j["id"]] == g for j in split) for g in "RNO"}
        print(name, len(split), "postings, group counts", counts)
    print("adjustments:", adjustments or "none")
    print("sampling ids (dev):", sampling)


def write_sheet(name, split, resume):
    skills = {path: resume["skills"][path.split(".", 1)[1]] for path in SKILL_FIELDS}
    lines = [
        f"# Labeling sheet — {'DEVELOPMENT' if name == 'dev' else 'HELD-OUT'} set ({len(split)} real postings)",
        "",
        "Source: Databricks Greenhouse board snapshot 2026-10-30T20:39:00Z (unchanged posting text).",
        "",
        "Apply **your CONTRACT.md §4 rule**, without consulting any program output. Write `relevant` or",
        f"`not_relevant` in the `label` column of `labeling/{name}_labels.csv`, adding a note if you like.",
        "",
        "Rule reminders, copied from CONTRACT.md:",
        "- **A.** The title contains one of: software engineer, data engineer, machine learning engineer, ai engineer, analytics engineer (whole words; hyphens count as spaces).",
        "- **B.** The title contains none of: senior, sr, staff, principal, lead, manager, director, head, vp, chief, distinguished, architect (whole words).",
        "- **C.** At least 2 distinct target skills (python, sql, spark, databricks, langgraph) appear in the title or description **and** in one entry of the résumé skill arrays below. Whole words only: `PostgreSQL`, `NoSQL` and `PySpark` don't count.",
        "- Normalization keeps only ASCII letters and digits, so a title with none (e.g. written entirely in Japanese) becomes empty and counts as missing, giving `not_relevant`.",
        "",
        "Priya Nair's permitted résumé skill arrays (fictional persona):",
        "",
    ]
    lines += [f"- `{path}`: {', '.join(v)}" for path, v in skills.items()]
    rows = []
    for i, job in enumerate(split, 1):
        loc = (job.get("location") or {}).get("name", "")
        depts = ", ".join(d.get("name", "") for d in job.get("departments") or [])
        lines += [
            "", "---", "",
            f"## Posting {i} of {len(split)} — id {job['id']}",
            "",
            f"- **title:** {job.get('title', '')}",
            f"- **location:** {loc}",
            f"- **departments:** {depts}",
            f"- **url:** {job.get('absolute_url', '')}",
            "",
            "**description:**",
            "",
            "```text",
            readable(job.get("content")),
            "```",
        ]
        rows.append({"posting_id": job["id"], "title": job.get("title", ""), "label": "", "notes": ""})
    (LABELING / f"{name}_sheet.md").write_text("\n".join(lines) + "\n")
    with open(LABELING / f"{name}_labels.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["posting_id", "title", "label", "notes"])
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
