"""Relevance is not entailment: rebuild audit/entailment-example.json.

    python3 src/entailment_example.py

Figma 'Software Engineer - Application Platform' (6242561004) was KEPT by filter v1.0: its
words matched. Its claims are checked twice: with the v1.0 years logic (the same logic the
filter used) and with the current logic. The years claim flips from supported to contradicted:
a checker that shares the filter's definitions repeats the filter's mistake.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filter as flt  # noqa: E402
import shortlist  # noqa: E402
from postings import ROOT, load_run  # noqa: E402
from run_filter import load_skills  # noqa: E402

POSTING = ("figma", "6242561004")


def main():
    postings, _, _ = load_run("live-20261114")
    p = next(x for x in postings if (x["board"], x["id"]) == POSTING)
    v = flt.judge(p, load_skills(), flt.V1_0)
    current = flt.CURRENT
    try:
        flt.CURRENT = flt.V1_0
        with_v1_0 = shortlist.claims_for(p, v)
    finally:
        flt.CURRENT = current
    out = {"posting": {"board": p["board"], "id": p["id"], "title": p["title"], "url": p["url"]},
           "v1_0_verdict": {k: v[k] for k in ("verdict", "rule", "reason", "skills", "score")},
           "claims_checked_with_v1_0_logic": with_v1_0,
           "claims_checked_with_current_logic": shortlist.claims_for(p, v),
           "smit_hand_verdict_in_audit": "not_relevant"}
    with open(os.path.join(ROOT, "audit", "entailment-example.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    for name in ("claims_checked_with_v1_0_logic", "claims_checked_with_current_logic"):
        print(name)
        for c in out[name]:
            print(f"  [{c['checker']:12}] {c['claim']}")


if __name__ == "__main__":
    main()
