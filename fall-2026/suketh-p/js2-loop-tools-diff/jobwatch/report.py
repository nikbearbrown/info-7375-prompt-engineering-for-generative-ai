"""Human-readable copies of results.json and trace.json. The JSON files are the record;
these Markdown files only restate them."""


def _cell(value):
    if value is None:
        return "—"
    return str(value).replace("|", "\\|").replace("\n", " ")


def results_md(result):
    budget, used = result["budget"], result["used"]
    lines = [
        f"# Run `{result['run_id']}`: **{result['status']}**",
        "",
        f"{result['reason']}",
        "",
        f"- Started {result['started_at']}, ended {result['ended_at']} (UTC).",
        f"- Used {used['boards']}/{budget['max_boards']} boards, {used['requests']}/{budget['max_requests']} requests, "
        f"{used['seconds']} s of {budget['max_seconds']:g} s (each request at most {budget['max_request_seconds']:g} s).",
        f"- State advanced: **{'yes' if result['state_advanced'] else 'no'}**."
        + ("" if result["state_advanced"] else " Every count below is provisional: the next finished run decides."),
        f"- Approval given: `{result['approval']['given']}`" if result["approval"]["given"] else "- Approval given: none",
    ]
    if result["approval"]["problem"]:
        lines.append(f"- Approval problem: {result['approval']['problem']}")
    lines += ["", "| Board | Role | Outcome | Jobs | Baseline | New | Reason |", "|---|---|---|---:|---|---:|---|"]
    for row in result["boards"]:
        new = len(row["new_keys"]) if row["new_keys"] is not None else None
        lines.append(f"| {row['board']} | {row['role']} | {row['outcome']} | {_cell(row['jobs'])} | "
                     f"{_cell(row['baseline'])} | {_cell(new)} | {_cell(row['reason'])} |")
    new_rows = [row for row in result["boards"] if row["new_postings"]]
    if new_rows:
        lines += ["", "## New postings and their rule records", ""]
        for row in new_rows:
            for record in row["new_postings"]:
                failed = ", ".join(record["failed_conditions"]) or "none"
                lines.append(f"- {row['board']} `{record['posting_id']}`: **{record['verdict']}** (failed: {failed})")
    lines.append("")
    return "\n".join(lines)


def trace_md(trace):
    lines = [
        f"# Trace of run `{trace['run_id']}`: **{trace['status']}**",
        "",
        "Every event the loop recorded, in order. Times are UTC; `elapsed_s` is measured by the run's clock.",
        "",
        "| # | At | Event | Board | HTTP | Elapsed s | Bytes | Outcome | Jobs | Raw file | Reason |",
        "|---:|---|---|---|---:|---:|---:|---|---:|---|---|",
    ]
    for e in trace["events"]:
        lines.append(f"| {e['seq']} | {e['at']} | {e['event']} | {_cell(e.get('board'))} | {_cell(e.get('status'))} | "
                     f"{_cell(e.get('elapsed_s'))} | {_cell(e.get('bytes'))} | {_cell(e.get('outcome'))} | "
                     f"{_cell(e.get('jobs'))} | {_cell(e.get('raw'))} | "
                     f"{_cell(e.get('reason') or e.get('detail'))} |")
    lines.append("")
    return "\n".join(lines)
