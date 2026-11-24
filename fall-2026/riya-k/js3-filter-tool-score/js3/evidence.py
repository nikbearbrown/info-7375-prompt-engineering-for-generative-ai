"""FILTER.md §2 evidence rules: label each claim supported / contradicted / insufficient against the posting's own text.

Each claim carries the exact quote it rests on (or None). Absence of a word is never a contradiction.
C2 contradiction ("X is not needed") is left to the hand check, as FILTER.md says.
"""

import re

from .text import find_span, find_word, plain_text, names_us_place, names_non_us_place


def us_city(location, flt):
    """v1.1 option: US city names (e.g. 'San Francisco') count as a US place. v1 has none."""
    return any(find_word(c, location) for c in flt.get("location", {}).get("us_cities", []))

YEARS = re.compile(r"(?<![\d.])(\d{1,2})\s*(?:\+|plus)?\s*(?:(?:-|–|to)\s*\d{1,2}\s*\+?\s*)?(?:years?|yrs)\b", re.I)
# v1.1 (2026-11-24): also "8 or more years", "five years" (Riya found "8 or more years" missed on card #41).
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
         "twelve": 12, "fifteen": 15}
_N = r"(\d{1,2}|" + "|".join(WORDS) + r")"
YEARS_V11 = re.compile(r"(?<![\d.])\b" + _N + r"\s*(?:\+|plus)?\s*(?:(?:-|–|to)\s*" + _N + r"\s*\+?\s*)?"
                       r"(?:or\s+more\s+|or\s+greater\s+)?(?:years?|yrs)\b", re.I)
NOT_FT_TEXT = ["part-time", "part time", "contract role", "temporary", "internship"]


def _quote(text, span, pad=60):
    if span is None:
        return None
    a, b = span
    return ("…" if a > pad else "") + text[max(0, a - pad): b + pad].strip() + ("…" if b + pad < len(text) else "")


def stated_years(text, pattern="v1"):
    """Every 'N years' (or 'N+ years', 'N-M years') with 'experience' within 80 characters after it: (N, quote)."""
    out = []
    for m in (YEARS_V11 if pattern == "v1.1" else YEARS).finditer(text):
        g = m.group(1).lower()
        n = WORDS[g] if g in WORDS else int(g)
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

    if names_us_place(location) or us_city(location, flt):
        lab = "supported"
    elif names_non_us_place(location):
        lab = "contradicted"
    else:
        lab = "insufficient"
    out.append({"claim": "C3 it is in the US", "label": lab, "evidence": f"location: '{location}'", "source": "location"})

    yrs = stated_years(text, flt["evidence"].get("years_pattern", "v1"))
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
