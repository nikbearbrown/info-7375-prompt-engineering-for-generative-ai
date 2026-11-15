"""Measure one filter change at a time against Smit's hand verdicts, dev and held-out separately.

    python3 src/measure_filter.py --run-id live-20261114

Each change is v1.0 plus ONE switch. Adoption is decided on dev only; held-out is reported
for every change, so a change cannot be picked by its held-out score without that showing.
Writes experiments/filter-changes.json. Offline, no model calls.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filter as flt  # noqa: E402
from postings import ROOT, load_run  # noqa: E402
from run_filter import load_skills  # noqa: E402

CHANGES = [
    ("v1.0 (no change)", {}),
    ("A: years uses the LARGEST lower bound", {"years_bound": "largest"}),
    ("B: intern/internship/PhD are level words (R2)", {"extra_level_words": ["intern", "internship", "phd"]}),
    ("C: 1 skill is enough (R6)", {"min_skills": 1}),
    ("D: allow 'Manager, Software Engineering'", {"allow_eng_manager": True}),
    ("v1.1 = A + B + C (adopted)", {k: v for k, v in flt.V1_1.items() if k != "version"}),
]


def confusion(rows):
    c = {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "cannot_tell": 0}
    for filt, hand in rows:
        if filt == "cannot_tell":
            c["cannot_tell"] += 1
        elif filt == "keep":
            c["tp" if hand == "relevant" else "fp"] += 1
        else:
            c["fn" if hand == "relevant" else "tn"] += 1
    c["errors"] = c["fp"] + c["fn"]
    c["n"] = len(rows)
    return c


def evaluate(config, postings, skills, hand, split_of):
    by_key = {(p["board"], p["id"]): p for p in postings}
    out = {"dev": [], "held_out": []}
    wrong = {"dev": [], "held_out": []}
    for key, h in hand.items():
        v = flt.judge(by_key[key], skills, config)
        split = split_of[key]
        out[split].append((v["verdict"], h))
        if (v["verdict"] == "keep") != (h == "relevant"):
            wrong[split].append(f"{by_key[key]['title']} ({v['verdict']} {v['rule']}, hand: {h})")
    kept_all = sum(flt.judge(p, skills, config)["verdict"] == "keep" for p in postings)
    return {s: {**confusion(out[s]), "wrong": wrong[s]} for s in out} | {"kept_in_full_run": kept_all}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    run_id = ap.parse_args().run_id
    postings, _, _ = load_run(run_id)
    skills = load_skills()
    with open(os.path.join(ROOT, "audit", "sample.json"), encoding="utf-8") as f:
        split_of = {(i["board"], i["id"]): i["split"] for i in json.load(f)["items"]}
    with open(os.path.join(ROOT, "audit", "hand-verdicts.json"), encoding="utf-8") as f:
        hand = {(v["board"], v["id"]): v["hand_verdict"] for v in json.load(f)["verdicts"]}
    results = []
    for name, cfg in CHANGES:
        r = evaluate(cfg, postings, skills, hand, split_of)
        results.append({"change": name, "config": cfg, **r})
        print(f"{name:48} dev errors {r['dev']['errors']:2}/{r['dev']['n']}  "
              f"held-out errors {r['held_out']['errors']:2}/{r['held_out']['n']}  kept(all) {r['kept_in_full_run']}")
    os.makedirs(os.path.join(ROOT, "experiments"), exist_ok=True)
    with open(os.path.join(ROOT, "experiments", "filter-changes.json"), "w", encoding="utf-8") as f:
        json.dump({"run_id": run_id, "labels": "audit/hand-verdicts.json", "results": results}, f,
                  indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
