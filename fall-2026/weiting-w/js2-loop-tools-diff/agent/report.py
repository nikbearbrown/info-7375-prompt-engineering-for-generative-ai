"""The run report, and the exit status derived from the trace.

GATE.md §1 E2: there is no code path in this package that sets `finished`
directly. `exit_status` reads the recorded observations and works it out, so a
run cannot claim to have succeeded just because the function that built the
summary row wanted it to.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import rule as rule_judge
from .http import utc_now
from .loop import LOOP_VERSION, RunResult

STATUSES = ("finished", "incomplete", "budget_exhausted", "error")


def exit_status(result: RunResult) -> tuple[str, bool]:
    """Return `(status, complete)`, derived from the trace. GATE.md §1.

    Order matters: a policy refusal outranks a budget, and a budget outranks an
    unobserved board, because each one makes the ones below it unknowable.
    """
    final = result.trace.final_outcome_per_board()
    if any(outcome == "policy" for outcome in final.values()):
        return "error", False
    if result.budget_hit:
        return "budget_exhausted", False
    failed = [b for b, o in final.items() if o not in ("ok", "budget")]
    if failed:
        return "incomplete", False
    observed = {o.board for o in result.outcomes if o.observed}
    if len(observed) < result.planned:
        return "incomplete", False
    return "finished", True


def judge_new(postings, resume) -> list[dict]:
    """One entry per new posting: the recomputable rule verdict, labelled."""
    entries = []
    for posting in postings:
        verdict = rule_judge.judge(posting.for_rule(), resume)
        entry = posting.summary()
        entry["rule_verdict"] = verdict
        entries.append(entry)
    return entries


def build(
    result: RunResult,
    *,
    policy,
    mode: str,
    label: str | None,
    new_entries: list[dict],
    is_first_run: bool,
    state_before_sha: str | None,
    state_after_sha: str | None,
    state_path,
) -> dict:
    status, complete = exit_status(result)
    final = result.trace.final_outcome_per_board()

    boards = []
    for outcome in result.outcomes:
        row = {
            "board": outcome.board,
            "provider": outcome.provider,
            "token": outcome.token,
            "status": outcome.status,
            "attempts": outcome.attempts,
            "deliberate_failure": outcome.deliberate,
        }
        if outcome.observed:
            # Only an observed board gets a count. A failed board has no count,
            # and inventing one is wrong version W1.
            row["postings_seen"] = len(outcome.postings)
            row["raw_response"] = outcome.raw
        else:
            row["error_class"] = outcome.error_class
            row["error"] = outcome.error
            row["postings_seen"] = None
        boards.append(row)

    return {
        "report_version": 2,
        "generated_at": utc_now(),
        "loop_version": LOOP_VERSION,
        "rule_version": rule_judge.RULE_VERSION,
        "mode": mode,
        "label": label,
        "exit_status": status,
        "complete": complete,
        "is_first_run": is_first_run,
        "policy": policy.describe(),
        "budget": result.budget.as_dict(),
        "budget_hit": result.budget_hit,
        "usage": {
            "boards_planned": result.planned,
            "boards_attempted": len(result.outcomes),
            "boards_observed": sum(1 for o in result.outcomes if o.observed),
            "boards_failed": sum(1 for o in result.outcomes if not o.observed),
            "boards_skipped": result.skipped,
            "requests_used": result.trace.requests_used(),
            "requests_limit": result.budget.requests,
            "seconds_used": result.seconds_used,
            "seconds_limit": result.budget.seconds,
        },
        "boards": boards,
        "final_outcome_per_board": final,
        "new_postings": 0 if is_first_run else len(new_entries),
        "entries": [] if is_first_run else new_entries,
        "state": {
            "path": str(state_path),
            "sha256_before": state_before_sha,
            "sha256_after": state_after_sha,
        },
        "trace": str(result.trace.path) if result.trace.path else None,
    }


def write(report: dict, runs_dir: str | Path, *, policy=None) -> Path:
    """Write the run report, through the write policy (GATE.md §5.2, A3).

    `policy` is keyword-only and defaults to None so that the collision test
    can call this directly, but `agent.cli` always passes one.
    """
    runs_dir = Path(runs_dir)
    stamp = report["generated_at"].replace(":", "").replace("-", "")
    path = runs_dir / f"run-{stamp}.json"
    suffix = 2
    while path.exists():
        path = runs_dir / f"run-{stamp}-{suffix}.json"
        suffix += 1
    if policy is not None:
        policy.check_write(path)
    runs_dir.mkdir(parents=True, exist_ok=True)
    report = {**report, "run_report_path": str(path)}
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def human_summary(report: dict) -> str:
    u = report["usage"]
    lines = [
        f"[{report['exit_status'].upper()}] complete={report['complete']}  "
        f"mode={report['mode']}  loop={report['loop_version']}  rule={report['rule_version']}",
        f"  boards planned={u['boards_planned']} attempted={u['boards_attempted']} "
        f"observed={u['boards_observed']} failed={u['boards_failed']}",
        f"  requests {u['requests_used']}/{u['requests_limit']}   "
        f"seconds {u['seconds_used']}/{u['seconds_limit']}"
        + (f"   budget_hit={report['budget_hit']}" if report["budget_hit"] else ""),
    ]
    if report["label"]:
        lines.append(f"  label: {report['label']}")
    for row in report["boards"]:
        if row["status"] == "ok":
            lines.append(
                f"  ok        {row['board']:28s} postings={row['postings_seen']}"
                f"  attempts={row['attempts']}"
            )
        else:
            mark = "DELIBERATE" if row["deliberate_failure"] else "FAILED"
            lines.append(
                f"  {row['status']:9s} {row['board']:28s} {mark}  "
                f"attempts={row['attempts']}  {row['error_class']}: {row['error']}"
            )
    if report["usage"]["boards_skipped"]:
        lines.append(f"  skipped (never attempted): {report['usage']['boards_skipped']}")

    if report["is_first_run"]:
        lines.append(
            "  first run: every posting recorded as seen, none reported as new."
        )
    else:
        lines.append(f"  new postings: {report['new_postings']}")
        for entry in report["entries"]:
            v = entry["rule_verdict"]
            lines.append(f"    #{entry['identity']}  {entry['title']}")
            lines.append(f"      {entry['url']}")
            lines.append(
                f"      RECORD (rule {v['rule_version']}): {v['verdict']}"
                + (f"  first failing gate: {v['gate_failed']}" if v["gate_failed"] else "")
            )
            for c in v["justification"]:
                extra = f" [provider: {c['provider_field']}]" if c.get("provider_field") else ""
                lines.append(
                    f"        because {c['resume_field']} = {c['resume_value']!r} "
                    f"vs posting.{c['posting_field']} containing {c['evidence']!r}{extra}"
                )

    if report["exit_status"] != "finished":
        failed = [
            f"{r['board']} ({r['status']})" for r in report["boards"] if r["status"] != "ok"
        ]
        lines.append("")
        lines.append(
            f"  ESCALATE: exit={report['exit_status']} complete=False. "
            + (f"failed boards: {', '.join(failed)}. " if failed else "")
            + "The posting list above is NOT complete."
        )
    return "\n".join(lines)
