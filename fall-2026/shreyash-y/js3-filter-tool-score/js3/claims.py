"""The source-grounded justification of a kept posting (FILTER.md, evidence rules, answer 11).

The justification is a list of claims the agent makes when it tells Alex a posting is worth a look.
Each claim is labeled against the posting's own text:
  supported     a quote copied exactly from the posting states it,
  contradicted  a quote states the opposite,
  insufficient  the posting says neither.
A claim with quotes both ways is labeled contradicted and marked as a conflict.

The abstention rule (FILTER.md answer 11, with follow-up B): the agent says "I cannot tell" for the
posting when a must-have claim (role, location, experience, exclusions) is insufficient or in
conflict, or the posting text is empty; "experience not stated" is the one exception (follow-up B).

This labeler is code, so it is strict where code can be strict (a quote must exist, and a skill must
be named under the ad's own requirements, preferred or responsibilities headings and not as something
to "pick up") and blind where code is blind (it cannot tell what a sentence means). SHORTLIST.md shows
where that matters."""
import re

from jsagent import rule as js2
from js3 import filtering, sections

LEARNING_RE = re.compile(r"(?i)\b(?:open to (?:learning|picking up|learn)|willing(?:ness)? to learn|eager to learn|"
                         r"pick(?:ing)? up new|learn (?:new )?(?:technologies|tools|languages))\b")
FULL_TIME_RE = re.compile(r"(?i)\b(?:is|as) an? full[- ]time (?:position|role|job|opportunity|employee)\b|"
                          r"\bfull[- ]time,? (?:permanent|regular|salaried) (?:position|role|employee|job)\b|"
                          r"\bemployment type:?\s*full[- ]time\b|\bthis (?:is a |role is |position is )?full[- ]time\b")
PAY_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?\s*[kK]?\s*(?:[-–—]|to)\s*\$?\s?\d|"
                    r"(?i:base (?:pay|salary)|salary range|pay range|compensation range|annual salary|hourly rate)"
                    r"[^.$]{0,80}\$\s?\d")
ASKED_KINDS = {"req", "pref", "resp"}


def q(field, text):
    return {"field": field, "quote": text}


def kind_at(p, pos):
    for start, end, kind, _ in p.get("blocks") or []:
        if start <= pos < end:
            return kind
    return None


def claim(cid, text, must_have, supporting=(), contradicting=(), why="", exception=None):
    supporting, contradicting = list(supporting), list(contradicting)
    if supporting and contradicting:
        label, conflict = "contradicted", True
    elif contradicting:
        label, conflict = "contradicted", False
    elif supporting:
        label, conflict = "supported", False
    else:
        label, conflict = "insufficient", False
    return {"id": cid, "claim": text, "must_have": must_have, "label": label, "conflict": conflict,
            "supporting": supporting, "contradicting": contradicting, "why": why, "exception": exception}


def sentences(p, rx, skip_kinds=("perk", "legal")):
    text = sections.text_outside(p["content"], p.get("blocks") or [], set(skip_kinds))
    return [filtering.sentence_with(p["content"], m.start(), m.end()) for m in rx.finditer(text)]


def justify(p, rec, persona, cfg):
    r = {l["n"]: l for l in rec["rules"]}
    content = p["content"]
    out = []
    if not content.strip():
        return {"claims": [], "answer": "I cannot tell", "abstain_because": ["the posting text is empty"]}

    # 1. Role (must-have)
    phrase = js2.find_terms(cfg["rule1_title_phrases"], p["title"])
    out.append(claim("role", f"The job is a {phrase[0] if phrase else 'target'} role, one Alex is looking for.", True,
                     [q("title", p["title"])] if phrase else [], why="the title names the role" if phrase else ""))

    # 2. Department (not a must-have in the evidence rules)
    out.append(claim("department", "It sits in an engineering department.", False,
                     [e for e in r[2]["evidence"]] if r[2]["outcome"] == filtering.PASS else [],
                     why=r[2]["detail"]))

    # 3. Location (must-have)
    contra = []
    for s in sentences(p, js2.HYBRID_RE):
        if not js2.term_re(cfg["rule3_home_city"]).search(s):
            contra.append(q("content", s))
    listed, list_quotes = filtering.ad_states(content)
    if listed and cfg["rule3_home_state"] not in listed:
        contra += [q("content", s) for s in list_quotes]
    support = r[3]["evidence"] if r[3]["outcome"] == filtering.PASS else []
    out.append(claim("location", "Alex can do this job from Boston without moving.", True, support, contra,
                     why=r[3]["detail"]))

    # 4. Skills (not a must-have): named where the ad asks for skills, not as something to pick up
    text = sections.text_outside(content, p.get("blocks") or [], set(cfg["rule4_ignore_sections"]))
    asked, mentioned_only = [], []
    for skill in persona["skills"]:
        hits = list(js2.term_re(skill).finditer(text))
        if not hits:
            continue
        good = None
        for m in hits:
            s = filtering.sentence_with(content, m.start(), m.end())
            if kind_at(p, m.start()) in ASKED_KINDS and not LEARNING_RE.search(s):
                good = s
                break
        if good:
            asked.append((skill, good))
        else:
            m = hits[0]
            mentioned_only.append((skill, filtering.sentence_with(content, m.start(), m.end()), kind_at(p, m.start())))
    why = (f"asked for under the ad's requirements/preferred/responsibilities headings: {[s for s, _ in asked]}; "
           f"named only elsewhere (a tech list, the company intro) or as something to pick up: "
           f"{[s for s, _, _ in mentioned_only]}")
    out.append(claim("skills", f"It asks for at least {cfg['rule4_min_skills']} of Alex's skills.", False,
                     [q("content", s) for _, s in asked] if len(asked) >= cfg["rule4_min_skills"] else [],
                     why=why))

    # 5. Experience (must-have, follow-up B)
    mandatory = [(n, ph) for cls, n, ph in js2.year_phrases(content) if cls == "mandatory"]
    if mandatory:
        years, ph = max(mandatory)
        ok = years <= cfg["rule5_max_years"]
        out.append(claim("experience", "It asks for 3 years of experience or less.", True,
                         [q("content", ph)] if ok else [], [] if ok else [q("content", ph)],
                         why=f"the highest required minimum is {years} years"))
    else:
        out.append(claim("experience", "It asks for 3 years of experience or less.", True,
                         why="experience not stated", exception="B: not stated, kept without assuming a match"))

    # 6. Exclusions (must-have), one claim per kind of exclusion
    out.append(claim("seniority", "It is not a Director, Staff, Principal, Manager or Lead role.", True,
                     [q("title", p["title"])] if not js2.find_terms(cfg["rule6_title_words"], p["title"]) else [],
                     why="the title has none of the five words"))
    et = p.get("employment_type")
    ft = [q("employment_type", et)] if et in cfg["rule6_full_time_values"] else []
    ft += [q("content", s) for s in sentences(p, FULL_TIME_RE)][:2]
    out.append(claim("full_time", "It is a full-time, permanent job (not an internship, part-time, temporary or "
                                  "contract).", True, ft,
                     why="the board's employment type or a sentence outside the benefits and legal text"
                         if ft else "no employment type field and no sentence saying full-time outside the benefits text"))
    pay = [q("content", s) for s in sentences(p, PAY_RE, skip_kinds=("legal",))][:1]
    out.append(claim("paid", "It is a paid job.", True, pay, why="a stated pay range" if pay else "no pay stated"))
    reloc = [q("content", s) for s in sentences(p, js2.RELOCATION_RE)]
    out.append(claim("relocation", "It does not require moving away from Boston.", True,
                     support, reloc, why="the job is in Boston or remote from Massachusetts" if support else ""))

    abstain = [f"{c['id']}: {'conflicting quotes' if c['conflict'] else c['label']}" for c in out
               if c["must_have"] and not c["exception"] and (c["label"] != "supported" or c["conflict"])]
    return {"claims": out, "answer": "I cannot tell" if abstain else "reaches Alex", "abstain_because": abstain}


def verify(justification, p):
    """WV4: every quote must be in the posting field it names."""
    fake = {"rules": [{"n": i, "evidence": c["supporting"] + c["contradicting"]}
                      for i, c in enumerate(justification["claims"], 1)]}
    return filtering.verify_quotes(fake, p)
