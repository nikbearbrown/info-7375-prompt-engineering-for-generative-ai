"""The reject audit: compare a filter version's verdicts with my hand labels, set by set.

    python -B scripts/audit_report.py [--version v1.0] [--sets audit|heldout]

Written before any hand label existed (so the analysis is fixed before the answers are seen).
Reads labels/hand_labels.csv, out/audit/sample_v1.0.json and the filter's verdicts. Writes
out/audit/report_<version>_<sets>.md and .json. For each disagreement it prints every matched
word with 70 characters of context on each side, so a false friend can be read, not guessed.
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent3 import corpus, filter as flt, policy  # noqa: E402
from agent3.stats import clopper_pearson, fmt_rate  # noqa: E402

AUDIT_SETS = ("audit_reject_random", "audit_close", "audit_kept_random")
HELDOUT_SETS = ("heldout_reject", "heldout_kept_or_close")


def load_labels(path: Path) -> dict:
    with Path(path).open(encoding="utf-8", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def context(text: str, at: int, width: int = 70) -> str:
    return text[max(0, at - width):at + width].replace("\n", " ")


def is_wrong(verdict: str, hand: str) -> bool:
    return (verdict == "keep") != (hand == "relevant")


def matched_terms(r: dict) -> list:
    """(kind, term, offset or None) for every match the score counted."""
    out = [("role", w, None) for w in r["role_hits"]]
    out += [("topic", f"{g}: {m['matched']}", m["at"]) for g, m in r["topic_hits"].items()]
    out += [("skill", s, m["at"]) for s, m in r["skill_hits"].items()]
    return out


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1.0", choices=sorted(flt.VERSIONS))
    ap.add_argument("--sets", default="audit", choices=["audit", "heldout"])
    ap.add_argument("--labels", type=Path, default=ROOT / "labels" / "hand_labels.csv")
    ap.add_argument("--dry-run", action="store_true", help="print only; write nothing (for testing on fake labels)")
    args = ap.parse_args(argv)
    cfg = flt.VERSIONS[args.version]
    sample = json.loads((policy.OUT / "audit" / "sample_v1.0.json").read_text(encoding="utf-8"))
    labels = load_labels(args.labels)
    c = corpus.load()["postings"]
    names = AUDIT_SETS if args.sets == "audit" else HELDOUT_SETS
    results = {pid: flt.apply(c[pid], cfg) for s in names for pid in sample["sets"][s]}

    lines = [f"# Audit report: filter {cfg['version']} vs my hand labels ({args.sets} sets)", "",
             "Sample drawn with seed 20261124 from the v1.0 verdicts (FILTER.md section 5). "
             "A posting counts as an error when keep != (hand label == relevant).", ""]
    summary = {}
    for s in names:
        ids = sample["sets"][s]
        lab = [pid for pid in ids if pid in labels]
        wrong = [pid for pid in lab if is_wrong(results[pid]["verdict"], labels[pid]["hand_label"])]
        kept = sum(results[pid]["verdict"] == "keep" for pid in lab)
        summary[s] = {"n": len(ids), "labeled": len(lab), "wrong": len(wrong), "wrong_ids": wrong,
                      "ci95": clopper_pearson(len(wrong), len(lab)), "kept_now": kept}
        lines.append(f"- **{s}**: labeled {len(lab)}/{len(ids)}; wrong {fmt_rate(len(wrong), len(lab))}; "
                     f"kept under {cfg['version']}: {kept}")
    lines.append("")

    if args.sets == "audit" and "audit_reject_random" in summary:
        s = summary["audit_reject_random"]
        pool = sample["pool_sizes"]["rejects"]
        lo, hi = s["ci95"]
        lines += ["## What 30 random rejects can and cannot say", "",
                  f"- {s['wrong']} of {s['labeled']} random v1.0 rejects were postings I labeled relevant.",
                  f"- 95% exact interval for the reject error rate: {lo:.1%} to {hi:.1%}.",
                  f"- Scaled to all {pool} v1.0 rejects: between about {lo * pool:.0f} and {hi * pool:.0f} "
                  "relevant postings could be among them. The sample cannot tell those apart.",
                  "- The sample is random over rejects, so it says almost nothing about rare kinds of reject: "
                  "a kind that is 3% of rejects has a 40% chance of not appearing in 30 draws at all.", ""]

    lines.append("## Every disagreement, with the words that moved the score")
    for s in names:
        for pid in summary[s]["wrong_ids"]:
            r, p, h = results[pid], c[pid], labels[pid]
            lines += ["", f"### [{s}] {r['title']} ({r['board']})",
                      f"- filter: **{r['verdict']}**, {r['because']}",
                      f"- my label: **{h['hand_label']}**: {h['note']}", f"- id `{pid}`"]
            for kind, term, at in matched_terms(r):
                ctx = f'"…{context(p["content_text"], at)}…"' if at is not None else f'title: "{r["title"]}"'
                lines.append(f"  - {kind} **{term}**: {ctx}")

    # Term-level view: for each counted term, in how many labeled postings it matched, and how many were relevant.
    term = defaultdict(lambda: [0, 0])
    for pid, r in results.items():
        if pid not in labels:
            continue
        for kind, t, _ in matched_terms(r):
            key = f"{kind}:{t.split(': ')[-1].lower() if kind == 'topic' else t}"
            term[key][0] += 1
            term[key][1] += labels[pid]["hand_label"] == "relevant"
    lines += ["", "## Each counted term across the labeled postings", "",
              "| term | matched in | of those, labeled relevant |", "|---|---:|---:|"]
    for k, (n, rel) in sorted(term.items(), key=lambda kv: (-kv[1][0], kv[0])):
        lines.append(f"| {k} | {n} | {rel} |")

    name = f"report_{cfg['version']}_{args.sets}"
    if args.dry_run:
        print("\n".join(lines))
        return 0
    policy.write_bytes(policy.OUT / "audit" / f"{name}.md", ("\n".join(lines) + "\n").encode("utf-8"))
    policy.write_bytes(policy.OUT / "audit" / f"{name}.json",
                       (json.dumps({"summary": summary, "terms": term}, indent=1) + "\n").encode("utf-8"))
    print("\n".join(lines[:40]))
    print(f"... -> out/audit/{name}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
