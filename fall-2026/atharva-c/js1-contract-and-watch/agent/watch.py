"""The watch: fetch Stripe's board, save the raw response, report only postings
whose ids were not seen in any earlier run. The first run is a baseline.

Usage:
    python3 -m agent.watch --resume examples/rohan-desai.resume.example.json
    python3 -m agent.watch --resume ... --replay runs/<earlier>/raw.json   # labeled SEEDED
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent import fetch, resume, rule

ROOT = Path(__file__).resolve().parent.parent


def load_state(path):
    if not path.exists():
        return None
    return json.loads(path.read_text())


def run_once(raw, resume_data, out_dir, run_label, seeded_from=None, claude=None):
    out_dir = Path(out_dir)
    run_dir = out_dir / "runs" / run_label
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "raw.json").write_bytes(raw)

    jobs = json.loads(raw)["jobs"]
    ids = [str(j["id"]) for j in jobs]
    state_path = out_dir / "state" / "seen_ids.json"
    state = load_state(state_path)
    baseline = state is None
    seen = set() if baseline else set(state["seen_ids"])

    new_jobs = [] if baseline else [j for j in jobs if str(j["id"]) not in seen]
    verdicts = rule.judge_all(new_jobs, resume_data)
    # Second judge (a judgment, not a record): one fresh Claude call per new posting.
    claude_verdicts = [claude(j) for j in new_jobs] if claude else []

    report = {
        "run": run_label,
        "board": fetch.BOARD,
        "source": seeded_from and f"SEEDED: replay of {seeded_from}" or fetch.BOARD_URL,
        "seeded": bool(seeded_from),
        "baseline": baseline,
        "postings_in_response": len(jobs),
        "previously_seen": len(seen),
        "new_count": len(new_jobs),
        "relevant_count": sum(v["verdict"] == "relevant" for v in verdicts),
        "new_postings": verdicts,
        "claude_judgments": claude_verdicts,
    }
    (run_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))

    state_path.parent.mkdir(parents=True, exist_ok=True)
    history = [] if baseline else state["runs"]
    history.append({"run": run_label, "seeded": bool(seeded_from), "ids_in_response": len(ids),
                    "new": [v["posting_id"] for v in verdicts]})
    state_path.write_text(json.dumps({"board": fetch.BOARD, "seen_ids": sorted(seen | set(ids)),
                                      "runs": history}, indent=2))
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resume", required=True, help="fictional persona résumé JSON")
    ap.add_argument("--replay", help="use a saved raw.json instead of fetching (labeled SEEDED)")
    ap.add_argument("--out", default=str(ROOT), help="folder holding runs/ and state/")
    ap.add_argument("--claude", action="store_true", help="also ask Claude about each new posting (a judgment)")
    args = ap.parse_args(argv)

    try:
        resume_data = resume.load(args.resume)
    except resume.ResumeError as e:
        sys.exit(f"résumé rejected: {e}")

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    if args.replay:
        raw, label = Path(args.replay).read_bytes(), f"{stamp}-seeded"
    else:
        raw, label = fetch.get(), stamp

    claude = None
    if args.claude:
        from agent import claude_judge
        log = Path(args.out) / "runs" / label / "claude_calls.jsonl"
        claude = lambda j: claude_judge.judge(j, resume_data, ROOT / "prompts" / "baseline.txt", log, tag=label)
    rep = run_once(raw, resume_data, args.out, label, seeded_from=args.replay, claude=claude)
    kind = "BASELINE" if rep["baseline"] else ("SEEDED run" if rep["seeded"] else "run")
    print(f"{kind} {rep['run']}: {rep['postings_in_response']} postings in response, "
          f"{rep['new_count']} new, {rep['relevant_count']} relevant by the rule (a record).")
    cj = {c["posting_id"]: c for c in rep["claude_judgments"]}
    for v in rep["new_postings"]:
        print(f"- [{v['verdict']}] {v['posting_id']} {v['posting_title']}\n    rule (record): {v['justification']}")
        c = cj.get(v["posting_id"])
        if c:
            shown = c["verdict"] if c["valid"] else f"REJECTED by validator: {c['rejected_because']}"
            print(f"    Claude (a model judgment, not a fact): {shown}" + (f" — {c['reason']}" if c["valid"] else ""))
    print(f"saved: runs/{rep['run']}/raw.json, runs/{rep['run']}/report.json, state/seen_ids.json")


if __name__ == "__main__":
    main()
