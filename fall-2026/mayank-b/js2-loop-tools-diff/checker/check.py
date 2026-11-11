#!/usr/bin/env python3
"""Independent check (GATE.md §5). Deliberately does NOT import the agent's code (src/jsa).

It decides from two things only:
  1. the run's saved raw responses (runs/<id>/raw/*), counted here from the bytes, and
  2. config/expected-boards.json, floors Mayank sets, each with a named source.
It reads the agent's report.json *afterwards*, only to show what the agent claimed next to the verdict.

  python3 checker/check.py runs/<run-id> --plan config/boards.json
Exit 0 = every planned board ok · 3 = at least one board needs Mayank.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parents[1]
RAW_RE = re.compile(r"^(greenhouse|ashby)__(.+)__a(\d+)__(\d+)\.json$")


def key(ats: str, slug: str) -> str:  # written again here on purpose, not imported
    return f"{ats.casefold()}/{unquote(slug).strip().casefold()}"


def safe(slug_key: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", slug_key)


def count_postings(path: Path):
    try:
        data = json.loads(path.read_bytes().decode("utf-8"))
        jobs = data.get("jobs") if isinstance(data, dict) else None
        return len(jobs) if isinstance(jobs, list) else None
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def latest_raw(run_dir: Path, ats: str, slug_key: str):
    """The last attempt's raw file for this board, or None."""
    best = None
    for f in (run_dir / "raw").glob(f"{ats}__{safe(slug_key)}__a*__*.json"):
        m = RAW_RE.match(f.name)
        if m and (best is None or int(m.group(3)) > best[0]):
            best = (int(m.group(3)), int(m.group(4)), f)
    return best


def classify(count, status, floor, prev, threshold):
    """-> (verdict, reason). verdict: ok | suspect | error-response | no-response."""
    if status is None:
        return "no-response", "no raw response saved (timeout or never sent)"
    if status != 200 or count is None:
        return "error-response", f"HTTP {status}" + ("" if count is not None else ", body is not a job list")
    if count == 0:
        return "suspect", "0 postings in the raw response (an empty board is not 'no new jobs')"
    if floor is not None and count < floor:
        return "suspect", f"{count} postings is below my floor of {floor}"
    if prev and prev > 0 and count < prev * (1 - threshold):
        return "suspect", f"{count} postings is a {100 * (1 - count / prev):.0f}% drop from the previous run's {prev}"
    return "ok", f"{count} postings" + (f", floor {floor}" if floor is not None else ", floor unknown (no source)")


def previous_count(runs: Path, current: Path, ats: str, slug_key: str):
    for d in sorted((p for p in runs.iterdir() if p.is_dir() and p.name < current.name), reverse=True):
        hit = latest_raw(d, ats, slug_key)
        if hit and hit[1] == 200:
            c = count_postings(hit[2])
            if c is not None:
                return c, d.name
    return None, None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--plan", default="config/boards.json")
    ap.add_argument("--expected", default="config/expected-boards.json")
    a = ap.parse_args(argv)
    run_dir = (Path(a.run_dir) if Path(a.run_dir).is_absolute() else HERE / a.run_dir).resolve()
    if not run_dir.is_relative_to((HERE / "runs").resolve()):
        print("refused: the checker only reads and writes inside runs/", file=sys.stderr)
        return 2
    plan = json.loads((HERE / a.plan).read_text())["plan"]
    exp = json.loads((HERE / a.expected).read_text())
    threshold = exp.get("drop_threshold", 0.8)
    out, seen = {}, set()
    for e in plan:
        k = key(e["ats"], e["slug"])
        if k in seen:
            continue
        seen.add(k)
        slug_key = k.split("/", 1)[1]
        hit = latest_raw(run_dir, e["ats"], slug_key)
        status = hit[1] if hit else None
        count = count_postings(hit[2]) if hit else None
        floor_rec = exp["boards"].get(k, {"floor": None, "source": "no entry: unknown"})
        prev, prev_run = previous_count(run_dir.parent, run_dir, e["ats"], slug_key)
        verdict, reason = classify(count, status, floor_rec["floor"], prev, threshold)
        out[k] = {"verdict": verdict, "reason": reason, "raw_file": hit[2].name if hit else None, "http": status,
                  "postings_in_raw": count, "floor": floor_rec["floor"], "floor_source": floor_rec["source"],
                  "previous": prev, "previous_run": prev_run}
    # Only now, and only for display: what did the agent itself claim?
    try:
        rep = json.loads((run_dir / "report.json").read_text())
        claims = {r["board"]: r for r in rep.get("results", [])}
    except FileNotFoundError:
        rep, claims = {}, {}
    for k, v in out.items():
        c = claims.get(k)
        v["agent_claimed"] = (None if c is None else
                              (f"ok, {c['postings']} postings, {len(c['new'])} new" + (" (baseline)" if c.get("baseline") else ""))
                              if c["result"] == "ok" else f"error: {c.get('error_kind')}")
    needs = [k for k, v in out.items() if v["verdict"] != "ok"]
    result = {"run_id": run_dir.name, "checker": "checker/check.py (does not import the agent)",
              "agent_exit": rep.get("exit"), "needs_mayank": needs, "boards": out}
    (run_dir / "check.json").write_text(json.dumps(result, indent=1))
    lines = [f"NEEDS MAYANK: {', '.join(needs) if needs else 'none'}", "",
             f"# Independent check of run {run_dir.name}", "",
             f"The agent's own exit was `{rep.get('exit')}`. That says how its loop ended, not whether it was right. "
             "This table is computed from the saved raw responses and my floors, not from the agent's report.", "",
             "| Board | Checker verdict | Why | Agent claimed | Floor (source) |", "|---|---|---|---|---|"]
    for k, v in out.items():
        lines.append(f"| {k} | **{v['verdict']}** | {v['reason']} | {v['agent_claimed']} | {v['floor']} ({v['floor_source']}) |")
    (run_dir / "check.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 3 if needs else 0


if __name__ == "__main__":
    sys.exit(main())
