"""The measurements behind FILTER.md v1.1's decisions A2 and A3 (AUDIT.md section 5), saved so they can be
rerun: each candidate applied to filter v1's records, compared with Shreyash's labels on the audit set
and the held-out set, and counted over the corpus. (A1, A4 and A5 are filter-file entries; their numbers
come from js3/score.py and from the v1.1 run itself.)

  python3 -m js3.whatif      writes results/whatif-v1.json
"""
import copy
import json
import pathlib

from jsagent import rule as js2
from js3 import audit_report, claims, corpus, filtering, sections

HERE = pathlib.Path(__file__).resolve().parent.parent
MAP = {"Relevant": "yes", "Not Relevant": "no", "I cannot tell": "cannot tell"}


def recompute(r):
    f = [l["n"] for l in r["rules"] if l["outcome"] == "fail"]
    u = [l["n"] for l in r["rules"] if l["outcome"] == "cannot tell"]
    r["failed"], r["unsure"] = f, u
    r["verdict"] = "Not Relevant" if f else ("I cannot tell" if u else "Relevant")
    return r


def a2_sql_family(p, r, persona, cfg):
    r = copy.deepcopy(r)
    text = sections.text_outside(p["content"], p["blocks"], {"perk"})
    hits = [s for s in persona["skills"] if js2.term_re(s).search(text)]
    if "SQL" not in hits and any(js2.term_re(t).search(text) for t in ("MySQL", "PostgreSQL", "Postgres")):
        hits.append("SQL")
    r["rules"][3]["outcome"] = "pass" if len(hits) >= cfg["rule4_min_skills"] else "fail"
    return recompute(r)


def a3_asked_only(p, r, persona, cfg):
    r = copy.deepcopy(r)
    if r["rules"][3]["outcome"] == "pass":
        skills = [c for c in claims.justify(p, r, persona, cfg)["claims"] if c["id"] == "skills"][0]
        if skills["label"] != "supported":
            r["rules"][3]["outcome"] = "fail"
    return recompute(r)


def more_numbers(persona, cfg, posts, base, sets, hand):
    """Numbers the documents cite that no other script wrote down (added after the independent review of
    2026-11-25): the comparison with JS2's rule, closest calls per filter change, the Claude conditions'
    differences from B, and the v1.1 shortlist's skills labels."""
    from jsagent import rule as js2rule
    from js3 import experiments
    out = {}
    js2 = {k: js2rule.judge(p, persona) for k, p in posts.items()}
    same = sum((base[k]["verdict"] == "Relevant") == (js2[k]["verdict"] == "Relevant") for k in posts)
    ct = [k for k in posts if base[k]["rules"][2]["outcome"] == "cannot tell"]
    out["v1_vs_js2_rule"] = {"postings": len(posts), "same_verdict": same, "rule3_cannot_tell": len(ct),
                             "of_those_js2_failed_condition_3": sum(3 in js2[k]["failed_conditions"] for k in ct)}
    changes = {"F0 v1": {}, "F1 min skills 1": {"rule4_min_skills": 1}, "F2 min skills 3": {"rule4_min_skills": 3},
               "F3 + Product Engineer": {"rule1_title_phrases": cfg["rule1_title_phrases"] + ["Product Engineer"]},
               "F4 max years 5": {"rule5_max_years": 5}, "F5 no Dev alias": {"rule2_department_aliases": {}}}
    table = {}
    for name, patch in changes.items():
        c = dict(cfg, **patch)
        recs = [filtering.evaluate(p, persona, c) for p in posts.values()]
        table[name] = {"kept": sum(r["verdict"] == "Relevant" for r in recs), "closest_calls": sum(r["closest_call"] for r in recs)}
    drop2 = []
    for k in posts:
        r = copy.deepcopy(base[k]); r["rules"][1]["outcome"] = "pass"; drop2.append(recompute(r))
    table["drop Rule 2"] = {"kept": sum(r["verdict"] == "Relevant" for r in drop2),
                            "closest_calls": sum(len(r["failed"]) == 1 and not r["unsure"] for r in drop2)}
    out["filter_changes_corpus"] = table
    held = sets["held_out"]
    conds = {}
    load = lambda c: {k: json.loads(experiments.path_for(c, k).read_text()) for k in held if experiments.path_for(c, k).exists()}
    B = load("B")
    for c in experiments.CONDITIONS:
        R = load(c)
        both = [k for k in R if R[k].get("parsed") and B[k].get("parsed")]
        pal = [k for k in R if k.startswith("palantir:") and R[k].get("parsed")]
        dev = [k for k in pal if posts[k]["departments"] == ["Dev"]]
        conds[c] = {"valid": sum(1 for r in R.values() if r.get("parsed")),
                    "verdict_differs_from_B": sum(R[k]["parsed"]["verdict"] != B[k]["parsed"]["verdict"] for k in both),
                    "failed_conditions_differ_from_B": sum(sorted(R[k]["parsed"]["failed_conditions"]) != sorted(B[k]["parsed"]["failed_conditions"]) for k in both),
                    "wording_differs_from_B": sum(R[k]["parsed"]["justification"] != B[k]["parsed"]["justification"] for k in both),
                    "palantir_postings": len(pal), "palantir_failing_department": sum(2 in R[k]["parsed"]["failed_conditions"] for k in pal),
                    "palantir_dev_postings": len(dev), "palantir_dev_failing_department": sum(2 in R[k]["parsed"]["failed_conditions"] for k in dev),
                    "cost_usd": round(sum(r.get("cost_usd") or 0 for r in R.values()), 4)}
    out["claude_conditions_vs_B"] = conds
    held_rejects = [k for k in held if base[k]["verdict"] == "Not Relevant"]
    out["held_out_rejects_by_failed_rules"] = {
        "only_location": sum(base[k]["failed"] == [3] for k in held_rejects),
        "only_experience": sum(base[k]["failed"] == [5] for k in held_rejects),
        "several_rules": sum(len(base[k]["failed"]) > 1 for k in held_rejects), "total": len(held_rejects)}
    v11 = filtering.load_config(HERE / "filter-v1.1.json")
    sl = []
    for k, p in posts.items():
        r = filtering.evaluate(p, persona, v11)
        if r["verdict"] != "Relevant":
            continue
        j = claims.justify(p, r, persona, v11)
        skills = [c for c in j["claims"] if c["id"] == "skills"][0]
        ft = [c for c in j["claims"] if c["id"] == "full_time"][0]
        sl.append({"key": k, "answer": j["answer"], "skills_label": skills["label"], "full_time_label": ft["label"],
                   "answer_if_skills_were_a_must_have": "I cannot tell" if (j["answer"] == "I cannot tell" or skills["label"] != "supported") else "reaches Alex"})
    out["shortlist_v1_1"] = sl
    return out


def main(argv=()):
    persona = json.loads((HERE / "persona" / "alex_morgan.json").read_text())
    cfg = filtering.load_config(HERE / "filter-v1.json")
    posts = {p["key"]: p for p in corpus.load()}
    sample = json.loads((HERE / "labels" / "sample.json").read_text())
    hand = {k: v["verdict"] for k, v in audit_report.load_verdicts().items()}
    sets = {"audit": sorted(set().union(*sample["audit"].values())),
            "held_out": sorted(set().union(*sample["held_out"].values()))}
    base = {k: filtering.evaluate(p, persona, cfg) for k, p in posts.items()}
    out = {}
    for name, fn in (("v1", lambda p, r, pe, c: r), ("A2 SQL family", a2_sql_family), ("A3 asked-for skills only", a3_asked_only)):
        recs = {k: fn(posts[k], base[k], persona, cfg) for k in posts}
        entry = {"kept_in_corpus": sorted(k for k, r in recs.items() if r["verdict"] == "Relevant")}
        for s, keys in sets.items():
            pairs = [(MAP[recs[k]["verdict"]], hand[k]) for k in keys]
            entry[s] = {"n": len(keys), "agree": sum(a == h for a, h in pairs),
                        "miss": sum(a == "no" and h == "yes" for a, h in pairs),
                        "false_positive": sum(a == "yes" and h == "no" for a, h in pairs)}
        out[name] = entry
    out["_more"] = more_numbers(persona, cfg, posts, base, sets, hand)
    (HERE / "results" / "whatif-v1.json").write_text(json.dumps(out, indent=1) + "\n")
    for name, e in out.items():
        if name == "_more":
            continue
        print(f"{name:26} kept {len(e['kept_in_corpus'])} | audit {e['audit']} | held-out {e['held_out']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
