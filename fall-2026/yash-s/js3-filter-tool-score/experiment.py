"""What moves the score: one change to one object at a time, measured on held-out labels.

    python3 experiment.py flips    # which postings each pre-registered change would flip
    python3 experiment.py report   # measure each change on my tuning and held-out labels

The candidate changes are pre-registered in experiments/candidates.json before any
held-out label exists. Each one changes exactly one value in the rules, in memory
only: rules/*.json and FILTER.md are never written by this script. Adopting a
change is my decision and would be a new FILTER.md version.

A posting whose decision is the same with and without a change cannot tell the two
apart, so a change is measured on the postings it flips. Every flip is counted
exactly over all 2,418 saved postings; whether the flips are improvements is a
sample estimate from my hand labels.
"""
import argparse
import copy
import csv
import json
import math
import sys
from pathlib import Path

import job_filter as J
import postings as P

HERE = Path(__file__).resolve().parent
EXP_DIR = HERE / "experiments"
CANDIDATES = EXP_DIR / "candidates.json"
BASE_RUN = HERE / "runs" / "filter-v1.1-2026-11-18T212545Z"
TUNING_SHEET = HERE / "audit" / "sample-filter-v1.1-2026-11-18T212545Z" / "labeling-sheet.csv"
HELDOUT_DIR = HERE / "audit" / "heldout-filter-v1.1-2026-11-18T212545Z"

# My verdict words -> the decision I think is right. The tuning sheet uses words
# relative to the filter's decision; the held-out sheet is blind and uses decisions.
VERDICT_TO_DECISION = {
    "correct reject": "rejected", "should have been rejected": "rejected", "reject": "rejected",
    "should have been kept for review": "review", "correctly in review": "review", "keep for review": "review",
    "should be confirmed": "confirmed", "confirm": "confirmed",
}
KEPT = ("review", "confirmed")


def key(r):
    return (r["board"], str(r["id"]))


# ------------------------------------------------------------- one change only

def get_path(d, path, default=None):
    for p in path[:-1]:
        d = d[p]
    return d.get(path[-1], default)


def leaves(d, prefix=()):
    if isinstance(d, dict):
        out = {}
        for k, v in d.items():
            out.update(leaves(v, prefix + (k,)))
        return out
    return {prefix: d}


def apply_change(rules, change):
    """Return a copy of rules with exactly one value changed. The original is untouched.
    Refuses if the current value is not the registered 'from' value, or if anything
    other than that one value would differ."""
    path = change["path"]
    current = get_path(rules["filter"], path, change.get("default"))
    if current != change["from"]:
        raise ValueError(f"{change['id']}: expected {path} = {change['from']!r}, found {current!r}")
    new = copy.deepcopy(rules)
    d = new["filter"]
    for p in path[:-1]:
        d = d[p]
    d[path[-1]] = change["to"]
    before, after = leaves(rules["filter"]), leaves(new["filter"])
    diff = {k for k in set(before) | set(after) if before.get(k, change.get("default")) != after.get(k, change.get("default"))}
    if diff != {tuple(path)}:
        raise ValueError(f"{change['id']}: changed {sorted(diff)}, not exactly {path}")
    return new


def load_candidates(path=CANDIDATES):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def evaluate_all(postings, rules):
    return {key(p): J.evaluate(p, rules) for p in postings}


def flips(base, changed):
    out = []
    for k in sorted(base):
        a, b = base[k], changed[k]
        if a["decision"] != b["decision"]:
            out.append({"board": k[0], "id": k[1], "title": a["title"], "from": a["decision"], "to": b["decision"],
                        "score_before": a["score"], "score_after": b["score"]})
    return out


# ---------------------------------------------------------------- statistics

def wilson(x, n, z=1.959964):
    if n == 0:
        return None
    p, d = x / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def exact(x, n, a=0.05):
    """Clopper-Pearson interval by bisection on the binomial distribution."""
    if n == 0:
        return None
    cdf = lambda k, p: sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))

    def solve(f):
        lo, hi = 0.0, 1.0
        for _ in range(100):
            m = (lo + hi) / 2
            lo, hi = (lo, m) if f(m) else (m, hi)
        return (lo + hi) / 2
    lo = 0.0 if x == 0 else solve(lambda p: 1 - cdf(x - 1, p) >= a / 2)
    hi = 1.0 if x == n else solve(lambda p: cdf(x, p) <= a / 2)
    return lo, hi


def pct(iv):
    return "n/a" if iv is None else f"{iv[0]:.0%} to {iv[1]:.0%}"


# ------------------------------------------------------------------- labels

def read_sheet(path):
    path = Path(path)
    if not path.exists():
        return {}
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return {(r["board"], r["posting_id"]): r for r in rows}


def judged(row):
    """The decision I think is right, 'cannot tell', or None if the row is not labeled yet."""
    v = (row.get("MY_VERDICT") or "").strip().lower()
    if not v:
        return None
    if v == "cannot tell":
        return "cannot tell"
    if v not in VERDICT_TO_DECISION:
        raise ValueError(f"unknown verdict {v!r} for {row['board']} {row['posting_id']}")
    return VERDICT_TO_DECISION[v]


def score_flip(flip, truth):
    """Is this one flip an improvement? Only the kept/rejected boundary matters here."""
    if truth in (None, "cannot tell"):
        return truth or "unlabeled"
    was_right = (flip["from"] in KEPT) == (truth in KEPT)
    now_right = (flip["to"] in KEPT) == (truth in KEPT)
    if now_right and not was_right:
        return "improved"
    if was_right and not now_right:
        return "regressed"
    return "no change"


# ----------------------------------------------------------------- commands

def baseline_rules(persona):
    """The rules the baseline run was made with (FILTER.md v1.1), checked against the hashes
    that run recorded. The current rules may be a later version."""
    summary = json.loads((BASE_RUN / "summary.json").read_text(encoding="utf-8"))
    folder = J.rules_dir_for(summary["filter_version"])
    for name, want in summary["rules_files"].items():
        if P.sha256(folder / name) != want:
            raise SystemExit(f"{folder.name}/{name} is not the file the baseline run used; stop")
    return J.load_rules(folder, persona=persona)


def cmd_flips(args):
    all_postings, _ = P.load_saved_postings(args.js2)
    persona, _ = P.load_persona(args.js2)
    rules = baseline_rules(persona)
    base = evaluate_all(all_postings, rules)
    saved = {key(r): r for r in json.loads((BASE_RUN / "results.json").read_text(encoding="utf-8"))}
    if set(saved) != set(base) or any(base[k] != saved[k] for k in saved):  # every field of every posting
        print("The baseline rules no longer reproduce the saved first run. Stop: compare before measuring.")
        return 2
    cand = load_candidates()
    out = {"baseline_run": BASE_RUN.name, "baseline_reproduced_exactly": True,
           "results_json_sha256": P.sha256(BASE_RUN / "results.json"),
           "candidates_sha256": P.sha256(CANDIDATES), "postings": len(all_postings), "changes": {}}
    for ch in cand["changes"]:
        changed = evaluate_all(all_postings, apply_change(rules, ch))
        fl = flips(base, changed)
        out["changes"][ch["id"]] = {"object": ch["object"], "path": ch["path"], "from": ch["from"], "to": ch["to"],
                                    "flip_count": len(fl), "flips": fl}
        kinds = {}
        for f in fl:
            kinds[f"{f['from']}->{f['to']}"] = kinds.get(f"{f['from']}->{f['to']}", 0) + 1
        print(f"{ch['id']}: {len(fl)} of {len(all_postings)} postings change decision {kinds}")
    path = EXP_DIR / f"flips-{BASE_RUN.name}.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(HERE)} (baseline reproduced the saved run exactly)")
    return 0


def measure(change_flips, labels):
    rows = []
    for f in change_flips:
        row = labels.get((f["board"], f["id"]))
        if row is None:
            continue
        truth = judged(row)
        rows.append({**f, "row": row.get("row"), "my_verdict": row.get("MY_VERDICT", ""),
                     "my_reason": row.get("MY_REASON", ""), "outcome": score_flip(f, truth)})
    return rows


def what_the_labels_say(info, tuning_rows, held_rows):
    """Turn the labeled flips into the strongest honest statement: a count when every flip
    has a label, otherwise a sample estimate over the flips outside the tuning labels."""
    count = lambda rows, o: sum(r["outcome"] == o for r in rows)
    if not held_rows:
        return []
    t_imp, t_reg = count(tuning_rows, "improved"), count(tuning_rows, "regressed")
    h_imp, h_reg = count(held_rows, "improved"), count(held_rows, "regressed")
    remaining = info["flip_count"] - len(tuning_rows)  # the flips the held-out sample was drawn from
    L = ["### What the labels say", ""]
    if h_imp + h_reg == remaining == len(held_rows):
        L += [f"Every one of the {info['flip_count']} flips has my label ({len(tuning_rows)} tuning, {len(held_rows)} "
              f"held-out), so this is a **count, not an estimate**: over all {info['flip_count']} postings this change "
              f"affects, by my judgment, {t_imp + h_imp} better and {t_reg + h_reg} worse. On the held-out labels "
              f"alone: {h_imp} better, {h_reg} worse. It says nothing about postings collected later.", ""]
        return L
    n = h_imp + h_reg
    if n == 0:
        return L + ["No decided held-out label yet.", ""]
    w, e = wilson(h_imp, n), exact(h_imp, n)
    L += [f"Held-out: {h_imp} of {n} flips improved ({h_imp / n:.0%}; 95% Wilson {pct(w)}, exact {pct(e)}). The held-out "
          f"postings are a random sample of the {remaining} flips outside my tuning labels, so among those {remaining} roughly "
          f"{w[0] * remaining:.0f} to {w[1] * remaining:.0f} would be improvements. That is a sample estimate. Adding the "
          f"{len(tuning_rows)} tuning flips ({t_imp} improved, {t_reg} regressed), the estimate over all {info['flip_count']} "
          f"flips is roughly {w[0] * remaining + t_imp:.0f} to {w[1] * remaining + t_imp:.0f} improvements, the rest regressions.", ""]
    if w[0] <= 0.5 <= w[1]:
        L += ["The interval includes 50%, so these labels **do not show** that the change helps more than it hurts.", ""]
    else:
        L += [f"The whole interval is {'above' if w[0] > 0.5 else 'below'} 50%, so on these labels the change "
              f"{'helps' if w[0] > 0.5 else 'hurts'} more often than not.", ""]
    return L


def cmd_report(args):
    flips_path = EXP_DIR / f"flips-{BASE_RUN.name}.json"
    fl = json.loads(flips_path.read_text(encoding="utf-8"))
    cand = {c["id"]: c for c in load_candidates()["changes"]}
    tuning = read_sheet(TUNING_SHEET)
    held = read_sheet(HELDOUT_DIR / "labeling-sheet.csv")
    heldout_labeled = sum(1 for r in held.values() if judged(r) is not None)
    L = ["# What moves the score: one change at a time", "",
         "Generated by `python3 experiment.py report`. Do not edit by hand; rerun it.", "",
         f"- Baseline: FILTER.md v1.1, saved run `{fl['baseline_run']}`, reproduced exactly in memory before measuring.",
         f"- Candidate changes: `experiments/candidates.json` (sha256 `{fl['candidates_sha256'][:12]}…`), "
         "registered before any held-out label existed.",
         f"- Tuning labels: my 60 audit labels (`{TUNING_SHEET.relative_to(HERE)}`). The changes were chosen from these.",
         f"- Held-out labels: `{(HELDOUT_DIR / 'labeling-sheet.csv').relative_to(HERE)}`, "
         f"{heldout_labeled} of {len(held)} labeled. Used only to measure, never to choose.", "",
         "Each change alters one value, in memory. A flip count is exact over all postings. Whether flips are "
         "improvements comes from my hand labels: a count when every flip is labeled, otherwise a sample estimate. "
         "It is never a measured rate for postings nobody labeled.", ""]
    base_review = sum(r["decision"] == "review" for r in json.loads((BASE_RUN / "results.json").read_text(encoding="utf-8")))
    for cid, info in fl["changes"].items():
        ch = cand[cid]
        to_review = sum(f["to"] == "review" for f in info["flips"]) - sum(f["from"] == "review" for f in info["flips"])
        L += [f"## {cid}", "", f"- Object changed: {ch['object']}: `{'.'.join(ch['path'])}` {ch['from']!r} → {ch['to']!r}",
              "- Everything else unchanged: the same postings, rules files, code and persona.",
              f"- Why it was proposed: {ch['why']}",
              f"- Postings whose decision changes (exact, all {fl['postings']}): **{info['flip_count']}**",
              f"- Review queue: {base_review} → {base_review + to_review} postings for me to read", ""]
        parts = {}
        for name, labels in (("Tuning labels (used to choose the change)", tuning), ("Held-out labels", held)):
            rows = measure(info["flips"], labels)
            parts[name] = rows
            n_imp = sum(r["outcome"] == "improved" for r in rows)
            n_reg = sum(r["outcome"] == "regressed" for r in rows)
            L += [f"### {name}", ""]
            if not rows:
                L += ["No flipped posting has a label here.", ""]
                continue
            L += [f"Flipped postings with a label: {len(rows)}. Improved {n_imp}, regressed {n_reg}, "
                  f"cannot tell {sum(r['outcome'] == 'cannot tell' for r in rows)}, "
                  f"not labeled yet {sum(r['outcome'] == 'unlabeled' for r in rows)}.", ""]
            L += ["| Row | Board | ID | Title | Filter v1.1 | With change | My verdict | Outcome |",
                  "|---:|---|---|---|---|---|---|---|"]
            for r in rows:
                L.append(f"| {r['row']} | {r['board']} | {r['id']} | {r['title']} | {r['from']} | {r['to']} | "
                         f"{r['my_verdict'] or '(blank)'} | {r['outcome']} |")
            L.append("")
        L += what_the_labels_say(info, *parts.values())
    L += ["## What this does not show", "",
          "- Nothing here was trained or fitted. Every weight and threshold is hand-set (FILTER.md section 10).",
          "- A change that looks better on these labels may still be worse on postings nobody labeled.",
          "- The decision to adopt a change is mine, recorded in FILTER.md as a new version. This report changes no rule.", ""]
    out = EXP_DIR / "REPORT.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {out.relative_to(HERE)} (held-out labeled: {heldout_labeled} of {len(held)})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["flips", "report"])
    ap.add_argument("--js2", default=str(P.DEFAULT_JS2))
    args = ap.parse_args(argv)
    return cmd_flips(args) if args.command == "flips" else cmd_report(args)


if __name__ == "__main__":
    sys.exit(main())
