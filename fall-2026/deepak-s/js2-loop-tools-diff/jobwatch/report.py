"""report.json and report.txt: CONTRACT.md Out (report.json) and Refuses 3."""


def agreement(record, judgment):
    if judgment["status"] != "accepted":
        return "n/a"
    return "agree" if judgment["verdict"] == record["verdict"] else "disagree"


def build_report(*, run_id, label, board, source, from_file, from_file_sha256, generated_at, parsed,
                 previously_seen, records, judge):
    return {
        "run_id": run_id,
        "label": label,
        "board": board,
        "source": source,
        "from_file": from_file,
        "from_file_sha256": from_file_sha256,
        "generated_at": generated_at,
        "counts": {
            "postings": parsed.total,
            "unique": len(parsed.kept),
            "previously_seen": previously_seen,
            "new": len(records),
            "agree": sum(r["agreement"] == "agree" for r in records),
            "disagree": sum(r["agreement"] == "disagree" for r in records),
        },
        "duplicates_dropped": parsed.duplicates_dropped,
        "skipped_bad_id": parsed.skipped_bad_id,
        "skipped_bad_title": parsed.skipped_bad_title,
        "judge": judge,
        "records": records,
    }


def _cites(citations):
    return "; ".join(f'{c["source"]} {c["path"]} = "{c["value"]}"' for c in citations or [])


def _judgment_line(j):
    if j["status"] == "not_run":
        return f"  JUDGMENT: not run ({j['reason']})"
    head = f"  JUDGMENT ({j['model']}, {(j['called_at'] or '')[:10]})"
    if j["status"] == "accepted":
        return f"{head}: {j['verdict']}; cites {_cites(j['citations'])}\n    reason: {j['reason']}"
    return f"{head}: {j['status']} ({j['reason']})"


def render_text(report):
    c = report["counts"]
    judge = report["judge"]
    if report["source"] == "file":
        source = f"source file {report['from_file']} (sha256 {report['from_file_sha256']})"
    else:
        source = "source network"
    backend = f"backend {judge['backend']}, " if "backend" in judge else ""
    lines = [
        f"JOBWATCH  run {report['run_id']}  label {report['label']}  board {report['board']}",
        source,
        f"generated_at {report['generated_at']}",
        f"counts: postings {c['postings']}, unique {c['unique']}, previously_seen {c['previously_seen']}, "
        f"new {c['new']}, agree {c['agree']}, disagree {c['disagree']}",
        f"duplicates_dropped {report['duplicates_dropped']}, skipped_bad_id {report['skipped_bad_id']}, "
        f"skipped_bad_title {report['skipped_bad_title']}",
        f"judge: {judge['status']} ({backend}model {judge['model']}, prompt sha256 {judge['prompt_sha256']})",
        "RECORD is the written rule's verdict. JUDGMENT is a model's output, not a fact; "
        "it is never merged into the RECORD.",
        "",
    ]
    if report["label"] == "baseline":
        lines.append("Baseline run: no posting is reported as new. Every id above is now remembered.")
    elif not report["records"]:
        lines.append("No new postings since the last run.")
    for r in report["records"]:
        lines += [
            f"[{r['posting_id']}] {r['title']} | {r['location'] if r['location'] is not None else 'no location'}",
            f"  {r['absolute_url']}",
            f"  RECORD (rule): {r['record']['verdict']}; cites {_cites(r['record']['citations'])}",
            _judgment_line(r["judgment"]),
        ]
        if r["agreement"] == "disagree":
            lines.append("  DISAGREE")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"
