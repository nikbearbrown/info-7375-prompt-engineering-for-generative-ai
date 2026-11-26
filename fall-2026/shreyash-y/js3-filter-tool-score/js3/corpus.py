"""Everything the agent has collected, as one list of postings the filter can read.

Sources (FILTER.md answers 1-3):
- this folder's live runs, `runs/<run_id>/` (the JS2 loop, copied unchanged), and
- JS2's three live runs (2026-11-09 and 2026-11-10). Postings from them that are not in this folder's
  latest run are kept in `data/inherited/js2-postings.json`, as the raw job objects exactly as JS2
  saved them, with the run, file and sha256 they came from.

Each posting is the JS2 view (jsagent/providers.py: title, departments, location, offices, content)
plus what JS3 needs: the employment type and workplace type the board reports, the blocks of the text
(js3/sections.py), when the agent first and last saw it, and whether it was open in the latest run.

A board that failed or came back empty contributes no postings and is reported by name with its
status, never as "0 postings" (FILTER.md wrong version 5).
"""
import hashlib
import json
import pathlib

from jsagent import providers
from js3 import sections

HERE = pathlib.Path(__file__).resolve().parent.parent


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def raw_jobs(ats, body):
    data = json.loads(body)
    return data if ats == "lever" else data["jobs"]


def enrich(ats, token, job, p):
    """JS2's posting view plus the fields JS3 reads. `p` is providers' parse of `job`."""
    p = dict(p)
    p["board"] = token
    p["ats"] = ats
    p["id"] = str(p["id"])
    if ats == "ashby":
        p["employment_type"] = job.get("employmentType")
    elif ats == "lever":
        p["employment_type"] = (job.get("categories") or {}).get("commitment")
    else:
        p["employment_type"] = None
    p.setdefault("workplace_type", None)
    p["url"] = p.pop("absolute_url", None)
    p["blocks"] = sections.blocks_for(ats, job, p["content"])
    return p


def parse_job(ats, token, job):
    body = json.dumps([job] if ats == "lever" else {"jobs": [job]}).encode()
    (p,), _ = providers.parse(ats, token, 200, body)
    return enrich(ats, token, job, p)


def read_run(run_dir, root=HERE):
    """Postings and board statuses of one saved run. Reads the raw files the summary names."""
    run_dir = pathlib.Path(run_dir)
    summary = json.loads((run_dir / "summary.json").read_text())
    postings, boards = [], {}
    for b in summary["boards"]:
        entry = {"ats": b["ats"], "status": b["status"], "error": b.get("error"), "fetched": b.get("fetched")}
        if b["status"] == "ok":
            raw_path = root / b["raw_files"][-1]
            body = raw_path.read_bytes()
            entry["raw_file"] = b["raw_files"][-1]
            entry["sha256"] = sha256(body)
            parsed, _ = providers.parse(b["ats"], b["token"], 200, body)
            jobs = raw_jobs(b["ats"], body)
            if len(jobs) != len(parsed):
                raise ValueError(f"{raw_path}: {len(jobs)} raw jobs but {len(parsed)} parsed postings")
            for job, p in zip(jobs, parsed):
                q = enrich(b["ats"], b["token"], job, p)
                q["seen_in"] = summary["run_id"]
                postings.append(q)
        boards[b["name"]] = entry
    return {"run_id": summary["run_id"], "exit": summary["exit"], "postings": postings, "boards": boards}


def inherit_js2(js2_folder, js2_run_ids, latest_keys):
    """One-off: collect JS2's postings. Returns the record written to data/inherited/js2-postings.json:
    where each JS2 posting was seen, and the raw job object of every one not in `latest_keys`."""
    js2_folder = pathlib.Path(js2_folder)
    seen, keep, sources = {}, {}, {}
    for run_id in js2_run_ids:
        run = read_run(js2_folder / "runs" / run_id, root=js2_folder)
        sources[run_id] = {name: {k: v for k, v in b.items() if k in ("status", "error", "raw_file", "sha256", "fetched")}
                           for name, b in run["boards"].items()}
        summary = json.loads((js2_folder / "runs" / run_id / "summary.json").read_text())
        for b in summary["boards"]:
            if b["status"] != "ok":
                continue
            body = (js2_folder / b["raw_files"][-1]).read_bytes()
            for job in raw_jobs(b["ats"], body):
                key = f"{b['token']}:{job['id']}"
                seen.setdefault(key, []).append(run_id)
                if key not in latest_keys:
                    keep[key] = {"ats": b["ats"], "board": b["token"], "run_id": run_id, "job": job}
    return {"note": "Postings JS2's live runs saw. 'jobs_not_in_latest_run' holds the raw job objects, unchanged, "
                    "of the ones this folder's latest run did not return (closed or removed since).",
            "js2_folder": "fall-2026/shreyash-y/js2-loop-tools-diff", "js2_commit": "177d5a8",
            "runs": sources, "seen": seen, "jobs_not_in_latest_run": keep}


def build(run_dirs, inherited=None, root=HERE):
    """The corpus: every posting any run saw, latest version first. Returns (postings, manifest)."""
    runs = [read_run(d, root=root) for d in sorted(run_dirs)]
    latest = runs[-1]
    latest_keys = {f"{p['board']}:{p['id']}" for p in latest["postings"]}
    by_key, first, last = {}, {}, {}
    inherited_seen = (inherited or {}).get("seen", {})
    for key, run_ids in inherited_seen.items():
        first[key] = min(run_ids)
        last[key] = max(run_ids)
    for run in runs:
        for p in run["postings"]:
            key = f"{p['board']}:{p['id']}"
            by_key[key] = p  # later runs replace earlier versions
            first.setdefault(key, run["run_id"])
            last[key] = run["run_id"]
    for key, item in ((inherited or {}).get("jobs_not_in_latest_run") or {}).items():
        if key not in by_key:
            by_key[key] = parse_job(item["ats"], item["board"], item["job"])
    postings = []
    for key in sorted(by_key):
        p = dict(by_key[key])
        p.pop("seen_in", None)
        p["key"] = key
        p["first_seen"] = first.get(key)
        p["last_seen"] = last.get(key)
        p["open_in_latest_run"] = key in latest_keys
        postings.append(p)
    manifest = {
        "latest_run": latest["run_id"],
        "latest_exit": latest["exit"],
        "runs_read": [r["run_id"] for r in runs] + sorted((inherited or {}).get("runs", {})),
        "boards_in_latest_run": latest["boards"],
        "postings": len(postings),
        "open_in_latest_run": sum(p["open_in_latest_run"] for p in postings),
        "by_board": {b: sum(1 for p in postings if p["board"] == b) for b in sorted({p["board"] for p in postings})},
    }
    return postings, manifest


def board_report(manifest):
    """One line per board of the latest run. A failed or empty board is named with its status and
    never reported as a board with zero postings (FILTER.md wrong version 5)."""
    lines = []
    for name, b in manifest["boards_in_latest_run"].items():
        if b["status"] == "ok":
            lines.append(f"{name}: ok, {b['fetched']} postings fetched")
        elif b["status"] == "empty":
            lines.append(f"{name}: checked, the board returned an empty list (no postings to filter)")
        else:
            lines.append(f"{name}: NOT CHECKED, the board failed ({b['error']}); its postings are unknown")
    return lines


def write(postings, manifest, out_dir):
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    body = "".join(json.dumps(p, ensure_ascii=False, sort_keys=True) + "\n" for p in postings).encode()
    (out_dir / "corpus.jsonl").write_bytes(body)
    manifest = dict(manifest, corpus_sha256=sha256(body))
    (out_dir / "corpus-manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return manifest


def load(path=HERE / "data" / "corpus.jsonl"):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
