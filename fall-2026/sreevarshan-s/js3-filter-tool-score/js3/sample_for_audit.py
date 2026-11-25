"""Draw a reproducible audit sample from output/filter_results.json.

Usage (from the repo root):
    python3 -m js3.sample_for_audit

Reads only output/filter_results.json (never the raw files) and writes
output/audit_sample.json and output/audit_sheet.md.

Buckets:
- random_rejects: 30 drawn uniformly from all rejected postings.
- closest_calls: 10 drawn from "no_match" postings whose title contains a
  role word (including "software engineer") or a topic word, excluding any
  already drawn as a random reject so the two hand-audit lists don't overlap.
- passed: every passed posting.

Overwrite protection: if either output file already exists with content
different from what this run would write (for example, an audit sheet with
verdicts filled in), the script writes nothing and exits with an error.
There is no override flag; move or delete the file by hand if you really
mean to replace it.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

from js3.filter import ROLE_WORDS, SOFTWARE_ENGINEER, TOPIC_WORDS, _find

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "output" / "filter_results.json"
SAMPLE_OUT = ROOT / "output" / "audit_sample.json"
SHEET_OUT = ROOT / "output" / "audit_sheet.md"

BOARDS = ["databricks", "stripe", "spotify"]  # fixed order for reproducibility
N_RANDOM = 30
N_CLOSEST = 10
SEED = 42


class OverwriteRefused(Exception):
    """Raised when an output file exists with different content."""


def _record(board: str, r: dict) -> dict:
    return {
        "board": board,
        "id": r.get("id"),
        "title": r.get("title", ""),
        "reason": r.get("reason"),
        "matched_words": r.get("matched_words", {}),
    }


def _title_hits(title: str) -> dict:
    return {
        "role": _find(ROLE_WORDS + [SOFTWARE_ENGINEER], title),
        "topic": _find(TOPIC_WORDS, title),
    }


def _md_cell(text: str) -> str:
    # Collapse tabs/newlines/runs of spaces (some raw titles carry them).
    return " ".join(str(text).split()).replace("|", "\\|")


def _table(rows: list[dict], start: int) -> list[str]:
    lines = [
        "| # | Board | Title | Reason | My verdict | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for i, row in enumerate(rows, start):
        lines.append(
            f"| {i} | {row['board']} | {_md_cell(row['title'])} | {row['reason']} | | |"
        )
    return lines


def build(results: dict) -> tuple[dict, str, dict]:
    """Return (sample, sheet_markdown, stats) without touching the disk."""
    # Only the three real boards are in filter_results.json; WRONG-DEMO files
    # were never part of the run, and any other key is ignored here.
    all_rows = [(b, r) for b in BOARDS for r in results.get(b, [])]
    rejected = [_record(b, r) for b, r in all_rows if not r.get("passed")]
    passed = [_record(b, r) for b, r in all_rows if r.get("passed")]

    rng = random.Random(SEED)
    random_rejects = rng.sample(rejected, min(N_RANDOM, len(rejected)))

    drawn = {(r["board"], r["id"]) for r in random_rejects}
    candidates = []
    for rec in rejected:
        if rec["reason"] != "no_match" or (rec["board"], rec["id"]) in drawn:
            continue
        hits = _title_hits(rec["title"])
        if hits["role"] or hits["topic"]:
            candidates.append({**rec, "title_hits": hits})
    closest_calls = rng.sample(candidates, min(N_CLOSEST, len(candidates)))

    sample = {
        "random_rejects": random_rejects,
        "closest_calls": closest_calls,
        "passed": passed,
    }
    sheet = [
        "# Reject audit sheet",
        "",
        f"Drawn from output/filter_results.json with random.seed({SEED}). "
        f"Rejected pool: {len(rejected)}. Closest-call pool: {len(candidates)}.",
        "",
        f"## Random rejects ({len(random_rejects)})",
        "",
        *_table(random_rejects, 1),
        "",
        f"## Closest calls ({len(closest_calls)})",
        "",
        *_table(closest_calls, len(random_rejects) + 1),
        "",
    ]
    stats = {
        "rejected_pool": len(rejected),
        "closest_pool": len(candidates),
        "random_rejects": len(random_rejects),
        "closest_calls": len(closest_calls),
        "passed": len(passed),
    }
    return sample, "\n".join(sheet), stats


def write_outputs(outputs: dict[Path, str]) -> None:
    """Write every file, or none of them if any would replace different content."""
    blocked = [
        p for p, text in outputs.items()
        if p.exists() and p.read_text(encoding="utf-8") != text
    ]
    if blocked:
        names = ", ".join(str(p) for p in blocked)
        raise OverwriteRefused(
            f"refusing to overwrite {names}: the existing content differs from what "
            "this run would write (it may hold review edits or verdicts). Nothing was written."
        )
    for p, text in outputs.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


def main(
    results_path: Path = RESULTS,
    sample_out: Path = SAMPLE_OUT,
    sheet_out: Path = SHEET_OUT,
) -> dict:
    with Path(results_path).open("r", encoding="utf-8") as f:
        results = json.load(f)
    sample, sheet, stats = build(results)
    sample_text = json.dumps(sample, indent=2, ensure_ascii=False) + "\n"
    write_outputs({Path(sample_out): sample_text, Path(sheet_out): sheet})

    for key, value in stats.items():
        print(f"{key + ':':<20}{value}")
    print(f"wrote {sample_out}")
    print(f"wrote {sheet_out}")
    return stats


if __name__ == "__main__":
    try:
        main()
    except OverwriteRefused as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
