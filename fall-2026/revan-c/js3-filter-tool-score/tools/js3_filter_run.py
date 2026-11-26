"""Run FILTER.md v1 on the JS2 snapshot and write the audit view, the audit sample, and the label split.

Usage: .venv/bin/python tools/js3_filter_run.py [--out runs/js3/filter_v1]

Writes (all inside --out):
  summary.json         board counts vs FILTER.md's expected counts, fates, kept ranking, closest calls
  audit_view.csv       one row per posting: key, source, every rule, components, total, fate
  audit_view.json      the same rows with matched words and quoted evidence
  audit_sample.json    the reject sample (seeded), the closest calls, the kept sample, and the label split
  LABEL_SHEET.csv      blind sheet for hand verdicts: no filter output in it
  READING.md           full text of every posting on the sheet, in sheet order, no filter output

Seeds are fixed strings from FILTER.md section 6 and this file; the sample depends only on (seed, board, id).
"""
import argparse
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jsfilter import filter as F  # noqa: E402

REJECT_SEED = "js3-reject-audit-2026-11-25"     # chosen by Claude Code; recorded before the sample was drawn
SPLIT_SEED = "js3-label-split-2026-11-25"       # FILTER.md section 6
SHEET_SEED = "js3-sheet-order-2026-11-25"      # chosen by Claude Code; only the reading order depends on it
N_REJECTS = 30


def split(keys, seed):
    """FILTER.md 6: 50% train, 25% dev, 25% held-out within a stratum; the remainder goes to train."""
    ordered = F._seeded_order([{"board": b, "id": i} for b, i in keys], seed)
    n = len(ordered)
    n_dev = n_held = n // 4
    roles = {}
    for pos, r in enumerate(ordered):
        roles[(r["board"], r["id"])] = ("held_out" if pos < n_held else
                                         "dev" if pos < n_held + n_dev else "train")
    return roles


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="runs/js3/filter_v1")
    args = ap.parse_args(argv)
    out = ROOT / args.out
    label_sheet = out / "LABEL_SHEET.csv"
    if label_sheet.exists():
        with label_sheet.open(newline="") as fh:
            if any(row.get("hand_verdict", "").strip() or row.get("reason", "").strip()
                   for row in csv.DictReader(fh)):
                sys.exit(f"{label_sheet.relative_to(ROOT)} has reviewed verdicts; refusing to overwrite it")
    out.mkdir(parents=True, exist_ok=True)

    resume = json.loads((ROOT / "resumes" / "aarav-patel.json").read_text())
    boards = F.load_snapshot(ROOT)
    descriptions = {(p["board"], p["id"]): p for b in boards for p in b["postings"]}
    result = F.run_filter(resume, boards)
    rows = result["rows"]

    # ---- summary ----
    closest = F.closest_calls(rows)
    summary = {
        "filter_version": F.FILTER_VERSION, "snapshot_trace": F.SNAPSHOT_TRACE,
        "boards": {b: {**s, "expected": F.EXPECTED_COUNTS[b],
                       "matches_expected": s["scored"] == F.EXPECTED_COUNTS[b]}
                   for b, s in result["boards"].items()},
        "total_scored": len(rows),
        "fates": {f: sum(r["fate"] == f for r in rows) for f in F.FATES},
        "kept_ranked": [{k: r[k] for k in ("board", "id", "title", "total", "components")} for r in result["kept"]],
        "closest_calls": [{k: r[k] for k in ("board", "id", "title", "total", "failed_rules")} for r in closest],
        "threshold": F.THRESHOLD,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (out / "audit_view.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    with (out / "audit_view.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["board", "id", "title", "location", "workplace_type", "source_path", "index",
                    "R1", "R2", "R3", "R4", "R5", "R6", "role", "topic", "skill", "total",
                    "zero_topic", "zero_skill", "failed_rules", "fate", "topic_words", "skill_words"])
        for r in rows:
            rr = r["rules"]
            w.writerow([r["board"], r["id"], r["title"], r["location"], r["workplace_type"] or "",
                        r["source_path"], r["index"]]
                       + [int(rr[k]["passed"]) if rr else "" for k in ("R1", "R2", "R3", "R4", "R5", "R6")]
                       + ([r["components"][k] for k in ("role", "topic", "skill")] if r["components"] else ["", "", ""])
                       + [r["total"], r["zero_topic"], r["zero_skill"], ";".join(r["failed_rules"]), r["fate"],
                          ";".join(rr["R5"]["matched"]) if rr else "", ";".join(rr["R6"]["matched"]) if rr else ""])

    # ---- audit sample ----
    rejects = F.sample_rejects(rows, N_REJECTS, REJECT_SEED)
    kept = F.sample_kept(rows, len(result["kept"]), "all-kept")   # all kept postings: the kept sample is every one
    strata = {}
    for name, group in (("random_reject", rejects), ("closest_call", closest), ("kept", kept)):
        for r in group:
            strata.setdefault((r["board"], r["id"]), []).append(name)
    # Sheet order is a seeded shuffle, so a row's position does not reveal its stratum or the filter's verdict.
    unique = {(r["board"], r["id"]): r for r in rejects + closest + kept}
    sheet = [(r["board"], r["id"]) for r in F._seeded_order(list(unique.values()), SHEET_SEED)]

    # Label split within the filter's kept and rejected strata (FILTER.md 6). Uses keys and fates only.
    by_key = {(r["board"], r["id"]): r for r in rows}
    kept_keys = [k for k in sheet if by_key[k]["fate"] == "kept"]
    rej_keys = [k for k in sheet if by_key[k]["fate"] != "kept"]
    roles = {**split(kept_keys, SPLIT_SEED), **split(rej_keys, SPLIT_SEED)}

    sample = {
        "reject_seed": REJECT_SEED, "split_seed": SPLIT_SEED, "n_random_rejects": N_REJECTS,
        "reject_population": sum(r["fate"] in F.REJECT_FATES for r in rows),
        "kept_population": len(result["kept"]),
        "sheet": [{"audit_id": f"A{n:02d}", "board": b, "id": i, "strata": strata[(b, i)],
                   "split": roles[(b, i)]} for n, (b, i) in enumerate(sheet, start=1)],
    }
    sample["split_sizes"] = {s: {"kept": sum(1 for e in sample["sheet"] if e["split"] == s and "kept" in e["strata"]),
                                 "rejected": sum(1 for e in sample["sheet"] if e["split"] == s and "kept" not in e["strata"])}
                             for s in ("train", "dev", "held_out")}
    (out / "audit_sample.json").write_text(json.dumps(sample, indent=2) + "\n")

    # ---- blind label sheet and reading aid ----
    with (out / "LABEL_SHEET.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["audit_id", "board", "id", "title", "location", "url",
                    "hand_verdict", "reason", "decisive_excerpt", "false_friend_word", "labeled_at"])
        for e in sample["sheet"]:
            r = by_key[(e["board"], e["id"])]
            w.writerow([e["audit_id"], e["board"], e["id"], r["title"], r["location"]
                        + (f" | workplaceType: {r['workplace_type']}" if r["workplace_type"] else ""),
                        r["url"], "", "", "", "", ""])
    lines = ["# Audit reading aid — JS3",
             "",
             "Full text of every posting on `LABEL_SHEET.csv`, in sheet order, from the JS2 snapshot "
             f"(`{F.SNAPSHOT_TRACE}`). **No filter output is shown here**, so verdicts are not anchored on it. "
             "Text is the saved posting with HTML stripped; whitespace collapsed.",
             ""]
    for e in sample["sheet"]:
        p = descriptions[(e["board"], e["id"])]
        lines += [f"## {e['audit_id']} — {p['title']}", "",
                  f"- board: `{e['board']}` · id: `{e['id']}` · location: {p['location']}"
                  + (f" · workplaceType: {p['workplace_type']}" if p["workplace_type"] else ""),
                  f"- source: `{p['source_path']}` (index {p['index']})", "",
                  " ".join((p["description"] or "").split()), ""]
    (out / "READING.md").write_text("\n".join(lines) + "\n")

    print(json.dumps({"out": args.out, "scored": len(rows), "fates": summary["fates"],
                      "sheet_rows": len(sheet), "split_sizes": sample["split_sizes"]}, indent=1))


if __name__ == "__main__":
    main()
