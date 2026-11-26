"""The source-grounded shortlist (FILTER.md section 2). Each kept posting gets a list of claims, and each claim is labeled
supported / contradicted / insufficient against the posting's own text, with the field and the quoted span.

Relevance is not entailment: the filter counts a skill when the word appears; the claim "requires <skill>" is supported only
when a sentence states it as a requirement. "Python a plus" makes the posting relevant but leaves the claim insufficient.
"""
import re

from . import filter as flt

CANNOT = "I cannot tell from the posting"
_NOT_REQUIRED = re.compile(r"\bnot (required|necessary|needed|a requirement)\b|\b(is|are) optional\b", re.I)
_PREFERRED = re.compile(r"\b(is |are )?a plus\b|\bpreferred\b|\bnice[- ]to[- ]have\b|\bbonus\b|\bideally\b|\bdesirable\b"
                        r"|\bfamiliarity\b|\bexposure to\b", re.I)
_REQUIRED = re.compile(r"\bmust\b|\brequired\b|\brequire(s|ments?)?\b|\bqualifications?\b|\byou have\b|\byou'll have\b"
                       r"|\byou bring\b|\bexperience (with|in|using|building)\b|\bproficien|\bexpert|\bstrong\b|\bminimum\b"
                       r"|\byears\b|\bhands-on\b", re.I)


def _claim(claim, label, field, span, answer):
    return {"claim": claim, "label": label, "field": field, "span": span, "answer": answer}


def _skill_claim(word, content):
    rx = flt._word(word)
    req = pref = contra = None
    for s in flt.sentences(content):
        if not rx.search(s):
            continue
        if _NOT_REQUIRED.search(s):
            contra = contra or s
        elif _PREFERRED.search(s):
            pref = pref or s
        elif _REQUIRED.search(s):
            req = req or s
    name = f"requires {word}"
    if req:
        return _claim(name, "supported", "description", req, f"supported: \"{req}\"")
    if contra:
        return _claim(name, "contradicted", "description", contra, f"contradicted: \"{contra}\"")
    span = pref or ""
    return _claim(name, "insufficient", "description", span,
                  f"{CANNOT} that {word} is required: it is mentioned, but no sentence states it as a requirement")


def claims(r):
    out = []
    f1 = r["rules"]["F1"]
    out.append(_claim("role matches a target title", "supported" if f1["result"] == "pass" else "contradicted",
                      "title", f1["span"], f1["why"]))
    f3 = r["rules"]["F3"]
    if f3["result"] == "pass":
        out.append(_claim("location is in the US", "supported", "location", r["location"], f3["why"]))
    elif f3["result"] == "fail":
        out.append(_claim("location is in the US", "contradicted", "location", r["location"], f3["why"]))
    else:
        out.append(_claim("location is in the US", "insufficient", "location", r["location"],
                          f"{CANNOT}: {f3['why']} (field: location)"))
    content = r["content"]
    if not content:
        out.append(_claim("requires at most 5 years", "insufficient", "description", "",
                          f"{CANNOT}: there is no description (field: description)"))
    elif r["years"] is None:
        out.append(_claim("requires at most 5 years", "insufficient", "description", "",
                          f"{CANNOT}: it states no years of experience (field: description)"))
    else:
        span = next((s for s in flt.sentences(content) if r["years_phrase"] in s), r["years_phrase"])
        label = "supported" if r["years"] <= flt.MAX_YEARS else "contradicted"
        out.append(_claim("requires at most 5 years", label, "description", span, f"{label}: \"{span}\""))
    for w in r["topic_words"]:
        out.append(_skill_claim(w, content))
    if r["visa"] == "offered":
        out.append(_claim("offers visa sponsorship", "supported", "description", r["visa_span"], f"supported: \"{r['visa_span']}\""))
    elif r["visa"] == "negative":
        out.append(_claim("offers visa sponsorship", "contradicted", "description", r["visa_span"],
                          f"contradicted: \"{r['visa_span']}\""))
    else:
        out.append(_claim("offers visa sponsorship", "insufficient", "description", "",
                          f"{CANNOT}: it never mentions visa sponsorship (field: description)"))
    return out


def build(results):
    """Kept postings ranked by score (ties by board, id), each with its claims; cannot-tell postings with what is missing."""
    kept = sorted((r for r in results if r["bucket"] == "kept"), key=lambda r: (-r["score"], r["board"], r["id"]))
    return {
        "kept": [{"rank": i, "board": r["board"], "id": r["id"], "title": r["title"], "location": r["location"], "url": r["url"],
                  "score": r["score"], "score_parts": r["score_parts"], "claims": claims(r)} for i, r in enumerate(kept, 1)],
        "cannot_tell": [{"board": r["board"], "id": r["id"], "title": r["title"], "location": r["location"],
                         "missing": r["missing"] or [k for k, v in r["rules"].items() if v["result"] == "cannot_tell"],
                         "why": [v["why"] for v in r["rules"].values() if v["result"] == "cannot_tell"]}
                        for r in results if r["bucket"] == "cannot_tell"],
    }
