"""Freeze the 20 postings and the 10/10 split for the prompt experiment, before any label or Claude answer.

Selection (changed 2026-10-30, before any label or Claude answer existed; the first freeze was commit 5b130b8):
  1. From each saved raw response (the Pinterest baseline first, then Figma and Twilio), keep jobs whose
     title has "Engineer" plus a role word (rule 1), whose location has United States, USA or US (rule 4),
     and whose title has no experience word (rule 3). These are the jobs a reader could not settle from the
     title alone.
  2. Take every Pinterest job that qualifies, sorted by job ID, then the Figma and Twilio jobs together,
     sorted by job ID, until there are 20.
  3. Walk that list in order and alternate dev, held-out, dev, held-out.
No verdict is computed or saved here: the hand labels come first.
"""
import csv
import hashlib
import json
from datetime import datetime, timezone

from . import rule
from .config import ROOT

EXPERIMENT = ROOT / "experiment"
EXPERIMENT_2 = ROOT / "experiment-2"
SET_2 = """Selection for experiment 2 (written 2026-10-31, before any label or Claude answer for these postings):
  1. From each saved raw response, keep the same candidates as experiment 1 (is_candidate), drop the
     20 postings of experiment 1, and keep only the lowest job ID of postings with the same title.
  2. Order the boards by how many candidates they have, most first (ties by company name), and take up to
     4 candidates from each board, lowest job ID first, until there are 20.
  3. Walk that list in order and alternate dev, held-out.
No verdict is computed or saved here: the hand labels come first."""
LABEL_COLUMNS = ["id", "split", "company", "title", "location", "role (Y/N)", "skills found", "experience (Y/N)",
                 "location (Y/N)", "label (Relevant / Not Relevant)", "labelled on", "notes"]


def is_candidate(job):
    title, location = job.get("title", ""), (job.get("location") or {}).get("name", "")
    return bool(rule.find_words(title, ("Engineer",)) and rule.find_words(title, rule.ROLE_WORDS)
                and rule.find_words(location, rule.US_WORDS)
                and not rule.find_words(title, rule.EXPERIENCE_WORDS))


def select(job_lists, n=20):
    """job_lists: one list of jobs per saved response, the watched board first."""
    first = sorted((j for j in job_lists[0] if is_candidate(j)), key=lambda j: j["id"])
    others = sorted((j for jobs in job_lists[1:] for j in jobs if is_candidate(j)), key=lambda j: j["id"])
    chosen = (first + others)[:n]
    return [(j, "dev" if i % 2 == 0 else "held-out") for i, j in enumerate(chosen)]


def select_set2(job_lists, exclude, per_board=4, n=20):
    """Experiment 2: up to per_board candidates from each board, the boards with the most candidates first."""
    boards = []
    for jobs in job_lists:
        seen, board = set(), []
        for j in sorted((j for j in jobs if is_candidate(j) and j["id"] not in exclude), key=lambda j: j["id"]):
            if j["title"] not in seen:
                seen.add(j["title"])
                board.append(j)
        boards.append(board)
    boards = sorted((b for b in boards if b), key=lambda b: (-len(b), b[0].get("company_name", "")))
    chosen = [j for b in boards for j in b[:per_board]][:n]
    return [(j, "dev" if i % 2 == 0 else "held-out") for i, j in enumerate(chosen)]


def freeze(raw_paths, out=EXPERIMENT, now=None, pick=select, selection=__doc__):
    raws = [p.read_bytes() for p in raw_paths]
    picked = pick([json.loads(raw)["jobs"] for raw in raws])
    now = now or datetime.now(timezone.utc).replace(microsecond=0)
    postings_dir = out / "postings"
    postings_dir.mkdir(parents=True, exist_ok=True)
    for old in postings_dir.glob("*.txt"):
        old.unlink()  # the earlier set stays in git history (commit 5b130b8)
    rows = []
    for job, split in picked:
        location = (job.get("location") or {}).get("name", "")
        text = rule.description_text(job)
        (postings_dir / f"{job['id']}.txt").write_text(
            f"Job ID: {job['id']}\nSplit: {split}\nCompany: {job.get('company_name', '')}\nTitle: {job['title']}\n"
            f"Location: {location}\nURL: {job.get('absolute_url', '')}\n\n"
            f"Description (plain text from the saved raw response):\n\n{text}\n", encoding="utf-8")
        rows.append({"id": job["id"], "split": split, "company": job.get("company_name", ""), "title": job["title"],
                     "location": location, "url": job.get("absolute_url", ""),
                     "first_published": job.get("first_published"),
                     "description_sha256": hashlib.sha256(text.encode()).hexdigest()})
    frozen = {"frozen_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
              "sources": [{"file": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(raw).hexdigest()}
                          for p, raw in zip(raw_paths, raws)],
              "selection": selection.strip(), "postings": rows}
    (out / "postings.json").write_text(json.dumps(frozen, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with open(out / "labels.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(LABEL_COLUMNS)
        for r in rows:
            writer.writerow([r["id"], r["split"], r["company"], r["title"], r["location"]]
                            + [""] * (len(LABEL_COLUMNS) - 5))
    return frozen
