"""Blind hand-label sheets: audit/audit-sheet.csv and labels/heldout-sheet.csv.

CLI: python -m agent.sheets --run evidence/runs/live-text-1 --results out/filter-v0.1/results.jsonl
     [--seed 7375] [--key out/filter-v0.1/sheet-key.json] [--force]

BLIND: the sheets and the posting text files show only what a reader of the posting would
see (board, id, title, locations, date, url, text). They never show the filter's verdict,
score, gate results, or which sample a row came from, and rows are shuffled. Which stratum
each row was drawn from goes to the key file under out/ (git-ignored). Don't open it until
labeling is done. This tool prints only sheet sizes and any shortfall.

Sampling (seed 7375, one random.Random for the whole draw, pools sorted by (board, id) first):
  audit = every near-threshold posting (all gates pass, score 1–3), or a random 15 if more,
          then 30 random rejects, 10 random keeps, 10 random cannot_tell, each drawn only
          from postings not already taken. A pool smaller than its target is taken whole and
          the shortfall is reported.
  held-out = 30 random postings, any verdict, from those not on the audit sheet.
"""

import argparse
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

from . import PROJECT_DIR
from .postings import RunError, load_run

SEED = 7375
NEAR_MAX = 15
AUDIT_TARGETS = (("reject", 30), ("keep", 10), ("cannot_tell", 10))
HELDOUT_SIZE = 30
COLUMNS = ("row", "board", "id", "title", "locations", "date", "url", "text_file", "my_verdict", "note")
LABEL_CHOICES = "keep | reject | cannot_tell"


def key_of(record: dict) -> tuple[str, str]:
    return (record["board"], str(record["id"]))


def select(results: list[dict], seed: int = SEED) -> dict:
    """{"audit": [keys], "heldout": [keys], "strata": {key: stratum}, "shortfalls": {...}}."""
    rng = random.Random(seed)
    ordered = sorted(results, key=key_of)
    strata, shortfalls = {}, {}

    near = [r for r in ordered if r["near_threshold"]]
    if len(near) > NEAR_MAX:
        near = rng.sample(near, NEAR_MAX)
    for r in near:
        strata[key_of(r)] = "near_threshold"

    for verdict, target in AUDIT_TARGETS:
        pool = [r for r in ordered if r["verdict"] == verdict and key_of(r) not in strata]
        picked = pool if len(pool) <= target else rng.sample(pool, target)
        if len(pool) < target:
            shortfalls[verdict] = {"target": target, "available": len(pool)}
        for r in picked:
            strata[key_of(r)] = verdict

    audit = list(strata)
    rng.shuffle(audit)
    pool = [key_of(r) for r in ordered if key_of(r) not in strata]
    heldout = rng.sample(pool, min(HELDOUT_SIZE, len(pool)))
    if len(pool) < HELDOUT_SIZE:
        shortfalls["heldout"] = {"target": HELDOUT_SIZE, "available": len(pool)}
    return {"audit": audit, "heldout": heldout, "strata": strata, "shortfalls": shortfalls}


def text_file_name(key: tuple[str, str]) -> str:
    board, posting_id = key
    return f"{board.replace('/', '-')}-{posting_id}.txt"


def _posting_text(p: dict) -> str:
    lines = [f"board: {p['board']}", f"id: {p['id']}", f"title: {p['title']}",
             f"locations: {' | '.join(p['locations']) if p['locations'] else None}",
             f"date: {p['date']}", f"url: {p['url']}", "", "--- posting text ---", "",
             p["text"] if p["text"] is not None else "(no posting text)"]
    return "\n".join(lines) + "\n"


def write_sheet(sheet: Path, keys: list, postings: dict) -> None:
    texts = sheet.parent / "texts"
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
                             p["date"] or "", p["url"] or "", f"texts/{name}", "", ""])


def build_sheets(run_dir, results_path, root=PROJECT_DIR, key_path=None, seed=SEED, force=False) -> dict:
    root = Path(root)
    audit_sheet = root / "audit" / "audit-sheet.csv"
    heldout_sheet = root / "labels" / "heldout-sheet.csv"
    existing = [p for p in (audit_sheet, heldout_sheet) if p.exists()]
    if existing and not force:
        raise FileExistsError(f"refusing to overwrite {', '.join(map(str, existing))} "
                              "(they may hold hand labels); pass --force to replace them")
    results_bytes = Path(results_path).read_bytes()
    results = [json.loads(line) for line in results_bytes.decode("utf-8").splitlines() if line.strip()]
    postings, _ = load_run(run_dir)
    by_key = {key_of(p): p for p in postings}
    missing = [k for k in map(key_of, results) if k not in by_key]
    if missing:
        raise RunError(f"{len(missing)} result(s) have no posting in {run_dir}, e.g. {missing[0]}")
    chosen = select(results, seed)
    write_sheet(audit_sheet, chosen["audit"], by_key)
    write_sheet(heldout_sheet, chosen["heldout"], by_key)
    key = {
        "seed": seed, "run": str(run_dir), "results": str(results_path),
        "results_sha256": hashlib.sha256(results_bytes).hexdigest(),
        "label_choices": LABEL_CHOICES,
        "audit": [{"board": b, "id": i, "stratum": chosen["strata"][(b, i)]} for b, i in chosen["audit"]],
        "heldout": [{"board": b, "id": i} for b, i in chosen["heldout"]],
        "shortfalls": chosen["shortfalls"],
    }
    if key_path is not None:
        key_path = Path(key_path)
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_text(json.dumps(key, indent=2) + "\n")
    return {"audit_rows": len(chosen["audit"]), "heldout_rows": len(chosen["heldout"]),
            "shortfalls": chosen["shortfalls"], "audit_sheet": audit_sheet, "heldout_sheet": heldout_sheet}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m agent.sheets", description="Blind hand-label sheets.")
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--key", type=Path, default=PROJECT_DIR / "out" / "filter-v0.1" / "sheet-key.json")
    parser.add_argument("--force", action="store_true", help="replace existing sheets (destroys hand labels)")
    args = parser.parse_args(argv)
    try:
        info = build_sheets(args.run, args.results, key_path=args.key, seed=args.seed, force=args.force)
    except (FileExistsError, RunError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    print(f"audit sheet: {info['audit_rows']} rows -> {info['audit_sheet']}")
    print(f"held-out sheet: {info['heldout_rows']} rows -> {info['heldout_sheet']}")
    for name, s in info["shortfalls"].items():
        print(f"shortfall: {name} target {s['target']}, only {s['available']} available")
    print(f"stratum key (do not open before labeling): {args.key}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
