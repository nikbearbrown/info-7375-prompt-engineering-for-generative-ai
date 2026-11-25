"""Evidence rules (FILTER.md v1.0 section 2). Each claim in a shortlist justification is labelled against the posting's
own text: SUPPORTED (stated as a requirement or duty), CONTRADICTED (the text states the opposite), INSUFFICIENT
(absent, or only nice-to-have / a plus / preferred / bonus). INSUFFICIENT means the agent says "I cannot tell".
A posting is never shortlisted on a guess: it needs at least min_skills SUPPORTED skill claims."""
import re
from js3 import filter as F

S, C, I = "SUPPORTED", "CONTRADICTED", "INSUFFICIENT"
NICE = re.compile(r"nice[- ]to[- ]haves?|\b(is|are|would be)? ?an? (big |huge |strong )?plus\b|\bpreferred\b|\bbonus\b|"
                  r"\bdesirable\b|\bnot required\b|\bideally\b|\bpreferably\b", re.I)
# A heading must START with a heading word (fix 2026-11-25: 'experience'/'skills' anywhere in a short bullet such as
# "Experience with Oracle Suite" used to count as a heading and ended the Preferred section; tests/test_evidence_regression.py)
HEADING_HINT = re.compile(r"^(preferred|minimum|basic|required|desired|additional|nice|bonus|what|who|about|responsibilities|"
                          r"qualifications|requirements|key|your|you'll|you will|in this role|the role|benefits|plus)\b", re.I)

def units(text):
    """[(sentence, in_nice_section)]: lines, then sentences; a short heading line sets the section for the lines below it."""
    out, nice_section = [], False
    for line in (text or "").splitlines():
        line = line.strip(" •·*-\t")
        if not line: continue
        if len(line) <= 60 and (line.endswith(":") or (not line.endswith(".") and HEADING_HINT.search(line) and len(line.split()) <= 6)):
            nice_section = bool(NICE.search(line))
            if line.endswith(":"): continue
        for s in re.split(r"(?<=[.!?;])\s+", line):
            if s.strip(): out.append((s.strip(), nice_section))
    return out

def _say(label, claim, quote):
    if label == S: return f'Supported: "{quote}"'
    if label == C: return f'Contradicted: "{quote}"'
    return f"I cannot tell whether the posting {claim}: " + (f'it appears only as "{quote}"' if quote else "the text does not say")

def label_skill(text, skill):
    hits = [(s, nice) for s, nice in units(text) if F.has_phrase(s, skill)]
    for s, nice in hits:
        if not nice and not NICE.search(s): return {"label": S, "quote": s, "cannot_tell": False}
    return {"label": I, "quote": hits[0][0] if hits else "", "cannot_tell": True}

def label_years(text, max_years, ignore=()):
    best = None
    for s, _ in units(text):
        for n, m in F.years_spans(s, ignore):
            if best is None or n > best[0]: best = (n, s)
    if best is None: return {"label": I, "quote": "", "cannot_tell": True}
    return {"label": S if best[0] <= max_years else C, "quote": best[1], "cannot_tell": False}

def justify(posting, cfg):
    d = F.evaluate(posting, cfg); text = posting.get("text") or ""
    j = {"id": posting.get("id"), "title": d["title"], "filter_status": d["status"], "score": d["score"], "claims": [],
         "shortlist": False, "cannot_tell": False, "why_not": ""}
    if d["status"] == "cannot_tell":
        j["cannot_tell"] = True; j["why_not"] = f"I cannot tell: {d['failed'][0]} (FILTER.md section 3)"; return j
    role = next((w for w in cfg["role_words"] if F.has_phrase(d["title"], w)), None)
    j["claims"].append({"kind": "title", "claim": "is an entry-level analyst role (title)", "source": "title",
                        "label": S if role and not d["r2_reject"] and not d.get("r1b_reject") else C, "quote": d["title"], "cannot_tell": False})
    for sk in d["skills"]:
        r = label_skill(text, sk); j["claims"].append(dict(r, kind="skill", claim=f"requires {sk}", source="text"))
    y = label_years(text, cfg["max_years"], cfg.get("years_ignore_if_followed_by", ()))
    j["claims"].append(dict(y, kind="years", claim=f"asks for at most {cfg['max_years']} years", source="text"))
    for c in j["claims"]: c["say"] = _say(c["label"], c["claim"], c["quote"])
    supported = sum(1 for c in j["claims"] if c["kind"] == "skill" and c["label"] == S)
    j["supported_skills"] = supported
    if d["status"] != "kept":
        j["why_not"] = "filter rejected: " + ", ".join(d["failed"])
    elif supported < cfg["min_skills"]:
        j["why_not"] = (f"filter kept it on word matches, but only {supported} skill claim(s) are SUPPORTED by the text; "
                        f"shortlisting it would be a guess")
    elif y["label"] == C:
        j["why_not"] = "years claim CONTRADICTED"
    else:
        j["shortlist"] = True
    return j
