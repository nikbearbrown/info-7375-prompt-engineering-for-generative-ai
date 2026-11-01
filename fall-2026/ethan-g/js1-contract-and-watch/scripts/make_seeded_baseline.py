"""Build the SEEDED baseline used for Run 1 (v3: a whole multi-board run folder).

    python3 scripts/make_seeded_baseline.py evidence/raw/<live run folder>

Copies every board's real list response and removes the postings below from it. Nothing is invented or edited.
The removed set exercises the rule: 2 postings it calls relevant, 1 Canada-only, 2 over 5 years, and 1 non-data control.
(The 131-board extension also removed postings at CarGurus, Formlabs, Branch, DoorDash, and Sigma Computing.)
"""
import json
import shutil
import sys
from pathlib import Path

REMOVED = {
    "samsara": ["8141959", "7922530", "8250423", "8039914", "8281491", "8304547"],
}

src = Path(sys.argv[1])
out = src.with_name(src.name.replace("_live", "_SEEDED-baseline"))
if out.exists():
    sys.exit(f"{out} exists; not overwriting evidence")
(out / "boards").mkdir(parents=True)
missing = []
for f in sorted((src / "boards").glob("*.json")):
    drop = set(REMOVED.get(f.stem, []))
    if not drop:
        shutil.copyfile(f, out / "boards" / f.name)
        continue
    d = json.loads(f.read_text())
    present = {str(j["id"]) for j in d["jobs"]}
    missing += [f"{f.stem}:{i}" for i in drop - present]
    d["jobs"] = [j for j in d["jobs"] if str(j["id"]) not in drop]
    (out / "boards" / f.name).write_text(json.dumps(d))
note = {"constructed": "2026-10-31 by scripts/make_seeded_baseline.py", "from": str(src), "removed": REMOVED,
        "missing_from_source": missing,
        "why": "No second calendar day before the deadline. This stands in for an 'earlier' snapshot so the next live run has a real change "
               "to detect. Every remaining posting is real and unmodified; nothing was invented."}
(out / "_SEEDED.json").write_text(json.dumps(note, indent=1) + "\n")
print(f"saved {out} ({len(list((out / 'boards').glob('*.json')))} boards; missing from source: {missing or 'none'})")
