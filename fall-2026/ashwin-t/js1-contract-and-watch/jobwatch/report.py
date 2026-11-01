"""The readable report.md for one run. report.json holds the same facts for machines."""
from __future__ import annotations


def _source_lines(run: dict) -> list:
    s = run["source"]
    if s.get("network"):
        return [f"- **Fetched live:** `{s['url']}` at {s['fetched_at']} (server date: {s.get('server_date')})",
                f"- **Raw response SHA-256:** `{s['sha256']}`"]
    lines = [f"- **Replayed from a saved file, no network:** `{s['fixture']}`",
             f"- **That response was actually collected:** {s['collected_at']}",
             f"- **SHA-256:** `{s['sha256']}`"]
    if run["mode"] == "SEEDED REPLAY":
        lines.append("- **SEEDED REPLAY:** the replayed file or the starting state was modified on purpose; "
                     "it is not a fresh live observation.")
    return lines


def _ai_block(ai: dict) -> list:
    if ai["status"] == "NOT REQUESTED":
        return ["**AI JUDGMENT:** not requested for this run (`--judge none`)."]
    head = f"**AI JUDGMENT** (Claude, model `{ai.get('model')}`, asked {ai.get('called_at')}, prompt `{ai['prompt']}`)"
    if ai["status"] != "VALID":
        return [f"{head}: **{ai['status']}**. The rule record above stands.", ""] + \
               [f"- {e}" for e in ai.get("errors", [])]
    lines = [f"{head}: **{ai['verdict']}**. This is a model's opinion, not a verified fact.", "",
             f"> {ai['reason']}", ""]
    lines += [f'- `resume.{e["resume_field"]}` ↔ `posting.{e["posting_field"]}`: "{e["posting_quote"]}"'
              for e in ai["evidence"]]
    return lines


def render_markdown(report: dict) -> str:
    run, results = report["run"], report["results"]
    out = [f"# Job watch: {run['board']}, {run['run_timestamp']}", "",
           f"**Mode: {run['mode']}**", ""]
    out += _source_lines(run)
    out += ["", "| Postings observed | Previously seen | New | RELEVANT by rule | AI valid | AI failed | Disagreements |",
            "|---:|---:|---:|---:|---:|---:|---:|",
            f"| {run['postings_observed']} | {run['previously_seen']} | {run['new_ids']} | {run['rule_relevant']} | "
            f"{run['ai_valid']} | {run['ai_validation_failed'] + run['ai_call_failed']} | {run['disagreements']} |", ""]
    if run["baseline"]:
        out += ["**Baseline run.** Every observed id was recorded as seen; none is reported as new.", ""]
        return "\n".join(out)
    if not results:
        out += [f"No new posting ids since the previous run ({run['previous_run']}).", ""]
        return "\n".join(out)

    out += ["## New postings", "", "| id | title | RULE RECORD | AI JUDGMENT | disagree |", "|---|---|---|---|:-:|"]
    for r in results:
        ai = r["ai_judgment"]
        out.append(f"| {r['posting_id']} | {r['title']} | {r['rule_record']['verdict']} | "
                   f"{ai['verdict'] or ai['status']} | {'yes' if r['disagreement'] else ''} |")
    for r in results:
        rec = r["rule_record"]
        out += ["", f"## {r['title']} ({r['posting_id']})", "",
                f"{r['location']} · offices: {', '.join(r['offices']) or 'none'} · {r['url']}", "",
                f"**RULE RECORD: {rec['verdict']}**", "",
                "| title | seniority | location | skills |", "|:-:|:-:|:-:|:-:|",
                "| " + " | ".join("PASS" if rec["checks"][c] else "FAIL"
                                 for c in ("title", "seniority", "location", "skills")) + " |", ""]
        out += [f"- `{line}`" for line in rec["justification"]]
        out += [""] + _ai_block(r["ai_judgment"])
    return "\n".join(out) + "\n"
