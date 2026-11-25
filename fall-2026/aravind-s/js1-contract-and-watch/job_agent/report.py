"""The run report (CONTRACT.md, Out): a counts line that is always there, then each new posting.

The rule's verdict is a record and Claude's is a judgment; they are written in separate sections
under fixed labels, and counted separately (Refuses 3). Nothing here reads résumé contact fields.
"""

from __future__ import annotations

import json
from pathlib import Path

RULE_LABEL = "Rule verdict (record)"
CLAUDE_LABEL = "Claude's judgment (model output, not verified)"


def counts(diff, verdicts: dict) -> dict:
    rule = sum(1 for v in verdicts.values() if v.get("rule", {}).get("verdict") == "relevant")
    claude = sum(1 for v in verdicts.values() if v.get("claude", {}).get("verdict") == "relevant")
    return {"new": len(diff.new), "gone": len(diff.gone), "new_relevant_rule": rule, "new_relevant_claude": claude}


def counts_line(run_id: str, postings: int, c: dict, baseline: bool) -> str:
    line = (
        f"{postings} postings in the response, {c['new']} new since the last run, {c['gone']} gone since the last run, "
        f"{c['new_relevant_rule']} new and relevant by the rule, {c['new_relevant_claude']} new and relevant in Claude's judgment."
    )
    if baseline:
        return f"Run {run_id} (baseline: {postings} postings recorded, 0 new). {line}"
    return f"Run {run_id}. {line}"


def locations(job: dict) -> str:
    names = [job.get("location") or ""] + [s.get("location") or "" for s in (job.get("secondaryLocations") or [])]
    return "; ".join(n for n in names if n) or "(none given)"


def screen_lines(diff, verdicts: dict) -> list:
    """One line per new posting (CONTRACT.md, Out); gone postings are listed in the report."""
    lines = []
    for job in diff.new:
        v = verdicts.get(job["id"], {})
        rule = v.get("rule", {}).get("verdict", "?")
        said = v.get("claude", {}).get("verdict") or "no valid judgment"
        lines.append(f"NEW {job['id']} {job['title']} [{locations(job)}] | {RULE_LABEL}: {rule} | {CLAUDE_LABEL}: {said}")
    return lines


def write(run_dir: Path, summary: dict, diff, verdicts: dict) -> None:
    data = dict(summary)
    data["new"] = [
        {
            "id": job["id"],
            "title": job["title"],
            "locations": locations(job),
            "jobUrl": job.get("jobUrl"),
            "rule": verdicts.get(job["id"], {}).get("rule"),
            "claude": verdicts.get(job["id"], {}).get("claude"),
        }
        for job in diff.new
    ]
    data["gone"] = [{"id": i, "title": t} for i, t in diff.gone]
    (Path(run_dir) / "report.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (Path(run_dir) / "report.md").write_text(_markdown(data), encoding="utf-8")


def _markdown(data: dict) -> str:
    out = [data["counts_line"], "", f"# Run {data['run_id']}", ""]  # the report starts with its counts line
    out += [
        f"- Board: {data['board_url']}",
        f"- Source: {data['source']}",
        f"- Response: response.json, {data['response_bytes']:,} bytes, SHA-256 {data['response_sha256']}",
        f"- Started (UTC): {data['started_at']}",
        f"- Résumé: {data['resume']} (fictional persona, validated)",
        f"- Contract: v{data['contract_version']}",
        f"- Code: job_agent fingerprint {data['code_sha256']} (git commit {data['git_head'] or 'not readable'};"
        " the fingerprint is what ran, even with uncommitted changes)",
        "",
        f"## New since the last run ({len(data['new'])})",
        "",
    ]
    if not data["new"]:
        out += ["None." if not data["baseline"] else "None: this is the baseline run, so every posting was recorded as seen.", ""]
    for item in data["new"]:
        out += [f"### {item['title']}", "", f"- id: `{item['id']}`", f"- Locations: {item['locations']}", f"- Link: {item['jobUrl']}", ""]
        out += [f"**{RULE_LABEL}:** {(item['rule'] or {}).get('verdict', 'missing')}", ""]
        for line in (item["rule"] or {}).get("lines", []):
            out.append(f"- {line}")
        out += ["", f"**{CLAUDE_LABEL}:** {(item['claude'] or {}).get('verdict') or 'no valid judgment'}", ""]
        for line in (item["claude"] or {}).get("lines", []):
            out.append(f"- {line}")
        out.append("")
    out += [f"## Gone since the last run ({len(data['gone'])})", ""]
    out += [f"- `{g['id']}` {g['title']}" for g in data["gone"]] or ["None."]
    out.append("")
    return "\n".join(out)
