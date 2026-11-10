"""Writes one run's output into runs/<UTC>/: verdicts.json (the record), summary.md (for people),
trace.jsonl (every request and event, JS2 R17) and claude_raw.jsonl (Claude's replies as received).

Isaac asked for the summary "so I know what you're doing" (D7): without it, a run that reports
3 relevant out of 20 new gives no hint which check did the cutting or where the evidence lives.
Since JS2 it starts with the run's exit and one line per board, so a failed board is visible
before any verdict. Rendering only: it reads results, it never judges.
"""

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .common.paths import Paths
from .common.policy import Policy
from .judges.checks import CHECKS
from .judges.verdict import RELEVANT
from .loop import codes
from .loop.results import OK, BoardResult


@dataclass(frozen=True)
class ClaudeInfo:
    """Which prompt and model produced the judgment column, so two runs' Claude numbers are never compared blindly."""
    prompt: str
    model: str
    via: str          # cli / api / injected (a test fake)
    on: bool = True   # False = Claude off for this run (the default since JS2, D1)


@dataclass(frozen=True)
class RunInfo:
    """The run-level facts the summary and verdicts.json open with."""
    run_at: str
    exit: str
    reason: str
    budget: dict


def _relevant(vs: list[dict]) -> int:
    return sum(v["status"] == "ok" and v["verdict"] == RELEVANT for v in vs)


def _errors(vs: list[dict]) -> int:
    return sum(v["status"] == "error" for v in vs)


def board_rows(results: list[BoardResult], paths: Paths) -> list[dict]:
    """Each board's line for verdicts.json: its result plus where its state and evidence are."""
    rows = []
    for r in results:
        row = r.row()
        row["state_file"] = paths.show(paths.state(r.board))
        row["raw_response"] = paths.show(r.watch.raw_path) if r.watch else None
        rows.append(row)
    return rows


def summary_text(run: RunInfo, results: list[BoardResult], claude: dict[str, list[dict]],
                 paths: Paths, profile_path: Path, info: ClaudeInfo, trace_path: Path) -> str:
    """claude maps board name -> that board's Claude verdicts."""
    b = run.budget
    # The run's seconds limit depends on Claude (GATE §2): 120 s with it off, 480 s with it on. The
    # 120 s board-phase limit still applies inside a Claude run, but as the denominator it made a
    # 129 s Claude run read "129.1/120", as if the budget had been broken (Step 6, 234257Z).
    run_limit = b['limits']['seconds_with_claude'] if info.on else b['limits']['seconds']
    out = [
        f"Run {run.run_at} · exit: **{run.exit}** ({run.reason})",
        f"Budget used: boards {b['boards_used']}/{b['limits']['boards']} · requests "
        f"{b['requests_used']}/{b['limits']['requests']} · seconds {b['seconds_used']:.1f}/{run_limit:.0f}",
        (f"Claude judge: {info.model} via {info.via} · prompt: prompts/{info.prompt}.md · calls "
         f"{b['claude_calls_used']}/{b['limits']['claude_calls']} · {b['claude_seconds_used']:.1f}/{b['limits']['claude_seconds']:.0f} s"
         f" (every new posting until 30 calls or 300 s are used)"
         if info.on else "Claude judge: off (turn on with --claude)"),
        f"Trace: {paths.show(trace_path)}",
        "",
        "| board | ats | status | code | reason | fetched | new | attempts |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        # A failed board shows "—", never 0: it returned no job list (GATE WV4).
        fetched = "—" if r.fetched is None else r.fetched
        new = len(r.watch.new) if r.watch else "—"
        code = codes.describe(r.code) if r.code else ""
        out.append(f"| {r.board} | {r.ats} | {r.status} | {code} | {r.reason} | {fetched} | {new} | {r.attempts} |")
    for r in results:
        if r.status == OK:
            out += ["", *_board_section(r, claude.get(r.board, []), paths, info.on)]
    out += ["", f'Missed a skill written another way? Add it under "skill_aliases" in {paths.show(profile_path)}']
    return "\n".join(out) + "\n"


def _board_section(r: BoardResult, claude: list[dict], paths: Paths, claude_on: bool) -> list[str]:
    """JS1's per-board table (which check cut how many), now one per ok board."""
    w, rule_results = r.watch, r.rule_results
    rule = [x.verdict for x in rule_results]
    cut = Counter(x.failed_check for x in rule_results)
    # Claude column stays "—" when there was nothing to judge; Claude never says which check failed.
    c = str if claude else (lambda _: "—")
    by_claude = {v["posting_id"]: v for v in claude}
    # D20: a posting the Claude budget never reached is not a Claude error; count it on its own row
    # so "error" still means "Claude was asked and failed".
    unsent = [v for v in claude if v.get("error_code") == "304"]
    asked = [v for v in claude if v.get("error_code") != "304"]
    # Only answers both judges actually gave count: a Claude error is "not_relevant" by rule of
    # the format, not by judgment, so it must not show up as a disagreement.
    disagree = sum(1 for v in rule if v["status"] == "ok" and v["posting_id"] in by_claude
                   and by_claude[v["posting_id"]]["status"] == "ok"
                   and by_claude[v["posting_id"]]["verdict"] != v["verdict"])
    source = "seeded (replayed saved response)" if w.source == "seeded" else "live"
    out = [
        f"## {w.board} · {source}{' · baseline' if w.baseline else ''}",
        f"State file: {paths.show(paths.state(w.board))} · Raw response: {paths.show(w.raw_path)}",
        "",
        "| | rule (record) | Claude (judgment) |",
        "|---|---|---|",
        f"| fetched postings | {w.fetched} | — |",
        f"| new postings | {len(w.new)} | {c(len(claude))} |",
        *[f"| cut at {ch.id} {ch.name} | {cut.get(ch.id, 0)} | — |" for ch in CHECKS],
        f"| not sent: Claude budget used up | — | {c(len(unsent))} |",
        f"| error | {_errors(rule)} | {c(_errors(asked))} |",
        f"| **relevant** | **{_relevant(rule)}** | {c(_relevant(asked))} |",
        f"| judges disagree | {c(disagree)} | |",
    ]
    if w.new:
        titles = {p.id: p.title for p in w.new}
        out += ["", "| posting_id | title | rule | cut at | Claude |", "|---|---|---|---|---|"]
        for x in rule_results:
            v = x.verdict
            where = x.failed_check or ("error" if v["status"] == "error" else "")
            cv = by_claude.get(v["posting_id"])
            if cv is None:
                judged = "not sent" if claude_on else "off"   # Claude on but couldn't be reached for this posting
            elif cv.get("error_code") == "304":
                judged = "not sent: budget"   # GATE §2 (D20): the Claude budget ran out before this posting
            elif cv["status"] == "error":
                judged = f"error {cv.get('error_code', '')}".strip()
            else:
                judged = cv["verdict"]
            out.append(f"| {v['posting_id']} | {titles[v['posting_id']]} | {v['verdict']} | {where} | {judged} |")
    return out


def write_run(folder: Path, run: RunInfo, boards: list[dict], verdicts: list[dict], summary: str,
              trace_jsonl: str, policy: Policy, claude_raw: list[dict] | None = None) -> None:
    # Every file is checked, not only the folder: the policy is the gate even if a caller skipped
    # the early check. exist_ok: an existing folder only gets here after an explicit yes (JS2 D15).
    policy.check_write(folder).mkdir(parents=True, exist_ok=True)
    doc = {"run_at": run.run_at, "exit": run.exit, "exit_reason": run.reason, "budget": run.budget,
           "boards": boards, "verdicts": verdicts}
    policy.check_write(folder / "verdicts.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    policy.check_write(folder / "summary.md").write_text(summary)
    policy.check_write(folder / "trace.jsonl").write_text(trace_jsonl)
    if claude_raw:
        # One line per posting, written even for rejected replies: the validator's error_message
        # says *that* a reply was refused, this file shows *what* Claude actually wrote.
        policy.check_write(folder / "claude_raw.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in claude_raw))
