"""Command line for JS3.

    python -m js3 filter                 # FILTER.md on everything collected -> filter-runs/v<version>/
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import sys

from . import ROOT, corpus, filterdoc, score


def run_filter(flt: dict = None, c: dict = None) -> tuple:
    flt = flt or filterdoc.load()
    c = c or corpus.load()
    results = [score.score(p, flt) for p in c["postings"].values()]
    latest = corpus.latest_keys(c)
    for r in results:
        r["in_latest_snapshot"] = r["key"] in latest
    return flt, c, sorted(results, key=lambda r: r["key"])


def summarize(flt: dict, c: dict, results: list) -> str:
    boards = sorted({r["board"] for r in results})
    table = collections.Counter((r["board"], r["decision"]) for r in results)
    by_rule = collections.Counter((r["decision"], r["decided_by"]) for r in results)
    lines = [f"# Filter run: FILTER.md v{flt['filter_version']}", "",
             f"- FILTER.md sha256: `{flt['filter_sha256']}`",
             f"- Corpus: {len(results)} unique postings from {len(c['snapshots'])} live snapshots "
             f"({', '.join(s['id'] for s in c['snapshots'])}); latest version of each posting used",
             f"- Run at: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}", "",
             "| board | kept | rejected | cannot tell | total |", "|---|---:|---:|---:|---:|"]
    for b in boards:
        k, r_, ct = (table[(b, d)] for d in (score.KEPT, score.REJECTED, score.CANNOT_TELL))
        lines.append(f"| {b} | {k} | {r_} | {ct} | {k + r_ + ct} |")
    tot = collections.Counter(r["decision"] for r in results)
    lines += [f"| **all** | **{tot[score.KEPT]}** | **{tot[score.REJECTED]}** | **{tot[score.CANNOT_TELL]}** | "
              f"**{len(results)}** |", "", "**Which rule decided:**", "",
              "| decision | rule | postings |", "|---|---|---:|"]
    for (d, rule), n in sorted(by_rule.items(), key=lambda x: (x[0][0], x[0][1])):
        lines.append(f"| {d} | {rule} | {n} |")
    missing = [(s["id"], b["board"], b["reason"]) for s in c["snapshots"] for b in s["boards_without_result"]]
    lines += ["", "**Boards with no result** (FILTER.md section 4: \"no result\", never \"nothing relevant\"):", ""]
    lines += [f"- {sid}: `{b}`: no result ({reason})" for sid, b, reason in missing] or ["- none"]
    kept_latest = sum(1 for r in results if r["decision"] == score.KEPT and r["in_latest_snapshot"])
    lines += ["", f"Kept postings still listed in the latest snapshot ({c['latest']}): {kept_latest}."]
    return "\n".join(lines) + "\n"


def cmd_filter(a) -> int:
    flt, c, results = run_filter()
    out = ROOT / "filter-runs" / f"v{flt['filter_version']}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "results.jsonl", "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    summary = summarize(flt, c, results)
    (out / "summary.md").write_text(summary)
    print(summary)
    return 0


def load_results(version: str) -> list:
    with open(ROOT / "filter-runs" / f"v{version}" / "results.jsonl") as f:
        return [json.loads(line) for line in f]


def cmd_sample(a) -> int:
    from . import labeling, sample
    seed_info = json.loads((ROOT / "audit" / "seed.json").read_text())
    results = load_results(a.version)
    s = sample.draw(results, seed=seed_info["seed"])
    s["results_file"] = f"filter-runs/v{a.version}/results.jsonl"
    (ROOT / "audit" / "samples.json").write_text(json.dumps(s, indent=2) + "\n")
    keys = s["heldout"] + s["audit_random_rejects"] + s["audit_closest"] + s["audit_kept"]
    c = corpus.load()
    items = labeling.build(keys, c["postings"], seed=seed_info["seed"] + 1)
    labeling.write_sheet(items, ROOT / "audit" / "labeling-sheet.md")
    labeling.write_template(items, ROOT / "audit" / "labels.csv")
    print(f"drew {len(keys)} postings: heldout {len(s['heldout'])}, random rejects {len(s['audit_random_rejects'])}, "
          f"closest {len(s['audit_closest'])}, kept {len(s['audit_kept'])}; population {s['population']}")
    return 0


def cmd_label(a) -> int:
    """Record Hemanth's verdicts, as given in chat, e.g.  1n 2y 3? 7n:too-senior"""
    import csv
    import re as _re
    from .labeling import VERDICTS
    path = ROOT / a.file
    rows = list(csv.DictReader(open(path, newline="")))
    by_item = {int(r["item"]): r for r in rows}
    stamp = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    for tok in a.verdicts:
        m = _re.fullmatch(r"(\d+)([yn?])(?::(.*))?", tok.strip())
        if not m:
            raise SystemExit(f"cannot read {tok!r} (expected e.g. 3y, 4n, 5?, 7n:reason)")
        item, v, note = int(m.group(1)), VERDICTS[m.group(2)], (m.group(3) or "").replace("-", " ")
        row = by_item[item]
        if row["verdict"] and row["verdict"] != v and not a.change:
            raise SystemExit(f"item {item} already labeled {row['verdict']!r}; use --change to change it")
        row.update(verdict=v, note=note or row.get("note", ""), labeled_at=stamp)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item", "key", "verdict", "note", "labeled_at"])
        w.writeheader()
        w.writerows(rows)
    done = sum(1 for r in rows if r["verdict"])
    print(f"recorded {len(a.verdicts)} verdicts at {stamp}; {done}/{len(rows)} labeled")
    return 0


def cmd_shortlist(a) -> int:
    from . import shortlist
    out = shortlist.build()
    d = ROOT / "shortlist"
    d.mkdir(exist_ok=True)
    (d / "claims.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    for e in out["entries"]:
        bad = sum(1 for c in e["claims"] if not c["valid"])
        print(f"{e['answer']['answer']:<15} {e['score']:>4} {e['title'][:60]:<60} invalid={bad} {e['models_used']}")
    return 0


def cmd_shortlist_final(a) -> int:
    from . import shortlist
    data = shortlist.finalize()
    (ROOT / "shortlist" / "final.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    (ROOT / "shortlist" / "shortlist-claims.md").write_text(shortlist.render(data))
    for i, e in enumerate(data["entries"], 1):
        print(f"#{i:<3}{e['answer']['answer']:<15}{e['title']}")
    return 0


def cmd_experiment(a) -> int:
    from . import experiment
    if a.action == "run":
        for exp in a.names:
            recs = experiment.run(exp)
            ok = sum(1 for r in recs if r["valid"])
            print(f"{exp}: {len(recs)} calls, {ok} valid, models {sorted({u for r in recs for u in r['models_used']})}")
    else:
        text = experiment.report()
        (ROOT / "experiments").mkdir(exist_ok=True)
        (ROOT / "experiments" / "report.md").write_text(text)
        print(text)
    return 0


def cmd_x1test(a) -> int:
    from . import x1test
    if a.action == "draw":
        out = x1test.draw()
        print(json.dumps(out["population"]))
    else:
        text = x1test.report()
        (ROOT / "audit" / "x1-results.md").write_text(text)
        print(text)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m js3")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("filter", help="run FILTER.md on everything collected").set_defaults(fn=cmd_filter)
    sp = sub.add_parser("sample", help="draw the held-out and audit samples; write the blind labeling sheet")
    sp.add_argument("--version", default="1.0")
    sp.set_defaults(fn=cmd_sample)
    sub.add_parser("audit", help="recompute the reject audit from the committed files").set_defaults(
        fn=lambda a: (print(__import__("js3.audit", fromlist=["run"]).run()), 0)[1])
    sub.add_parser("shortlist", help="top-N kept postings, every claim labeled by Claude with a checked quote"
                   ).set_defaults(fn=cmd_shortlist)
    sub.add_parser("shortlist-final", help="apply the hand check and write the final shortlist"
                   ).set_defaults(fn=cmd_shortlist_final)
    ep = sub.add_parser("experiment", help="held-out experiments: run E0a|E0b|E2|E3|E4, or report")
    ep.add_argument("action", choices=["run", "report"])
    ep.add_argument("names", nargs="*")
    ep.set_defaults(fn=cmd_experiment)
    xp = sub.add_parser("x1test", help="out-of-sample test of X1: draw | report")
    xp.add_argument("action", choices=["draw", "report"])
    xp.set_defaults(fn=cmd_x1test)
    lp = sub.add_parser("label", help="record Hemanth's verdicts from chat, e.g. 1n 2y 3?")
    lp.add_argument("verdicts", nargs="+")
    lp.add_argument("--change", action="store_true", help="allow changing an earlier verdict")
    lp.add_argument("--file", default="audit/labels.csv", help="which labels file (audit/x1-labels.csv for the X1 test)")
    lp.set_defaults(fn=cmd_label)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
