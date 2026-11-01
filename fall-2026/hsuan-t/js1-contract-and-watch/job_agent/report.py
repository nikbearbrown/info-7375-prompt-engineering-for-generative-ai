"""Writes one run's output: runs/<UTC>/verdicts.json (the verdicts), summary.md (the counts) and
claude_raw.jsonl (Claude's replies exactly as received, accepted or rejected).

Isaac asked for the summary "so I know what you're doing" (D7): without it, a run that reports
3 relevant out of 20 new gives no hint which check did the cutting or where the evidence lives.
Rendering only — it reads results, it never judges.
"""

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .common.paths import Paths
from .judges.checks import CHECKS
from .judges.rule import RuleResult
from .judges.verdict import RELEVANT
from .watch import WatchResult


@dataclass(frozen=True)
class ClaudeInfo:
    """Which prompt and model produced the judgment column, so two runs' Claude numbers are never compared blindly."""
    prompt: str
    model: str
    via: str          # cli / api / injected (a test fake)


def _relevant(vs: list[dict]) -> int:
    return sum(v["status"] == "ok" and v["verdict"] == RELEVANT for v in vs)


def _errors(vs: list[dict]) -> int:
    return sum(v["status"] == "error" for v in vs)


def summary_text(w: WatchResult, rule_results: list[RuleResult], claude: list[dict],
                 paths: Paths, profile_path: Path, info: ClaudeInfo) -> str:
    rule = [r.verdict for r in rule_results]
    cut = Counter(r.failed_check for r in rule_results)
    # Claude column stays "—" when there was nothing to judge; Claude never says which check failed.
    c = str if claude else (lambda _: "—")
    by_claude = {v["posting_id"]: v for v in claude}
    # Only answers both judges actually gave count: a Claude error is "not_relevant" by rule of
    # the format, not by judgment, so it must not show up as a disagreement.
    disagree = sum(1 for v in rule if v["status"] == "ok" and v["posting_id"] in by_claude
                   and by_claude[v["posting_id"]]["status"] == "ok"
                   and by_claude[v["posting_id"]]["verdict"] != v["verdict"])

    source = "seeded (replayed saved response)" if w.source == "seeded" else "live"
    out = [
        f"Run {w.run_at} · board: {w.board} · {source}{' · baseline' if w.baseline else ''}",
        f"State file: {paths.show(paths.state(w.board))} · updated: {w.run_at}",
        f"Raw response: {paths.show(w.raw_path)}",
        f"Claude judge: {info.model} via {info.via} · prompt: prompts/{info.prompt}.md",
        "",
        "| | rule (record) | Claude (judgment) |",
        "|---|---|---|",
        f"| fetched postings | {w.fetched} | — |",
        f"| new postings | {len(w.new)} | {c(len(claude))} |",
        *[f"| cut at {ch.id} {ch.name} | {cut.get(ch.id, 0)} | — |" for ch in CHECKS],
        f"| error | {_errors(rule)} | {c(_errors(claude))} |",
        f"| **relevant** | **{_relevant(rule)}** | {c(_relevant(claude))} |",
        f"| judges disagree | {c(disagree)} | |",
    ]
    if w.new:
        titles = {p.id: p.title for p in w.new}
        out += ["", "| posting_id | title | rule | cut at | Claude |", "|---|---|---|---|---|"]
        for r in rule_results:
            v = r.verdict
            where = r.failed_check or ("error" if v["status"] == "error" else "")
            cv = by_claude.get(v["posting_id"])
            judged = "—" if cv is None else ("error" if cv["status"] == "error" else cv["verdict"])
            out.append(f"| {v['posting_id']} | {titles[v['posting_id']]} | {v['verdict']} | {where} | {judged} |")
    out += ["", f'Missed a skill written another way? Add it under "skill_aliases" in {paths.show(profile_path)}']
    return "\n".join(out) + "\n"


def write_run(folder: Path, w: WatchResult, verdicts: list[dict], summary: str, paths: Paths,
              claude_raw: list[dict] | None = None) -> None:
    folder.mkdir(parents=True, exist_ok=False)
    doc = {
        "run_at": w.run_at,
        "board": w.board,
        "source": w.source,
        "baseline": w.baseline,
        "raw_response": paths.show(w.raw_path),
        "verdicts": verdicts,
    }
    (folder / "verdicts.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    (folder / "summary.md").write_text(summary)
    if claude_raw:
        # One line per posting, written even for rejected replies: the validator's error_message
        # says *that* a reply was refused, this file shows *what* Claude actually wrote.
        (folder / "claude_raw.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in claude_raw))
