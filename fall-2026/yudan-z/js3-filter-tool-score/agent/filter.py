"""JS3 filter (FILTER.md). Reads only the versioned rule file and the posting's own title, location and text.

score(posting, cfg) -> {"score", "decision": keep | reject | cannot tell, "keep", "abstain", "abstain_reasons",
                        "parts", "claims": [{"claim", "label": supported | contradicted | insufficient, "evidence"}]}
"""
import json
import re

from agent.rule import CITIZEN, EEO, NO_SPONSOR, _segment_is_us, sentences, stated_minimums, word_in

MIN_TEXT = 200
SPONSOR_WORDS = ["sponsor", "sponsorship", "visa", "visas", "work authorization"]


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


VISA_WORDS = ["visa", "visas", "immigration", "H-1B", "H1B", "work authorization"]
NEGATION = re.compile(r"(not|no|unable|cannot|can't|won't|without|ineligible)|n't", re.I)


def _strict_sponsor_sentence(text):
    """A sentence that says sponsorship of a visa is available: a sponsor word AND a visa word, no negation."""
    for s in sentences(text):
        if (word_in("sponsor", s) or word_in("sponsorship", s) or word_in("sponsors", s))                 and any(word_in(v, s) for v in VISA_WORDS) and not NEGATION.search(s):
            return s[:220]
    return ""


def _sentence_with(text, words):
    for s in sentences(text):
        if any(word_in(w, s) for w in words):
            return s[:220]
    return ""


def score(posting, cfg):
    title, loc, text = posting.get("title", ""), (posting.get("location") or ""), posting.get("text", "")
    w = cfg["weights"]

    role = [r for r in cfg["role_words"] if word_in(r, title)]
    exact = set(cfg.get("case_sensitive_topics", []))
    topics = sorted({t for t in cfg["topic_words"]
                     if (re.search(r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])", text) if t in exact
                         else word_in(t, text))}, key=str.lower)
    senior = [s for s in cfg["senior_words"] if word_in(s, title)]
    mins = stated_minimums(text)
    years3 = [m for m in mins if m >= 3]
    us = bool(loc.strip()) and any(_segment_is_us(seg) for seg in loc.split(";"))
    no_sponsor = [p for p in NO_SPONSOR + cfg.get("extra_no_sponsor", []) if word_in(p, text)]
    citizen = sorted({p for s in sentences(text) if not any(e in s.lower() for e in EEO)
                      for p in CITIZEN + cfg.get("extra_citizen", []) if word_in(p, s)})
    edu = [e for e in cfg.get("education_title_words", []) if word_in(e, title)]

    total = (w["role"] if role else 0) + w["topic_each"] * min(len(topics), w["topic_cap"])
    total += w["senior"] if senior else 0
    total += w["years_3plus"] if years3 else 0
    total += w["not_us"] if (loc.strip() and not us) else 0
    total += w["sponsor_or_citizen"] if (no_sponsor or citizen) else 0
    total += w.get("education", 0) if edu else 0

    claims = []

    def add(name, label, evidence):
        claims.append({"claim": name, "label": label, "evidence": evidence})

    add("the title names a target role", "supported" if role else "insufficient",
        f"title '{title}' contains {role}" if role else f"title '{title}' contains no target role word")
    if not loc.strip():
        add("the job is in the US", "insufficient", "location is empty")
    else:
        add("the job is in the US", "supported" if us else "contradicted", f"location '{loc}'")
    add("the posting asks for skills the persona has", "supported" if topics else "insufficient",
        f"topic words found: {topics}" if topics else "no topic word found")
    add("the title is not senior", "contradicted" if senior else "supported", f"title '{title}' senior words: {senior or 'none'}")
    if years3 or (cfg.get("experience_claim") == "strict" and any(m >= 1 for m in mins)):
        add("the stated experience fits a new graduate", "contradicted", f"stated minimum years: {mins}")
    elif mins:
        add("the stated experience fits a new graduate", "supported", f"stated minimum years: {mins}")
    else:
        add("the stated experience fits a new graduate", "insufficient", "no stated minimum found")
    if edu:
        add("the degree asked for fits the persona", "contradicted", f"title '{title}' words: {edu}")
    if no_sponsor or citizen:
        add("the posting does not rule out sponsorship", "contradicted", f"phrases: {no_sponsor + citizen}")
    else:
        s = _strict_sponsor_sentence(text) if cfg.get("sponsor_support") == "strict" else _sentence_with(text, SPONSOR_WORDS)
        add("the posting does not rule out sponsorship", "supported" if s else "insufficient",
            f"'{s}'" if s else ("no sentence says visa sponsorship is available" if cfg.get("sponsor_support") == "strict"
                                else "the posting never mentions sponsorship, visas or work authorization"))

    reasons = []
    if len(text) < MIN_TEXT:
        reasons.append(f"description shorter than {MIN_TEXT} characters")
    if not loc.strip():
        reasons.append("location is empty")
    if total >= cfg["threshold"] and claims[-1]["label"] == "insufficient":
        reasons.append("sponsorship: I cannot tell")
    abstain = bool(reasons)
    keep = total >= cfg["threshold"] and not abstain
    decision = "cannot tell" if abstain else ("keep" if keep else "reject")
    return {"key": posting.get("key"), "score": total, "decision": decision, "keep": keep, "abstain": abstain,
            "abstain_reasons": reasons,
            "parts": {"role": role, "topics": topics, "senior": senior, "years": mins, "us": us,
                      "no_sponsor": no_sponsor, "citizen": citizen, "education": edu},
            "claims": claims}
