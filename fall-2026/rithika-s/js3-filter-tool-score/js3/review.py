"""Human review of the Claude Code label suggestions.

One file holds the review decisions: labels/review_decisions.csv, one row
per posting (24 held-out + 50 audit). The reviewer edits only three columns:

    status         pending | approved | corrected
    final_verdict  relevant | not | unsure   (only when status = corrected)
    final_reason   short phrase, no commas   (only when status = corrected)
    reviewer_note  optional free text

Commands:

    python3 -m js3.review init      create review_decisions.csv, all pending
                                    (refuses if it already exists)
    python3 -m js3.review doc       (re)write labels/REVIEW.md from the
                                    suggestions and the current decisions
    python3 -m js3.review status    counts of pending/approved/corrected
    python3 -m js3.review apply --pending keep|blank [--dry-run]
                                    write the decisions into
                                    labels/<dataset>_verdicts.csv

apply: approved -> the suggested verdict and reason; corrected -> the
reviewer's final_verdict and final_reason; pending -> left as the
suggestion (--pending keep) or emptied so js3.measure reports it as
unlabeled (--pending blank). The choice is required on purpose.
A CSV row that differs from both the suggestion and the decision (an edit
made outside this file) is not overwritten unless --approve-overwrite.

Reads only labels/ (sheets, suggestions, rubric, verdict CSVs, decisions).
Never reads labels/audit_key.json or filter output. REVIEW.md must not let
the reader infer the filter's decision on any posting: it shows no filter
score or decision, never compares a title with the filter's role words
(FILTER.md R1, the same list as Priya's target title keywords), and leaves
out suggestion remarks that make that comparison (see omit_keyword_remarks).
"""

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

from js3 import batch_label as bl
from js3.filter import term_pattern

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = "review_decisions.csv"
DOC = "REVIEW.md"
STATUSES = ("pending", "approved", "corrected")
FIELDS = ["dataset", "row", "id", "board", "title", "suggested_verdict",
          "suggested_reason", "confidence", "borderline", "status",
          "final_verdict", "final_reason", "reviewer_note"]
EDITABLE = ("status", "final_verdict", "final_reason", "reviewer_note")

# Generic AI/ML-sounding title words, used only to flag titles whose
# wording and suggested verdict disagree. Deliberately not the filter's R1
# list and never compared with it. Bare "data" is not on the list: it
# matched non-ML titles such as "Data Centers".
AI_FLAVOUR = ["ai", "ml", "machine learning", "genai", "generative ai",
              "llm", "agent", "agents", "agentic", "data scientist",
              "data science", "research"]

# Suggestion text that compares a title with the target keywords (= the
# filter's R1 role words) and so hints at the filter's score.
KEYWORD_REMARK = re.compile(r"target (keyword|title)", re.IGNORECASE)

# Role-type groups for borderline cases, by title, first match wins.
ROLE_GROUPS = [
    ("Forward-deployed engineers", r"forward deployed|\bfde\b"),
    ("Applied AI Engineers on customer teams", r"applied ai engineer"),
    ("Solutions architects and developer advocates",
     r"solutions architect|developer advocate"),
    ("Research engineers and scientists",
     r"research engineer|research scientist"),
    ("Data platform, database and experimentation infrastructure",
     r"ingestion|database|experimentation|backend|data engineer"),
    ("Applied LLM, agent and AI-product engineering",
     r"agent|agentic|\bai\b|codex|cxi|growth|integration"),
    ("Unclear team or not an engineering job", r"."),
]


class ReviewError(Exception):
    """Review decisions cannot be used as they are."""


def title_hits(title, words):
    return [w for w in words if term_pattern(w).search(title or "")]


def role_group(title):
    for name, pattern in ROLE_GROUPS:
        if re.search(pattern, title or "", re.IGNORECASE):
            return name
    return ROLE_GROUPS[-1][0]


def keyword_note(s):
    """AI/ML wording in the title but suggested not or unsure, else ''."""
    if s["verdict"] == "relevant":
        return ""
    flavour = title_hits(s["title"], AI_FLAVOUR)
    flavour = [w for w in flavour
               if not any(w != o and w in o for o in flavour)]
    if not flavour:
        return ""
    return (f"AI/ML-sounding title word ({', '.join(flavour)}) but "
            f"suggested {s['verdict']}")


def omit_keyword_remarks(text):
    """Drop '; '-separated clauses that compare the title with the target
    keywords. The batch files keep the full text; only REVIEW.md omits it."""
    parts = [x for x in text.split("; ") if not KEYWORD_REMARK.search(x)]
    out = "; ".join(parts).strip()
    if out and out[-1] not in ".!?":
        out += "."
    return out[:1].upper() + out[1:]


def load_all_suggestions(labels):
    """{dataset: [suggestion, ...] in sheet order}, validated."""
    out = {}
    for dataset in bl.DATASETS:
        p = bl.paths(labels, dataset)
        sheet = bl.parse_sheet(p["sheet"])
        data = bl.load_suggestions(p, dataset)
        errors, _ = bl.validate(dataset, sheet, data,
                                bl.sha256_file(p["rubric"]))
        if errors:
            raise ReviewError(f"{dataset} suggestions invalid: {errors[0]}")
        by_id = {s["id"]: s for s in data["suggestions"]}
        out[dataset] = [by_id[r["id"]] for r in sheet]
    return out


def read_decisions(path):
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ReviewError(f"{path}: columns changed; expected {FIELDS}")
        return list(reader)


def check_decisions(decisions, suggestions):
    """Return a list of problems (empty if the decisions can be applied)."""
    problems = []
    expected = [(d, s["id"]) for d, rows in suggestions.items()
                for s in rows]
    got = [(r["dataset"], r["id"]) for r in decisions]
    if sorted(got) != sorted(expected) or len(set(got)) != len(got):
        problems.append("decision rows do not match the 74 suggested "
                        "postings one-to-one")
    by_key = {(d, s["id"]): s for d, rows in suggestions.items()
              for s in rows}
    for r in decisions:
        where = f"{r['dataset']} row {r['row']} ({r['id']})"
        s = by_key.get((r["dataset"], r["id"]))
        if s is None:
            continue
        if (r["suggested_verdict"], r["suggested_reason"]) != (
                s["verdict"], s["reason"]):
            problems.append(f"{where}: suggested_verdict/reason no longer "
                            "match the suggestion files; do not edit them")
        status = r["status"].strip().lower()
        verdict = r["final_verdict"].strip().lower()
        reason = r["final_reason"].strip()
        if status not in STATUSES:
            problems.append(f"{where}: status {r['status']!r} is not "
                            "pending/approved/corrected")
        elif status == "corrected":
            if verdict not in bl.VERDICTS:
                problems.append(f"{where}: corrected needs final_verdict "
                                "relevant/not/unsure")
            if not reason or "," in reason:
                problems.append(f"{where}: corrected needs a final_reason "
                                "without commas")
        elif status == "approved" and verdict and verdict != s["verdict"]:
            problems.append(f"{where}: approved but final_verdict "
                            f"{verdict!r} differs; use corrected")
        elif status == "pending" and (verdict or reason):
            problems.append(f"{where}: final_verdict/reason filled but "
                            "status is pending")
    return problems


# --- commands -------------------------------------------------------------

def cmd_init(args):
    labels = Path(args.labels)
    path = labels / DECISIONS
    if path.exists():
        raise ReviewError(f"{path} exists; it may hold your decisions, so "
                          "it is never recreated")
    suggestions = load_all_suggestions(labels)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for dataset, rows in suggestions.items():
            for s in rows:
                writer.writerow({
                    "dataset": dataset, "row": s["row"], "id": s["id"],
                    "board": s["board"], "title": s["title"],
                    "suggested_verdict": s["verdict"],
                    "suggested_reason": s["reason"],
                    "confidence": s["confidence"],
                    "borderline": "yes" if s["borderline"] else "no",
                    "status": "pending", "final_verdict": "",
                    "final_reason": "", "reviewer_note": ""})
    print(f"wrote {path} (74 rows, all pending)")
    return 0


def _cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def render_doc(suggestions, decisions):
    status = {(r["dataset"], r["id"]): r for r in decisions}
    counts = Counter(r["status"].strip().lower() for r in decisions)
    out = [
        "# Label review: held-out (24) and audit (50)",
        "",
        "Generated by `python3 -m js3.review doc` from "
        "`labels/suggestions/*_batch_NN.json` and "
        "`labels/review_decisions.csv`. Do not edit this file; edit "
        "`review_decisions.csv` and regenerate.",
        "",
        "**Every suggested verdict below was proposed by Claude Code, not "
        "by a human.** The *status* column shows the review state recorded "
        "in `review_decisions.csv`: `pending` means nobody has reviewed it.",
        "",
        f"Review status now: pending {counts['pending']}, approved "
        f"{counts['approved']}, corrected {counts['corrected']} "
        f"(of {len(decisions)}).",
        "",
        "No filter score or filter decision appears in this document, and "
        "`labels/audit_key.json` was not read. Titles are never compared "
        "with the filter's role words; suggestion remarks that did so are "
        "left out here (the batch files are unchanged).",
        "",
        "Legend: **B** = borderline (review first). Confidence is Claude's "
        "own: high / medium / low.",
        "",
        "## Contents",
        "",
        "1. Borderline cases grouped by role type",
        "2. Where AI/ML wording in the title may not show real job "
        "relevance",
        "3. Held-out postings (24)",
        "4. Audit postings (50)",
        "5. How to record and apply decisions",
        "",
    ]

    def ref(dataset, s):
        st = status[(dataset, s["id"])]["status"]
        return (f"{dataset} {s['row']} — {s['title']} "
                f"(`{s['id']}`): **{s['verdict']}**, {s['confidence']}, "
                f"status {st}")

    out += ["## 1. Borderline cases grouped by role type", ""]
    groups = {}
    for dataset, rows in suggestions.items():
        for s in rows:
            if s["borderline"]:
                groups.setdefault(role_group(s["title"]), []).append(
                    (dataset, s))
    for name, _ in ROLE_GROUPS:
        if name not in groups:
            continue
        verdicts = Counter(s["verdict"] for _, s in groups[name])
        out += [f"### {name} ({len(groups[name])})", "",
                "Suggested: " + ", ".join(f"{v} {n}" for v, n in
                                          sorted(verdicts.items())), ""]
        for dataset, s in groups[name]:
            out.append(f"- {ref(dataset, s)}  ")
            out.append(f"  {omit_keyword_remarks(s['borderline_note'])}")
        out.append("")

    out += ["## 2. Where AI/ML wording in the title may not show real job "
            "relevance",
            "",
            "Titles with generic AI/ML wording that were suggested not or "
            "unsure. AI/ML wording in a title is not evidence that the work "
            "fits Priya, and its absence is not evidence that it does not: "
            "judge every posting from its text.", ""]
    for dataset, rows in suggestions.items():
        for s in rows:
            note = keyword_note(s)
            if note:
                out.append(f"- {ref(dataset, s)}: {note}.")
    out.append("")

    for number, (dataset, label) in enumerate(
            (("heldout", "Held-out postings (24)"),
             ("audit", "Audit postings (50)")), 3):
        rows = suggestions[dataset]
        vc = Counter(s["verdict"] for s in rows)
        out += [f"## {number}. {label}", "",
                f"Suggested: relevant {vc['relevant']}, not {vc['not']}, "
                f"unsure {vc['unsure']}. Borderline: "
                f"{sum(s['borderline'] for s in rows)}.", "",
                "| row | B | title | board | suggested | conf. | status |",
                "|---|---|---|---|---|---|---|"]
        for s in rows:
            st = status[(dataset, s["id"])]["status"]
            out.append(f"| {s['row']} | {'**B**' if s['borderline'] else ''}"
                       f" | {_cell(s['title'])} | {s['board']} | "
                       f"{s['verdict']} | {s['confidence']} | {st} |")
        out.append("")
        for s in rows:
            d = status[(dataset, s["id"])]
            flag = " — **BORDERLINE**" if s["borderline"] else ""
            out += [f"### {dataset} {s['row']}: {s['title']}{flag}", "",
                    f"- id: `{s['id']}` · board: {s['board']}",
                    f"- suggested: **{s['verdict']}** (confidence "
                    f"{s['confidence']}) · CSV reason: {s['reason']}",
                    f"- review status: **{d['status']}**"
                    + (f" → {d['final_verdict']} ({d['final_reason']})"
                       if d["status"].strip().lower() == "corrected" else ""),
                    "- justification: "
                    + omit_keyword_remarks(s["justification"]),
                    "- evidence: " + " / ".join(f"\"{q}\""
                                                for q in s["evidence"]),
                    "- uncertainty: "
                    + omit_keyword_remarks(s["uncertainty"])]
            if s["borderline"]:
                out.append("- borderline: "
                           + omit_keyword_remarks(s["borderline_note"]))
            note = keyword_note(s)
            if note:
                out.append(f"- keyword note: {note}")
            if d["reviewer_note"].strip():
                out.append(f"- reviewer note: {d['reviewer_note']}")
            out.append("")

    out += [
        "## 5. How to record and apply decisions",
        "",
        "1. Open `labels/review_decisions.csv` (one row per posting). Edit "
        "only `status`, `final_verdict`, `final_reason`, `reviewer_note`.",
        "   - agree: set `status` to `approved` and leave the final columns "
        "empty;",
        "   - disagree: set `status` to `corrected`, `final_verdict` to "
        "relevant / not / unsure, and `final_reason` to a short phrase "
        "without commas;",
        "   - not yet looked at: leave `pending`.",
        "2. `python3 -m js3.review status` shows progress; "
        "`python3 -m js3.review doc` refreshes this document.",
        "3. `python3 -m js3.review apply --pending blank --dry-run` shows "
        "what would change; drop `--dry-run` to write the two verdict CSVs.",
        "   `--pending blank` empties unreviewed rows so measurement reports "
        "them as unlabeled; `--pending keep` leaves Claude's suggestion in "
        "place for them (then the measurement is partly Claude's judgment).",
        "4. `python3 -m js3.batch_label check` confirms the CSVs and counts "
        "rows that differ from the suggestion.",
        "",
    ]
    return "\n".join(out)


def cmd_doc(args):
    labels = Path(args.labels)
    suggestions = load_all_suggestions(labels)
    decisions = read_decisions(labels / DECISIONS)
    problems = check_decisions(decisions, suggestions)
    if problems:
        raise ReviewError("review_decisions.csv: " + "; ".join(problems[:5]))
    (labels / DOC).write_text(
        render_doc(suggestions, decisions), "utf-8")
    print(f"wrote {labels / DOC}")
    return 0


def cmd_status(args):
    labels = Path(args.labels)
    suggestions = load_all_suggestions(labels)
    decisions = read_decisions(labels / DECISIONS)
    for dataset in bl.DATASETS:
        rows = [r for r in decisions if r["dataset"] == dataset]
        c = Counter(r["status"].strip().lower() for r in rows)
        print(f"{dataset}: pending {c['pending']}, approved "
              f"{c['approved']}, corrected {c['corrected']} "
              f"(of {len(rows)})")
    problems = check_decisions(decisions, suggestions)
    for p in problems:
        print(f"PROBLEM: {p}")
    return 1 if problems else 0


def planned_csv(dataset, suggestions, decisions, pending):
    by_id = {r["id"]: r for r in decisions if r["dataset"] == dataset}
    rows = []
    for s in suggestions[dataset]:
        d = by_id[s["id"]]
        status = d["status"].strip().lower()
        if status == "approved":
            verdict, reason = s["verdict"], s["reason"]
        elif status == "corrected":
            verdict = d["final_verdict"].strip().lower()
            reason = d["final_reason"].strip()
        elif pending == "keep":
            verdict, reason = s["verdict"], s["reason"]
        else:
            verdict, reason = "", ""
        rows.append({"id": s["id"], "verdict": verdict, "reason": reason})
    return rows


def cmd_apply(args):
    labels = Path(args.labels)
    suggestions = load_all_suggestions(labels)
    decisions = read_decisions(labels / DECISIONS)
    problems = check_decisions(decisions, suggestions)
    if problems:
        raise ReviewError("not applied:\n  " + "\n  ".join(problems))
    plans = {}
    for dataset in bl.DATASETS:
        path = bl.paths(labels, dataset)["csv"]
        current = bl.read_csv(path)
        planned = planned_csv(dataset, suggestions, decisions, args.pending)
        if [r["id"] for r in current] != [r["id"] for r in planned]:
            raise ReviewError(f"{path}: ids or order differ from the sheet")
        sugg = {s["id"]: s for s in suggestions[dataset]}
        foreign = [c["id"] for c, p in zip(current, planned)
                   if c["verdict"].strip() and c != p
                   and (c["verdict"], c["reason"]) != (
                       sugg[c["id"]]["verdict"], sugg[c["id"]]["reason"])]
        if foreign and not args.approve_overwrite:
            raise ReviewError(
                f"{path}: {len(foreign)} row(s) were edited outside "
                f"review_decisions.csv (first {foreign[0]}); record them "
                "there or rerun with --approve-overwrite")
        changes = sum(1 for c, p in zip(current, planned) if c != p)
        plans[dataset] = (path, planned, changes)

    for dataset, (path, planned, changes) in plans.items():
        c = Counter(r["status"].strip().lower() for r in decisions
                    if r["dataset"] == dataset)
        print(f"{dataset}: approved {c['approved']}, corrected "
              f"{c['corrected']}, pending {c['pending']} "
              f"({args.pending}); {changes} CSV row(s) "
              f"{'would change' if args.dry_run else 'changed'}")
        if not args.dry_run:
            with open(path, "w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=bl.COLUMNS)
                writer.writeheader()
                writer.writerows(planned)
    if args.dry_run:
        print("dry run: nothing written")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--labels", default="labels")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("doc")
    sub.add_parser("status")
    apply = sub.add_parser("apply")
    apply.add_argument("--pending", choices=("keep", "blank"), required=True)
    apply.add_argument("--dry-run", action="store_true")
    apply.add_argument("--approve-overwrite", action="store_true")
    args = parser.parse_args(argv)
    commands = {"init": cmd_init, "doc": cmd_doc, "status": cmd_status,
                "apply": cmd_apply}
    try:
        return commands[args.command](args)
    except (ReviewError, bl.LabelError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
