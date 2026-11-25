"""What moves the score: every condition against Shreyash's held-out hand verdicts (SCORE.md).

Agreement: Relevant = hand yes, Not Relevant = hand no, I cannot tell = hand cannot tell. A hand
"cannot tell" against a yes/no answer is reported apart, never as right or wrong. An answer the
validator rejected counts as invalid, never repaired.

  python3 -m js3.score      writes results/score-v1.{json,md}
"""
import copy
import json
import pathlib

from js3 import audit_report, corpus, experiments, filtering, judge

HERE = pathlib.Path(__file__).resolve().parent.parent
MAP = {"Relevant": "yes", "Not Relevant": "no", "I cannot tell": "cannot tell"}

# One change to the filter file at a time (deterministic; no Claude). Fixed before the held-out labels.
FILTER_CHANGES = {
    "F0 filter v1 (as written)": lambda c: c,
    "F1 min skills 2 -> 1": lambda c: {**c, "rule4_min_skills": 1},
    "F2 min skills 2 -> 3": lambda c: {**c, "rule4_min_skills": 3},
    "F3 + title phrase 'Product Engineer'": lambda c: {**c, "rule1_title_phrases": c["rule1_title_phrases"] + ["Product Engineer"]},
    "F4 max years 3 -> 5": lambda c: {**c, "rule5_max_years": 5},
    "F5 no Palantir Dev alias (JS2's reading)": lambda c: {**c, "rule2_department_aliases": {}},
}


def tally(pairs):
    t = {"n": len(pairs), "agree": 0, "miss": 0, "false_positive": 0, "said_cannot_tell": 0,
         "hand_cannot_tell": 0, "invalid": 0, "unlabeled": 0}
    for answer, hand in pairs:
        if hand is None:
            t["unlabeled"] += 1
        elif answer is None:
            t["invalid"] += 1
        elif hand == "cannot tell" and answer != "cannot tell":
            t["hand_cannot_tell"] += 1
        elif answer == hand:
            t["agree"] += 1
        elif answer == "cannot tell":
            t["said_cannot_tell"] += 1
        elif hand == "yes":
            t["miss"] += 1
        else:
            t["false_positive"] += 1
    return t


def claude_conditions(keys, hand):
    postings = {p["key"]: p for p in corpus.load()}
    out = {}
    for cond in experiments.CONDITIONS:
        recs = {}
        for k in keys:
            p = experiments.path_for(cond, k)
            if p.exists():
                recs[k] = json.loads(p.read_text())
        answers = {k: (MAP[r["parsed"]["verdict"]] if r.get("parsed") else None) for k, r in recs.items()}
        t = tally([(answers.get(k), hand.get(k)) for k in keys if k in recs])
        t.update({"calls_saved": len(recs),
                  "made_up_quotes": sum(len(r.get("made_up_quotes") or []) for r in recs.values()),
                  "made_up_quotes_normalized": sum(len(judge.made_up_quotes_normalized(r["parsed"]["justification"], postings[k]))
                                                   for k, r in recs.items() if r.get("parsed")),
                  "answers_with_made_up_quotes": sum(1 for r in recs.values() if r.get("made_up_quotes")),
                  "tool_calls": sum(r.get("tool_calls") or 0 for r in recs.values()),
                  "cost_usd": round(sum(r.get("cost_usd") or 0 for r in recs.values()), 4),
                  "models": sorted({r["model"] for r in recs.values()}),
                  "first_call": min((r["called_at"] for r in recs.values()), default=None),
                  "last_call": max((r["called_at"] for r in recs.values()), default=None)})
        out[cond] = {"tally": t, "answers": answers}
    base = out.get("B", {}).get("answers", {})
    for cond, v in out.items():
        v["tally"]["differs_from_B"] = sum(1 for k, a in v["answers"].items() if k in base and a != base[k])
    return out


def filter_changes(keys, hand, audit_keys=()):
    persona = json.loads((HERE / "persona" / "alex_morgan.json").read_text())
    base = filtering.load_config(HERE / "filter-v1.json")
    postings = {p["key"]: p for p in corpus.load()}
    out = {}
    for name, change in FILTER_CHANGES.items():
        cfg = change(copy.deepcopy(base))
        ans = {k: MAP[filtering.evaluate(postings[k], persona, cfg)["verdict"]] for k in keys}
        whole = sum(1 for p in postings.values() if filtering.evaluate(p, persona, cfg)["verdict"] == "Relevant")
        out[name] = {"held_out": tally([(ans[k], hand.get(k)) for k in keys]),
                     "audit": tally([(MAP[filtering.evaluate(postings[k], persona, cfg)["verdict"]], hand.get(k))
                                     for k in audit_keys]),
                     "kept_in_corpus": whole}
    return out


def fit_min_skills(audit_keys, held_keys, hand):
    """The one number fitted on labels: rule 4's minimum, chosen on the AUDIT labels, then tested on H."""
    persona = json.loads((HERE / "persona" / "alex_morgan.json").read_text())
    base = filtering.load_config(HERE / "filter-v1.json")
    postings = {p["key"]: p for p in corpus.load()}
    rows = {}
    for m in (1, 2, 3, 4):
        cfg = {**base, "rule4_min_skills": m}
        a = tally([(MAP[filtering.evaluate(postings[k], persona, cfg)["verdict"]], hand.get(k)) for k in audit_keys])
        h = tally([(MAP[filtering.evaluate(postings[k], persona, cfg)["verdict"]], hand.get(k)) for k in held_keys])
        rows[m] = {"audit": a, "held_out": h}
    best = max(rows, key=lambda m: (rows[m]["audit"]["agree"], -abs(m - 2)))  # ties go to the hand-set value
    return {"candidates": rows, "chosen_on_audit": best}


def main(argv=()):
    sample = json.loads((HERE / "labels" / "sample.json").read_text())
    hand = {k: v["verdict"] for k, v in audit_report.load_verdicts().items()}
    held = sorted(set().union(*sample["held_out"].values()))
    aud = sorted(set().union(*sample["audit"].values()))
    out = {"held_out_keys": len(held), "held_out_labeled": sum(k in hand for k in held),
           "claude": claude_conditions(held, hand), "filter_file": filter_changes(held, hand, aud),
           "fitted": fit_min_skills(aud, held, hand)}
    (HERE / "results" / "score-v1.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"held-out labeled {out['held_out_labeled']}/{len(held)}")
    for cond, v in out["claude"].items():
        print(f"  {cond:3} {v['tally']}")
    for name, v in out["filter_file"].items():
        print(f"  {name:45} H {v['held_out']} | kept in corpus {v['kept_in_corpus']}")
    print("  fitted min skills on audit:", out["fitted"]["chosen_on_audit"])
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
