"""Batch labeling workflow for the held-out and audit sheets.

The verdicts themselves are SUGGESTIONS recorded by Claude Code in
labels/suggestions/<dataset>_batch_NN.json, one batch at a time, from the blind
sheet only (see labels/LABELING_RUBRIC.md and labels/LABELING_METHOD.md).
This script does everything around that judgment, reproducibly:

    python3 -m js3.batch_label show --dataset heldout --batch 1
        print one batch of postings from the blind sheet (what the labeler
        sees; nothing else is read)
    python3 -m js3.batch_label assemble --dataset heldout
        validate the suggestions against the sheet and the rubric hash,
        write labels/<dataset>_verdicts.csv (id,verdict,reason) and
        labels/suggestions/<dataset>_review.md
    python3 -m js3.batch_label check
        quality checks on both verdict CSVs and both suggestion files;
        counts per dataset; borderline cases; how many CSV verdicts now
        differ from the suggestion (i.e. were changed by a human)

It reads only labels/<dataset>_sheet.md, labels/<dataset>_verdicts.csv,
labels/LABELING_RUBRIC.md and labels/suggestions/. It never reads
labels/audit_key.json or any filter output.

A verdict CSV that already holds a verdict different from what would be
written is never overwritten unless --approve-overwrite is given.
"""

import argparse
import csv
import difflib
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

DATASETS = {"heldout": 24, "audit": 50}
VERDICTS = ("relevant", "not", "unsure")
CONFIDENCE = ("high", "medium", "low")
COLUMNS = ["id", "verdict", "reason"]
BATCH_SIZE = 8
RUBRIC = "LABELING_RUBRIC.md"
REASON_MAX_WORDS = 10
SIMILAR = 0.85

_FIELD = re.compile(r"^- (board|id|title|location|url): ?(.*)$")


class LabelError(Exception):
    """Suggestions or verdict files fail a check."""


def norm(text):
    return re.sub(r"\s+", " ", text or "").strip()


def parse_sheet(path):
    """Return the sheet's postings in row order."""
    rows, current, body, in_body = [], None, [], False
    for line in Path(path).read_text("utf-8").splitlines():
        if in_body:
            if line == "~~~~":
                current["body"] = "\n".join(body)
                in_body, body = False, []
            else:
                body.append(line)
            continue
        heading = re.match(r"^## (\d+)$", line)
        if heading:
            current = {"row": int(heading.group(1))}
            rows.append(current)
        elif current is not None and line == "~~~~text":
            in_body = True
        elif current is not None:
            field = _FIELD.match(line)
            if field:
                current[field.group(1)] = field.group(2)
    for number, row in enumerate(rows, 1):
        if row["row"] != number or "body" not in row or "id" not in row:
            raise LabelError(f"{path}: row {number} is malformed")
        if row["body"] == "(no body text)":
            row["body"] = ""
    return rows


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def batch_of(row, size=BATCH_SIZE):
    return math.ceil(row / size)


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != COLUMNS:
            raise LabelError(f"{path}: columns {reader.fieldnames}, "
                             f"expected {COLUMNS}")
        return list(reader)


def paths(labels, dataset):
    labels = Path(labels)
    return {
        "sheet": labels / f"{dataset}_sheet.md",
        "csv": labels / f"{dataset}_verdicts.csv",
        "suggestions": labels / "suggestions",
        "review": labels / "suggestions" / f"{dataset}_review.md",
        "rubric": labels / RUBRIC,
    }


# --- validation -----------------------------------------------------------

def validate(dataset, sheet, data, rubric_sha):
    """Return (errors, warnings) for one suggestion file."""
    errors, warnings = [], []
    if data.get("dataset") != dataset:
        errors.append(f"dataset is {data.get('dataset')!r}")
    if data.get("rubric_sha256") != rubric_sha:
        errors.append("rubric_sha256 does not match labels/"
                      f"{RUBRIC}: the criteria changed after labeling")
    if data.get("human_reviewed") is not False:
        errors.append("human_reviewed must stay false in the suggestion "
                      "file; human review is recorded in the CSV and in "
                      "LABELING_METHOD.md")
    by_id = {r["id"]: r for r in sheet}
    seen = Counter(s.get("id") for s in data.get("suggestions", []))
    for pid, n in seen.items():
        if n > 1:
            errors.append(f"id {pid}: {n} suggestions")
        if pid not in by_id:
            errors.append(f"id {pid}: not on the {dataset} sheet")
    for pid in by_id:
        if pid not in seen:
            errors.append(f"id {pid}: no suggestion")
    if len(sheet) != DATASETS[dataset]:
        errors.append(f"sheet has {len(sheet)} rows, expected "
                      f"{DATASETS[dataset]}")

    for s in data.get("suggestions", []):
        pid = s.get("id")
        row = by_id.get(pid)
        if row is None:
            continue
        where = f"row {row['row']} ({pid})"
        for field in ("board", "title"):
            if norm(s.get(field)) != norm(row[field]):
                errors.append(f"{where}: {field} {s.get(field)!r} != "
                              f"sheet {row[field]!r}")
        if s.get("row") != row["row"]:
            errors.append(f"{where}: row {s.get('row')} != sheet")
        if s.get("batch") != batch_of(row["row"]):
            errors.append(f"{where}: batch {s.get('batch')} != "
                          f"{batch_of(row['row'])}")
        if s.get("verdict") not in VERDICTS:
            errors.append(f"{where}: verdict {s.get('verdict')!r}")
        if s.get("confidence") not in CONFIDENCE:
            errors.append(f"{where}: confidence {s.get('confidence')!r}")
        reason = s.get("reason") or ""
        if not reason.strip() or "," in reason \
                or len(reason.split()) > REASON_MAX_WORDS:
            errors.append(f"{where}: reason must be one short phrase "
                          f"without commas: {reason!r}")
        for field in ("justification", "uncertainty"):
            if not norm(s.get(field)):
                errors.append(f"{where}: empty {field}")
        evidence = s.get("evidence") or []
        if not evidence:
            errors.append(f"{where}: no evidence quote")
        texts = [norm(row["title"]), norm(row["location"]),
                 norm(row["body"])]
        for quote in evidence:
            q = norm(quote)
            if not q or not any(q in t for t in texts):
                errors.append(f"{where}: evidence not found verbatim in "
                              f"this posting's sheet text: {quote!r}")
        must_flag = (s.get("verdict") == "unsure"
                     or s.get("confidence") == "low")
        if must_flag and not s.get("borderline"):
            errors.append(f"{where}: unsure/low must be borderline")
        if s.get("borderline") and not norm(s.get("borderline_note")):
            errors.append(f"{where}: borderline without borderline_note")

    sugg = data.get("suggestions", [])
    for i, a in enumerate(sugg):
        for b in sugg[i + 1:]:
            ratio = difflib.SequenceMatcher(
                None, norm(a.get("justification")).lower(),
                norm(b.get("justification")).lower()).ratio()
            if ratio >= SIMILAR:
                warnings.append(f"justifications of {a.get('id')} and "
                                f"{b.get('id')} are {ratio:.0%} similar")
    return errors, warnings


def batch_files(p, dataset):
    return sorted(p["suggestions"].glob(f"{dataset}_batch_*.json"))


def load_suggestions(p, dataset):
    """Merge labels/suggestions/<dataset>_batch_NN.json into one record.

    Every batch file must name the same dataset, rubric hash and labeler,
    keep human_reviewed false, and hold only rows of its own batch.
    """
    files = batch_files(p, dataset)
    if not files:
        raise LabelError(f"no {dataset}_batch_*.json in {p['suggestions']}")
    merged = {"dataset": dataset, "suggestions": [], "batches": []}
    for path in files:
        data = json.loads(path.read_text("utf-8"))
        for field in ("dataset", "rubric_sha256", "labeler",
                      "human_reviewed"):
            if field in merged and merged[field] != data.get(field):
                raise LabelError(f"{path.name}: {field} differs from "
                                 "the other batch files")
            merged[field] = data.get(field)
        for s in data.get("suggestions", []):
            if s.get("batch") != data.get("batch"):
                raise LabelError(f"{path.name}: row {s.get('row')} has "
                                 f"batch {s.get('batch')}")
        merged["batches"].append(data.get("batch"))
        merged["suggestions"] += data.get("suggestions", [])
    return merged


# --- commands -------------------------------------------------------------

def cmd_show(args):
    sheet = parse_sheet(paths(args.labels, args.dataset)["sheet"])
    rows = [r for r in sheet if batch_of(r["row"]) == args.batch]
    if not rows:
        raise LabelError(f"no batch {args.batch}")
    for r in rows:
        print(f"## row {r['row']} | {r['board']} | {r['id']}")
        print(f"title: {r['title']}")
        print(f"location: {r['location']}")
        print(r["body"] or "(no body text)")
        print()
    return 0


def planned_rows(sheet, data):
    by_id = {s["id"]: s for s in data["suggestions"]}
    return [{"id": r["id"], "verdict": by_id[r["id"]]["verdict"],
             "reason": by_id[r["id"]]["reason"]} for r in sheet]


def cmd_assemble(args):
    p = paths(args.labels, args.dataset)
    sheet = parse_sheet(p["sheet"])
    data = load_suggestions(p, args.dataset)
    errors, warnings = validate(args.dataset, sheet, data,
                                sha256_file(p["rubric"]))
    for w in warnings:
        print(f"WARNING: {w}")
    if errors:
        raise LabelError("suggestions invalid:\n  " + "\n  ".join(errors))

    existing = read_csv(p["csv"])
    if [r["id"] for r in existing] != [r["id"] for r in sheet]:
        raise LabelError(f"{p['csv']} ids differ from the sheet; not "
                         "touching it")
    planned = planned_rows(sheet, data)
    conflicts = [old["id"] for old, new in zip(existing, planned)
                 if old["verdict"].strip() and old != new]
    if conflicts and not args.approve_overwrite:
        raise LabelError(f"{p['csv']} already has {len(conflicts)} "
                         "verdict(s) that differ from the suggestions "
                         "(first: " + conflicts[0] + "). Not overwritten; "
                         "rerun with --approve-overwrite only if you mean "
                         "to replace them.")
    with open(p["csv"], "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(planned)
    p["review"].write_text(render_review(args.dataset, sheet, data),
                           "utf-8")
    print(f"wrote {p['csv']} ({len(planned)} rows) and {p['review']}")
    return 0


def render_review(dataset, sheet, data):
    by_id = {s["id"]: s for s in data["suggestions"]}
    counts = Counter(s["verdict"] for s in data["suggestions"])
    out = [f"# {dataset}: Claude Code suggestions for review",
           "",
           "AUTOMATED SUGGESTIONS, NOT REVIEWED BY A HUMAN. Each verdict "
           "below was proposed by Claude Code from the blind sheet text "
           f"only, using labels/{RUBRIC} (sha256 "
           f"{data['rubric_sha256'][:12]}...). They become your verdicts "
           "only after you review them in the CSV.",
           "",
           f"Counts: relevant {counts['relevant']}, not {counts['not']}, "
           f"unsure {counts['unsure']}.",
           "",
           "## Borderline cases (review these first)", ""]
    for r in sheet:
        s = by_id[r["id"]]
        if s["borderline"]:
            out.append(f"- row {r['row']} `{r['id']}` {r['title']}: "
                       f"**{s['verdict']}** ({s['confidence']}). "
                       f"{s['borderline_note']}")
    out += ["", "## All postings", ""]
    for r in sheet:
        s = by_id[r["id"]]
        out += [f"### row {r['row']}: {r['title']}",
                "",
                f"- id: `{r['id']}` | board: {r['board']} | batch "
                f"{s['batch']}",
                f"- suggested verdict: **{s['verdict']}** "
                f"(confidence {s['confidence']})",
                f"- CSV reason: {s['reason']}",
                f"- justification: {s['justification']}",
                "- evidence: " + " / ".join(f"\"{q}\""
                                            for q in s["evidence"]),
                f"- uncertainty: {s['uncertainty']}",
                ""]
    return "\n".join(out)


def check_dataset(labels, dataset):
    """Return (report lines, error count)."""
    p = paths(labels, dataset)
    lines, nerr = [f"== {dataset}"], 0
    sheet = parse_sheet(p["sheet"])
    rows = read_csv(p["csv"])
    ids = [r["id"] for r in rows]
    sheet_ids = [r["id"] for r in sheet]
    problems = []
    if len(rows) != DATASETS[dataset]:
        problems.append(f"{len(rows)} rows, expected {DATASETS[dataset]}")
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    if dupes:
        problems.append(f"duplicate ids: {dupes}")
    missing = sorted(set(sheet_ids) - set(ids))
    extra = sorted(set(ids) - set(sheet_ids))
    if missing:
        problems.append(f"ids on the sheet but not in the CSV: {missing}")
    if extra:
        problems.append(f"ids in the CSV but not on the sheet: {extra}")
    blank = [r["id"] for r in rows if not r["verdict"].strip()]
    if blank:
        problems.append(f"{len(blank)} blank verdict(s): {blank}")
    bad = [r["id"] for r in rows
           if r["verdict"].strip() and r["verdict"].strip() not in VERDICTS]
    if bad:
        problems.append(f"verdicts outside relevant/not/unsure: {bad}")
    lines.append(f"rows {len(rows)}; one verdict each: "
                 f"{'yes' if not (blank or dupes) else 'NO'}; "
                 f"duplicates {len(dupes)}; missing {len(missing)}; "
                 f"invalid verdicts {len(bad)}")
    counts = Counter(r["verdict"].strip() for r in rows)
    lines.append(f"CSV counts: relevant {counts['relevant']}, not "
                 f"{counts['not']}, unsure {counts['unsure']}")

    if batch_files(p, dataset):
        data = load_suggestions(p, dataset)
        errors, warnings = validate(dataset, sheet, data,
                                    sha256_file(p["rubric"]))
        problems += errors
        lines += [f"WARNING: {w}" for w in warnings]
        by_id = {s["id"]: s for s in data["suggestions"]}
        changed = [r["id"] for r in rows if r["id"] in by_id
                   and r["verdict"].strip() and (
            r["verdict"].strip() != by_id[r["id"]]["verdict"]
            or r["reason"] != by_id[r["id"]]["reason"])]
        lines.append(f"suggestions validated: {len(by_id)}; evidence "
                     "quotes all found verbatim: "
                     f"{'yes' if not errors else 'see errors'}")
        lines.append(f"CSV rows that differ from the Claude suggestion "
                     f"(changed by a human): {len(changed)}"
                     + (f" {changed}" if changed else ""))
        border = [s for s in data["suggestions"] if s.get("borderline")]
        lines.append(f"borderline: {len(border)}")
        for s in sorted(border, key=lambda s: s["row"]):
            lines.append(f"  row {s['row']} {s['id']} {s['title']!r}: "
                         f"{s['verdict']} ({s['confidence']})")
    else:
        lines.append("no suggestion file")
    lines += [f"ERROR: {e}" for e in problems]
    nerr += len(problems)
    return lines, nerr


def cmd_check(args):
    total = 0
    for dataset in DATASETS:
        lines, nerr = check_dataset(args.labels, dataset)
        print("\n".join(lines))
        total += nerr
    print(f"\n{'OK' if not total else f'{total} problem(s)'}")
    return 0 if not total else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--labels", default="labels")
    sub = parser.add_subparsers(dest="command", required=True)
    show = sub.add_parser("show")
    show.add_argument("--dataset", choices=DATASETS, required=True)
    show.add_argument("--batch", type=int, required=True)
    assemble = sub.add_parser("assemble")
    assemble.add_argument("--dataset", choices=DATASETS, required=True)
    assemble.add_argument("--approve-overwrite", action="store_true")
    sub.add_parser("check")
    args = parser.parse_args(argv)
    try:
        return {"show": cmd_show, "assemble": cmd_assemble,
                "check": cmd_check}[args.command](args)
    except LabelError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
