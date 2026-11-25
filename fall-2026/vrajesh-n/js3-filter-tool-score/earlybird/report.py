"""Markdown summary of one run. Failed boards say "error" with the reason, never a made-up number."""
from datetime import date

from .gate import Budget


def markdown(result, source, max_rows=40):
    r = result
    lines = [f"# Early Bird run: {r['label']}", "",
             f"- Run on: {date.today().isoformat()} · Board day: {r['day']} · Source: {source}",
             f"- **Exit: `{r['exit']}`**" + (f" ({r['reason']})" if r["reason"] else ""),
             f"- Budget used: {Budget.describe(r['budget'])}",
             "- `finished` means the loop reached the end of the list, not that the counts are right; "
             "run `python -m earlybird check` for the independent recount.", "",
             "| Board | Status | Postings | New | Relevant (rule) | Records citing a missing field | Raw response |",
             "|---|---|---|---|---|---|---|"]
    for b in r["boards"]:
        if b["status"] == "ok":
            new = "baseline (0)" if b["baseline"] else str(b["new"])
            lines.append(f"| {b['key']} | ok | {b['postings']} | {new} | {b['relevant']} | "
                         f"{b['invalid_records']} | `{b['raw_path']}` |")
        else:
            raw = f"`{b['raw_path']}`" if b.get("raw_path") else "-"
            lines.append(f"| {b['key']} | **{b['status']}**: {b['error']} | - | - | - | - | {raw} |")
    for key in r["not_attempted"]:
        lines.append(f"| {key} | not attempted | - | - | - | - | - |")
    total = sum(len(b.get("rows") or []) for b in r["boards"])
    shown = 0
    for b in r["boards"]:
        rows = b.get("rows") or []
        if not rows or shown >= max_rows:
            continue
        lines += ["", f"## New on {b['key']} ({len(rows)})", ""]
        for row in rows[: max_rows - shown]:
            rec = row["record"]
            flag = f" · **record invalid:** {'; '.join(row['record_errors'])}" if row["record_errors"] else ""
            check = f" {rec['failed_check']}" if rec["failed_check"] else ""
            lines.append(f"- **{rec['title']}** ({row['location']}) - {rec['verdict']}{check}: "
                         f"{rec['justification']}{flag}")
            shown += 1
    if total > shown:
        lines += ["", f"... {total - shown} more new postings in `reports/{r['label']}.json`."]
    return "\n".join(lines) + "\n"
