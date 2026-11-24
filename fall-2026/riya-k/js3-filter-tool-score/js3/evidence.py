"""FILTER.md §2 evidence rules: label each claim supported / contradicted / insufficient against the posting's own text.

Each claim carries the exact quote it rests on (or None). Absence of a word is never a contradiction.
C2 contradiction ("X is not needed") is left to the hand check, as FILTER.md says.
"""

import re

from .text import find_span, plain_text, names_us_place, names_non_us_place

YEARS = re.compile(r"(?<![\d.])(\d{1,2})\s*(?:\+|plus)?\s*(?:(?:-|–|to)\s*\d{1,2}\s*\+?\s*)?(?:years?|yrs)\b", re.I)
NOT_FT_TEXT = ["part-time", "part time", "contract role", "temporary", "internship"]


def _quote(text, span, pad=60):
    if span is None:
        return None
    a, b = span
    return ("…" if a > pad else "") + text[max(0, a - pad): b + pad].strip() + ("…" if b + pad < len(text) else "")


def stated_years(text):
    """Every 'N years' (or 'N+ years', 'N-M years') with 'experience' within 80 characters after it: (N, quote)."""
    out = []
    for m in YEARS.finditer(text):
        n = int(m.group(1))
        if n == 0 or n > 20:
            continue
        if "experience" in text[m.end(): m.end() + 80].lower():
            out.append((n, _quote(text, m.span(), 40)))
    return out


def claims(posting, flt):
    title = posting.get("title", "")
    location = (posting.get("location") or {}).get("name", "")
    text = plain_text(posting.get("content", ""))
    body = title + " " + text
    out = []

    role = [w for w in flt["score"]["role"]["words"] if find_span(w, title)]
    out.append({"claim": "C1 it is an AI/data role", "label": "supported" if role else "insufficient",
                "evidence": f"title: '{title}'" if role else None, "source": "title"})

    for s in flt["score"]["skill"]["words"]:
        span = find_span(s, body)
        if span:
            out.append({"claim": f"C2 it asks for {s}", "label": "supported", "evidence": _quote(body, span), "source": "text"})

    if names_us_place(location):
        lab = "supported"
    elif names_non_us_place(location):
        lab = "contradicted"
    else:
        lab = "insufficient"
    out.append({"claim": "C3 it is in the US", "label": lab, "evidence": f"location: '{location}'", "source": "location"})

    yrs = stated_years(text)
    if not yrs:
        out.append({"claim": "C4 it fits an early-career candidate", "label": "insufficient",
                    "evidence": None, "source": "text", "note": "I cannot tell: no years of experience stated (A4)"})
    else:
        n, q = min(yrs, key=lambda t: t[0])
        lab = "supported" if n <= flt["evidence"]["max_years_early_career"] else "contradicted"
        out.append({"claim": "C4 it fits an early-career candidate", "label": lab, "evidence": q, "source": "text",
                    "note": f"smallest stated years = {n}"})

    emp = posting.get("employment")
    ft_span = find_span("full-time", text) or find_span("full time", text)
    nft = [w for w in NOT_FT_TEXT if find_span(w, text)]
    if emp is not None:
        lab, ev = ("supported", f"employmentType: {emp}") if emp == "FullTime" else ("contradicted", f"employmentType: {emp}")
    elif nft:
        lab, ev = "contradicted", _quote(text, find_span(nft[0], text))
    elif ft_span:
        lab, ev = "supported", _quote(text, ft_span)
    else:
        lab, ev = "insufficient", None
    out.append({"claim": "C5 it is full-time", "label": lab, "evidence": ev, "source": "employmentType/text"})
    return out
