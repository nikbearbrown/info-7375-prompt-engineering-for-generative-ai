"""One change at a time, measured once on the held-out set (JS3 step 2, item 4; the book, chapter 9).

Runs FILTER.md v1.0 (twice, to show the noise) and each change listed in js3/score/CHANGES-TO-MEASURE.md on the 30
held-out postings, and compares every run with Aravind's frozen held-out verdicts. Refuses to start unless that list
is committed and unchanged, and unless the held-out answers still match the SHA-256 their README published. Refuses
a second measurement (a held-out set is touched once) unless --again is given, which is recorded.

Writes every run to js3/score/runs/<UTC time>/, the report js3/score/EXPERIMENTS.md, and a dated note in the held-out
kit's CHANGES.md. No model is called. Standard library only.

Usage: python3 tools/heldout_experiments.py [--again]      measure (once)
       python3 tools/heldout_experiments.py report           rebuild EXPERIMENTS.md from the saved runs (no new touch)
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

import audit_kit  # noqa: E402
from job_agent import filter as flt  # noqa: E402
from score_audit import upper_bound  # noqa: E402

RUN_ID = "2026-11-21T044414Z"
HELDOUT = REPO / "js3" / "heldout" / RUN_ID
FILTER_RUN = REPO / "js3" / "filter-run" / RUN_ID
SCORE = REPO / "js3" / "score"
PLAN = SCORE / "CHANGES-TO-MEASURE.md"


def _drop(words, gone):
    return [w for w in words if w not in gone]


def variant(rules: dict, name: str) -> dict:
    """The rules for one run: a deep copy of FILTER.md v1.0's, with exactly one change (or none)."""
    r = copy.deepcopy(rules)
    if name in ("R0", "R0b"):
        pass
    elif name == "X1":
        r["splitter_keeps"] = ["U.S.", "e.g.", "i.e."]
    elif name == "X2":
        r["years_company_words"] = _drop(r["years_company_words"], {"growth", "revenue", "customers"})
    elif name == "X3":
        r["topic_groups"]["Developer tools"] = _drop(r["topic_groups"]["Developer tools"], {"build systems"})
    elif name == "X4":
        r["ranking"]["caution_penalty"] = -10
    elif name == "X5":
        r["ranking"]["shortlist_min"] = 55
    elif name == "X6":
        r["ranking"]["shortlist_min"] = 50
    else:
        raise ValueError(f"unknown run {name}")
    return r


RUNS = ["R0", "R0b", "X1", "X2", "X3", "X4", "X5", "X6"]
PREDICTIONS = {
    "R0b": "identical to R0, card for card",
    "X1": "no fate changes", "X2": "no fate changes",
    "X3": "no fate changes; a few scores fall by 5", "X4": "no fate changes; fewer recommended",
    "X5": "no fate changes; cutoff agreement rises", "X6": "no fate changes; cutoff agreement rises further",
}


def read_verdicts(path: Path) -> dict:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| (\d{2}) \| (Keep|Reject|\?) \|", line)
        if m:
            out[int(m.group(1))] = m.group(2)
    return out


def pool_of(name: str) -> str:
    """The held-out kit names its pools "random kept" and "random rejected"."""
    return "kept" if "kept" in name else "rejected"


def metrics(rows: list, cutoff: int) -> dict:
    """Fate and cutoff agreement against his verdicts, per pool, on the cards he did not mark '?'."""
    out = {}
    for pool in ("kept", "rejected", "all"):
        sub = [r for r in rows if r["his"] != "?" and (pool == "all" or pool_of(r["pool"]) == pool)]
        fate_agree = sum(1 for r in sub if (r["fate"] == "kept") == (r["his"] == "Keep"))
        rec = lambda r: r["fate"] == "kept" and r["score"] is not None and r["score"] >= cutoff
        cut_agree = sum(1 for r in sub if rec(r) == (r["his"] == "Keep"))
        n = len(sub)
        out[pool] = {"n": n, "fate_agree": fate_agree, "fate_disagree": n - fate_agree,
                     "fate_bound": upper_bound(n - fate_agree, n) if n else None,
                     "cutoff_agree": cut_agree, "recommended": sum(1 for r in sub if rec(r))}
    return out


def _git(*args) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True).stdout.strip()


def preflight(again: bool) -> str:
    if not _git("log", "-1", "--format=%h", "--", str(PLAN.relative_to(REPO))):
        raise SystemExit("STOP: js3/score/CHANGES-TO-MEASURE.md is not committed; the changes must be fixed first")
    if _git("status", "--porcelain", "--", str(PLAN.relative_to(REPO))):
        raise SystemExit("STOP: js3/score/CHANGES-TO-MEASURE.md has uncommitted changes")
    sealed = HELDOUT / "sealed" / "answers.json"
    digest = hashlib.sha256(sealed.read_bytes()).hexdigest()
    if f"`{digest}`" not in (HELDOUT / "README.md").read_text(encoding="utf-8"):
        raise SystemExit("STOP: the held-out answers do not match the SHA-256 their README published")
    if (SCORE / "runs").exists() and any((SCORE / "runs").iterdir()) and not again:
        raise SystemExit("STOP: the held-out set was already measured (js3/score/runs/); a held-out set is touched once")
    return _git("log", "-1", "--format=%h", "--", str(PLAN.relative_to(REPO)))


def whole_counts(whole: dict) -> dict:
    """For each run: how many of the whole run's fates and scores differ from v1.0's (development data, for scale)."""
    return {name: {"fates": sum(1 for k, v in recs.items() if v[0] != whole["R0"][k][0]),
                   "scores": sum(1 for k, v in recs.items() if v[1] != whole["R0"][k][1])} for name, recs in whole.items()}


def whole_run(base_rules: dict) -> dict:
    """Every run over all postings of the filter run; it reads no held-out answer."""
    data = json.loads((FILTER_RUN / "verdicts.json").read_text(encoding="utf-8"))
    postings = {key: p for key, (p, _) in audit_kit.saved_postings(data).items()}
    jane, out = flt.load_profile(), {}
    for name in RUNS:
        rules = variant(base_rules, name)
        out[name] = {f"{k[0]}/{k[1]}": (lambda r: (r["fate"], r["score"]))(flt.judge(p, jane, rules, k[0]))
                     for k, p in sorted(postings.items())}
    return out


def report_from_saved() -> int:
    """Rebuild EXPERIMENTS.md from the newest saved runs; nothing is measured again."""
    stamp = sorted(d.name for d in (SCORE / "runs").iterdir() if d.is_dir())[-1]
    folder = SCORE / "runs" / stamp
    saved = {name: json.loads((folder / f"{name}.json").read_text(encoding="utf-8")) for name in RUNS}
    results = {}
    for name, s in saved.items():
        cutoff = variant(flt.load_rules(version="1.0"), name)["ranking"]["shortlist_min"]
        results[name] = {"rows": s["rows"], "metrics": metrics(s["rows"], cutoff), "cutoff": cutoff}
    counts_file = folder / "whole-run.json"
    if not counts_file.exists():
        counts_file.write_text(json.dumps(whole_counts(whole_run(flt.load_rules(version="1.0"))), indent=1) + "\n",
                               encoding="utf-8")
    counts = json.loads(counts_file.read_text(encoding="utf-8"))
    text = write_report(results, counts, stamp, saved["R0"]["plan_commit"], False)
    print(text.split("## Every run")[0])
    return 0


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv[:1] == ["report"]:
        return report_from_saved()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--again", action="store_true", help="measure again (recorded as a second touch)")
    args = ap.parse_args(argv)
    plan_commit = preflight(args.again)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    sealed = json.loads((HELDOUT / "sealed" / "answers.json").read_text(encoding="utf-8"))
    his = read_verdicts(HELDOUT / "VERDICTS.md")
    data = json.loads((FILTER_RUN / "verdicts.json").read_text(encoding="utf-8"))
    postings = {key: p for key, (p, _) in audit_kit.saved_postings(data).items()}
    boards = {(r["board"], r["id"]) for r in data["records"]}
    base_rules, jane = flt.load_rules(version="1.0"), flt.load_profile()
    results, whole, files = {}, {}, {}
    for name in RUNS:
        rules = variant(base_rules, name)
        rows = []
        for a in sealed["answers"]:
            rec = flt.judge(postings[(a["board"], a["id"])], jane, rules, a["board"])
            rows.append({"card": a["card"], "board": a["board"], "id": a["id"], "title": a["title"], "pool": a["pool"],
                         "his": his[a["card"]], "fate": rec["fate"], "deciding_rule": rec["deciding_rule"],
                         "score": rec["score"], "failed_rules": rec["failed_rules"]})
        all_recs = {key: flt.judge(postings[key], jane, rules, key[0]) for key in sorted(boards) if key in postings}
        whole[name] = {f"{k[0]}/{k[1]}": (r["fate"], r["score"]) for k, r in all_recs.items()}
        m = metrics(rows, rules["ranking"]["shortlist_min"])
        results[name] = {"rows": rows, "metrics": m, "cutoff": rules["ranking"]["shortlist_min"]}
        files[name] = json.dumps({"run": name, "measured_at": stamp, "plan_commit": plan_commit,
                                  "prediction": PREDICTIONS.get(name, "baseline"), "metrics": m, "rows": rows},
                                 indent=1) + "\n"
    out_dir = SCORE / "runs" / stamp  # written only once every run has finished
    out_dir.mkdir(parents=True)
    for name, text in files.items():
        (out_dir / f"{name}.json").write_text(text, encoding="utf-8")
    (out_dir / "whole-run.json").write_text(json.dumps(whole_counts(whole), indent=1) + "\n", encoding="utf-8")
    report = write_report(results, whole_counts(whole), stamp, plan_commit, args.again)
    note = (f"\n\n## {stamp[:10]}: answers opened for the pre-registered experiments\n\n"
            f"`tools/heldout_experiments.py` opened `sealed/answers.json` at {stamp} (UTC), after the list of changes was "
            f"committed (`{plan_commit}`), and measured each run once (`js3/score/EXPERIMENTS.md`). If a result here "
            "leads to adopting a change, this set is development data from then on, and a later claim about a change needs "
            "a new held-out set." + (" This was a second touch (--again)." if args.again else "") + "\n")
    changes = HELDOUT / "CHANGES.md"
    changes.write_text(changes.read_text(encoding="utf-8").rstrip("\n") + note, encoding="utf-8")
    print(report.split("## Every run")[0])
    return 0


def write_report(results: dict, counts: dict, stamp: str, plan_commit: str, again: bool) -> str:
    base = {r["card"]: r for r in results["R0"]["rows"]}
    lines = ["# One change at a time, measured once on the held-out set", "",
             f"Measured by `tools/heldout_experiments.py` at {stamp} (UTC), after the changes and predictions were committed "
             f"in `js3/score/CHANGES-TO-MEASURE.md` (`{plan_commit}`). Against Aravind's 30 frozen held-out verdicts "
             "(`1e2b1e1`: 12 Keep, 15 Reject, 3 \"?\"). Every run is in `js3/score/runs/" + stamp + "/`. No model is "
             "called, so every run costs $0 at API prices." + (" Second touch (--again)." if again else ""), "",
             "## Results", "",
             "| Run | Change | Fate agreement, kept pool | Fate agreement, rejected pool | Disagreements, 95% bound | "
             "Cutoff | Recommended | Cutoff agreement | Held-out cards that change | Whole run: fates / scores that change | "
             "Prediction |", "|---|---|---|---|---|---:|---:|---|---|---|---|"]
    for name in RUNS:
        res, m = results[name], results[name]["metrics"]
        changed = [r for r in res["rows"] if (r["fate"], r["score"]) != (base[r["card"]]["fate"], base[r["card"]]["score"])]
        fate_changes = [r for r in changed if r["fate"] != base[r["card"]]["fate"]]
        w_fate, w_score = counts[name]["fates"], counts[name]["scores"]
        a = m["all"]
        if name == "R0":
            held = ""
        elif name == "R0b":
            held = "held" if not changed and w_fate == 0 and w_score == 0 else "FAILED"
        else:
            ok = not fate_changes
            if name == "X3":  # predicted: a few scores fall by 5
                ok = ok and bool(changed) and all(base[r["card"]]["score"] - r["score"] == 5 for r in changed)
            if name == "X4":  # predicted: fewer recommended
                ok = ok and a["recommended"] < results["R0"]["metrics"]["all"]["recommended"]
            if name == "X5":
                ok = ok and a["cutoff_agree"] > results["R0"]["metrics"]["all"]["cutoff_agree"]
            if name == "X6":
                ok = ok and a["cutoff_agree"] >= results["X5"]["metrics"]["all"]["cutoff_agree"]
            held = "held" if ok else ("partly: no fate changed, the rest did not happen here" if not fate_changes
                                      else "FAILED")
        kp, rp = m["kept"], m["rejected"]
        lines.append(f"| {name} | {PREDICTIONS.get(name, 'v1.0 as committed') if name != 'R0' else 'v1.0 as committed'} | "
                     f"{kp['fate_agree']} of {kp['n']} | {rp['fate_agree']} of {rp['n']} | {a['fate_disagree']} of {a['n']}, "
                     f"at most {a['fate_bound'] * 100:.1f}% | {res['cutoff']} | {a['recommended']} | "
                     f"{a['cutoff_agree']} of {a['n']} | {len(changed)} ({len(fate_changes)} fates) | {w_fate} / {w_score} | "
                     f"{held} |")
    lines += ["", "\"Prediction\" checks each run against what `CHANGES-TO-MEASURE.md` predicted before the answers were "
              "opened. The bound is the exact one-sided 95% upper bound on the share of disagreements, for the 27 cards "
              "he judged; it says what this sample allows, not a rate for all postings.", "",
              "## Every run, card by card, where it differs from v1.0", ""]
    for name in RUNS[1:]:
        diffs = [r for r in results[name]["rows"]
                 if (r["fate"], r["score"]) != (base[r["card"]]["fate"], base[r["card"]]["score"])]
        rec = lambda r, cut: r["fate"] == "kept" and r["score"] is not None and r["score"] >= cut
        flips = [r for r in results[name]["rows"]
                 if rec(r, results[name]["cutoff"]) != rec(base[r["card"]], results["R0"]["cutoff"])]
        lines.append(f"**{name}:** " + ("no card changes." if not diffs and not flips else ""))
        for r in flips:
            lines.append(f"- card {r['card']:02d} ({r['title'].strip()}; his verdict {r['his']}): score {r['score']}, "
                         f"{'now' if rec(r, results[name]['cutoff']) else 'no longer'} recommended at cutoff "
                         f"{results[name]['cutoff']}")
        for r in diffs:
            b = base[r["card"]]
            lines.append(f"- card {r['card']:02d} ({r['title'].strip()}; his verdict {r['his']}): {b['fate']} {b['score']} "
                         f"-> {r['fate']} {r['score']}")
        lines.append("")
    lines += ["## What persistence is not proof of", "",
              "A behavior that stays the same across runs or sessions does not mean anything was trained. R0 and R0b agree "
              "card for card because the filter is a fixed program reading a fixed file over saved text, with no "
              "randomness and no model call; nothing in it learns from Aravind's labels. A change persists here only "
              "because it is written in FILTER.md and read by the program; training is identified by its mechanism "
              "(chapter 9), and there is none.", ""]
    text = "\n".join(lines)
    (SCORE / "EXPERIMENTS.md").write_text(text, encoding="utf-8")
    return text


if __name__ == "__main__":
    sys.exit(main())
