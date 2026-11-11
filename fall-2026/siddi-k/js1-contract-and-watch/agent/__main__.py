"""python -m agent run --mode live | --mode seeded --seeded-from <board.json>
python -m agent check             read-time validation of output/verdicts.jsonl
python -m agent select-labels --board raw/<baseline_run_id>/board.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import config, labels, lines, persona, watch


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):        # titles carry ™ and –; a Windows console must not crash on them
        stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="python -m agent", description="Job-Search Agent 1 (see CONTRACT.md)")
    ap.add_argument("--root", type=Path, default=config.ROOT, help=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="one watch run")
    r.add_argument("--mode", choices=("live", "seeded"), required=True)
    r.add_argument("--seeded-from", help="saved board file (seeded mode only)")
    sub.add_parser("check", help="read-time validation of output/verdicts.jsonl")
    s = sub.add_parser("select-labels", help="the contract's 20-posting hand-label selection")
    s.add_argument("--board", required=True)
    a = ap.parse_args(argv)
    root = a.root.resolve()

    if a.cmd == "run":
        if a.mode == "live" and a.seeded_from:
            ap.error("--seeded-from is only for --mode seeded")
        watch.run(root, a.mode, a.seeded_from)
        return 0
    cfg = config.load(root)
    p = persona.load(root / "data" / "persona_resume.json", cfg.vocab)
    if a.cmd == "check":
        good, bad = lines.read_valid(root, cfg, p)
        print(f"{len(good)} valid verdict lines; {len(bad)} rejected or ignored")
        for i, errors in bad:
            print(f"  line {i}: {'; '.join(errors)}")
        return 0
    board_path = (root / a.board).resolve()
    board = json.loads(board_path.read_bytes())
    sel = labels.select(board, p, cfg)
    rel = board_path.relative_to(root).as_posix() if board_path.is_relative_to(root) else str(board_path)
    labels.write_sheet(board, sel, rel, root / "experiments" / "output")
    print(f"{sel['board_postings']} postings, {sel['candidates']} pass title+seniority; selected 20 "
          f"({len(sel['A'])} from candidates, {len(sel['B'])} from the rest); dev {len(sel['dev'])}, "
          f"held_out {len(sel['held_out'])}")
    print(f"base-rate check: {sel['rule_relevant_count']} of 20 are rule-relevant (count only, by design)")
    print("wrote experiments/output/label_selection.json, to_label.md, hand_labels.template.jsonl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
