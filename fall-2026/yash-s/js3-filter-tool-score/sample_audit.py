"""Draw the reject-audit samples from a saved filter run (FILTER.md section 8).

    python3 sample_audit.py --run runs/<filter run folder> [--seed 20261118]
                            [--rejects 30] [--borderline-each 10] [--kept 10]

Three separate groups, drawn in this order with one seeded random generator, each
from postings not already drawn:

1. random_reject: a simple random sample of the rejected postings.
2. borderline: postings scoring 55-75, drawn as two halves, 55-64 and 65-75.
   This is a deliberate selection near the threshold, not a random sample of all postings.
3. kept: every confirmed posting, plus a random sample of the review queue.

Populations are sorted by board and posting ID before sampling, so the same run and
seed always give the same sample. The output folder is created new; an existing one
is never overwritten, so my hand labels cannot be replaced by a rerun.

Every hand-judgment field is left blank. This script does not judge anything.

Held-out mode, for measuring one change at a time (experiment.py):

    python3 sample_audit.py --heldout experiments/flips-<run>.json \\
        --exclude-sheet audit/sample-<run>/labeling-sheet.csv [--seed 20261124] [--flips-each 15]

draws, for each pre-registered change, a random sample of the postings that change
would flip, leaving out every posting in the excluded sheets (my tuning labels).
The held-out sheet is blind: it shows no filter decision, score, or group, so I
judge each posting before knowing what either version decided. The groups and
both decisions are kept in sample.json, which I should not open until I finish.
"""
import argparse
import csv
import json
import random
import sys
from pathlib import Path

import postings as P

HERE = Path(__file__).resolve().parent
HAND_FIELDS = ["MY_VERDICT", "MY_REASON", "FALSE_FRIEND_WORD", "MY_NOTES"]


def key(r):
    return (r["board"], str(r["id"]))


def draw(rng, population, k, taken):
    pool = sorted((r for r in population if key(r) not in taken), key=key)
    picked = rng.sample(pool, min(k, len(pool)))
    taken.update(key(r) for r in picked)
    return sorted(picked, key=key), len(pool)


HELDOUT_VERDICTS = ["reject", "keep for review", "confirm", "cannot tell"]


def sheet_keys(path):
    with open(path, encoding="utf-8", newline="") as f:
        return {(r["board"], r["posting_id"]) for r in csv.DictReader(f)}


def draw_heldout(flips, exclude, seed, each):
    """One group per change with flips: a random sample of its flipped postings that are
    not in `exclude` and not already drawn for an earlier change. Changes are taken in
    the order they were registered."""
    rng, taken, groups, pops = random.Random(seed), set(exclude), {}, {}
    for cid, info in flips["changes"].items():
        if info["flips"]:
            g = f"flip_{cid}"
            groups[g], pops[g] = draw(rng, info["flips"], each, taken)
    return groups, pops


def heldout_main(args):
    flips_path = Path(args.heldout).resolve()
    flips = json.loads(flips_path.read_text(encoding="utf-8"))
    run_name = flips["baseline_run"]
    exclude, excluded_files = set(), []
    for s in args.exclude_sheet:
        exclude |= sheet_keys(s)
        excluded_files.append({"file": str(Path(s).resolve().relative_to(HERE)), "sha256": P.sha256(s),
                               "postings": len(sheet_keys(s))})
    groups, pops = draw_heldout(flips, exclude, args.seed, args.flips_each)

    out = HERE / "audit" / f"heldout-{run_name}"
    out.mkdir()  # fails if it already exists: never overwrite hand labels

    by_key = {(p["board"], p["id"]): p for p in P.load_saved_postings(args.js2)[0]}
    drawn = sorted(((g, f) for g, fs in groups.items() for f in fs), key=lambda x: key(x[1]))
    rows, md = [], [f"# Held-out postings to judge (from {run_name})", "",
                    "Judge each posting on its own: what should the decision be for Priya? "
                    "This file shows no filter decision, score or group on purpose.",
                    f"Verdict words: {', '.join(HELDOUT_VERDICTS)}.",
                    "Every posting below is real, from my saved JS2 responses. Nothing here is constructed.", ""]
    for n, (g, f) in enumerate(drawn, 1):
        p = by_key[key(f)]
        rows.append({"row": n, "board": p["board"], "posting_id": p["id"], "title": p["title"],
                     "location": p["location"], "url": p["url"], **{h: "" for h in HAND_FIELDS}})
        md += [f"### Row {n}: {p['title']}", "",
               f"- Board: {p['board']} · ID: `{p['id']}` · Location: {p['location'] or '(none)'}",
               f"- URL: {p['url'] or '(none)'}",
               f"- Source: JS2 `runs/{p['source_run']}/{p['source_file']}`", "",
               "**Posting text (cleaned from the saved HTML):**", "", "```text",
               P.plain_text(p["markup"]) or "(empty description)", "```", ""]
    with open(out / "labeling-sheet.csv", "x", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["row", "board", "posting_id", "title", "location", "url"] + HAND_FIELDS)
        w.writeheader()
        w.writerows(rows)
    with open(out / "source-text.md", "x", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    meta = {
        "purpose": "held-out labels for experiment.py; drawn after the tuning labels and the candidate changes were fixed",
        "flips_file": str(flips_path.relative_to(HERE)), "flips_sha256": P.sha256(flips_path),
        "candidates_sha256": flips.get("candidates_sha256"), "baseline_run": run_name,
        "excluded_sheets": excluded_files, "seed": args.seed, "flips_each": args.flips_each,
        "generator": "random.Random(seed).sample per change, flip lists sorted by (board, posting ID)",
        "population_sizes_at_draw_time": pops,
        "verdict_words": HELDOUT_VERDICTS,
        "groups": {g: [{"row": next(r["row"] for r in rows if (r["board"], r["posting_id"]) == key(f)),
                        "board": f["board"], "id": f["id"], "v1.1": f["from"], "with_change": f["to"]} for f in fs]
                   for g, fs in groups.items()},
        "note": "Blind sheet: decisions are only here. No hand verdicts are filled in.",
    }
    with open(out / "sample.json", "x", encoding="utf-8") as fh:
        fh.write(json.dumps(meta, indent=2) + "\n")
    print(f"wrote {out.relative_to(HERE)}/  ({len(rows)} postings, blind)")
    for g, fs in groups.items():
        print(f"  {g:36} {len(fs):3} drawn from {pops[g]}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", help="a runs/filter-... folder written by run_filter.py")
    ap.add_argument("--js2", default=str(P.DEFAULT_JS2))
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--rejects", type=int, default=30)
    ap.add_argument("--borderline-each", type=int, default=10)
    ap.add_argument("--kept", type=int, default=10)
    ap.add_argument("--heldout", help="an experiments/flips-<run>.json file: draw the held-out sample instead")
    ap.add_argument("--exclude-sheet", action="append", default=[], help="a labeling sheet whose postings are left out")
    ap.add_argument("--flips-each", type=int, default=15)
    args = ap.parse_args(argv)
    if args.heldout:
        if args.seed is None:
            args.seed = 20261124
        return heldout_main(args)
    if not args.run:
        ap.error("--run is required unless --heldout is given")
    if args.seed is None:
        args.seed = 20261118

    run = Path(args.run).resolve()
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    rng, taken, groups, pops = random.Random(args.seed), set(), {}, {}

    rejected = [r for r in results if r["decision"] == "rejected"]
    groups["random_reject"], pops["random_reject"] = draw(rng, rejected, args.rejects, taken)
    below = [r for r in results if 55 <= r["score"] <= 64]
    above = [r for r in results if 65 <= r["score"] <= 75]
    groups["borderline_55_to_64"], pops["borderline_55_to_64"] = draw(rng, below, args.borderline_each, taken)
    groups["borderline_65_to_75"], pops["borderline_65_to_75"] = draw(rng, above, args.borderline_each, taken)
    confirmed = sorted((r for r in results if r["decision"] == "confirmed"), key=key)
    taken.update(key(r) for r in confirmed)
    groups["kept_confirmed"], pops["kept_confirmed"] = confirmed, len(confirmed)
    queue = [r for r in results if r["decision"] == "review"]
    groups["kept_review_queue"], pops["kept_review_queue"] = draw(rng, queue, args.kept, taken)

    out = HERE / "audit" / f"sample-{run.name}"
    out.parent.mkdir(exist_ok=True)
    out.mkdir()  # fails if it already exists: never overwrite hand labels

    by_key = {(p["board"], p["id"]): p for p in P.load_saved_postings(args.js2)[0]}
    rows, md = [], [f"# Postings to judge: sample from {run.name}", "",
                    "Read the posting first and decide. The filter's decision is at the end of each entry.",
                    "Every posting below is real, from my saved JS2 responses. Nothing here is constructed.", ""]
    n = 0
    for group, recs in groups.items():
        md += [f"## Group: {group} ({len(recs)})", ""]
        for r in recs:
            n += 1
            p = by_key[(r["board"], str(r["id"]))]
            rows.append({"row": n, "group": group, "board": r["board"], "posting_id": r["id"], "title": r["title"],
                         "location": r["location"], "url": r["url"],
                         "filter_decision": r["decision"], "decision_step": r["decision_step"], "score": r["score"],
                         "role": r["role"], "topics": "; ".join(r["topics"]), "skills": "; ".join(r["skills"]),
                         "location_status": r["location_status"], "experience_status": r["experience_status"],
                         "experience_reason": r["experience_reason"],
                         "filter_reasons": " | ".join(r["hard_exclusions"] or r["review_reasons"]),
                         **{f: "" for f in HAND_FIELDS}})
            md += [f"### Row {n}: {r['title']}", "",
                   f"- Board: {r['board']} · ID: `{r['id']}` · Location: {r['location'] or '(none)'}",
                   f"- URL: {r['url'] or '(none)'}",
                   f"- Source: JS2 `runs/{p['source_run']}/{p['source_file']}`", "",
                   "**Posting text (cleaned from the saved HTML):**", "", "```text",
                   P.plain_text(p["markup"]) or "(empty description)", "```", "",
                   f"**Filter said (read after you decide):** {r['decision']} at step {r['decision_step']}, "
                   f"score {r['score']}. " + (" | ".join(r["hard_exclusions"] or r["review_reasons"]) or "no reasons"), ""]

    fields = list(rows[0].keys()) if rows else []
    with open(out / "labeling-sheet.csv", "x", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    with open(out / "source-text.md", "x", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    meta = {
        "filter_run": run.name, "results_json_sha256": P.sha256(run / "results.json"),
        "filter_version": summary.get("filter_version"),
        "seed": args.seed, "generator": "random.Random(seed).sample, populations sorted by (board, posting ID)",
        "draw_order": list(groups), "sizes_requested": {"random_reject": args.rejects,
                                                          "borderline_each_half": args.borderline_each, "kept_review_queue": args.kept},
        "population_sizes_at_draw_time": pops,
        "note": ("Each group is drawn from postings not already drawn. random_reject is a simple random sample of "
                 "rejected postings. The borderline groups are a deliberate selection near the 65 threshold. "
                 "kept_review_queue is a random sample of the review queue. No hand verdicts are filled in."),
        "groups": {g: [[r["board"], r["id"]] for r in recs] for g, recs in groups.items()},
    }
    with open(out / "sample.json", "x", encoding="utf-8") as f:
        f.write(json.dumps(meta, indent=2) + "\n")

    print(f"wrote {out.relative_to(HERE)}/  ({n} postings)")
    for g, recs in groups.items():
        print(f"  {g:22} {len(recs):3} drawn from {pops[g]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
