"""Blind changed-postings sheet: labels/changed-sheet.csv and labels/changed-texts/.

CLI: python tools/changed_sheet.py [--force]        (run from js3-filter-tool-score/)

Rows: every posting that is on neither the audit sheet nor the held-out sheet and whose verdict
under any of v0.1+C1 … v0.1+C6 or v0.2 differs from v0.1 ("changed", N rows), plus N random
postings from the same pool whose verdict is the same in every mode ("control"). Rules are the
ones frozen at commit f3edf99; filter results are computed in-process.

BLIND: the sheet and its text files show only what a reader of the posting would see (board,
id, title, locations, date, url, text), in the same columns as the other sheets, rows shuffled.
Which group each row is in, the verdicts, and the modes that move it go to out/changed-key.json
(git-ignored). This tool prints only counts. Only the board/id columns of the audit and held-out
sheets are read, never their labels.

Sampling: seed 7375, one random.Random for the whole draw; the control pool is sorted by
(board, id) first; controls are drawn with sample(), then all rows are shuffled.
"""

import argparse
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent import filter as flt  # noqa: E402
from agent.postings import load_run  # noqa: E402
from agent.sheets import COLUMNS, _posting_text, text_file_name  # noqa: E402

RUN = ROOT / "evidence" / "runs" / "live-text-1"
SEED = 7375
MODES = tuple(f"v0.1+C{i}" for i in range(1, 7)) + ("v0.2",)
TEXT_DIR = "changed-texts"


def sheet_keys(path: Path) -> set[tuple[str, str]]:
    """(board, id) of every row; no other column is read."""
    with open(path, newline="", encoding="utf-8") as fh:
        return {(r["board"], r["id"]) for r in csv.DictReader(fh)}


def choose(results: dict, excluded: set, seed: int = SEED) -> dict:
    """{"rows": [keys, shuffled], "groups": {key: "changed" | "control"}, "moved_by": {key: [modes]}}."""
    base = results["v0.1"]
    pool = sorted(k for k in base if k not in excluded)
    moved_by = {k: [m for m in MODES if results[m][k]["verdict"] != base[k]["verdict"]] for k in pool}
    changed = [k for k in pool if moved_by[k]]
    unchanged = [k for k in pool if not moved_by[k]]
    rng = random.Random(seed)
    if len(unchanged) < len(changed):
        raise ValueError("not enough unchanged postings for one control per changed posting")
    controls = rng.sample(unchanged, len(changed))
    rows = changed + controls
    rng.shuffle(rows)
    groups = {k: "changed" for k in changed} | {k: "control" for k in controls}
    return {"rows": rows, "groups": groups, "moved_by": {k: moved_by[k] for k in rows}}


def write_sheet(sheet: Path, keys: list, postings: dict) -> None:
    texts = sheet.parent / TEXT_DIR
    texts.mkdir(parents=True, exist_ok=True)
    with open(sheet, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(COLUMNS)
        for row, key in enumerate(keys, start=1):
            p = postings[key]
            name = text_file_name(key)
            (texts / name).write_text(_posting_text(p), encoding="utf-8")
            writer.writerow([row, p["board"], p["id"], p["title"] or "",
                             " | ".join(p["locations"]) if p["locations"] else "",
                             p["date"] or "", p["url"] or "", f"{TEXT_DIR}/{name}", "", ""])


def build(root: Path = ROOT, run_dir: Path = RUN, key_path: Path | None = None, force: bool = False) -> dict:
    sheet = root / "labels" / "changed-sheet.csv"
    key_path = key_path or root / "out" / "changed-key.json"
    if sheet.exists() and not force:
        raise FileExistsError(f"{sheet} exists; refusing to overwrite labels (use --force only before labeling)")
    excluded = sheet_keys(root / "audit" / "audit-sheet.csv") | sheet_keys(root / "labels" / "heldout-sheet.csv")
    postings, failures = load_run(run_dir, with_blocks=True)
    if failures:
        raise ValueError(f"board failures in {run_dir}: {failures}")
    by_key = {(p["board"], str(p["id"])): p for p in postings}
    persona = flt.load_persona(flt.DEFAULT_PERSONA)
    results = {m: {k: flt.evaluate(p, persona, flt.RULE_MODES[m]) for k, p in by_key.items()}
               for m in ("v0.1",) + MODES}
    chosen = choose(results, excluded)
    write_sheet(sheet, chosen["rows"], by_key)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(json.dumps({
        "seed": SEED, "run": str(run_dir.relative_to(root) if run_dir.is_relative_to(root) else run_dir),
        "rules": "frozen at commit f3edf99", "modes": ["v0.1", *MODES],
        "sheet_sha256": hashlib.sha256(sheet.read_bytes()).hexdigest(),
        "rows": [{"row": i, "board": k[0], "id": k[1], "group": chosen["groups"][k],
                  "moved_by": chosen["moved_by"][k],
                  "verdicts": {m: results[m][k]["verdict"] for m in ("v0.1",) + MODES}}
                 for i, k in enumerate(chosen["rows"], start=1)],
    }, indent=2, ensure_ascii=False) + "\n")
    n = sum(g == "changed" for g in chosen["groups"].values())
    return {"changed": n, "controls": len(chosen["rows"]) - n, "rows": len(chosen["rows"]),
            "pool": len(by_key) - len(excluded), "sheet": sheet, "key": key_path}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="tools/changed_sheet.py", description="Blind changed-postings sheet.")
    parser.add_argument("--force", action="store_true", help="overwrite an existing sheet (only before labeling)")
    args = parser.parse_args(argv)
    try:
        info = build(force=args.force)
    except (FileExistsError, ValueError) as err:
        print(f"error: {err}")
        return 2
    print(f"pool {info['pool']} postings; N = {info['changed']} changed + {info['controls']} controls "
          f"= {info['rows']} rows -> {info['sheet']}")
    print(f"group key (do not open before labeling): {info['key']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
