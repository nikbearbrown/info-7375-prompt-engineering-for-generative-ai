"""The loop's report (GATE.md, Exits; CONTRACT.md, Out): the exit first, then the counts, then each board.

The rule's verdict is a record and Claude's is a judgment: they stay in separate sections under
the same fixed labels as layer 1, and are counted separately. Nothing here reads résumé contact fields.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import CONTRACT_VERSION, gate, providers
from .report import CLAUDE_LABEL, RULE_LABEL, locations

WAITING = "waiting for Claude (budget)"


def summary(context, boards, repeats, over, verdicts, status, reasons, requests_used, claude_used, seconds) -> dict:
    budgets = context["budgets"]
    entries = [_board(b, verdicts) for b in boards] + [_over(b) for b in over]
    read = [b for b in boards if b.status == "read"]
    with_diff = [b for b in boards if b.diff is not None]
    new = [(b, p) for b in with_diff for p in b.diff.new]
    counts = {
        "boards_listed": len(boards) + len(over),
        "boards_read": len(read),
        "boards_unverified": sum(1 for b in boards if b.status == "unverified"),
        "boards_not_visited": sum(1 for b in boards if b.status == "not visited") + len(over),
        "repeats_skipped": len(repeats),
        "postings": sum(len(b.postings) for b in read),
        "new": len(new),
        "gone": sum(len(b.diff.gone) for b in with_diff),
        "new_relevant_rule": sum(1 for b, p in new if _rule(verdicts, b, p) == "relevant"),
        "new_relevant_claude": sum(1 for b, p in new if _claude(verdicts, b, p) == "relevant"),
        "judged_after_waiting": sum(len(_judged_now(b, verdicts)) for b in read),
        "waiting_for_claude": sum(len(b.still_waiting) for b in boards),
    }
    data = {
        "run_id": context["run_id"],
        "started_at": context["started_at"],
        "source": context["source"],
        "exit": status,
        "exit_code": gate.EXIT_CODES[status],
        "reasons": reasons,
        "gate_version": gate.GATE_VERSION,
        "contract_version": CONTRACT_VERSION,
        "budgets": budgets.as_dict(),
        "used": {"boards": len(boards) - counts["boards_not_visited"] + len(over), "requests": requests_used,
                 "claude_calls": claude_used, "seconds": seconds},
        "approval": context["approve"] or None,
        "boards": entries,
        "repeats_skipped": [b.key for b in repeats],
        "counts": counts,
    }
    data["exit_line"] = exit_line(data)
    data["counts_line"] = counts_line(counts)
    return data


def exit_line(data: dict) -> str:
    because = " ".join(r.rstrip(".") + "." for r in data["reasons"]) or "Every board on the list was read."
    return f"Exit: {data['exit']} (code {data['exit_code']}). {because}"


def counts_line(c: dict) -> str:
    return (f"{c['boards_listed']} boards: {c['boards_read']} read, {c['boards_unverified']} unverified, "
            f"{c['boards_not_visited']} not visited. {c['postings']} postings in the answers read, {c['new']} new "
            f"since the last run, {c['gone']} gone since the last run, {c['new_relevant_rule']} new and relevant by "
            f"the rule, {c['new_relevant_claude']} new and relevant in Claude's judgment, "
            f"{c['judged_after_waiting']} judged by Claude after waiting, {c['waiting_for_claude']} waiting for Claude.")


def screen_lines(data: dict) -> list:
    lines = [data["exit_line"], data["counts_line"]]
    for board in data["boards"]:
        lines.append(f"BOARD {board['key']}: {board['status']}"
                     + (f" ({board['reason']})" if board["reason"] else "")
                     + (f", {board['postings']} postings, {len(board['new'])} new, {len(board['gone'])} gone"
                        if board["postings"] is not None else ""))
        for item in board["new"]:
            lines.append(f"NEW {board['key']} {item['id']} {item['title']} [{item['locations']}] | "
                         f"{RULE_LABEL}: {item['rule_verdict']} | {CLAUDE_LABEL}: {item['claude_verdict']}")
        for item in board["judged_after_waiting"]:
            lines.append(f"WAITED {board['key']} {item['id']} {item['title']} [{item['locations']}] | "
                         f"{RULE_LABEL}: {item['rule_verdict']} | {CLAUDE_LABEL}: {item['claude_verdict']}")
    return lines


def write(files, run_dir: Path, data: dict) -> None:
    files.check_write(Path(run_dir) / "report.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    files.check_write(Path(run_dir) / "report.md").write_text(_markdown(data), encoding="utf-8")


def _board(b, verdicts) -> dict:
    diff = b.diff
    return {
        "key": b.key, "system": b.system, "name": b.name, "company": b.company, "url": b.url,
        "deliberate_failure": b.deliberate_failure,
        "status": b.status, "reason": b.reason,
        "needs_you": ("check the board name, or try again later" if b.status == "unverified" else None),
        "attempts": b.attempts,
        "postings": len(b.postings) if b.status == "read" else None,
        "baseline": diff.baseline if diff else None,
        "new": [_posting(b, p, verdicts) for p in diff.new] if diff else [],
        "gone": [{"id": i, "title": t} for i, t in diff.gone] if diff else [],
        "judged_after_waiting": [_posting(b, p, verdicts) for p in _judged_now(b, verdicts)],
        "waiting_gone": list(b.waiting_gone),
        "still_waiting": list(b.still_waiting),
        "mapped_from": providers.MAPPED_FROM[b.system],
        "state": ("updated after this report (the trace records the write)" if b.status == "read"
                  else "kept exactly as it was"),
    }


def _judged_now(b, verdicts) -> list:
    """Postings that waited from an earlier run and got Claude's call in this one (not every one still waiting)."""
    return [p for p in b.waiting_found if "claude" in verdicts.get((b.key, p["id"]), {})]


def _over(b) -> dict:
    return {"key": b.key, "system": b.system, "name": b.name, "company": b.company, "url": b.url,
            "deliberate_failure": b.deliberate_failure, "status": "not visited",
            "reason": "over the boards budget", "needs_you": None, "attempts": [], "postings": None,
            "baseline": None, "new": [], "gone": [], "judged_after_waiting": [], "waiting_gone": [],
            "still_waiting": [], "mapped_from": providers.MAPPED_FROM[b.system], "state": "kept exactly as it was"}


def _posting(b, p, verdicts) -> dict:
    v = verdicts.get((b.key, p["id"]), {})
    claude = v.get("claude")
    return {
        "id": p["id"], "title": p["title"], "locations": locations(p), "jobUrl": p.get("jobUrl"),
        "rule_verdict": (v.get("rule") or {}).get("verdict", "missing"),
        "claude_verdict": (claude.get("verdict") or "no valid judgment") if claude else WAITING,
        "rule": v.get("rule"), "claude": claude,
    }


def _rule(verdicts, b, p):
    return (verdicts.get((b.key, p["id"]), {}).get("rule") or {}).get("verdict")


def _claude(verdicts, b, p):
    return (verdicts.get((b.key, p["id"]), {}).get("claude") or {}).get("verdict")


def _markdown(data: dict) -> str:
    used, budgets = data["used"], data["budgets"]
    out = [data["exit_line"], "", data["counts_line"], "", f"# Run {data['run_id']}", ""]
    out += [
        f"- Source: {data['source']}",
        f"- Started (UTC): {data['started_at']}",
        f"- Budgets used: boards {used['boards']}/{budgets['boards']}, requests {used['requests']}/{budgets['requests']}, "
        f"Claude calls {used['claude_calls']}/{budgets['claude_calls']}, seconds {used['seconds']}/{budgets['seconds']}",
        f"- Gate v{data['gate_version']}, contract v{data['contract_version']}; the code fingerprint and git commit are "
        "in the trace's first line",
        f"- Approval given on the command line: {data['approval'] or 'none'}",
    ]
    if data["repeats_skipped"]:
        out.append(f"- Listed twice and visited once: {', '.join(data['repeats_skipped'])}")
    out += ["", "## Boards", "", "| Board | Status | Postings | New | Gone |", "|---|---|---:|---:|---:|"]
    for b in data["boards"]:
        shown = "not read" if b["postings"] is None else b["postings"]
        out.append(f"| {b['key']}{' (fails on purpose)' if b['deliberate_failure'] else ''} | {b['status']} | "
                   f"{shown} | {len(b['new'])} | {len(b['gone'])} |")
    for b in data["boards"]:
        out += ["", f"## {b['company'] or b['name']} ({b['system']}/{b['name']})", "", f"- URL: {b['url']}",
                f"- Status: {b['status']}" + (f": {b['reason']}" if b["reason"] else "")]
        if b["deliberate_failure"]:
            out.append("- This board is on the list to fail on purpose (GATE.md, Boards).")
        if b["needs_you"]:
            out.append(f"- **Needs you:** {b['needs_you']}.")
        for a in b["attempts"]:
            got = (f"HTTP {a['status']}, {a['bytes']:,} bytes, SHA-256 {a['sha256']}, "
                   f"saved as boards/{b['key']}/{a['file']}" if "status" in a else f"no answer: {a['no_answer']}")
            out.append(f"- Attempt {a['attempt']}{' (retry)' if a['retry'] else ''}: {got} ({a['seconds']} s)")
        if b["mapped_from"]:
            out.append("- Fields the rule reads, mapped from this system: "
                       + "; ".join(f"{k} from {v}" for k, v in b["mapped_from"].items()))
        out.append(f"- State: {b['state']}")
        if b["baseline"]:
            out.append("- First run of this board: every posting was recorded as seen, and none counts as new.")
        out += _postings_md(f"New since the last run ({len(b['new'])})", b["new"])
        if b["judged_after_waiting"]:
            out += _postings_md(f"Judged now, after waiting for Claude ({len(b['judged_after_waiting'])})",
                                b["judged_after_waiting"])
        if b["still_waiting"]:
            out += ["", f"### Still waiting for Claude ({len(b['still_waiting'])})", "",
                    "Judged first next run: " + ", ".join(f"`{i}`" for i in b["still_waiting"])]
        if b["waiting_gone"]:
            out += ["", "Gone before Claude judged them: " + ", ".join(f"`{i}`" for i in b["waiting_gone"])]
        if b["gone"]:
            out += ["", f"### Gone since the last run ({len(b['gone'])})", ""]
            out += [f"- `{g['id']}` {g['title']}" for g in b["gone"]]
    out.append("")
    return "\n".join(out)


def _postings_md(heading: str, items: list) -> list:
    if not items:
        return []
    out = ["", f"### {heading}", ""]
    for item in items:
        out += [f"#### {item['title']}", "", f"- id: `{item['id']}`", f"- Locations: {item['locations']}",
                f"- Link: {item['jobUrl']}", "", f"**{RULE_LABEL}:** {item['rule_verdict']}", ""]
        out += [f"- {line}" for line in (item["rule"] or {}).get("lines", [])]
        out += ["", f"**{CLAUDE_LABEL}:** {item['claude_verdict']}", ""]
        out += [f"- {line}" for line in (item["claude"] or {}).get("lines", [])]
        out.append("")
    return out
