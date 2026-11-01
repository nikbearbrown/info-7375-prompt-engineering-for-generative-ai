"""The watch: save the raw response first, then report only job IDs not seen before (CONTRACT.md, Out)."""
import hashlib
import json
import os
from dataclasses import dataclass

from .config import BOARD, ROOT


class NotAJobList(Exception):
    """The response is not a Greenhouse job list, so nothing is recorded as seen."""


@dataclass
class RunResult:
    at: str
    raw_path: object
    raw_sha256: str
    total: int
    baseline: bool
    seeded: bool
    new_jobs: list


def parse_jobs(raw):
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as e:
        raise NotAJobList(f"response is not JSON ({e})") from None
    jobs = data.get("jobs") if isinstance(data, dict) else None
    if not isinstance(jobs, list) or not all(isinstance(j, dict) and isinstance(j.get("id"), int) for j in jobs):
        raise NotAJobList("response is not a Greenhouse job list")
    return jobs


def stamp(now):
    return now.strftime("%Y%m%dT%H%M%SZ")


def save_raw(raw, raw_dir, now, seeded, board=BOARD):
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{board}-{stamp(now)}{'-SEEDED' if seeded else ''}.json"
    path.write_bytes(raw)
    return path


def load_state(path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def run_watch(raw, *, raw_dir, state_path, now, seeded=False):
    raw_path = save_raw(raw, raw_dir, now, seeded)  # evidence first, before anything can fail
    jobs = parse_jobs(raw)  # a bad response stops here, so the state file is not touched
    state = load_state(state_path)
    baseline = state is None
    seen = set() if baseline else set(state["seen_ids"])
    new_jobs, reported = [], set()
    if not baseline:
        for job in jobs:
            if job["id"] not in seen and job["id"] not in reported:
                new_jobs.append(job)
                reported.add(job["id"])
    at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    runs = [] if baseline else state["runs"]
    runs.append({"at": at, "raw": rel(raw_path), "jobs": len(jobs), "new": len(new_jobs),
                 "baseline": baseline, "seeded": seeded})
    write_state(state_path, {"board": BOARD, "seen_ids": sorted(seen | {j["id"] for j in jobs}), "runs": runs})
    return RunResult(at, raw_path, hashlib.sha256(raw).hexdigest(), len(jobs), baseline, seeded, new_jobs)


def rel(path):
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def format_report(result, source, judgments=None):
    label = " (SEEDED)" if result.seeded else ""
    lines = [
        f"# Watch run {result.at}{label}",
        "",
        f"- Board: {BOARD}",
        f"- Source: {source}",
        f"- Raw response: `{rel(result.raw_path)}` (sha256 `{result.raw_sha256[:16]}…`)",
        f"- Jobs in the response: {result.total}",
    ]
    if result.baseline:
        lines.append("- Baseline run: every job ID recorded as seen, 0 reported as new.")
    else:
        lines.append(f"- New since the last run: {len(result.new_jobs)}")
    if result.new_jobs:
        lines += ["", "| Job ID | Title | Company | Location |", "|---|---|---|---|"]
        for job in result.new_jobs:
            location = (job.get("location") or {}).get("name", "")
            lines.append(f"| {job['id']} | {job.get('title', '')} | {job.get('company_name', '')} | {location} |")
    for job in result.new_jobs if judgments else []:
        entry = judgments[job["id"]]
        lines += ["", f"### {job['id']}: {job.get('title', '')}", "",
                  f"- **Rule (record, recomputable):** {entry['rule'].reason}"]
        record = entry["claude"]
        if record is None:
            lines.append("- **Claude (judgment):** not run (`--no-claude`).")
        elif record.get("valid"):
            lines.append(f"- **Claude (judgment, not a fact):** {record['parsed']['verdict']}. {record['parsed']['reason']}"
                         f" (reply saved: `{rel(entry['claude_file'])}`)")
        else:
            lines.append(f"- **Claude (judgment):** invalid reply, rejected by the validator: {record.get('error')}"
                         f" (reply saved: `{rel(entry['claude_file'])}`)")
    return "\n".join(lines) + "\n"
