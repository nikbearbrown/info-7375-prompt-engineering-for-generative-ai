"""Shortlist claims for the kept postings (FILTER.md section 2).

  .venv/bin/python tools/js3_shortlist.py draft    # write runs/js3/shortlist/CLAIMS.csv, every label `not reviewed`
  .venv/bin/python tools/js3_shortlist.py render   # read the labeled CLAIMS.csv, write runs/js3/shortlist/SHORTLIST.md

`draft` refuses to overwrite a CLAIMS.csv that already has a label other than `not reviewed`.
`render` refuses a label outside FILTER.md's four, and a `supported`/`contradicted`/`insufficient` row with no reviewer.
"""
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jsfilter import filter as F, shortlist as S  # noqa: E402

OUT = ROOT / "runs" / "js3" / "shortlist"
CLAIMS = OUT / "CLAIMS.csv"
COLS = ["claim_id", "board", "id", "title", "kind", "claim", "field", "excerpt",
        "label", "reviewer", "missing", "note"]


def _kept():
    resume = json.loads((ROOT / "resumes" / "aarav-patel.json").read_text())
    boards = F.load_snapshot(ROOT)
    desc = {(p["board"], p["id"]): p["description"] for b in boards for p in b["postings"]}
    return F.run_filter(resume, boards)["kept"], desc


def draft():
    if CLAIMS.exists():
        with CLAIMS.open() as fh:
            if any(r["label"] != "not reviewed" for r in csv.DictReader(fh)):
                sys.exit("CLAIMS.csv already has reviewed labels; not overwriting")
    OUT.mkdir(parents=True, exist_ok=True)
    kept, desc = _kept()
    with CLAIMS.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for row in kept:
            for c in S.draft_claims(row, desc[(row["board"], row["id"])]):
                w.writerow({"board": row["board"], "id": row["id"], "title": row["title"],
                            **{k: c.get(k) or "" for k in COLS if k not in ("board", "id", "title")}})
    print(f"wrote {CLAIMS.relative_to(ROOT)} for {len(kept)} kept postings")


def render():
    kept, _ = _kept()
    with CLAIMS.open() as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        if r["label"] not in S.LABELS:
            sys.exit(f"{r['claim_id']}: label {r['label']!r} is not one of {S.LABELS}")
        if r["label"] != "not reviewed" and not r["reviewer"].strip():
            sys.exit(f"{r['claim_id']}: labeled {r['label']} with no reviewer")
    lines = ["# Shortlist — JS3 (FILTER.md v1)", "",
             "Rendered by `tools/js3_shortlist.py render` from `CLAIMS.csv`. A claim is stated as fact only if a "
             "reviewer marked it `supported` after reading the saved posting; otherwise the agent abstains.", ""]
    for row in kept:
        claims = [dict(r, label=r["label"], reviewer=r["reviewer"].strip() or None)
                  for r in rows if (r["board"], r["id"]) == (row["board"], row["id"])]
        counts = {lab: sum(c["label"] == lab for c in claims) for lab in S.LABELS}
        lines += [f"## {row['title']}", "", "```text", S.render(row, claims), "```", "",
                  "Labels: " + ", ".join(f"{k} {v}" for k, v in counts.items()), ""]
    (OUT / "SHORTLIST.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {(OUT / 'SHORTLIST.md').relative_to(ROOT)}")


if __name__ == "__main__":
    {"draft": draft, "render": render}[sys.argv[1] if len(sys.argv) > 1 else "draft"]()
