"""The watch: fetch one board, save the raw response, report only new posting ids, judge each twice.

    python -m agent.watch --board databricks --resume resume/priya-nair.resume.example.json \
        --state state/seen.json --runs-dir evidence/runs --label live

A missing state file makes this run the baseline (all ids recorded, none judged, zero new).
`--from-file` replays a saved response instead of fetching (label such runs as seeded).
"""
import argparse
import datetime as dt
import hashlib
import json
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import judge as judge_mod
from .board import BoardError, RefusedError, board_url, decode_body, fetch, parse_jobs
from .resume import ResumeError, load_resume
from .rules import evaluate
from .state import StateError, load_state, new_and_retry_ids, save_state
from .validate import validate_judgment

MAX_ATTEMPTS = 3
EXIT_OK, EXIT_INPUT, EXIT_INCOMPLETE = 0, 2, 3


def _utc():
    return dt.datetime.now(dt.timezone.utc)


def default_judge(prompt_version="v1"):
    system, prompt_sha = judge_mod.load_prompt(prompt_version)

    def judge(posting, resume):
        rec = judge_mod.call_claude(system, judge_mod.build_user_message(posting, resume))
        rec["prompt_version"], rec["prompt_sha256"] = prompt_version, prompt_sha
        return rec

    return judge


def acquire(args, run_dir):
    """Save the raw response bytes unchanged next to provenance metadata; return the bytes."""
    existing = [p for p in run_dir.glob("raw_response.*") if not p.name.endswith(".meta.json")]
    if existing:  # --resume-run: reuse the saved response, never refetch
        return existing[0].read_bytes()
    if args.from_file:
        src = Path(args.from_file)
        body = src.read_bytes()
        suffix = ".json.gz" if body[:2] == b"\x1f\x8b" else ".json"
        meta = {
            "kind": "SEEDED — replay of a saved earlier response, not a live fetch by this run",
            "source_file": str(src),
            "source_sha256": hashlib.sha256(body).hexdigest(),
            "seeded_note": args.seeded_note,
        }
    else:
        url = board_url(args.board)
        body, info = fetch(url)
        suffix = ".json"
        meta = {"kind": "LIVE fetch", "url": url, **info}
    raw_path = run_dir / f"raw_response{suffix}"
    raw_path.write_bytes(body)
    meta.update({"saved_as": raw_path.name, "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body),
                 "acquired_at_utc": _utc().isoformat(timespec="seconds")})
    (run_dir / "raw_response.meta.json").write_text(json.dumps(meta, indent=1))
    return body


def judge_one(posting, resume, judge_fn, jdir):
    """Up to MAX_ATTEMPTS fresh calls; every attempt is saved. Returns the summary dict."""
    pid = posting["id"]
    final = jdir / f"{pid}.json"
    if final.exists():
        prior = json.loads(final.read_text())
        if prior.get("valid"):
            return prior
    attempts = []
    for n in range(1, MAX_ATTEMPTS + 1):
        rec = judge_fn(posting, resume)
        ok, errors, parsed = (False, ["transport: no response text"], None)
        if rec.get("response_text") is not None:
            ok, errors, parsed = validate_judgment(rec["response_text"], posting, resume)
        rec.update({"posting_id_requested": pid, "attempt": n, "valid": ok, "validation_errors": errors})
        path = jdir / f"{pid}.attempt{n}.json"
        path.write_text(json.dumps(rec, indent=1, ensure_ascii=False))
        attempts.append(path.name)
        if ok:
            summary = {"posting_id": pid, "valid": True, "judgment": parsed, "attempt_files": attempts,
                       "models_used": rec.get("models_used"), "session_id": rec.get("session_id"),
                       "prompt_version": rec.get("prompt_version"), "prompt_sha256": rec.get("prompt_sha256")}
            final.write_text(json.dumps(summary, indent=1, ensure_ascii=False))
            return summary
    summary = {"posting_id": pid, "valid": False, "judgment": None, "attempt_files": attempts,
               "last_errors": errors}
    final.write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    return summary


def run(args, judge_fn=None):
    started = _utc()
    try:
        resume = load_resume(args.resume)
        state = load_state(args.state)
        if state is not None and state["board"] != args.board:
            raise StateError(f"state belongs to board {state['board']!r}, not {args.board!r}")
    except (ResumeError, StateError) as e:
        print(f"ERROR: {e}. State unchanged.", file=sys.stderr)
        return EXIT_INPUT

    if args.resume_run:
        run_dir = Path(args.resume_run)
    else:
        run_dir = Path(args.runs_dir) / f"{started.strftime('%Y%m%dT%H%M%SZ')}_{args.label}"
    run_dir.mkdir(parents=True, exist_ok=True)

    try:
        body = acquire(args, run_dir)
        jobs = parse_jobs(decode_body(body))
    except (RefusedError, BoardError) as e:
        print(f"ERROR: {e}. State unchanged.", file=sys.stderr)
        (run_dir / "error.txt").write_text(str(e) + "\n")
        return EXIT_INPUT

    by_id = {j["id"]: j for j in jobs}
    run_entry = {"run_dir": run_dir.name, "started_at_utc": started.isoformat(timespec="seconds"),
                 "label": args.label, "seeded": bool(args.from_file), "postings_in_response": len(jobs)}

    if state is None:
        state = {"board": args.board, "ids": {str(i): "baseline" for i in by_id}, "runs": []}
        run_entry.update({"kind": "baseline", "new": 0, "baseline_ids_recorded": len(by_id)})
        state["runs"].append(run_entry)
        save_state(args.state, state)
        shutil.copy(args.state, run_dir / "state_after_run.json")
        write_report(run_dir, run_entry, [])
        print(f"BASELINE: recorded {len(by_id)} posting ids; 0 reported as new. Report: {run_dir}/report.md")
        return EXIT_OK

    new, retry = new_and_retry_ids(state, list(by_id))
    targets = new + retry
    for pid in targets:  # pending until both verdicts exist (R5)
        state["ids"][str(pid)] = "pending"
    save_state(args.state, state)

    jdir = run_dir / "judgments"
    jdir.mkdir(exist_ok=True)
    judge_fn = judge_fn or default_judge(args.prompt_version)
    records = {pid: evaluate(by_id[pid], resume) for pid in targets}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        summaries = dict(zip(targets, pool.map(lambda p: judge_one(by_id[p], resume, judge_fn, jdir), targets)))

    rows = []
    for pid in targets:  # joined by id, never by position
        s = summaries[pid]
        if s["valid"]:
            state["ids"][str(pid)] = "completed"
        rows.append({"posting": by_id[pid], "record": records[pid], "judgment": s, "retry": pid in retry})
    pending = [r["posting"]["id"] for r in rows if not r["judgment"]["valid"]]
    run_entry.update({"kind": "watch", "new": len(new), "retried_pending": len(retry),
                      "completed": len(rows) - len(pending), "pending": len(pending),
                      "finished_at_utc": _utc().isoformat(timespec="seconds")})
    state["runs"].append(run_entry)
    save_state(args.state, state)
    shutil.copy(args.state, run_dir / "state_after_run.json")
    write_report(run_dir, run_entry, rows)
    status = "COMPLETE" if not pending else f"INCOMPLETE ({len(pending)} pending, will retry next run)"
    print(f"{status}: {len(new)} new posting(s), {len(retry)} retried. Report: {run_dir}/report.md")
    return EXIT_OK if not pending else EXIT_INCOMPLETE


def write_report(run_dir, entry, rows):
    out = []
    for r in rows:
        p, rec, s = r["posting"], r["record"], r["judgment"]
        j = s.get("judgment") or {}
        out.append({
            "posting_id": p["id"], "title": p.get("title"), "url": p.get("absolute_url"),
            "location": (p.get("location") or {}).get("name"),
            "RECORD": {"verdict": rec["verdict"], "checks": rec["checks"], "missing": rec["missing"],
                       "explanation": rec["explanation"]},
            "JUDGMENT": {"label": "Claude's judgment under a prompt contract — an opinion, validated for "
                                  "format and cited evidence, NOT for correctness",
                         "valid": s["valid"], "verdict": j.get("verdict"), "explanation": j.get("explanation"),
                         "evidence": j, "attempt_files": s.get("attempt_files"),
                         "models_used": s.get("models_used"), "session_id": s.get("session_id"),
                         "prompt_version": s.get("prompt_version"), "errors": s.get("last_errors")},
        })
    (run_dir / "report.json").write_text(json.dumps({"run": entry, "new_postings": out}, indent=1, ensure_ascii=False))

    md = [f"# Watch run `{run_dir.name}`", ""]
    meta_path = run_dir / "raw_response.meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        md += [f"- **Response:** {meta['kind']} — `{meta['saved_as']}` (sha256 `{meta['sha256'][:16]}…`)"]
    md += [f"- **{k}:** {v}" for k, v in entry.items()]
    if not rows:
        md += ["", "No new postings reported." + (" (Baseline: ids recorded, nothing judged.)" if entry.get("kind") == "baseline" else "")]
    else:
        agree = sum(1 for o in out if o["JUDGMENT"]["valid"] and o["JUDGMENT"]["verdict"] == o["RECORD"]["verdict"])
        valid = sum(1 for o in out if o["JUDGMENT"]["valid"])
        md += ["", f"RECORD = the deterministic rule (recomputable). JUDGMENT = Claude's opinion (validated format/evidence; may be wrong).",
               f"Valid judgments: {valid}/{len(out)}. RECORD–JUDGMENT agreement among valid: {agree}/{valid}.", "",
               "| id | title | location | RECORD | JUDGMENT (opinion) |", "|---|---|---|---|---|"]
        for o in out:
            jv = o["JUDGMENT"]["verdict"] if o["JUDGMENT"]["valid"] else "INVALID (pending)"
            md.append(f"| {o['posting_id']} | {(o['title'] or '').replace('|', '/')} | {(o['location'] or '').replace('|', '/')} | {o['RECORD']['verdict']} | {jv} |")
        md += ["", "## Explanations", ""]
        for o in out:
            md += [f"### {o['posting_id']} — {o['title']}", "",
                   f"- RECORD: {o['RECORD']['explanation']}",
                   f"- JUDGMENT (Claude, opinion): {o['JUDGMENT']['explanation'] or o['JUDGMENT']['errors']}", ""]
    (run_dir / "report.md").write_text("\n".join(md) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", required=True)
    ap.add_argument("--resume", required=True, help="fictional persona résumé JSON")
    ap.add_argument("--state", required=True)
    ap.add_argument("--runs-dir", default="evidence/runs")
    ap.add_argument("--label", default="run")
    ap.add_argument("--from-file", help="replay a saved response (a SEEDED run)")
    ap.add_argument("--seeded-note", default="")
    ap.add_argument("--resume-run", help="continue an interrupted run directory")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--prompt-version", default="v1")
    return run(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
