"""report.md for one run. report.json holds the same facts for machines; trace.jsonl holds every step."""
from __future__ import annotations


def _board_row(e: dict) -> str:
    if e["outcome"] == "observed":
        if e["baseline"]:
            what = f"{e['postings_observed']} postings; **baseline** (no saved state for this board, none reported as new)"
        else:
            what = (f"{e['postings_observed']} postings; {len(e['new'])} new id(s) since "
                    f"{e.get('previous_observation')}; {e['rule_relevant']} RELEVANT by rule")
    elif e["outcome"] == "empty-needs-review":
        what = "valid listing with **0 postings**: needs review; this is not \"no new jobs\""
    elif e["outcome"] == "failed":
        what = "**failed**: nothing about its postings is known"
    else:
        what = "**not observed**: nothing about its postings is known"
    tries = len(e["attempts"])
    return (f"| `{e['provider']}/{e['board']}` | {e['purpose']} | {e['outcome']} | {tries} | {what} | "
            f"{e['reason']} |")


def render_markdown(report: dict) -> str:
    run, boards = report["run"], report["boards"]
    out = [f"# Job loop run {run['run_id']}", ""]
    if run["mode"] != "LIVE":
        out += [f"> **{run['mode']}.** Responses were replayed from saved files in `{run['replay_source']}`; "
                "no network was used. This is not a fresh live observation.", ""]
    if run.get("label"):
        out += [f"> **Label: {run['label']}.** See the label's README; this run is a labeled demonstration.", ""]
    out += [f"**Mode:** {run['mode']} · **Status: {run['status'].upper()}** (exit {run['exit_code']}) · "
            f"started {run['started_utc']} · {run['elapsed_seconds']} s · "
            f"{run['attempts_used']} of {run['budget']['max_attempts']} attempts used", ""]
    if run["reasons"]:
        out += ["Why the status is not simply \"finished\":" if run["status"] != "finished" else "Notes:", ""]
        out += [f"- {r}" for r in run["reasons"]] + [""]
    out += ["| board | purpose | outcome | attempts | what is known | reason |",
            "|---|---|---|---:|---|---|"]
    out += [_board_row(e) for e in boards] + [""]
    out += [f"**State update:** {run['state_update']}", ""]
    if run["deliberate_failure"]:
        out += ["**Deliberate failure:**", ""] + [f"- {d}" for d in run["deliberate_failure"]] + [""]
    if report["attention_required"]:
        out += ["## Attention required", "", "| board | last attempt | failure | next manual check |",
                "|---|---:|---|---|"]
        out += [f"| {a['board']} | {a['attempt']} | {a['failure']} | {a['next_check']} |"
                for a in report["attention_required"]] + [""]
    out += ["## Attempts", ""]
    for e in boards:
        for a in e["attempts"]:
            raw = f"`{a['raw_file']}` ({a['bytes']} bytes, sha256 `{a['sha256'][:12]}…`)" if a.get("raw_file") \
                else a.get("response", "no response")
            out.append(f"- `{e['provider']}/{e['board']}` attempt {a['attempt']}: HTTP {a.get('status')} · "
                       f"{a['kind']} · {a['detail']} · {raw}")
    out.append("")
    new_rows = [(e, n) for e in boards for n in (e["new"] or [])]
    if new_rows:
        out += ["## New posting ids (RULE RECORD only; no AI judgment in JS2 runs)", "",
                "| board | title | location | rule verdict |", "|---|---|---|---|"]
        out += [f"| `{e['provider']}/{e['board']}` | {n['title']} | {n['location']} | {n['rule_verdict']} |"
                for e, n in new_rows] + [""]
    return "\n".join(out) + "\n"
