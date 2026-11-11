"""Shared helpers for the sampling report and the prompt experiment."""
import csv
import hashlib
import json
import math
import pathlib
import subprocess
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXP = ROOT / "experiment"
SNAPSHOT = ROOT / "evidence" / "klaviyo_2026-10-31_preimplementation_live.json"
RESUME = ROOT / "resumes" / "aarav-patel.json"
LABELS = EXP / "labels.csv"
SPLIT = EXP / "split.json"
VERDICTS = ("relevant", "not_relevant")
LABEL_COLUMNS = [
    "posting_id", "title", "location", "source", "label_date", "label",
    "decisive_phrases", "resume_fields", "required_vs_preferred", "uncertainty",
]


class ExperimentError(Exception):
    """A guard refused the step; nothing was called or written."""


def now_utc():
    return datetime.now(timezone.utc)


def stamp(moment):
    return moment.strftime("%Y-%m-%dT%H-%M-%SZ")


def load_postings(snapshot=SNAPSHOT):
    return {job["id"]: job for job in json.loads(pathlib.Path(snapshot).read_text())["jobs"]}


def load_labels(path=LABELS, require_complete=True):
    """Return {posting_id: row}. Refuses blank or misspelled labels when require_complete."""
    path = pathlib.Path(path)
    if not path.exists():
        raise ExperimentError(f"{path} does not exist; create it with experiment.make_label_sheet")
    with path.open(newline="") as f:
        rows = {int(r["posting_id"]): r for r in csv.DictReader(f)}
    if require_complete:
        bad = [pid for pid, r in rows.items() if r["label"].strip() not in VERDICTS]
        if bad:
            raise ExperimentError(f"labels missing or not in {VERDICTS} for ids: {bad}")
    return rows


def load_split(path=SPLIT):
    path = pathlib.Path(path)
    if not path.exists():
        raise ExperimentError(f"{path} does not exist; run experiment.split after labeling")
    return json.loads(path.read_text())


def prompt_fingerprint(prompt_path):
    """sha256 of the prompt file, the last commit that touched it, and whether it has uncommitted edits."""
    prompt_path = pathlib.Path(prompt_path).resolve()
    rel = prompt_path.relative_to(ROOT)

    def git(*args):
        proc = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
        return proc.stdout.strip() if proc.returncode == 0 else None

    return {
        "path": str(rel),
        "sha256": hashlib.sha256(prompt_path.read_bytes()).hexdigest(),
        "last_commit": git("log", "-1", "--format=%H", "--", str(rel)),
        "uncommitted_changes": bool(git("status", "--porcelain", "--", str(rel))),
    }


def wilson(k, n, z=1.96):
    """95% Wilson score interval for k successes out of n."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centre - half), min(1.0, centre + half))


def write_json(path, data):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def new_run_dir(parent, name):
    """A fresh directory per invocation, so earlier results are never overwritten."""
    base = pathlib.Path(parent) / name
    path, n = base, 1
    while path.exists():
        path = base.with_name(f"{base.name}-{n}")
        n += 1
    path.mkdir(parents=True)
    return path
