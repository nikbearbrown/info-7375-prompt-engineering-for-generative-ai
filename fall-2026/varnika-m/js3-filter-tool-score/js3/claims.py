"""The evidence rules of FILTER.md section 2: each claim is supported, contradicted or insufficient,
judged only against the posting's own text, with the quote that decides it."""

import html
import re

from js3 import rule
from js3.filter import text_of

EARLY = re.compile(r"(?i)\b(new grads?|new graduates?|entry[- ]level|early[- ]career|junior|recent graduates?|"
                   r"university graduates?)\b")
ASKS = re.compile(r"(?i)\b(you have|you'll have|have experience|experience (?:with|in|using|building)|proficien\w*|"
                  r"require\w*|must|strong|fluency|fluent|expertise|knowledge of|familiarity with|background in|"
                  r"skills? (?:in|with))\b")
NICE = re.compile(r"(?i)\b(plus|nice[- ]to[- ]have|preferred|bonus|ideally|not required)\b")
CORE = ("C1", "C3", "C4")  # FILTER.md D2: any of these insufficient -> "I cannot tell"


def sentences(posting):
    markup = html.unescape(posting.get("content") or "")
    out = []
    for part in re.split(r"(?i)</li>|</p>|<br\s*/?>|</h[1-6]>|\n", markup):
        for sentence in re.split(r"(?<=[.!?])\s+", text_of(part)):
            if sentence:
                out.append(sentence)
    return out


def claim(cid, text, label, quote=None, why=""):
    return {"claim": cid, "text": text, "label": label, "quote": quote, "why": why}


def years_quotes(posting):
    found = []
    for sentence in sentences(posting):
        for item in rule.years_phrases(sentence):
            found.append((item["years"], item["phrase"], sentence))
    return found


def label_claims(posting, result):
    checks = {c["rule"]: c for c in result["checks"]}
    title = posting.get("title") or ""
    out = []

    role = [p for p in rule.TITLE_PHRASES if rule.term_pattern(p).search(title)]
    out.append(claim("C1", "It is a software engineering role of his kind",
                     "supported" if role else "insufficient", title if role else None,
                     ('the title contains "%s"' % role[0]) if role else "no role phrase in the title"))

    years = years_quotes(posting)
    high = [y for y in years if y[0] > rule.MAX_YEARS]
    low = [y for y in years if y[0] <= rule.MAX_YEARS]
    early = next((s for s in [title] + sentences(posting) if EARLY.search(s)), None)
    senior = checks["R2"]["excluded_words_found"]
    if senior or high:
        out.append(claim("C2", "It is open to an early-career engineer", "contradicted",
                         title if senior else high[0][2],
                         ("seniority word in the title: %s" % ", ".join(senior)) if senior
                         else '"%s" asks for more than %d years' % (high[0][1], rule.MAX_YEARS)))
    elif early or low:
        out.append(claim("C2", "It is open to an early-career engineer", "supported",
                         early or low[0][2], "early-career wording" if early else '"%s"' % low[0][1]))
    else:
        out.append(claim("C2", "It is open to an early-career engineer", "insufficient", None,
                         "no early-career wording and no years phrase"))

    us = checks["R3"]["us_locations"]
    out.append(claim("C3", "It can be done from the United States", "supported" if us else "insufficient",
                     "; ".join(us) if us else None, "location.name" if us else "no US place in location.name"))

    if high:
        out.append(claim("C4", "It asks for 3 years or fewer", "contradicted", high[0][2], '"%s"' % high[0][1]))
    elif low:
        out.append(claim("C4", "It asks for 3 years or fewer", "supported", low[0][2], '"%s"' % low[0][1]))
    else:
        out.append(claim("C4", "It asks for 3 years or fewer", "insufficient", None,
                         "no years phrase anywhere: nothing shows that 29 months is enough"))

    for skill in result["skills"]:
        pattern = rule.term_pattern(skill)
        hits = [s for s in sentences(posting) if pattern.search(s)] or ([title] if pattern.search(title) else [])
        asked = [s for s in hits if ASKS.search(s) and not NICE.search(s)]
        if asked:
            out.append(claim("C5", "It asks for %s" % skill, "supported", asked[0], "asked for in this sentence"))
        else:
            out.append(claim("C5", "It asks for %s" % skill, "insufficient", hits[0] if hits else None,
                             "the word appears, but not as something the job asks for"))
    return out


def answer(claims):
    """FILTER.md D2: "I cannot tell" if a core claim is insufficient; never "fits" without evidence."""
    missing = [c for c in claims if c["claim"] in CORE and c["label"] == "insufficient"]
    against = [c for c in claims if c["label"] == "contradicted"]
    if against:
        return {"answer": "does not fit", "because": [c["text"] for c in against]}
    if missing:
        return {"answer": "I cannot tell", "because": ["no evidence: " + c["text"] for c in missing]}
    return {"answer": "fits by the evidence rules (the decision is mine)", "because": []}
