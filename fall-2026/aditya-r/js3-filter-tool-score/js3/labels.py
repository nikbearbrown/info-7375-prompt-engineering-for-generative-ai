"""Import Aditya's returned label sheet, seal it, and open the held-out rows only after the freeze.

  .venv/bin/python -m js3.labels import     validate review/LABEL_SHEET.csv, write labels/SEAL.json and
                                            labels/dev_labels.csv (dev rows only; prints nothing about held-out)
  .venv/bin/python -m js3.labels heldout    only if FREEZE.json is committed and the sheet still matches the seal:
                                            write labels/heldout_labels.csv
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
LABELS = ROOT / "labels"
ALLOWED = {"yes", "no", "unsure"}


def read_sheet():
    groups = json.loads((ROOT / "splits" / "groups.json").read_text())
    with SHEET.open(encoding="utf-8-sig", newline="") as f:
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
    return rows, groups["split_of_sheet_id"], problems


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
            "rows": len(rows), "dev_rows": sum(split[r["sheet_id"]] == "dev" for r in rows),
            "heldout_rows": sum(split[r["sheet_id"]] == "heldout" for r in rows),
            "note": "Held-out labels are not extracted or summarized until FREEZE.json is committed."}
    (LABELS / "SEAL.json").write_text(json.dumps(seal, indent=1) + "\n")
    dev = [r for r in rows if split[r["sheet_id"]] == "dev"]
    write(LABELS / "dev_labels.csv", dev)
    print(f"sealed sheet sha256 {seal['sheet_sha256'][:16]}…; dev rows {len(dev)}: {dict(Counter(r['label'] for r in dev))}; "
          f"held-out rows {seal['heldout_rows']} left unread")
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
    seal = json.loads((LABELS / "SEAL.json").read_text())
    if sha(SHEET) != seal["sheet_sha256"]:
        print("REFUSED: review/LABEL_SHEET.csv changed since it was sealed")
        return 1
    rows, split, _ = read_sheet()
    write(LABELS / "heldout_labels.csv", [r for r in rows if split[r["sheet_id"]] == "heldout"])
    print(f"held-out labels opened after freeze commit {tracked[:7]}")
    return 0


def write(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sheet_id", "key", "label", "reason"])
        for r in sorted(rows, key=lambda r: r["sheet_id"]):
            w.writerow([r["sheet_id"], r["key"], r["label"], r["reason"]])


def load(path):
    with path.open(encoding="utf-8") as f:
        return {r["key"]: r for r in csv.DictReader(f)}


if __name__ == "__main__":
    sys.exit({"import": cmd_import, "heldout": cmd_heldout}[sys.argv[1]]())
