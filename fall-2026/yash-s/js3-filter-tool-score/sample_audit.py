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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True, help="a runs/filter-... folder written by run_filter.py")
    ap.add_argument("--js2", default=str(P.DEFAULT_JS2))
    ap.add_argument("--seed", type=int, default=20261118)
    ap.add_argument("--rejects", type=int, default=30)
    ap.add_argument("--borderline-each", type=int, default=10)
    ap.add_argument("--kept", type=int, default=10)
    args = ap.parse_args(argv)

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
