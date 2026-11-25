"""Import Aditya's returned label sheet, seal it, and open the held-out rows only after the freeze.

  .venv/bin/python -m js3.labels import     validate review/LABEL_SHEET.csv, write labels/SEAL.json and
                                            labels/dev_labels.csv (dev rows only; prints nothing about held-out)
  .venv/bin/python -m js3.labels seal-h2    validate review/LABEL_SHEET_H2.csv and record its sha256 in labels/SEAL_H2.json,
                                            printing only row problems (never labels or counts)
  .venv/bin/python -m js3.labels heldout    only if FREEZE.json is committed and the H2 sheet still matches its seal:
                                            write labels/heldout2_labels.csv

Amendment A3 (FILTER.md): the 23 rows first drawn as held-out were read by Claude before the freeze, so all 63
rows of LABEL_SHEET.csv are dev evidence; each keeps its original sampling-group names in dev_labels.csv.
The held-out set is H2 (review/LABEL_SHEET_H2.csv, splits/heldout2.json).
"""
import csv
import datetime as dt
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "review" / "LABEL_SHEET.csv"
SHEET_H2 = ROOT / "review" / "LABEL_SHEET_H2.csv"
LABELS = ROOT / "labels"
ALLOWED = {"yes", "no", "unsure"}


def read_sheet(sheet=SHEET, groups_file="groups.json"):
    groups = json.loads((ROOT / "splits" / groups_file).read_text())
    with sheet.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    ids = groups["sheet_ids"]                      # key -> sheet_id
    expected = {sid: key for key, sid in ids.items()}
    problems = []
    if len(rows) != len(expected):
        problems.append(f"{len(rows)} rows, expected {len(expected)}")
    for r in rows:
        sid = (r.get("sheet_id") or "").strip()
        if expected.get(sid) != (r.get("key") or "").strip():
            problems.append(f"{sid}: key changed or unknown")
        lab = (r.get("label") or "").strip().lower()
        if lab not in ALLOWED:
            problems.append(f"{sid}: label {r.get('label')!r} is not yes/no/unsure")
        r["label"] = lab
        r["reason"] = (r.get("reason") or "").strip()
    return rows, groups.get("split_of_sheet_id"), problems


def group_names(groups_file="groups.json"):
    g = json.loads((ROOT / "splits" / groups_file).read_text())
    names = {}
    for part in ("dev", "heldout", "heldout2"):
        for grp, items in g.get(part, {}).items():
            for it in items:
                names.setdefault(it["key"], []).append(grp)
    return {k: "+".join(v) for k, v in names.items()}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cmd_import():
    rows, split, problems = read_sheet()
    if problems:
        print("NOT IMPORTED. Please fix in review/LABEL_SHEET.csv:\n  " + "\n  ".join(problems))
        return 1
    LABELS.mkdir(exist_ok=True)
    seal = {"sheet": "review/LABEL_SHEET.csv", "sheet_sha256": sha(SHEET),
            "imported_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "rows": len(rows), "drawn_as_dev": sum(split[r["sheet_id"]] == "dev" for r in rows),
            "drawn_as_heldout_now_dev_A3": sum(split[r["sheet_id"]] == "heldout" for r in rows),
            "source": "transcribed by Claude Code from Aditya's two screenshots (labels/TRANSCRIPTION.md)"}
    (LABELS / "SEAL.json").write_text(json.dumps(seal, indent=1) + "\n")
    names = group_names()
    for r in rows:
        r["group"] = names.get(r["key"], "")
        r["drawn_as"] = split[r["sheet_id"]]
    write(LABELS / "dev_labels.csv", rows)
    print(f"sealed sheet sha256 {seal['sheet_sha256'][:16]}…; dev rows {len(rows)} (A3): {dict(Counter(r['label'] for r in rows))}")
    return 0


def cmd_seal_h2():
    rows, _, problems = read_sheet(SHEET_H2, "heldout2.json")
    if problems:
        print("NOT SEALED. Please fix in review/LABEL_SHEET_H2.csv:\n  " + "\n  ".join(problems))
        return 1
    LABELS.mkdir(exist_ok=True)
    seal = {"sheet": "review/LABEL_SHEET_H2.csv", "sheet_sha256": sha(SHEET_H2), "rows": len(rows),
            "sealed_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "note": "Validated and hashed without printing labels. Opened only after FREEZE.json is committed."}
    (LABELS / "SEAL_H2.json").write_text(json.dumps(seal, indent=1) + "\n")
    print(f"H2 sheet valid ({len(rows)} rows) and sealed: sha256 {seal['sheet_sha256'][:16]}…  (labels not shown)")
    return 0


def cmd_heldout():
    freeze = ROOT / "FREEZE.json"
    if not freeze.exists():
        print("REFUSED: FREEZE.json does not exist")
        return 1
    tracked = subprocess.run(["git", "log", "-1", "--format=%H", "--", str(freeze)], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", str(freeze)], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    if not tracked or dirty:
        print("REFUSED: FREEZE.json must be committed and unmodified before held-out labels are opened")
        return 1
    seal = json.loads((LABELS / "SEAL_H2.json").read_text())
    if sha(SHEET_H2) != seal["sheet_sha256"]:
        print("REFUSED: review/LABEL_SHEET_H2.csv changed since it was sealed")
        return 1
    rows, _, _ = read_sheet(SHEET_H2, "heldout2.json")
    names = group_names("heldout2.json")
    for r in rows:
        r["group"], r["drawn_as"] = names.get(r["key"], ""), "heldout2"
    write(LABELS / "heldout2_labels.csv", rows)
    print(f"held-out labels opened after freeze commit {tracked[:7]}")
    return 0


def write(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sheet_id", "key", "label", "reason", "group", "drawn_as"])
        for r in sorted(rows, key=lambda r: r["sheet_id"]):
            w.writerow([r["sheet_id"], r["key"], r["label"], r["reason"], r.get("group", ""), r.get("drawn_as", "")])


def load(path):
    with path.open(encoding="utf-8") as f:
        return {r["key"]: r for r in csv.DictReader(f)}


if __name__ == "__main__":
    sys.exit({"import": cmd_import, "seal-h2": cmd_seal_h2, "heldout": cmd_heldout}[sys.argv[1]]())
