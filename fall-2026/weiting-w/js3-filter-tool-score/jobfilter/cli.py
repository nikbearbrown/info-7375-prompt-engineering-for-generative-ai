"""Run the filter over JS2's captured corpus and write the artifacts.

    python3 -m jobfilter run                 # decisions + summary into audit/
    python3 -m jobfilter summary             # counts only, to the terminal

No network: every posting comes from the bytes JS2 saved on 2026-11-11.
Deliberately absent: any flag that changes a weight, a word list or the
threshold. FILTER.md §5 says those move only by an amendment recorded in §7,
and a number any caller can set is not a declared number.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from inherited import resume as resume_mod

from . import corpus as corpus_mod
from . import pipeline

ROOT = Path(__file__).resolve().parents[1]


def cmd_run(args) -> int:
    postings = corpus_mod.load(args.raw_dir)
    persona = resume_mod.load(args.persona)
    decisions = pipeline.run(postings, persona)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = pipeline.summary(decisions)
    summary["corpus"] = corpus_mod.inventory(postings)

    (out_dir / "decisions.json").write_text(
        json.dumps([d.as_dict() for d in decisions], indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(human(summary))
    print(f"\n  decisions: {out_dir / 'decisions.json'}")
    print(f"  summary:   {out_dir / 'summary.json'}")
    return 0


def cmd_summary(args) -> int:
    postings = corpus_mod.load(args.raw_dir)
    persona = resume_mod.load(args.persona)
    decisions = pipeline.run(postings, persona)
    summary = pipeline.summary(decisions)
    summary["corpus"] = corpus_mod.inventory(postings)
    print(human(summary))
    return 0


def human(summary: dict) -> str:
    c = summary["counts"]
    corpus_info = summary.get("corpus", {})
    lines = [
        f"filter={summary['filter_version']}  scorer={summary['scorer_version']}  "
        f"threshold={summary['threshold']}",
        f"corpus: {corpus_info.get('total')} postings, "
        f"{corpus_info.get('with_body')} with a body, "
        f"{corpus_info.get('without_body')} without",
        "",
        f"  shortlisted      {c['shortlisted']:>4d}",
        f"  below_threshold  {c['below_threshold']:>4d}",
        f"  gated            {c['gated']:>4d}",
        f"  cannot_score     {c['cannot_score']:>4d}   "
        "(no body on that board; not a zero, not a rejection)",
        f"  {'-' * 34}",
        f"  total            {summary['total']:>4d}",
        "",
        "  gates: " + ", ".join(
            f"{k}={v}" for k, v in sorted(summary["gate_breakdown"].items())
        ),
        f"  scored: {summary['scored']}   range: {summary['score_range']}",
    ]
    if summary["scored"] == 0:
        lines += [
            "",
            "  NOTE: the scorer never ran. Every posting that carries a body was",
            "  stopped by a gate, so S-v1 decided nothing about this corpus.",
        ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python3 -m jobfilter", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for name, fn in (("run", cmd_run), ("summary", cmd_summary)):
        s = sub.add_parser(name)
        s.add_argument("--raw-dir", default=None)
        s.add_argument("--persona", default=str(ROOT / "data" / "resume.persona.json"))
        s.add_argument("--out", default=str(ROOT / "audit"))
        s.set_defaults(func=fn)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
