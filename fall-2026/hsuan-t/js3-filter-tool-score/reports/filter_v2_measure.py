"""Measure the FILTER.md v2 candidates A, B, C (JS3 2.1) on every saved posting and on Isaac's labels.

Why it exists: the brief wants every rule added, cut or rejected *after measuring*, with the
measurement recorded. The candidates come from the 8 disagreements in audit/AUDIT.md (2026-11-25):
  A  rule 4 also cuts a posting whose experience *ceiling* is below Aarav's years
     ("0-1 years", "no more than 18 months": new-grad roles Aarav is too experienced for; S01, S20)
  B  rule 4 reads "six (6) years" (B1), and also judges by the largest years number (B2; S16)
  C  rule 3 needs at least 2 résumé skills instead of 1 (LABELING_RULE step 3; S17, S24, S46)
  L1 (FILTER v1 §5, D2) US city names and abbreviations in profile.locations, measured on top of the
     adopted v2 code by re-judging every posting (it loosens rule 2, so it can also add postings)
Nothing here changes the rule code: v1 stays in force until Isaac picks what to adopt.

Every candidate is stricter than v1 at rule 3 or 4, so it can only turn a v1 "relevant" into
"not_relevant"; a posting v1 already cut stays cut. That is why only the v1-relevant postings are
re-checked. Reads audit/v1/all_verdicts.json (the v1 run Isaac audited), the raw files it names, the profile and the hand labels.

Run: .venv/bin/python reports/filter_v2_measure.py   -> reports/filter_v2_measure/result.md
"""

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "reports"))   # filter_v1_measure holds L1's list

from job_agent.judges.words import strip_html, years_in  # noqa: E402
from job_agent.watch.boards import ashby, greenhouse  # noqa: E402

PARSERS = {"stripe": greenhouse, "cloudflare": greenhouse, "openai": ashby}
# Ceilings a JD states for new-grad roles; months are turned into years.
_CAP_NO_MORE = re.compile(r"no more than (\d+)\s*(months?|years?)", re.I)
_CAP_RANGE = re.compile(r"\b(\d+)\s*[-–—]\s*(\d+)\s*\+?\s*(?:years?|yrs)\b", re.I)
# "six (6) years": v1's pattern stops at the ")" so the number is invisible to it.
_PAREN_YEARS = re.compile(r"\((\d+)\+?\)\s*\+?\s*(?:years?|yrs)\b", re.I)


def ceilings(jd: str) -> list[float]:
    caps = [int(n) / (12 if unit.lower().startswith("month") else 1) for n, unit in _CAP_NO_MORE.findall(jd)]
    return caps + [int(hi) for _, hi in _CAP_RANGE.findall(jd)]


def years_b(jd: str) -> list[int]:
    return years_in(jd) + [int(n) for n in _PAREN_YEARS.findall(jd)]


def cut_reason(variant: str, entry: dict, jd: str, profile: dict) -> str | None:
    """Why the variant cuts this v1-relevant posting, or None if it keeps it."""
    have, limit = profile["years_experience"], profile["years_experience"] + profile["years_stretch"]
    if variant == "A":
        low = [c for c in ceilings(jd) if c < have]
        return f"ceiling {min(low):g} years < Aarav's {have}" if low else None
    if variant in ("B1", "B2"):
        found = years_b(jd)
        if not found:
            return None
        n = min(found) if variant == "B1" else max(found)
        return f"{'min' if variant == 'B1' else 'max'} {n} years > {limit}" if n > limit else None
    if variant == "C":
        result = entry["justification"][3]["result"]
        return f"rule 3 {result.split(':')[0]} < 2" if int(result.split()[0]) < 2 else None
    raise ValueError(variant)


def l1_on_v2(postings_v1) -> list[str]:
    """L1 loosens rule 2, so unlike A/B/C it can turn cuts into passes: every posting is re-judged
    with the current (v2) rule code, once with the shipped profile and once with L1's places added."""
    from dataclasses import replace
    from job_agent import inputs
    from job_agent.common.paths import Paths
    from job_agent.judges import rule
    from filter_v1_measure import L1_EXTRA
    paths = Paths()
    base = inputs.load_criteria(paths.default_resume, paths.default_profile, paths)
    l1 = replace(base, profile=dict(base.profile, locations=base.profile["locations"] + L1_EXTRA))
    cache, rows, still_cut = {}, [], {}
    for e in postings_v1:
        if e["raw_file"] not in cache:
            cache[e["raw_file"]] = {str(p.id): p for p in PARSERS[e["board"]].parse((ROOT / e["raw_file"]).read_bytes())}
        p = cache[e["raw_file"]][str(e["posting_id"])]
        a, b = rule.judge(p, base), rule.judge(p, l1)
        if a.verdict["verdict"] != b.verdict["verdict"]:
            rows.append(f"| {e['board']} | {e['posting_id']} | {p.title} | {p.location} | {a.verdict['verdict']} → {b.verdict['verdict']} |")
        if b.failed_check == "2":
            still_cut[p.location] = still_cut.get(p.location, 0) + 1
    top = sorted(still_cut.items(), key=lambda x: -x[1])[:15]
    return [f"## L1 on top of v2 — add {L1_EXTRA} to profile.locations", "",
            f"Verdicts that change: **{len(rows)}** of {len(postings_v1)}.", "",
            "| board | posting id | title | location | v2 → v2 + L1 |", "|---|---|---|---|---|", *rows, "",
            f"Still cut at rule 2 with L1 ({sum(still_cut.values())}), most common locations:", "",
            "| location | postings |", "|---|---|", *[f"| {loc} | {n} |" for loc, n in top], ""]


def load_jds(entries):
    cache, out = {}, {}
    for e in entries:
        if e["raw_file"] not in cache:
            mod = PARSERS[e["board"]]
            cache[e["raw_file"]] = {str(p.id): p for p in mod.parse((ROOT / e["raw_file"]).read_bytes())}
        out[(e["board"], str(e["posting_id"]))] = strip_html(cache[e["raw_file"]][str(e["posting_id"])].content)
    return out


def main() -> None:
    audit = ROOT / "audit"
    all_v = json.loads((audit / "v1" / "all_verdicts.json").read_text())   # the v1 run Isaac audited
    profile = json.loads((ROOT / "personas" / "aarav-patel.profile.json").read_text())
    key = json.loads((audit / "sample_key.json").read_text())
    labels = {r["sample_id"]: r for r in csv.DictReader((audit / "hand_verdicts.csv").open())}
    relevant = [e for e in all_v["postings"] if e["verdict"] == "relevant" and e["status"] == "ok"]
    jds = load_jds(relevant)
    by_id = {(e["board"], str(e["posting_id"])): e for e in relevant}
    variants = ["A", "B1", "B2", "C"]
    cuts = {v: {k: r for k, e in by_id.items() if (r := cut_reason(v, e, jds[k], profile))} for v in variants}
    cuts["A+B2+C"] = {k: "; ".join(cuts[v][k] for v in ("A", "B2", "C") if k in cuts[v])
                      for k in set(cuts["A"]) | set(cuts["B2"]) | set(cuts["C"])}

    lines = [f"# FILTER v2 candidates — measured {len(all_v['postings'])} postings "
             f"({len(relevant)} relevant under v1), hand labels from audit/hand_verdicts.csv", "",
             "Only v1-relevant postings can change (every candidate is stricter). "
             "\"fixed\" = a hand-labeled sample where Isaac disagreed with v1 and agrees with the variant; "
             "\"broken\" = Isaac agreed with v1 and disagrees with the variant.", "",
             "| variant | v1 relevant → cut (all postings) | relevant left | hand-labeled samples: disagreements (v1 = 8) | fixed | broken |",
             "|---|---|---|---|---|---|"]
    detail = []
    for v, cut in cuts.items():
        dis, fixed, broken = 0, [], []
        for sid, k in key.items():
            pk = (k["board"], str(k["posting_id"]))
            v1 = k["verdict"]
            new = "not_relevant" if pk in cut else v1
            mine = labels[sid]["my_label"]
            dis += new != mine
            if v1 != mine and new == mine:
                fixed.append(sid)
            if v1 == mine and new != mine:
                broken.append(sid)
        lines.append(f"| {v} | {len(cut)} | {len(relevant) - len(cut)} | {dis} | {', '.join(sorted(fixed)) or '—'} | {', '.join(sorted(broken)) or '—'} |")
        detail += [f"## {v} — postings cut", "", "| board | posting id | title | why |", "|---|---|---|---|",
                   *[f"| {b} | {i} | {by_id[(b, i)]['title']} | {r} |" for (b, i), r in sorted(cut.items())], ""]
    lines += ["", "Caution: the candidates were found by reading these same hand-labeled samples, so the "
              "\"fixed\" column is not an independent test; it shows only that each variant does what it was "
              "built for. \"broken\" and the full-list cuts below are the part worth checking.", "", *detail,
              *l1_on_v2(all_v["postings"])]
    out = ROOT / "reports" / "filter_v2_measure" / "result.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines))
    print("\n".join(lines[:12]))


if __name__ == "__main__":
    main()
