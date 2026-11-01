"""One watch run: validate, fetch or replay, find new IDs, judge twice, save, then update state.

Usage (from this folder):
    python3 -m jobwatch                                   # live fetch, rule only
    python3 -m jobwatch --judge claude                    # live fetch, rule + Claude
    python3 -m jobwatch --fixture F --collected-at 2026-10-30T12:00:30Z [--seeded]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from . import board, judge, rule
from .persona import PersonaError, load_resume
from .report import render_markdown
from .state import StateError, load_state, save_state

LIVE, FIXTURE, SEEDED = "LIVE", "FIXTURE REPLAY", "SEEDED REPLAY"


def _utc(now: Optional[datetime] = None) -> datetime:
    return now or datetime.now(timezone.utc)


def _run_dir(runs: Path, run_id: str) -> Path:
    candidate, n = runs / run_id, 2
    while candidate.exists() or candidate.with_name(candidate.name + ".partial").exists():
        candidate, n = runs / f"{run_id}-{n}", n + 1
    return candidate


def write_outputs(run_dir: Path, raw: bytes, report: dict) -> None:
    """Write everything into <run>.partial, then rename it. A crash leaves only .partial behind."""
    partial = run_dir.with_name(run_dir.name + ".partial")
    partial.mkdir(parents=True)
    (partial / "raw-response.json").write_bytes(raw)
    replies = [r["ai_judgment"] for r in report["results"] if r["ai_judgment"].get("raw_reply") is not None]
    if replies:
        (partial / "claude").mkdir()
        for j in replies:
            (partial / "claude" / f"{j['posting_id']}.txt").write_text(j["raw_reply"], encoding="utf-8")
    (partial / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (partial / "report.md").write_text(render_markdown(report), encoding="utf-8")
    os.replace(partial, run_dir)


def run(resume_path: Path, state_path: Path, runs_path: Path, *, fixture: Optional[Path] = None,
        collected_at: Optional[str] = None, seeded: bool = False, caller: Optional[Callable] = None,
        prompt_path: Optional[Path] = None, fetcher: Callable = board.fetch,
        writer: Callable = write_outputs, now: Optional[datetime] = None) -> dict:
    started = _utc(now)
    run_ts = started.strftime("%Y-%m-%dT%H:%M:%SZ")
    resume = load_resume(resume_path)                       # stops before any fetch
    prompt_name, template = judge.load_prompt(prompt_path) if caller else (None, None)
    state = load_state(state_path, board.BOARD)             # stops on a bad state file

    if fixture is not None:
        if not collected_at:
            raise ValueError("--fixture needs --collected-at (when the saved response was really collected)")
        try:
            raw = Path(fixture).read_bytes()
        except OSError as exc:
            raise board.BoardError(f"cannot read fixture {fixture}: {exc}") from None
        mode = SEEDED if seeded else FIXTURE
        source = {"fixture": str(fixture), "sha256": hashlib.sha256(raw).hexdigest(),
                  "collected_at": collected_at, "network": False}
    else:
        if seeded:
            raise ValueError("--seeded only applies to --fixture runs")
        raw, meta = fetcher()
        mode = LIVE
        source = {**meta, "sha256": hashlib.sha256(raw).hexdigest(), "network": True}
    postings = board.parse_board(raw)

    seen = set(state["seen_ids"]) if state else set()
    baseline = state is None
    new = [] if baseline else [p for p in postings if rule.posting_id(p) not in seen]

    results = []
    for p in new:
        record = rule.classify(p, resume)
        ai = judge.judge(p, resume, prompt_name, template, caller)
        results.append({
            "posting_id": rule.posting_id(p),
            "title": p["title"],
            "location": (p.get("location") or {}).get("name"),
            "offices": [o.get("name") for o in p.get("offices") or []],
            "url": p.get("absolute_url"),
            "rule_record": record,
            "ai_judgment": ai,
            "disagreement": ai["status"] == judge.VALID and ai["verdict"] != record["verdict"],
            "run_timestamp": run_ts,
            "run_mode": mode,
        })

    statuses = [r["ai_judgment"]["status"] for r in results]
    report = {
        "run": {
            "board": board.BOARD, "run_timestamp": run_ts, "mode": mode, "source": source,
            "baseline": baseline, "previous_run": state["last_successful_run"] if state else None,
            "postings_observed": len(postings), "previously_seen": len(seen), "new_ids": len(results),
            "rule_relevant": sum(r["rule_record"]["verdict"] == rule.RELEVANT for r in results),
            "ai_judge": prompt_name or judge.NOT_REQUESTED,
            "ai_valid": statuses.count(judge.VALID),
            "ai_validation_failed": statuses.count(judge.VALIDATION_FAILED),
            "ai_call_failed": statuses.count(judge.CALL_FAILED),
            "disagreements": sum(r["disagreement"] for r in results),
            "failures": [],
        },
        "results": results,
    }
    run_dir = _run_dir(Path(runs_path), started.strftime("%Y-%m-%dT%H-%M-%SZ"))
    writer(run_dir, raw, report)                            # any failure here leaves state untouched
    save_state(state_path, board.BOARD, seen | {rule.posting_id(p) for p in postings}, run_ts)
    return {"run_dir": str(run_dir), **report["run"]}


def _record_failure(runs_path: Path, error: Exception, now: Optional[datetime] = None) -> Optional[Path]:
    try:
        runs_path.mkdir(parents=True, exist_ok=True)
        path = runs_path / f"{_utc(now).strftime('%Y-%m-%dT%H-%M-%SZ')}-FAILED.json"
        path.write_text(json.dumps({"error_type": type(error).__name__, "error": str(error),
                                    "state_changed": False}, indent=2) + "\n", encoding="utf-8")
        return path
    except OSError:
        return None


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(prog="python3 -m jobwatch", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resume", type=Path, default=Path("data/supriya-sharma.resume.json"))
    ap.add_argument("--state", type=Path, default=Path("state/seen_ids.json"))
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--fixture", type=Path, help="replay a saved Greenhouse response instead of fetching")
    ap.add_argument("--collected-at", help="UTC time the fixture was really collected (required with --fixture)")
    ap.add_argument("--seeded", action="store_true", help="label a modified fixture as SEEDED REPLAY")
    ap.add_argument("--judge", choices=["none", "claude"], default="none")
    ap.add_argument("--prompt", type=Path, default=Path("prompts/baseline-v1.md"))
    ap.add_argument("--model", help="Claude model for --judge claude (default: Claude Code's default)")
    args = ap.parse_args(argv)

    if args.judge == "claude" and shutil.which("claude") is None:
        print("RUN FAILED: --judge claude needs the Claude Code CLI on PATH", file=sys.stderr)
        return 2
    caller = (lambda prompt: judge.call_claude(prompt, model=args.model)) if args.judge == "claude" else None
    try:
        summary = run(args.resume, args.state, args.runs, fixture=args.fixture,
                      collected_at=args.collected_at, seeded=args.seeded, caller=caller,
                      prompt_path=args.prompt)
    except (PersonaError, StateError, board.BoardError, ValueError, OSError) as exc:
        where = _record_failure(args.runs, exc)
        print(f"RUN FAILED ({type(exc).__name__}): {exc}", file=sys.stderr)
        print(f"State was not changed.{' Failure recorded in ' + str(where) if where else ''}", file=sys.stderr)
        return 2
    print(f"{summary['mode']} run {summary['run_timestamp']} on {summary['board']}: "
          f"{summary['postings_observed']} postings, {summary['new_ids']} new"
          f"{' (baseline: none reported as new)' if summary['baseline'] else ''}, "
          f"{summary['rule_relevant']} RELEVANT by rule, {summary['disagreements']} disagreement(s).")
    print(f"Report: {summary['run_dir']}/report.md")
    return 0
