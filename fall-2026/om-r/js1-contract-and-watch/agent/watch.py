"""The watch: fetch one board, save the raw response as evidence, report only
postings whose id is not in the state file, then update the state file.

The first run (no state file) is a BASELINE: it records every current id as
seen and reports none as new (assignment, Step 2).

    python3 -m agent.watch --board gitlab --resume resume.json
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent import fetch as fetch_mod
from agent import rule

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_RESUME_FIELDS = {
    "name": str,
    "target_roles": list,
    "key_skills": list,
    "years_of_experience": (int, float),
    "location_preference": (dict, str),
    "visa_sponsorship_needed": bool,
}


def validate_resume(resume):
    """Reject anything that isn't the fictional persona shape."""
    errors = []
    for field, typ in REQUIRED_RESUME_FIELDS.items():
        if field not in resume:
            errors.append(f"missing {field}")
        elif not isinstance(resume[field], typ):
            errors.append(f"{field} has wrong type")
    if not resume.get("fictional"):
        errors.append('"fictional": true is required (only the fictional persona is ever shown)')
    if "email" in resume and not str(resume["email"]).endswith("@example.com"):
        errors.append("email must be an @example.com address")
    if "phone" in resume and "555" not in str(resume["phone"]):
        errors.append("phone must be a 555 number")
    have = {s.lower() for s in resume.get("key_skills", [])}
    missing = [s for s in rule.RULE_SKILLS if s.lower() not in have]
    if missing:
        errors.append(f"key_skills missing rule skills {missing}")
    if errors:
        raise ValueError("invalid resume: " + "; ".join(errors))
    return resume


def _write_json_atomic(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2) + "\n")
    os.replace(tmp, path)


def run(board, resume, state_path, evidence_dir, fetch=fetch_mod.fetch, now=None, from_file=None):
    """With from_file, read a saved response from disk instead of fetching
    (no network); that file is itself the evidence, so nothing is re-saved."""
    now = now or datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")

    if from_file:
        evidence_file = Path(from_file)
        raw = evidence_file.read_bytes()
        url = f"file:{evidence_file.name}"
    else:
        url = fetch_mod.board_jobs_url(board)
        raw = fetch(url)
        evidence_dir.mkdir(parents=True, exist_ok=True)
        evidence_file = evidence_dir / f"{board}_jobs_{stamp}.json"
        evidence_file.write_bytes(raw)  # exactly as received
    seeded = "SEEDED" in evidence_file.name

    jobs = json.loads(raw)["jobs"]
    current_ids = [j["id"] for j in jobs]

    baseline = not state_path.exists()
    if baseline:
        state = {"board": board, "seen_ids": [], "runs": []}
        new_jobs = []
    else:
        state = json.loads(state_path.read_text())
        if state.get("board") != board:
            raise ValueError(f"state file {state_path} is for board {state.get('board')!r}")
        seen = set(state["seen_ids"])
        new_jobs = [j for j in jobs if j["id"] not in seen]

    records = rule.evaluate(new_jobs, resume)

    state["seen_ids"] = sorted(set(state["seen_ids"]) | set(current_ids))
    state["runs"].append({
        "at": now.isoformat(timespec="seconds"),
        "url": url,
        "evidence_file": str(evidence_file.relative_to(ROOT)) if evidence_file.is_relative_to(ROOT) else str(evidence_file),
        "baseline": baseline,
        "seeded": seeded,
        "postings_in_response": len(jobs),
        "new_ids": [j["id"] for j in new_jobs],
    })
    state_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json_atomic(state_path, state)

    return {
        "board": board,
        "at": now.isoformat(timespec="seconds"),
        "baseline": baseline,
        "seeded": seeded,
        "source": url,
        "evidence_file": str(evidence_file),
        "postings_in_response": len(jobs),
        "seen_ids_after_run": len(state["seen_ids"]),
        "new": records,
    }


def print_report(report, out=sys.stdout):
    kind = "BASELINE (first run: every current id recorded as seen, none reported as new)" if report["baseline"] else "WATCH RUN"
    if report["seeded"]:
        kind = "SEEDED " + kind + " - constructed input, NOT live board data"
    print(f"[{report['at']}] board={report['board']}  {kind}", file=out)
    print(f"  source: {report['source']}", file=out)
    print(f"  evidence: {report['evidence_file']}", file=out)
    print(f"  postings in response: {report['postings_in_response']}  "
          f"seen ids after run: {report['seen_ids_after_run']}  new: {len(report['new'])}", file=out)
    for r in report["new"]:
        print(f"\n  - id {r['id']}: {r['title']}\n    {r['absolute_url']}", file=out)
        print(f"    RECORD verdict: {r['verdict']}\n    RECORD justification: {r['justification']}", file=out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", default="gitlab")
    ap.add_argument("--resume", default=str(ROOT / "resume.json"))
    ap.add_argument("--state", default=None, help="default: state/<board>_seen.json")
    ap.add_argument("--evidence-dir", default=str(ROOT / "evidence"))
    ap.add_argument("--from-file", default=None,
                    help="read a saved response instead of fetching (requires --state, "
                         "so a replay never touches the live state file)")
    args = ap.parse_args(argv)
    if args.from_file and not args.state:
        ap.error("--from-file requires an explicit --state")

    resume = validate_resume(json.loads(Path(args.resume).read_text()))
    state_path = Path(args.state) if args.state else ROOT / "state" / f"{args.board}_seen.json"
    report = run(args.board, resume, state_path, Path(args.evidence_dir), from_file=args.from_file)
    print_report(report)


if __name__ == "__main__":
    main()
