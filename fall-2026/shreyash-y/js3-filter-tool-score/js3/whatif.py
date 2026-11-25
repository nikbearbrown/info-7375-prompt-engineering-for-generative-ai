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
    (HERE / "results" / "whatif-v1.json").write_text(json.dumps(out, indent=1) + "\n")
    for name, e in out.items():
        print(f"{name:26} kept {len(e['kept_in_corpus'])} | audit {e['audit']} | held-out {e['held_out']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
