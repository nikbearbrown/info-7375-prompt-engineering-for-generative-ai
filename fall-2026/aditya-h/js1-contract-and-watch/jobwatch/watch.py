"""One watch run: fetch (or read a seeded response), diff by id, judge new postings, write outputs."""
import datetime as dt
import json
import pathlib

from . import fetch, report, resume, rule, state

CONTRACT_VERSION = "v1"


def run(board, resume_path, state_path, runs_dir, fetcher=fetch.http_get, now=None,
        claude_judge=None, seeded_raw=None, seeded_from=None):
    now = (now or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    runs_dir = pathlib.Path(runs_dir)
    seeded = seeded_raw is not None

    # Refusals come before any network access.
    resume_data = resume.load_checked(json.loads(pathlib.Path(resume_path).read_text()))
    prev = state.load_state(state_path)
    url = fetch.board_url(board)

    if seeded:
        raw = seeded_raw
    else:
        fetch.check_url(url)
        raw = fetcher(url)

    raw_dir = runs_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{board}-{stamp}{'-SEEDED' if seeded else ''}.json"
    raw_path.write_bytes(raw)
    jobs = fetch.parse_jobs(raw)  # raises after the evidence is saved; state untouched

    rec = {
        "board": board,
        "source_url": url,
        "run_time": now.isoformat(),
        "contract_version": CONTRACT_VERSION,
        "rule_id": rule.RULE_ID,
        "seeded": seeded,
        "seeded_from": seeded_from,
        "baseline": prev is None,
        "suspect_empty": False,
        "raw_response_path": str(raw_path),
        "state_path": str(state_path),
        "verdicts": [],
    }
    new = []
    if prev is not None and prev["seen_ids"] and not jobs:
        rec["suspect_empty"] = True  # Refuses 4: do not overwrite seen_ids from an empty board
    elif prev is None:
        state.save_state(state_path, board, {j["id"] for j in jobs}, now.isoformat())
    else:
        new = state.new_postings(jobs, prev["seen_ids"])
        for p in new:
            entry = {"posting_id": p["id"], "title": p.get("title"), "url": p.get("absolute_url"),
                     "rule": rule.judge(p, resume_data)}
            entry["claude"] = claude_judge(p, resume_data) if claude_judge else {"status": "not_run"}
            c = entry["claude"]
            entry["disagree"] = c.get("status") == "valid" and c["verdict"] != entry["rule"]["verdict"]
            rec["verdicts"].append(entry)
        state.save_state(state_path, board, set(prev["seen_ids"]) | {j["id"] for j in jobs}, now.isoformat())

    v = rec["verdicts"]
    rule_rel = sum(1 for e in v if e["rule"]["verdict"] == "relevant")
    rec["counts"] = {
        "fetched": len(jobs),
        "new": len(new),
        "relevant_rule": rule_rel,
        "skipped": len(new) - rule_rel,
        "relevant_claude": sum(1 for e in v if e["claude"].get("verdict") == "relevant"
                               and e["claude"].get("status") == "valid"),
        "invalid_claude": sum(1 for e in v if e["claude"].get("status") == "invalid"),
        "disagreements": sum(1 for e in v if e["disagree"]),
    }

    for sub in ("records", "reports"):
        (runs_dir / sub).mkdir(parents=True, exist_ok=True)
    suffix = "-SEEDED" if seeded else ""
    rec["record_path"] = str(runs_dir / "records" / f"run-{stamp}{suffix}.json")
    rec["report_path"] = str(runs_dir / "reports" / f"report-{stamp}{suffix}.md")
    pathlib.Path(rec["record_path"]).write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    pathlib.Path(rec["report_path"]).write_text(report.markdown(rec))
    return rec
