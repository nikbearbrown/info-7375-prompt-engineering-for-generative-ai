"""The watch: fetch one board, save the raw response, report only new postings.

    python3 -m agent.watch --board databricks --resume persona/priya-nair.resume.json

A run from a saved response instead of the live board must say so:

    python3 -m agent.watch ... --from-file evidence/raw/X.json.gz --seeded
"""

import argparse
import datetime
import gzip
import hashlib
import json
import os

from agent import fetch, persona, rule, state


def now_stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H%M%SZ")


def read_saved(path):
    with open(path, "rb") as f:
        data = f.read()
    return gzip.decompress(data) if path.endswith(".gz") else data


def save_raw(raw, board, stamp, out_dir):
    """Save the exact response bytes, gzipped. Returns (path, sha256)."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{board}-{stamp}.json.gz")
    with open(path, "wb") as f:
        # mtime=0 keeps the .gz byte-identical for identical responses
        f.write(gzip.compress(raw, mtime=0))
    return path, hashlib.sha256(raw).hexdigest()


def render_markdown(report):
    r = report
    lines = [
        f"# Run {r['run']['stamp']} — board `{r['run']['board']}`",
        "",
        f"- **Kind:** {r['run']['kind']}"
        + (f" (source: `{r['run']['source']}`)" if r['run']['kind'] != "live"
           else ""),
        f"- **Raw response:** `{r['run']['raw_path']}` "
        f"(sha256 `{r['run']['raw_sha256'][:16]}…`)",
        f"- **Postings on board:** {r['run']['posting_count']}",
        f"- **New since last run:** {len(r['new'])}"
        + (" — baseline run, nothing is new by definition"
           if r['run']['baseline'] else ""),
        "",
    ]
    if r["new"]:
        lines += ["| id | title | location | rule verdict (record) | "
                  "failed checks |", "|---|---|---|---|---|"]
        for v in r["new"]:
            failed = [c["check"] for c in v["justification"] if not c["passed"]]
            lines.append(f"| {v['posting_id']} | {v['title']} | "
                         f"{v['location']} | {v['verdict']} | "
                         f"{', '.join(failed) or '—'} |")
        lines += ["", "Full justifications (every check, field and match) "
                  "are in the matching `.json` report."]
    return "\n".join(lines) + "\n"


def run(board, resume_path, state_path, raw_dir, report_dir,
        from_file=None, seeded=False, stamp=None, get=fetch.get):
    if from_file and not seeded:
        raise SystemExit("--from-file needs --seeded: a run from a saved "
                         "response must be labeled as seeded")
    resume = persona.load(resume_path)
    stamp = stamp or now_stamp()

    if from_file:
        raw, kind, source = read_saved(from_file), "seeded", from_file
    else:
        url = fetch.board_url(board)
        raw, kind, source = get(url), "live", url
    raw_path, sha = save_raw(raw, board, stamp, raw_dir)

    postings = json.loads(raw)["jobs"]
    by_id = {p["id"]: p for p in postings}
    previous = state.load(state_path)
    if previous is not None and previous["board"] != board:
        raise SystemExit(f"{state_path} belongs to board "
                         f"{previous['board']!r}, not {board!r}")
    fresh = state.new_ids(previous, by_id)
    verdicts = rule.judge_all([by_id[i] for i in fresh], resume)

    run_record = {"stamp": stamp, "board": board, "kind": kind,
                  "source": source, "raw_path": raw_path, "raw_sha256": sha,
                  "posting_count": len(postings),
                  "baseline": previous is None, "new_ids": fresh}
    report = {"run": run_record, "new": [verdicts[i] for i in fresh]}

    os.makedirs(report_dir, exist_ok=True)
    base = os.path.join(report_dir, f"run-{board}-{stamp}")
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write(render_markdown(report))
    state.save(state_path, state.updated(previous, board, by_id, run_record))
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--board", default="databricks")
    ap.add_argument("--resume", default="persona/priya-nair.resume.json")
    ap.add_argument("--state", help="default: state/<board>-seen_ids.json")
    ap.add_argument("--raw-dir", default="evidence/raw")
    ap.add_argument("--report-dir", default="reports")
    ap.add_argument("--from-file", help="use a saved response, not the board")
    ap.add_argument("--seeded", action="store_true",
                    help="required with --from-file; labels the run seeded")
    a = ap.parse_args(argv)
    state_path = a.state or f"state/{a.board}-seen_ids.json"
    report = run(a.board, a.resume, state_path, a.raw_dir, a.report_dir,
                 from_file=a.from_file, seeded=a.seeded)
    print(render_markdown(report))


if __name__ == "__main__":
    main()
