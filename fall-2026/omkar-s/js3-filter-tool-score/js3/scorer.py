"""FILTER.md sections 1 and 2 as code: gates, points, threshold, claims, evidence labels, abstention.

evaluate(posting, persona, cfg) -> record. Each rule that fires writes one justification line with
its points; the lines sum to the score (tests check this). Nothing here calls Claude or the network.
"""
import json
import os
import re

from . import textutil as tu
from .js2.persona import shipped_skills
from .js2.rule import location_ok

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# filter/CURRENT names the version in force; older versions stay for comparison (run_filter --filter).
with open(os.path.join(BASE, "filter", "CURRENT"), encoding="utf-8") as _f:
    DEFAULT_FILTER = os.path.join(BASE, "filter", _f.read().strip())
_USA_END = re.compile(r"(?<![A-Za-z])(USA|United States)$")


def load_filter(path=DEFAULT_FILTER):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _unshipped(persona):
    return list(persona["skills"].get("familiar_with_not_shipped") or [])


def evaluate(p, persona, cfg):
    w = cfg["weights"]
    title = p.get("title") or ""
    loc = (p.get("location") or {}).get("name") or ""
    offices = p.get("offices") or []
    text = tu.clean(p.get("content"))
    rec = {"id": p.get("id"), "source": p.get("source"), "company": p.get("company"), "title": title,
           "location": loc, "url": p.get("absolute_url") or "", "filter_version": cfg["version"],
           "content_chars": len(text)}

    # gates
    g1, g1_why = location_ok(loc, offices)
    if not g1 and cfg.get("G1_usa_suffix"):
        # v1.1: a location part that ends in "USA" or "United States" is a US location
        # (Datadog writes "New York, New York, USA", which JS1's location_ok rejects).
        part = next((x.strip() for x in loc.split(";") if _USA_END.search(x.strip())), None)
        if part:
            g1, g1_why = True, f'"{part}" ends in USA / United States (v1.1)'
    g2_word = tu.has_any(title, cfg["excluded_title_words"])
    my, stmts = tu.min_years(text, cfg.get("years_plus_alone", False), cfg.get("years_ignore_sub", False))
    g3 = not (my is not None and my > cfg["max_years"])
    rec["gates"] = {
        "G1": {"pass": g1, "why": g1_why},
        "G2": {"pass": g2_word is None, "why": f'title has "{g2_word}"' if g2_word else "no excluded word"},
        "G3": {"pass": g3, "min_years": my, "statements": [q for _, q in stmts][:4],
               "why": ("no years statement" if my is None else f"smallest stated minimum = {my}")},
    }

    # points
    lines = []
    role = tu.has_any(title, cfg["role_phrases"])
    nonsw = tu.has_any(title, cfg["non_software_phrases"])
    eng = tu.has_any(title, cfg["engineer_words"])
    if role:
        lines.append({"rule": "T1", "points": w["T1_role_title"], "why": f'title has "{role}"'})
    elif eng and not nonsw:
        lines.append({"rule": "T2", "points": w["T2_engineer_title"], "why": f'title has "{eng}" (no role phrase)'})
    sen = tu.has_any(title, cfg["seniority_words"])
    if sen:
        lines.append({"rule": "T3", "points": w["T3_seniority"], "why": f'title has "{sen}"'})
    found = []
    for _, s in shipped_skills(persona):
        if s.lower() not in {f.lower() for f in found} and tu.ww(s).search(text):
            found.append(s)
    counted = found[:w["K1_cap"]]
    for s in counted:
        lines.append({"rule": "K1", "points": w["K1_shipped_skill"], "why": f'content has "{s}"'})
    for s in _unshipped(persona):
        if tu.ww(s).search(text):
            lines.append({"rule": "K2", "points": w["K2_unshipped_skill"], "why": f'content has "{s}" (not shipped)'})
    entry = tu.has_any(title + " \n " + text, cfg["entry_phrases"])
    if (my is not None and my <= cfg["max_years"]) or entry:
        why = f"stated minimum {my} years" if (my is not None and my <= cfg["max_years"]) else f'"{entry}"'
        lines.append({"rule": "Y1", "points": w["Y1_level_evidence"], "why": why})
    score = round(sum(l["points"] for l in lines), 2)
    rec.update(lines=lines, score=score, skills_found=found, role_phrase=role, non_software=nonsw,
               seniority=sen, entry_phrase=entry)

    # verdict
    reasons = []
    if not title.strip() or len(text) < cfg["min_content_chars"]:
        verdict = "cannot_tell"
        reasons.append(f"AB1: posting text too short to check any claim ({len(text)} chars)")
    else:
        for g in ("G1", "G2", "G3"):
            if not rec["gates"][g]["pass"]:
                reasons.append(f"{g} failed: {rec['gates'][g]['why']}")
        if score < cfg["threshold"]:
            reasons.append(f"score {score} < threshold {cfg['threshold']}")
        verdict = "keep" if not reasons else "reject"
    rec["verdict"] = verdict
    rec["reasons"] = reasons
    gates_ok = all(rec["gates"][g]["pass"] for g in rec["gates"])
    rec["close_call"] = bool(verdict != "cannot_tell" and gates_ok and
                             abs(score - cfg["threshold"]) <= cfg["close_call_band"] and
                             score < cfg["threshold"] + cfg["close_call_band"])
    return rec


# --- section 2: claims and evidence labels -------------------------------------------------

def claims(p, rec, cfg):
    """Every claim in the justification of `rec`, labelled against the posting's own text."""
    out = []
    title, loc = rec["title"], rec["location"]
    if rec["role_phrase"]:
        out.append(_c("CL-role", "The title names a software-engineering role", "supported", "title", title))
    elif rec["non_software"]:
        out.append(_c("CL-role", "The title names a software-engineering role", "contradicted", "title", title))
    else:
        out.append(_c("CL-role", "The title names a software-engineering role", "insufficient", "title", title,
                      "only a generic engineer/developer word"))
    g1 = rec["gates"]["G1"]
    if g1["pass"]:
        out.append(_c("CL-loc", "The job is in the US", "supported", "location.name", loc, g1["why"]))
    elif loc.strip().lower() in ("", "remote", "anywhere"):
        out.append(_c("CL-loc", "The job is in the US", "insufficient", "location.name", loc or "(empty)"))
    else:
        out.append(_c("CL-loc", "The job is in the US", "contradicted", "location.name", loc, g1["why"]))
    g3 = rec["gates"]["G3"]
    my = g3["min_years"]
    if my is not None and my > cfg["max_years"]:
        out.append(_c("CL-level", "Open to someone with 3 or fewer years", "contradicted", "content",
                      g3["statements"][0] if g3["statements"] else ""))
    elif my is not None:
        out.append(_c("CL-level", "Open to someone with 3 or fewer years", "supported", "content",
                      g3["statements"][0]))
    elif rec["entry_phrase"]:
        out.append(_c("CL-level", "Open to someone with 3 or fewer years", "supported", "title/content",
                      f'"{rec["entry_phrase"]}"'))
    else:
        out.append(_c("CL-level", "Open to someone with 3 or fewer years", "insufficient", "content", "",
                      "no years statement and no entry phrase: I cannot tell"))
    segs = tu.segments(p.get("html") or p.get("content") or "", cfg["requirement_headings"], cfg["end_headings"],
                       cfg.get("plural_headings", False))
    for s in rec["skills_found"][:cfg["weights"]["K1_cap"]]:
        where, quote, head = tu.skill_context(segs, s, cfg["negations"])
        label = {"required": "supported", "negated": "contradicted"}.get(where, "insufficient")
        note = f'under heading "{head}"' if head else "no heading above it"
        if where == "outside":
            note = "mentioned, but not in a requirements section; " + note
        out.append(_c(f"CL-skill:{s}", f"The posting asks for {s}", label, "content", quote, note))
    return out


def _c(cid, text, label, field, quote, note=""):
    return {"claim": cid, "text": text, "label": label, "field": field, "quote": quote, "note": note}


def shortlist_status(cl, cfg):
    """worth_reading, or kept_cannot_tell with the abstention reasons (AB2, AB3, ...)."""
    by = {c["claim"]: c for c in cl}
    reasons = []
    if by["CL-role"]["label"] != "supported":
        reasons.append(f"role: {by['CL-role']['label']}")
    if by["CL-loc"]["label"] != "supported":
        reasons.append(f"location: {by['CL-loc']['label']}")
    if by["CL-level"]["label"] == "insufficient":
        reasons.append("AB3: level: I cannot tell from the posting")
    elif by["CL-level"]["label"] == "contradicted":
        reasons.append("level: contradicted")
    sup = sum(1 for c in cl if c["claim"].startswith("CL-skill:") and c["label"] == "supported")
    if sup < cfg["min_supported_skills"]:
        reasons.append(f"AB2: only {sup} skill claim(s) supported: the words matched, but the posting "
                       "does not say it asks for them")
    return ("worth_reading" if not reasons else "kept_cannot_tell"), reasons
