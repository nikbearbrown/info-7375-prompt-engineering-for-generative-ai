"""The watch: fetch (or read a saved response), save the raw bytes first, remember ids per
board, report only ids never seen before, and judge each new posting with the rule."""
import hashlib
import json
import pathlib

from jsagent import fetch, persona, posting, rule


def empty_state():
    return {"version": 1, "boards": {}}


def load_state(path):
    path = pathlib.Path(path)
    return json.loads(path.read_text()) if path.exists() else empty_state()


def save_state(state, path):
    pathlib.Path(path).write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def process(board_token, payload, state, resume, run_at, source, raw_file=None, claude=None):
    """payload is the raw response bytes. Mutates state; returns the run report."""
    data = json.loads(payload)
    jobs = data["jobs"]
    ids = [j["id"] for j in jobs]
    if len(ids) != len(set(ids)):
        raise ValueError("response repeats a posting id; refusing to guess which copy is real")
    state.setdefault("version", 1)
    boards = state.setdefault("boards", {})
    baseline = board_token not in boards
    board = boards.setdefault(board_token, {"seen_ids": [], "last_ids": [], "runs": []})
    seen = set(board["seen_ids"])
    removed = sorted(set(board["last_ids"]) - set(ids))
    new_records = []
    if not baseline:
        view = persona.public_view(resume)
        for job in jobs:
            if job["id"] in seen:
                continue
            p = posting.normalize(job, board_token)
            rec = rule.judge(p, view)
            rec["is_new"] = True
            rec["location"] = p["location"]
            rec["absolute_url"] = p["absolute_url"]
            if claude:
                rec["claude"] = claude(p, view)
            new_records.append(rec)
    board["seen_ids"] = sorted(seen | set(ids))
    board["last_ids"] = sorted(ids)
    report = {
        "board_token": board_token,
        "run_at": run_at,
        "source": source,
        "raw_file": raw_file,
        "raw_sha256": hashlib.sha256(payload).hexdigest(),
        "fetched": len(ids),
        "baseline": baseline,
        "seen_before_this_run": len(seen),
        "new_count": len(new_records),
        "new": new_records,
        "removed_since_last_run": removed,
    }
    board["runs"].append({k: report[k] for k in ("run_at", "source", "raw_file", "raw_sha256",
                                                 "fetched", "baseline", "new_count")}
                         | {"new_ids": [r["posting_id"] for r in new_records]})
    return report


def markdown(report):
    out = [f"# Run report: {report['board_token']} at {report['run_at']}", "",
           f"- Source: {report['source']}",
           f"- Raw response: `{report['raw_file']}` (sha256 `{report['raw_sha256'][:16]}…`)",
           f"- Postings fetched: {report['fetched']}; ids seen before this run: {report['seen_before_this_run']}",
           f"- Baseline run: {'yes, so nothing is reported as new' if report['baseline'] else 'no'}",
           f"- New postings: {report['new_count']}",
           f"- Ids gone since the last run: {len(report['removed_since_last_run'])}", ""]
    for r in report["new"]:
        out += [f"## {r['posting_id']} · {r['title']} · {r['location']}", "",
                f"**Rule verdict (record, recomputable): {r['verdict']}**"
                + (f" (failed conditions {r['failed_conditions']})" if r["failed_conditions"] else ""),
                "", "```text", r["justification"], "```", ""]
        c = r.get("claude")
        if c:
            if c.get("valid"):
                out += [f"**Claude verdict (a model's judgment, not a fact; {c['model']}, {c['called_at']}): "
                        f"{c['parsed']['verdict']}** (failed conditions {c['parsed']['failed_conditions']})",
                        "", "> " + c["parsed"]["justification"], ""]
            else:
                out += [f"**Claude output rejected by the validator** ({c.get('model')}, {c.get('called_at')}): "
                        + "; ".join(c["errors"]), ""]
    return "\n".join(out) + "\n"


def run(board_token, resume_path, runs_dir, run_at, from_raw=None, seeded_label=None, claude=None):
    resume = persona.load(resume_path)
    runs_dir = pathlib.Path(runs_dir)
    (runs_dir / "raw").mkdir(parents=True, exist_ok=True)
    stamp = run_at.replace(":", "").replace("-", "")
    if from_raw:
        payload = pathlib.Path(from_raw).read_bytes()
        raw_file = str(from_raw)
        source = f"SEEDED: saved response {from_raw}" + (f" ({seeded_label})" if seeded_label else "")
    else:
        url = fetch.board_url(board_token)
        payload = fetch.get(url)
        raw_path = runs_dir / "raw" / f"{board_token}-{stamp}.json"
        raw_path.write_bytes(payload)  # evidence first, before anything parses it
        raw_file = str(raw_path)
        source = f"LIVE: GET {url}"
    state_path = runs_dir / "state.json"
    state = load_state(state_path)
    report = process(board_token, payload, state, resume, run_at, source, raw_file, claude)
    save_state(state, state_path)
    (runs_dir / f"report-{board_token}-{stamp}.json").write_text(json.dumps(report, indent=2) + "\n")
    (runs_dir / f"report-{board_token}-{stamp}.md").write_text(markdown(report))
    return report
