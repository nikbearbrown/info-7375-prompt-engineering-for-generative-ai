"""Run FILTER.md v1.1 over every saved JS2 posting and save the results.

    python3 run_filter.py [--js2 PATH] [--runs-dir runs]

Reads the saved JS2 responses (read-only), checks that the input is complete
(2,418 unique postings, FILTER.md section 2), scores and decides every posting,
and writes a new folder runs/filter-v1.1-<UTC time>/. Files are create-only: an
existing results folder is never overwritten. No network is used.

Exit codes: 0 results saved; 2 the input was incomplete, so nothing was scored.
"""
import argparse
import collections
import datetime
import hashlib
import json
import platform
import sys
from pathlib import Path

import job_filter as J
import postings as P

HERE = Path(__file__).resolve().parent


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_run_dir(runs_dir, name):
    runs_dir.mkdir(parents=True, exist_ok=True)
    path, n = runs_dir / name, 2
    while path.exists():
        path, n = runs_dir / f"{name}-{n}", n + 1
    path.mkdir()
    return path


def write_new(path, text):
    with open(path, "x", encoding="utf-8") as f:  # create-only
        f.write(text)


def dump(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def reason_type(reason):
    for prefix, label in (("excluded title", "excluded title"), ("seniority word", "seniority word in title"),
                          ("seniority statement", "seniority statement in description"),
                          ("special program", "special program"), ("no matching role", "no matching role"),
                          ("every location part", "outside the US"),
                          ("mandatory requirement", "experience above the 2-year cutoff"),
                          ("special review role", "special review role"), ("experience unknown", "experience unknown"),
                          ("location unknown", "location unknown"), ("minimum experience", "1-2 year minimum"),
                          ("matches no résumé skill", "no résumé skill"), ("failed confirmed", "failed a confirmed condition")):
        if reason.startswith(prefix):
            return label
    return reason


def summarize(results, rules):
    S = rules["filter"]["scoring"]
    lo, hi = S["near_threshold_range"]
    by_board = collections.defaultdict(collections.Counter)
    for r in results:
        by_board[r["board"]][r["decision"]] += 1
    hard = collections.Counter(reason_type(x) for r in results for x in r["hard_exclusions"])
    review = collections.Counter(reason_type(x) for r in results if r["decision"] == "review" for x in r["review_reasons"])
    bins = collections.Counter(f"{10 * (r['score'] // 10)}-{10 * (r['score'] // 10) + 9}" for r in results)
    return {
        "decisions": dict(collections.Counter(r["decision"] for r in results)),
        "decisions_by_board": {b: dict(c) for b, c in sorted(by_board.items())},
        "rejected_by_step": dict(collections.Counter(r["decision_step"] for r in results if r["decision"] == "rejected")),
        "hard_exclusion_reasons": dict(hard.most_common()),
        "review_reasons": dict(review.most_common()),
        "role_categories": dict(collections.Counter(r["role"] for r in results)),
        "experience_status": dict(collections.Counter(r["experience_status"] for r in results)),
        "location_status": dict(collections.Counter(r["location_status"] for r in results)),
        "score_bins": dict(sorted(bins.items(), key=lambda x: int(x[0].split("-")[0]))),
        "near_threshold_count": sum(lo <= r["score"] <= hi for r in results),
        "rejected_with_score_at_least_threshold": sum(r["decision"] == "rejected" and r["score"] >= S["threshold"] for r in results),
    }


def report_md(meta, summ, confirmed, candidates):
    L = [f"# Filter run {meta['run']}", "",
         f"FILTER.md Version {meta['filter_version']} on {meta['postings']['total']} saved JS2 postings. "
         f"Approved boilerplate sentences: {meta['approved_boilerplate_sentences']}. No network was used.", "",
         "| Decision | Count |", "|---|---:|"]
    for k in ("confirmed", "review", "rejected"):
        L.append(f"| {k} | {summ['decisions'].get(k, 0)} |")
    L += ["", "| Board | Confirmed | Review | Rejected |", "|---|---:|---:|---:|"]
    for b, c in summ["decisions_by_board"].items():
        L.append(f"| {b} | {c.get('confirmed', 0)} | {c.get('review', 0)} | {c.get('rejected', 0)} |")
    L += ["", "## Confirmed shortlist", ""]
    if confirmed:
        L += ["| Board | ID | Title | Score |", "|---|---|---|---:|"]
        L += [f"| {r['board']} | {r['id']} | {r['title']} | {r['score']} |" for r in confirmed]
    else:
        L.append("Empty: no posting met every confirmed-shortlist condition.")
    L += ["", "## Review-candidate shortlist (top 10 of the review queue; unconfirmed)", "",
          "| # | Board | ID | Title | Score | Why it is not confirmed |", "|---:|---|---|---|---:|---|"]
    for i, r in enumerate(candidates, 1):
        L.append(f"| {i} | {r['board']} | {r['id']} | {r['title']} | {r['score']} | {'; '.join(r['review_reasons'])} |")
    L += ["", "## Hard-exclusion reasons (a posting can have several)", "", "| Reason | Postings |", "|---|---:|"]
    L += [f"| {k} | {v} |" for k, v in summ["hard_exclusion_reasons"].items()]
    L += ["", "## Review reasons", "", "| Reason | Postings |", "|---|---:|"]
    L += [f"| {k} | {v} |" for k, v in summ["review_reasons"].items()]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--js2", default=str(P.DEFAULT_JS2), help="the JS2 project folder (read-only)")
    ap.add_argument("--runs-dir", default=str(HERE / "runs"))
    args = ap.parse_args(argv)
    js2 = Path(args.js2).resolve()

    all_postings, sources = P.load_saved_postings(js2)
    persona, persona_src = P.load_persona(js2)
    rules = J.load_rules(persona=persona)
    expected = rules["filter"]["expected_postings"]
    counts = collections.Counter(p["board"] for p in all_postings)
    problems = [f"{b}: expected {expected[b]}, found {counts.get(b, 0)}" for b in ("Databricks", "Anthropic", "OpenAI")
                if counts.get(b, 0) != expected[b]]
    if len(all_postings) != expected["total"]:
        problems.append(f"total: expected {expected['total']}, found {len(all_postings)}")
    if problems:
        print("INPUT INCOMPLETE - nothing was scored:\n  " + "\n  ".join(problems))
        return 2

    results = [J.evaluate(p, rules) for p in all_postings]
    confirmed = J.confirmed_shortlist(results)
    candidates = J.review_candidates(results, rules)
    queue = [r for r in results if r["decision"] == "review"]
    unknown_parts = collections.Counter(part for r in results for part, kind in r["location_parts"] if kind == "unknown")

    now = datetime.datetime.now(datetime.timezone.utc)
    out = make_run_dir(Path(args.runs_dir), f"filter-v{rules['filter']['version']}-{now:%Y-%m-%dT%H%M%SZ}")
    meta = {
        "run": out.name, "run_at": now.isoformat(timespec="seconds"),
        "filter_version": rules["filter"]["version"],
        "python": platform.python_version(),
        "inputs": {"js2_folder": str(js2.relative_to(HERE.parent)) if js2.is_relative_to(HERE.parent) else str(js2),
                   "saved_responses": sources, "persona": persona_src},
        "rules_files": {f.name: sha256_file(f) for f in sorted((HERE / "rules").glob("*.json"))},
        "filter_md_sha256": sha256_file(HERE / "FILTER.md"),
        "code_sha256": {f: sha256_file(HERE / f) for f in ("job_filter.py", "postings.py", "run_filter.py")},
        "approved_boilerplate_sentences": sum(len(v) for v in rules["approved_boilerplate"].values()),
        "counted_skills": rules["skills"],
        "postings": {"total": len(all_postings), "by_board": dict(sorted(counts.items()))},
    }
    summ = summarize(results, rules)
    write_new(out / "summary.json", dump({**meta, **summ,
                                          "confirmed_shortlist": [[r["board"], r["id"]] for r in confirmed],
                                          "review_candidate_shortlist": [[r["board"], r["id"], r["score"]] for r in candidates]}))
    write_new(out / "results.json", dump(results))
    write_new(out / "confirmed.json", dump(confirmed))
    write_new(out / "review_queue.json", dump(sorted(queue, key=lambda r: (-r["score"], r["board"], r["id"]))))
    write_new(out / "review_candidates_top10.json", dump(candidates))
    write_new(out / "unknown_location_parts.json", dump(dict(unknown_parts.most_common())))
    write_new(out / "report.md", report_md(meta, summ, confirmed, candidates))

    print(f"saved {out.relative_to(HERE)}/")
    print(f"  postings {len(all_postings)} {dict(sorted(counts.items()))}")
    print(f"  confirmed {len(confirmed)}  review {len(queue)}  rejected {summ['decisions'].get('rejected', 0)}")
    print(f"  review candidates (top {len(candidates)}): " + ", ".join(f"{r['board']}:{r['id']}({r['score']})" for r in candidates))
    return 0


if __name__ == "__main__":
    sys.exit(main())
